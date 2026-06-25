#!/usr/bin/env python3
"""bump.py, fast-path version bumps for ros2-rpm specs.

Updates Version:, Source0:, and %changelog in a spec to match the current
rosdistro/<distro>/distribution.yaml. Closes the loop with
scripts/check-upstream.py: when the weekly drift workflow flags a package as
behind, run this against that package to bring it back in sync.

Covers the 80% case: upstream bumped a patch / minor version with no
dependency changes. If %BuildRequires shifted, you still need to regenerate
via scripts/generate-spec.py and hand-finish per
docs/PACKAGING-LESSONS.md. bump.py preserves any Patch%N: lines on the
existing spec without touching them, so locally-carried patches survive.

Usage:
    scripts/bump.py rclcpp                          # bump one package (auto-detect distro)
    scripts/bump.py --distro jazzy rclcpp           # disambiguate when both distros have it
    scripts/bump.py rclcpp 28.1.19                  # bump to a specific version
    scripts/bump.py --all-behind                    # bump every drifted package, all distros
    scripts/bump.py --distro lyrical --all-behind   # one distro only
    scripts/bump.py --dry-run rclcpp                # print the diff, change nothing
    scripts/bump.py --commit rclcpp                 # also git commit
"""
from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys

import distros

REPO_ROOT = distros.REPO_ROOT

PACKAGER_NAME = "Nick Schuetz"
PACKAGER_EMAIL = "nschuetz@redhat.com"


def fetch_rosdistro(distro: str) -> dict:
    from urllib.request import urlopen
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ERROR: PyYAML required. dnf install python3-pyyaml\n")
        sys.exit(2)
    with urlopen(distros.rosdistro_url(distro), timeout=30) as r:
        return yaml.safe_load(r.read())


def find_upstream_version(distro_yaml: dict, pkg: str) -> tuple[str, str] | None:
    """Return (upstream_version, full_version_with_release) for `pkg`, or None."""
    repos = distro_yaml.get("repositories") or {}
    for repo_name, repo in repos.items():
        release = (repo or {}).get("release") or {}
        release_pkgs = release.get("packages") or []
        if not release_pkgs:
            release_pkgs = [repo_name]
        if pkg not in release_pkgs:
            continue
        ver_full = release.get("version", "")
        if not ver_full:
            return None
        upstream = ver_full.split("-")[0]
        return (upstream, ver_full)
    return None


def detect_distro(pkg: str, requested: str | None) -> str | None:
    """Pick the distro whose tree holds this package's spec."""
    if requested:
        return requested if distros.spec_path(requested, pkg).is_file() else None
    have = [d for d in distros.DISTROS if distros.spec_path(d, pkg).is_file()]
    if len(have) == 1:
        return have[0]
    if len(have) > 1:
        sys.stderr.write(
            f"{pkg}: present in multiple distros ({', '.join(have)}); "
            f"pass --distro to disambiguate\n")
        return None
    return None


def parse_spec_version(text: str) -> str | None:
    m = re.search(r"^Version:\s+(\S+)", text, re.MULTILINE)
    return m.group(1) if m else None


def update_spec(text: str, distro: str, new_upstream: str, full_version: str,
                date_str: str, reason: str) -> str:
    """Return spec text updated to the new version with a fresh changelog entry."""
    new_text = re.sub(
        r"^(Version:\s+)\S+",
        rf"\g<1>{new_upstream}",
        text,
        count=1,
        flags=re.MULTILINE,
    )

    # Two Source0 conventions appear in this repo:
    #   1. ros2-gbp `<repo>-release` tags: .../release/<distro>/<pkg>/<ver>-<counter>
    #      carry the bloom release counter, so they take the full version-counter.
    #   2. bare upstream tags: .../ros2/<repo>/archive/refs/tags/<ver>.tar.gz
    #      carry no counter, so they take the bare upstream version only.
    # The two patterns are mutually exclusive (pattern 1's `<ver>-<counter>` is
    # not followed by `.tar.gz`, so pattern 2 cannot also match it). Don't touch
    # tarball filename macros (those use %{version}, already = new_upstream).
    def source0_sub(m: re.Match) -> str:
        url = m.group(1)
        url = re.sub(rf"(release/{distro}/[^/]+/)([0-9][0-9.A-Za-z]*-\d+)",
                     lambda x: f"{x.group(1)}{full_version}", url)
        url = re.sub(r"(/v?)\d[0-9.A-Za-z]*(\.tar\.gz)",
                     lambda x: f"{x.group(1)}{new_upstream}{x.group(2)}", url)
        return f"Source0:        {url}"

    new_text = re.sub(
        r"^Source0:\s+(.+)$",
        source0_sub,
        new_text,
        count=1,
        flags=re.MULTILINE,
    )

    # Reset Release: to 1 on every upstream bump.
    new_text = re.sub(
        r"^(Release:\s+)\d+(%.*)$",
        r"\g<1>1\g<2>",
        new_text,
        count=1,
        flags=re.MULTILINE,
    )

    entry = (
        f"* {date_str} {PACKAGER_NAME} <{PACKAGER_EMAIL}> - {new_upstream}-1\n"
        f"- {reason}\n"
    )
    new_text = re.sub(
        r"^(%changelog\s*\n)",
        lambda m: m.group(1) + entry + "\n",
        new_text,
        count=1,
        flags=re.MULTILINE,
    )
    return new_text


