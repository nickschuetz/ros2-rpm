#!/usr/bin/env python3
"""copr-drive.py, dependency-ordered COPR build driver for one distro.

Submits each spec to its distro's COPR project as soon as all of its in-tree
ros-<distro>- dependencies have succeeded, so a full tree builds in topological
order without hand-sequencing waves. Idempotent: packages already succeeded or
currently building are skipped.

Usage:
    scripts/copr-drive.py --distro lyrical            # submit the ready wave
    scripts/copr-drive.py --distro lyrical --dry-run  # show the plan only
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import distros

ACTIVE = {"running", "pending", "starting", "importing", "waiting", "forked"}

# A freshly-submitted build does not appear in `copr-cli list-packages
# --with-latest-build` (or `monitor`) until COPR finishes importing its SRPM and
# registers the package, which can lag several minutes. Without a memory of what
# we just submitted, the driver would see such packages as neither succeeded nor
# active and re-submit them every tick (thrash + duplicate builds). A local
# ledger records the submit time per package; a package submitted within
# SUBMIT_COOLDOWN seconds is skipped unless COPR already reports it as failed
# (in which case we want to resubmit the fix).
SUBMIT_COOLDOWN = 3600


def _ledger_path(build: Path, distro: str) -> Path:
    return build / f".copr-submitted-{distro}.json"


def load_ledger(build: Path, distro: str) -> dict:
    p = _ledger_path(build, distro)
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def save_ledger(build: Path, distro: str, ledger: dict) -> None:
    p = _ledger_path(build, distro)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ledger))


def spec_meta(spec: Path, distro: str) -> dict:
    text = spec.read_text()
    def find(pat, default=None):
        m = re.search(pat, text, re.M)
        return m.group(1) if m else default
    pkg_name = find(r"^%global pkg_name\s+(\S+)")
    version = find(r"^Version:\s+(\S+)")
    name = find(r"^Name:\s+(\S+)")
    # Resolve the RPM Name (ros-<distro>-<x>) by expanding the common macros.
    if name:
        name = name.replace("%{ros_distro}", distro).replace("%{pkg_name}",
                 (pkg_name or "")).replace("-%{pkg_name}", "-" + (pkg_name or ""))
    src0 = find(r"^Source0:\s+(\S+)")
    src_url = src0.split("#")[0] if src0 else None
    if src_url and version:
        src_url = src_url.replace("%{version}", version)
    # The %autosetup -n dir is the tarball top-dir the build cd's into; cache
    # validation compares against it so a stale same-named tarball (e.g. a Jazzy
    # tarball cached under the same <pkg>-<version> name) is detected + refetched.
    topdir = find(r"^%autosetup[^\n]*-n\s+(\S+)")
    if topdir and version:
        topdir = topdir.replace("%{version}", version).replace("%{pkg_name}", pkg_name or "")
    deps = set(re.findall(rf"^(?:Requires|BuildRequires):\s+(ros-{distro}-\S+)", text, re.M))
    # Patch files (relative paths under specs/<distro>/patches/) get staged into
    # _sourcedir so rpmbuild -bs can include them in the SRPM.
    patches = re.findall(r"^Patch\d+:\s+(\S+)", text, re.M)
    return {"spec": spec, "rpm_name": name, "pkg_name": pkg_name,
            "version": version, "src_url": src_url, "topdir": topdir,
            "patches": patches, "deps": deps}


def copr_states(project: str) -> dict[str, str]:
    r = subprocess.run(["copr-cli", "list-packages", project, "--with-latest-build"],
                       capture_output=True, text=True, check=True)
    out = {}
    for p in json.loads(r.stdout):
        lb = p.get("latest_build") or {}
        out[p["name"]] = lb.get("state") or "none"
    return out


def _topdir_matches(target: Path, expected: str | None) -> bool:
    """True if the tarball's top-level dir matches the expected %autosetup -n dir."""
    if not expected:
        return True  # nothing to check against; trust the cache
    import tarfile
    try:
        with tarfile.open(target) as t:
            first = next((m.name for m in t), "")
        return first.split("/")[0] == expected
    except Exception:
        return False


def ensure_source(meta: dict, sources: Path) -> bool:
    """Fetch Source0 into build/SOURCES/<pkg>-<ver>.tar.gz, refetching if stale.

    The cache key (<pkg>-<version>.tar.gz) omits the distro/release counter, so a
    same-version tarball from another distro can collide. Validate the cached
    tarball's top-dir against the spec's %autosetup -n and refetch on mismatch.
    """
    # Metapackages (ros_core/ros_base) carry a local Source0 with no URL scheme:
    # a stub tarball rpmbuild requires to exist but %prep ignores. Stage an empty
    # one at the Source0 basename so the driver can build them like any other.
    if meta["src_url"] and "://" not in meta["src_url"]:
        import io, tarfile
        stub = sources / Path(meta["src_url"]).name
        if not stub.is_file():
            with tarfile.open(stub, "w:gz"):
                pass
        return True
    if not (meta["src_url"] and meta["pkg_name"] and meta["version"]):
        return False
    target = sources / f"{meta['pkg_name']}-{meta['version']}.tar.gz"
    if target.is_file() and _topdir_matches(target, meta.get("topdir")):
        return True
    try:
        data = urllib.request.urlopen(meta["src_url"], timeout=90).read()
        target.write_bytes(data)
        return True
    except Exception as e:
        sys.stderr.write(f"  fetch failed for {meta['pkg_name']}: {str(e)[:80]}\n")
        return False


