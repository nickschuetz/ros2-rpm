#!/usr/bin/env python3
"""scripts/check-upstream.py, diff packages.yaml against rosdistro/jazzy.

Fetches https://raw.githubusercontent.com/ros/rosdistro/master/jazzy/distribution.yaml
and compares the `version:` field for every package present in
scripts/packages.yaml against the version we have locally registered (parsed
from the spec's Source0 URL).

Outputs a Markdown-formatted report. Intended to run in CI nightly so a
GitHub Action can post the report to a tracking issue when drift is
detected; runs locally too.

Usage:
  python3 scripts/check-upstream.py            # report to stdout, exit 0 always
  python3 scripts/check-upstream.py --strict   # exit 1 if any package is behind
  python3 scripts/check-upstream.py --json     # machine-readable output
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.request import urlopen

ROSDISTRO_URL = "https://raw.githubusercontent.com/ros/rosdistro/master/jazzy/distribution.yaml"
SPEC_DIR = Path(__file__).resolve().parent.parent / "specs"
PACKAGES_YAML = Path(__file__).resolve().parent / "packages.yaml"


def fetch_distribution_yaml() -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ERROR: PyYAML required. dnf install python3-pyyaml\n")
        sys.exit(2)
    with urlopen(ROSDISTRO_URL, timeout=30) as r:
        return yaml.safe_load(r.read())


def load_packages_yaml() -> dict[str, dict]:
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ERROR: PyYAML required. dnf install python3-pyyaml\n")
        sys.exit(2)
    with PACKAGES_YAML.open() as f:
        return yaml.safe_load(f) or {}


def parse_local_version(pkg: str) -> str | None:
    """Read the live version we built by inspecting the spec file."""
    spec = SPEC_DIR / f"ros-jazzy-{pkg.replace('_', '-')}.spec"
    if not spec.is_file():
        return None
    for line in spec.read_text().splitlines():
        m = re.match(r"^Version:\s+(\S+)", line)
        if m:
            return m.group(1)
    return None


def compare(distro_yaml: dict, our_packages: dict) -> list[dict]:
    repos = distro_yaml.get("repositories") or {}

    report: list[dict] = []
    for pkg_name in sorted(our_packages.keys()):
        local_version = parse_local_version(pkg_name)
        if local_version is None:
            report.append({
                "package": pkg_name,
                "local": None,
                "upstream": None,
                "status": "no-spec",
                "note": "no spec file in specs/",
            })
            continue

        # Find the upstream version. distribution.yaml lays out as:
        #   repositories:
        #     <repo>:
        #       release:
        #         packages: [<pkg1>, <pkg2>, ...]
        #         version: <version>-<bloom_release>
        #         tags:
        #           release: release/jazzy/{package}/{version}
        upstream_version = None
        upstream_repo = None
        for repo_name, repo in repos.items():
            release = (repo or {}).get("release") or {}
            release_pkgs = release.get("packages") or []
            # If the repo doesn't enumerate packages, the repo name IS the pkg.
            if not release_pkgs:
                release_pkgs = [repo_name]
            if pkg_name not in release_pkgs:
                continue
            ver_full = release.get("version", "")
            # Strip the trailing "-<bloom_release>", we only care about upstream version.
            upstream_version = ver_full.split("-")[0] if ver_full else None
            upstream_repo = repo_name
            break

        if upstream_version is None:
            report.append({
                "package": pkg_name,
                "local": local_version,
                "upstream": None,
                "status": "not-in-rosdistro",
                "note": "no entry in jazzy/distribution.yaml, upstream may have removed or renamed",
            })
            continue

        if upstream_version == local_version:
            report.append({
                "package": pkg_name,
                "local": local_version,
                "upstream": upstream_version,
                "status": "current",
                "repo": upstream_repo,
            })
        else:
            report.append({
                "package": pkg_name,
                "local": local_version,
                "upstream": upstream_version,
                "status": "behind",
                "repo": upstream_repo,
            })

    return report


def render_markdown(report: list[dict]) -> str:
    behind = [r for r in report if r["status"] == "behind"]
    current = [r for r in report if r["status"] == "current"]
    no_spec = [r for r in report if r["status"] == "no-spec"]
    not_in_rosdistro = [r for r in report if r["status"] == "not-in-rosdistro"]

    lines: list[str] = []
    lines.append("# Upstream drift report, `hellaenergy/ros2`")
    lines.append("")
    lines.append(f"Snapshot of upstream `rosdistro/jazzy/distribution.yaml` versus this COPR's published spec versions.")
    lines.append("")
    lines.append(f"- **{len(current)}** packages current")
    lines.append(f"- **{len(behind)}** packages behind upstream")
    lines.append(f"- **{len(not_in_rosdistro)}** packages no longer in rosdistro")
    lines.append(f"- **{len(no_spec)}** registered in packages.yaml but no spec file present")
    lines.append("")

    if behind:
        lines.append("## Packages behind upstream")
        lines.append("")
        lines.append("| Package | Local | Upstream | Repo |")
        lines.append("|---|---|---|---|")
        for r in behind:
            lines.append(f"| `{r['package']}` | `{r['local']}` | `{r['upstream']}` | `{r['repo']}` |")
        lines.append("")
        lines.append("Action: bump the entry in `scripts/packages.yaml`, regenerate the spec, push to COPR.")
        lines.append("")

    if not_in_rosdistro:
        lines.append("## No longer in rosdistro")
        lines.append("")
        lines.append("These packages we ship are no longer enumerated in jazzy/distribution.yaml. They may have been removed or renamed upstream.")
        lines.append("")
        for r in not_in_rosdistro:
            lines.append(f"- `{r['package']}` (we ship `{r['local']}`)")
        lines.append("")

    if no_spec:
        lines.append("## Registered without spec")
        lines.append("")
        for r in no_spec:
            lines.append(f"- `{r['package']}`: {r['note']}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--strict", action="store_true",
                   help="Exit non-zero if any package is behind upstream.")
    p.add_argument("--json", action="store_true",
                   help="Emit JSON instead of Markdown.")
    args = p.parse_args()

    distro_yaml = fetch_distribution_yaml()
    our_packages = load_packages_yaml()
    report = compare(distro_yaml, our_packages)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_markdown(report))

    if args.strict and any(r["status"] == "behind" for r in report):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