def bump_one(pkg: str, distro: str, distro_yaml: dict, target_version: str | None,
             dry_run: bool) -> tuple[bool, str]:
    """Returns (changed, message)."""
    spec = distros.spec_path(distro, pkg)
    if not spec.is_file():
        return (False, f"{pkg} ({distro}): no spec at {spec.relative_to(REPO_ROOT)}")

    text = spec.read_text()
    current = parse_spec_version(text)
    if current is None:
        return (False, f"{pkg} ({distro}): could not parse Version: from spec")

    if target_version:
        new_upstream = target_version
        full_version = f"{target_version}-1"
        reason = f"Pin to {new_upstream} (manual override)."
    else:
        upstream_info = find_upstream_version(distro_yaml, pkg)
        if upstream_info is None:
            return (False, f"{pkg} ({distro}): not found in rosdistro/{distro}/distribution.yaml")
        new_upstream, full_version = upstream_info
        if new_upstream == current:
            return (False, f"{pkg} ({distro}): already at {current}")
        reason = f"Sync with upstream {distro}: {new_upstream}."

    date_str = datetime.date.today().strftime("%a %b %d %Y")
    new_text = update_spec(text, distro, new_upstream, full_version, date_str, reason)

    if new_text == text:
        return (False, f"{pkg} ({distro}): substitution produced no change (regex miss?)")

    if dry_run:
        diff = subprocess.run(
            ["diff", "-u", str(spec), "-"],
            input=new_text, capture_output=True, text=True,
        )
        sys.stdout.write(diff.stdout)
        return (False, f"{pkg} ({distro}): dry-run, {current} -> {new_upstream}")

    spec.write_text(new_text)
    return (True, f"{pkg} ({distro}): {current} -> {new_upstream}")


def git_commit(changed: list[tuple[str, str]], custom_msg: str | None) -> None:
    if not changed:
        return
    distro_set = sorted({d for d, _ in changed})
    if custom_msg:
        body = custom_msg
    elif len(changed) > 1:
        body = f"Bump {len(changed)} package(s) to current rosdistro versions ({', '.join(distro_set)})"
    else:
        d, p = changed[0]
        body = f"Bump ros-{d}-{p.replace('_', '-')} to current rosdistro/{d}"
    spec_files = [str(distros.spec_path(d, p).relative_to(REPO_ROOT)) for d, p in changed]
    subprocess.run(["git", "-C", str(REPO_ROOT), "add", *spec_files], check=True)
    subprocess.run(["git", "-C", str(REPO_ROOT), "commit", "-m", body], check=True)


def collect_drifted(selected: tuple[str, ...]) -> list[tuple[str, str]]:
    """Run check-upstream.py and return [(distro, package), ...] for behind packages."""
    import json
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "check-upstream.py"), "--json"]
    if len(selected) == 1:
        cmd += ["--distro", selected[0]]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    report = json.loads(r.stdout)
    return [(e["distro"], e["package"]) for e in report if e.get("status") == "behind"]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("package", nargs="?", help="Package name (rosdep key form, e.g. rclcpp)")
    p.add_argument("version", nargs="?", help="Target version (default: query rosdistro)")
    p.add_argument("--distro", choices=distros.DISTROS,
                   help="Target distro (auto-detected for a single package if omitted).")
    p.add_argument("--all-behind", action="store_true",
                   help="Bump every package the drift checker reports behind.")
    p.add_argument("--dry-run", action="store_true",
                   help="Show the diff without writing the spec.")
    p.add_argument("--commit", action="store_true",
                   help="git commit after bumping.")
    p.add_argument("--message", help="Custom commit message (with --commit).")
    args = p.parse_args()

    if not args.all_behind and not args.package:
        p.error("provide a package name or pass --all-behind")
    if args.all_behind and args.package:
        p.error("--all-behind is mutually exclusive with a package argument")
    if args.commit and args.dry_run:
        p.error("--commit and --dry-run are mutually exclusive")

    selected = (args.distro,) if args.distro else distros.DISTROS

    # Build the work list of (distro, package).
    if args.all_behind:
        work = collect_drifted(selected)
        if not work:
            print("No packages behind upstream.")
            return 0
        print(f"Bumping {len(work)} drifted package(s): "
              + ", ".join(f"{p}({d})" for d, p in work))
    else:
        distro = detect_distro(args.package, args.distro)
        if distro is None:
            return 2
        work = [(distro, args.package)]

    # Fetch each needed distro's rosdistro once.
    needed_distros = sorted({d for d, _ in work})
    distro_yamls = {d: fetch_rosdistro(d) for d in needed_distros}

    changed: list[tuple[str, str]] = []
    for d, pkg in work:
        ok, msg = bump_one(pkg, d, distro_yamls[d],
                           args.version if not args.all_behind else None,
                           dry_run=args.dry_run)
        print(msg)
        if ok:
            changed.append((d, pkg))

    if args.commit and changed:
        git_commit(changed, args.message)
        print(f"Committed {len(changed)} bump(s).")

    # Run verifier as a final guard.
    if changed and not args.dry_run:
        spec_args = [str(distros.spec_path(d, p)) for d, p in changed]
        v = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "verify-specs.py"), *spec_args],
            check=False,
        )
        if v.returncode != 0:
            print("\nWARNING: verify-specs.py reported issues. Review the diff carefully.",
                  file=sys.stderr)
            return v.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
