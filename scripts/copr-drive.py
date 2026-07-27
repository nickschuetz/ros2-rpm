#!/usr/bin/env python3
"""copr-drive.py, dependency-ordered COPR build driver for one distro.

Submits each spec to its distro's COPR project as soon as all of its in-tree
ros-<distro>- dependencies have succeeded, so a full tree builds in topological
order without hand-sequencing waves. Idempotent: packages already succeeded or
currently building are skipped.

Success is judged PER CHROOT against the target chroot set (the --chroots
subset, or every project chroot when --chroots is omitted): a package is "done"
only when it succeeded at the current spec version on every target chroot. So a
package built on a subset (e.g. the 4 stable chroots with fedora-rawhide skipped)
reads as not-done for a later run that includes rawhide and is rebuilt there, in
dependency order, with its deps required green on rawhide first.

Usage:
    scripts/copr-drive.py --distro lyrical            # submit the ready wave
    scripts/copr-drive.py --distro lyrical --dry-run  # show the plan only
    # catch a chroot up (e.g. rawhide): first force-rebuild the noarch python
    # foundation there (version-invisible py-path staleness), then plain-drive:
    scripts/copr-drive.py --distro lyrical \\
        --chroots fedora-rawhide-x86_64,fedora-rawhide-aarch64 \\
        --force ros-lyrical-ament-package,ros-lyrical-ament-index-python,...
    scripts/copr-drive.py --distro lyrical \\
        --chroots fedora-rawhide-x86_64,fedora-rawhide-aarch64 --exclude <visual chain>
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

ACTIVE = {"running", "pending", "starting", "importing", "waiting"}
# States that mean "a usable RPM exists at this version". "forked" is terminal:
# a maintenance COPR created by forking another project (as ros2-jazzy was forked
# from ros2) carries every package's last build as "forked", which is a real,
# installable build, not an in-flight one. Treated as success-equivalent for both
# the dependency gate and version-drift detection.
SUCCESS = {"succeeded", "forked"}

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
    # The Source0 "#/<localname>" fragment is the filename rpmbuild looks for in
    # _sourcedir; it is not always <pkg_name>-<version> (jazzy rosidl specs use
    # the repo name, e.g. "#/rosidl-%{version}.tar.gz"). Honor it so the fetched
    # tarball lands under the exact name the spec references; fall back to
    # <pkg_name>-<version> when no fragment is present.
    frag = src0.split("#", 1)[1].lstrip("/") if (src0 and "#" in src0) else None
    if frag:
        src_name = frag.replace("%{version}", version or "").replace(
            "%{pkg_name}", pkg_name or "")
    elif pkg_name and version:
        src_name = f"{pkg_name}-{version}.tar.gz"
    else:
        src_name = None
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
            "version": version, "src_url": src_url, "src_name": src_name,
            "topdir": topdir, "patches": patches, "deps": deps}


def copr_package_info(project: str) -> dict[str, dict]:
    """Map each COPR package to its latest build's state and upstream version.

    The version is taken from latest_build.source_package.version (e.g.
    "28.1.18-1") with the trailing "-<release>" stripped, so it can be compared
    directly against a spec's Version: field. Lets the driver tell a genuinely
    finished package from one whose COPR build succeeded at a now-stale version
    (i.e. the spec was bumped since), which must be rebuilt.
    """
    r = subprocess.run(["copr-cli", "list-packages", project, "--with-latest-build"],
                       capture_output=True, text=True, check=True)
    out = {}
    for p in json.loads(r.stdout):
        lb = p.get("latest_build") or {}
        sp = lb.get("source_package") or {}
        ver = sp.get("version") or ""
        out[p["name"]] = {
            "state": lb.get("state") or "none",
            "version": ver.split("-")[0] if ver else "",
        }
    return out


def copr_states(project: str) -> dict[str, str]:
    return {n: i["state"] for n, i in copr_package_info(project).items()}


def copr_chroot_info(project: str) -> dict[str, dict[str, dict]]:
    """Map each COPR package to its latest per-chroot build state and version.

    `copr-cli list-packages --with-latest-build` only exposes one global
    latest_build, which hides the case where a package's newest build targeted a
    chroot SUBSET (e.g. the drift catch-ups drove `--chroots <4 stable>`, leaving
    fedora-rawhide on an older build). `copr-cli monitor` reports one row per
    package per chroot, each carrying that chroot's own latest build state and
    version, so the driver can tell "green on all target chroots at the current
    version" from "green on the 4 stable but stale/failed on rawhide".

    Returns {name: {chroot: {"state": str, "version": str}}}. Absent (name,
    chroot) pairs mean the package has never built on that chroot.
    """
    r = subprocess.run(["copr-cli", "monitor", project, "--output-format", "json"],
                       capture_output=True, text=True, check=True)
    out: dict[str, dict[str, dict]] = {}
    for row in json.loads(r.stdout):
        ver = row.get("pkg_version") or ""
        out.setdefault(row["name"], {})[row["chroot"]] = {
            "state": row.get("state") or "none",
            "version": ver.split("-")[0] if ver else "",
        }
    return out


def classify(chroots_for_pkg: dict[str, dict], target: list[str],
             spec_version: str | None) -> str:
    """Per-chroot status of one package over the `target` chroot set.

    - "done":    succeeded at the current spec version on EVERY target chroot.
    - "active":  in-flight on some target chroot (build it out, don't resubmit).
    - "failed":  failed on some target chroot (and not active anywhere).
    - "drifted": succeeded on every target chroot but at least one is a stale
                 version (spec bumped, or the chroot never got the rebuild).
    - "todo":    never built on some target chroot (new pkg / missing chroot).
    """
    entries = [chroots_for_pkg.get(ch) for ch in target]
    if any(e and e["state"] in ACTIVE for e in entries):
        return "active"
    if any(e is None for e in entries):
        return "todo"
    if all(e["state"] in SUCCESS
           and (not spec_version or not e["version"] or e["version"] == spec_version)
           for e in entries):
        return "done"
    if any(e["state"] == "failed" for e in entries):
        return "failed"
    if all(e["state"] in SUCCESS for e in entries):
        return "drifted"
    return "todo"


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
    if not (meta["src_url"] and meta["src_name"]):
        return False
    # Save under the exact name the spec's Source0 references (the "#/<name>"
    # fragment), which rpmbuild looks for; not all specs use <pkg_name>-<version>.
    target = sources / meta["src_name"]
    if target.is_file() and _topdir_matches(target, meta.get("topdir")):
        return True
    try:
        data = urllib.request.urlopen(meta["src_url"], timeout=90).read()
        target.write_bytes(data)
        return True
    except Exception as e:
        sys.stderr.write(f"  fetch failed for {meta['pkg_name']}: {str(e)[:80]}\n")
        return False


def build_and_submit(meta: dict, project: str, build: Path, dry: bool,
                     chroots: list[str] | None = None) -> str | None:
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
    cmd = ["copr-cli", "build", "--nowait", project, str(srpm[0])]
    # Restrict to a chroot subset when asked (e.g. excluding fedora-rawhide,
    # which is broken for the ament_cmake set during a Python minor transition).
    # COPR marks a build succeeded based only on the chroots it was submitted to,
    # so a 4-chroot build reads as "succeeded" and clears drift / unblocks the
    # dependency gate without the rawhide failure dragging the whole build red.
    for ch in (chroots or []):
        cmd += ["-r", ch]
    s = subprocess.run(cmd, capture_output=True, text=True)
    return "submitted" if s.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--distro", choices=distros.DISTROS, required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--chroots",
                    help="comma-separated chroot subset to build AND to judge "
                         "'done' against (default: all project chroots). Skip a "
                         "broken chroot, e.g. --chroots fedora-44-x86_64,"
                         "fedora-44-aarch64,centos-stream-10-x86_64,"
                         "centos-stream-10-aarch64 to leave fedora-rawhide alone; "
                         "or add the rawhide pair to catch it up once healthy.")
    ap.add_argument("--exclude",
                    help="comma-separated rpm package names to skip this run, e.g. "
                         "packages that build on a different chroot set (jazzy rqt "
                         "is Fedora-only). Run them separately with their own "
                         "--chroots.")
    ap.add_argument("--force",
                    help="comma-separated rpm package names to rebuild even though "
                         "COPR reports them succeeded at the current version. Use "
                         "when the staleness is invisible to version comparison, "
                         "e.g. the noarch python foundation after a Python minor "
                         "bump: ament_package etc. read as done but their modules "
                         "sit in the old pythonX.Y/site-packages, so every compiled "
                         "consumer fails 'ModuleNotFoundError'. Forced packages "
                         "rebuild in dependency order on the target chroots and are "
                         "held for one cooldown after submit so they do not thrash; "
                         "drop --force once they are green and resume a plain drive.")
    args = ap.parse_args()
    chroots = [c.strip() for c in args.chroots.split(",")] if args.chroots else None
    exclude = {c.strip() for c in args.exclude.split(",")} if args.exclude else set()
    force = {c.strip() for c in args.force.split(",")} if args.force else set()

    project = distros.copr_project(args.distro)
    build = distros.REPO_ROOT / "build"
    specs = [spec_meta(s, args.distro) for s in sorted(distros.spec_dir(args.distro).glob("*.spec"))]
    by_name = {m["rpm_name"]: m for m in specs if m["rpm_name"]}
    spec_ver = {m["rpm_name"]: m["version"] for m in specs if m["rpm_name"]}

    # Per-chroot build state. "Done" is judged against the target chroot set, so
    # a package built on a subset (e.g. the 4 stable chroots, rawhide skipped)
    # correctly reads as not-done for a run that includes rawhide, and gets
    # rebuilt there in dependency order. When --chroots is omitted, the target is
    # every chroot the project has, matching "green everywhere at this version".
    chroot_info = copr_chroot_info(project)
    all_chroots = sorted({ch for chs in chroot_info.values() for ch in chs})
    target = chroots if chroots else all_chroots

    status = {n: classify(chroot_info.get(n, {}), target, spec_ver.get(n))
              for n in by_name}
    succeeded = {n for n, s in status.items() if s == "done"}
    drifted = {n for n, s in status.items() if s == "drifted"}
    active = {n for n, s in status.items() if s == "active"}
    failed = {n for n, s in status.items() if s == "failed"}

    ledger = load_ledger(build, args.distro)
    now = time.time()
    # A package we submitted recently but that COPR has not registered yet (so it
    # is absent from `states`) is treated as in-flight, not re-submitted. Once it
    # surfaces as failed, drop it from the ledger so a fix can be resubmitted.
    # Forced packages are held for the full cooldown regardless of their reported
    # state: a --force target reads as succeeded, so without this it would be
    # eligible again the very next tick and thrash.
    cooling = {n for n, t in ledger.items()
               if now - t < SUBMIT_COOLDOWN
               and (n in force or (n not in succeeded and n not in failed))}
    for n in list(ledger):
        if n not in force and (n in succeeded or n in failed):
            ledger.pop(n, None)

    ready = []
    for m in specs:
        n = m["rpm_name"]
        if not n or n in active or n in cooling or n in exclude:
            continue
        # Skip packages already done, UNLESS forced (a forced target reads as done
        # by version but must rebuild anyway). Forced packages still count as
        # succeeded for OTHER packages' dep gate below (via `succeeded`), so a
        # forced chain does not deadlock: an outer forced package sees its inner
        # forced dep as satisfied once that dep has actually rebuilt green.
        if n in succeeded and n not in force:
            continue
        # only build deps that are in our tree; all must be succeeded
        intree = {d for d in m["deps"] if d in by_name}
        if intree <= succeeded:
            ready.append(m)

    submitted = []
    for m in ready:
        res = build_and_submit(m, project, build, args.dry_run, chroots)
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
          f"failed {len(failed & set(by_name))} | drifted {len(drifted & set(by_name))} | "
          f"{'would-submit' if args.dry_run else 'submitted'} {len(submitted)} | "
          f"remaining {total - done}"
          + (f" | forcing {len(force & set(by_name))}" if force else ""))
    if failed & set(by_name):
        print("FAILED:", ", ".join(sorted(failed & set(by_name))))
    if drifted & set(by_name):
        print("DRIFTED (spec bumped, COPR stale):",
              ", ".join(sorted(drifted & set(by_name))))
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