def build_and_submit(meta: dict, project: str, build: Path, dry: bool) -> str | None:
    sources, srpms = build / "SOURCES", build / "SRPMS"
    sources.mkdir(parents=True, exist_ok=True)
    srpms.mkdir(parents=True, exist_ok=True)
    if not ensure_source(meta, sources):
        return None
    # Stage Patch files into _sourcedir (preserving their relative path) so
    # rpmbuild -bs includes them in the SRPM.
    import shutil
    patches_root = meta["spec"].parent / "patches"
    for rel in meta.get("patches", []):
        src = patches_root / rel
        # rpm resolves Patch paths by basename in _sourcedir, so stage flat even
        # though the Patch tag and verify-specs use the patches/<pkg>/ subpath.
        dst = sources / Path(rel).name
        if src.is_file():
            shutil.copy2(src, dst)
        else:
            sys.stderr.write(f"  patch missing for {meta['rpm_name']}: {src}\n")
            return None
    if dry:
        return "would-submit"
    r = subprocess.run(
        ["rpmbuild", "-bs", "--define", f"_topdir {build}",
         "--define", f"_sourcedir {sources}", "--define", f"_srcrpmdir {srpms}",
         str(meta["spec"])], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(f"  SRPM build failed for {meta['rpm_name']}: {r.stderr.strip()[:120]}\n")
        return None
    srpm = sorted(srpms.glob(f"{meta['rpm_name']}-*.src.rpm"),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    if not srpm:
        return None
    s = subprocess.run(["copr-cli", "build", "--nowait", project, str(srpm[0])],
                       capture_output=True, text=True)
    return "submitted" if s.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--distro", choices=distros.DISTROS, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    project = distros.copr_project(args.distro)
    build = distros.REPO_ROOT / "build"
    specs = [spec_meta(s, args.distro) for s in sorted(distros.spec_dir(args.distro).glob("*.spec"))]
    by_name = {m["rpm_name"]: m for m in specs if m["rpm_name"]}
    states = copr_states(project)

    succeeded = {n for n, s in states.items() if s == "succeeded"}
    active = {n for n, s in states.items() if s in ACTIVE}
    failed = {n for n, s in states.items() if s == "failed"}

    ledger = load_ledger(build, args.distro)
    now = time.time()
    # A package we submitted recently but that COPR has not registered yet (so it
    # is absent from `states`) is treated as in-flight, not re-submitted. Once it
    # surfaces as failed, drop it from the ledger so a fix can be resubmitted.
    cooling = {n for n, t in ledger.items()
               if now - t < SUBMIT_COOLDOWN and n not in succeeded and n not in failed}
    for n in list(ledger):
        if n in succeeded or n in failed:
            ledger.pop(n, None)

    ready = []
    for m in specs:
        n = m["rpm_name"]
        if not n or n in succeeded or n in active or n in cooling:
            continue
        # only build deps that are in our tree; all must be succeeded
        intree = {d for d in m["deps"] if d in by_name}
        if intree <= succeeded:
            ready.append(m)

    submitted = []
    for m in ready:
        res = build_and_submit(m, project, build, args.dry_run)
        if res:
            submitted.append(m["rpm_name"])
            if not args.dry_run:
                ledger[m["rpm_name"]] = time.time()

    if not args.dry_run:
        save_ledger(build, args.distro, ledger)

    total = len(specs)
    done = len(succeeded & set(by_name))
    # In-flight = COPR-reported active plus packages just submitted this run and
    # those still cooling down (submitted recently, not yet registered by COPR).
    inflight = (active & set(by_name)) | cooling | set(submitted)
    print(f"[{args.distro}] succeeded {done}/{total} | building {len(inflight)} | "
          f"failed {len(failed & set(by_name))} | {'would-submit' if args.dry_run else 'submitted'} {len(submitted)} | "
          f"remaining {total - done}")
    if failed & set(by_name):
        print("FAILED:", ", ".join(sorted(failed & set(by_name))))
    if submitted:
        print(("WOULD SUBMIT: " if args.dry_run else "SUBMITTED: ") + ", ".join(submitted))
    # Exit 0 normally; exit 3 signals "all done"; exit 4 signals "stuck" (failures block, nothing in flight)
    if done == total:
        return 3
    if not inflight and (failed & set(by_name)):
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
