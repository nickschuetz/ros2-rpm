#!/usr/bin/env python3
"""scripts/check-upstream.py, diff each distro's packages.yaml against rosdistro.

For every distro in scripts/distros.py (jazzy, lyrical, ...), fetches
https://raw.githubusercontent.com/ros/rosdistro/master/<distro>/distribution.yaml
and compares the `version:` field for every package present in that distro's
distros/<distro>/packages.yaml against the version we have locally registered
(parsed from the spec's Version: field under specs/<distro>/).

Outputs a Markdown-formatted report. Intended to run in CI weekly so a GitHub
Action can post the report to a tracking issue when drift is detected; runs
locally too.

Usage:
  python3 scripts/check-upstream.py              # all distros, report to stdout
  python3 scripts/check-upstream.py --distro jazzy
  python3 scripts/check-upstream.py --strict     # exit 1 if any package is behind
  python3 scripts/check-upstream.py --json       # machine-readable output
"""

import argparse
import json
import sys
from typing import Any
from urllib.request import urlopen

import distros


def _require_yaml():
    try:
        import yaml
        return yaml
    except ImportError:
        sys.stderr.write("ERROR: PyYAML required. dnf install python3-pyyaml\n")
        sys.exit(2)


def fetch_distribution_yaml(distro: str) -> dict[str, Any]:
    yaml = _require_yaml()
    with urlopen(distros.rosdistro_url(distro), timeout=30) as r:
        return yaml.safe_load(r.read())


def load_packages_yaml(distro: str) -> dict[str, dict]:
    yaml = _require_yaml()
    path = distros.packages_yaml(distro)
    if not path.is_file():
        return {}
    with path.open() as f:
        return yaml.safe_load(f) or {}


def parse_local_version(pkg: str, distro: str) -> str | None:
    """Read the live version we built by inspecting the spec file."""
    import re
    spec = distros.spec_path(distro, pkg)
    if not spec.is_file():
        return None
    for line in spec.read_text().splitlines():
        m = re.match(r"^Version:\s+(\S+)", line)
        if m:
            return m.group(1)
    return None


def compare(distro_yaml: dict, our_packages: dict, distro: str) -> list[dict]:
    repos = distro_yaml.get("repositories") or {}

    report: list[dict] = []
    for pkg_name in sorted(our_packages.keys()):
        local_version = parse_local_version(pkg_name, distro)
        if local_version is None:
            report.append({
                "distro": distro,
                "package": pkg_name,
                "local": None,
                "upstream": None,
                "status": "no-spec",
                "note": f"no spec file in specs/{distro}/",
            })
            continue

        # Find the upstream version. distribution.yaml lays out as:
        #   repositories:
        #     <repo>:
        #       release:
        #         packages: [<pkg1>, <pkg2>, ...]
        #         version: <version>-<bloom_release>
        #         tags:
        #           release: release/<distro>/{package}/{version}
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
                "distro": distro,
                "package": pkg_name,
                "local": local_version,
                "upstream": None,
                "status": "not-in-rosdistro",
                "note": f"no entry in {distro}/distribution.yaml, upstream may have removed or renamed",
            })
            continue

        status = "current" if upstream_version == local_version else "behind"
        report.append({
            "distro": distro,
            "package": pkg_name,
            "local": local_version,
            "upstream": upstream_version,
            "status": status,
            "repo": upstream_repo,
        })

    return report


def render_distro_section(report: list[dict], distro: str) -> list[str]:
    behind = [r for r in report if r["status"] == "behind"]
    current = [r for r in report if r["status"] == "current"]
    no_spec = [r for r in report if r["status"] == "no-spec"]
    not_in_rosdistro = [r for r in report if r["status"] == "not-in-rosdistro"]

    lines: list[str] = []
    lines.append(f"## `{distros.copr_project(distro)}` ({distro})")
    lines.append("")
    lines.append(f"- **{len(current)}** packages current")
    lines.append(f"- **{len(behind)}** packages behind upstream")
    lines.append(f"- **{len(not_in_rosdistro)}** packages no longer in rosdistro")
    lines.append(f"- **{len(no_spec)}** registered in packages.yaml but no spec file present")
    lines.append("")

    if behind:
        lines.append("### Packages behind upstream")
        lines.append("")
        lines.append("| Package | Local | Upstream | Repo |")
        lines.append("|---|---|---|---|")
        for r in behind:
            lines.append(f"| `{r['package']}` | `{r['local']}` | `{r['upstream']}` | `{r['repo']}` |")
        lines.append("")
        lines.append(f"Action: bump the entry in `distros/{distro}/packages.yaml`, "
                     f"regenerate the spec, push to COPR (`scripts/bump.py --distro {distro} --all-behind`).")
        lines.append("")

    if not_in_rosdistro:
        lines.append("### No longer in rosdistro")
        lines.append("")
        lines.append(f"These packages we ship are no longer enumerated in {distro}/distribution.yaml. "
                     "They may have been removed or renamed upstream.")
        lines.append("")
        for r in not_in_rosdistro:
            lines.append(f"- `{r['package']}` (we ship `{r['local']}`)")
        lines.append("")

    if no_spec:
        lines.append("### Registered without spec")
        lines.append("")
        for r in no_spec:
            lines.append(f"- `{r['package']}`: {r['note']}")
        lines.append("")

    return lines


def render_markdown(report: list[dict], selected: tuple[str, ...]) -> str:
    lines: list[str] = []
    lines.append("# Upstream drift report")
    lines.append("")
    lines.append("Snapshot of upstream `rosdistro/<distro>/distribution.yaml` versus this "
                 "repo's published spec versions, per distro.")
    lines.append("")
    for distro in selected:
        section = [r for r in report if r["distro"] == distro]
        lines.extend(render_distro_section(section, distro))
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--distro", choices=distros.DISTROS,
                   help="Limit to one distro (default: all).")
    p.add_argument("--strict", action="store_true",
                   help="Exit non-zero if any package is behind upstream.")
    p.add_argument("--json", action="store_true",
                   help="Emit JSON instead of Markdown.")
    args = p.parse_args()

    selected = (args.distro,) if args.distro else distros.DISTROS

    report: list[dict] = []
    for distro in selected:
        distro_yaml = fetch_distribution_yaml(distro)
        our_packages = load_packages_yaml(distro)
        report.extend(compare(distro_yaml, our_packages, distro))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_markdown(report, selected))

    if args.strict and any(r["status"] == "behind" for r in report):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
