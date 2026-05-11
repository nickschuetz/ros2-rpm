#!/usr/bin/env python3
"""bump.py, fast-path version bumps for ros2-rpm specs.

Updates Version:, Source0:, and %changelog in a spec to match the current
rosdistro/jazzy/distribution.yaml. Closes the loop with scripts/check-upstream.py:
when the weekly drift workflow flags a package as behind, run this against
that package to bring it back in sync.

Covers the 80% case: upstream bumped a patch / minor version with no
dependency changes. If %BuildRequires shifted, you still need to regenerate
via scripts/generate-spec.py and hand-finish per
docs/PACKAGING-LESSONS.md. bump.py preserves any Patch%N: lines on the
existing spec without touching them, so locally-carried patches survive.

Usage:
    scripts/bump.py rclcpp                          # bump one package to upstream
    scripts/bump.py rclcpp 28.1.19                  # bump to a specific version
    scripts/bump.py --all-behind                    # bump every drifted package
    scripts/bump.py --dry-run rclcpp                # print the diff, change nothing
    scripts/bump.py --commit rclcpp                 # also git commit
"""
from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

ROSDISTRO_URL = "https://raw.githubusercontent.com/ros/rosdistro/master/jazzy/distribution.yaml"
REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = REPO_ROOT / "specs"

PACKAGER_NAME = "Nick Schuetz"
PACKAGER_EMAIL = "nschuetz@redhat.com"


def fetch_rosdistro() -> dict:
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ERROR: PyYAML required. dnf install python3-pyyaml\n")
        sys.exit(2)
    with urlopen(ROSDISTRO_URL, timeout=30) as r:
        return yaml.safe_load(r.read())


def find_upstream_version(distro: dict, pkg: str) -> tuple[str, str] | None:
    """Return (upstream_version, full_version_with_release) for `pkg`, or None."""
    repos = distro.get("repositories") or {}
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


def spec_path_for(pkg: str) -> Path:
    return SPEC_DIR / f"ros-jazzy-{pkg.replace('_', '-')}.spec"


def parse_spec_version(text: str) -> str | None:
    m = re.search(r"^Version:\s+(\S+)", text, re.MULTILINE)
    return m.group(1) if m else None


def parse_spec_release(text: str) -> int:
    m = re.search(r"^Release:\s+(\d+)%", text, re.MULTILINE)
    return int(m.group(1)) if m else 1


def update_spec(text: str, new_upstream: str, full_version: str,
                date_str: str, reason: str) -> str:
    """Return spec text updated to the new version with a fresh changelog entry."""
    new_text = re.sub(
        r"^(Version:\s+)\S+",
        rf"\g<1>{new_upstream}",
        text,
        count=1,
        flags=re.MULTILINE,
    )

    # Source0 embeds the bloom-tag form `<upstream>-<release_counter>`. Substitute
    # any matching token in the Source0 URL. Don't touch tarball filename
    # macros (those use %{version} which already expanded to new_upstream).
    def source0_sub(m: re.Match) -> str:
        url = m.group(1)
        url = re.sub(r"(release/jazzy/[^/]+/)([0-9][0-9.A-Za-z]*-\d+)",
                     lambda x: f"{x.group(1)}{full_version}", url)
        url = re.sub(r"(/v?)\d[0-9.A-Za-z]*(\.tar\.gz)",
                     lambda x: f"{x.group(1)}{full_version}{x.group(2)}", url)
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


def bump_one(pkg: str, distro: dict, target_version: str | None,
             dry_run: bool) -> tuple[bool, str]:
    """Returns (changed, message)."""
    spec = spec_path_for(pkg)
    if not spec.is_file():
        return (False, f"{pkg}: no spec at {spec.relative_to(REPO_ROOT)}")

    text = spec.read_text()
    current = parse_spec_version(text)
    if current is None:
        return (False, f"{pkg}: could not parse Version: from spec")

    if target_version:
        new_upstream = target_version
        full_version = f"{target_version}-1"
        reason = f"Pin to {new_upstream} (manual override)."
    else:
        upstream_info = find_upstream_version(distro, pkg)
        if upstream_info is None:
            return (False, f"{pkg}: not found in rosdistro/jazzy/distribution.yaml")
        new_upstream, full_version = upstream_info
        if new_upstream == current:
            return (False, f"{pkg}: already at {current}")
        reason = f"Sync with upstream jazzy: {new_upstream}."

    date_str = datetime.date.today().strftime("%a %b %d %Y")
    new_text = update_spec(text, new_upstream, full_version, date_str, reason)

    if new_text == text:
        return (False, f"{pkg}: substitution produced no change (regex miss?)")

    if dry_run:
        diff = subprocess.run(
            ["diff", "-u", str(spec), "-"],
            input=new_text, capture_output=True, text=True,
        )
        sys.stdout.write(diff.stdout)
        return (False, f"{pkg}: dry-run, {current} -> {new_upstream}")

    spec.write_text(new_text)
    return (True, f"{pkg}: {current} -> {new_upstream}")


def git_commit(packages: list[str], custom_msg: str | None) -> None:
    if not packages:
        return
    body = custom_msg or (
        f"Bump {len(packages)} package(s) to current rosdistro/jazzy versions"
        if len(packages) > 1
        else f"Bump ros-jazzy-{packages[0].replace('_', '-')} to current rosdistro/jazzy"
    )
    spec_files = [str(spec_path_for(p).relative_to(REPO_ROOT)) for p in packages]
    subprocess.run(["git", "-C", str(REPO_ROOT), "add", *spec_files], check=True)
    subprocess.run(
        ["git", "-C", str(REPO_ROOT), "commit", "-m", body],
        check=True,
    )


def collect_drifted() -> list[str]:
    """Run check-upstream.py and return the list of behind packages."""
    import json
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check-upstream.py"), "--json"],
        capture_output=True, text=True, check=True,
    )
    report = json.loads(r.stdout)
    return [e["package"] for e in report if e.get("status") == "behind"]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("package", nargs="?", help="Package name (rosdep key form, e.g. rclcpp)")
    p.add_argument("version", nargs="?", help="Target version (default: query rosdistro)")
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

    distro = fetch_rosdistro()

    if args.all_behind:
        targets = collect_drifted()
        if not targets:
            print("No packages behind upstream.")
            return 0
        print(f"Bumping {len(targets)} drifted package(s): {', '.join(targets)}")
    else:
        targets = [args.package]

    changed_pkgs: list[str] = []
    for t in targets:
        changed, msg = bump_one(t, distro, args.version if not args.all_behind else None,
                                dry_run=args.dry_run)
        print(msg)
        if changed:
            changed_pkgs.append(t)

    if args.commit and changed_pkgs:
        git_commit(changed_pkgs, args.message)
        print(f"Committed {len(changed_pkgs)} bump(s).")

    # Run verifier as a final guard.
    if changed_pkgs and not args.dry_run:
        spec_args = [str(spec_path_for(p)) for p in changed_pkgs]
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
