#!/usr/bin/env python3
"""generate-spec.py — render an RPM spec from a ROS 2 package source.

Reads package.xml (for version, description, license, deps) and
scripts/packages.yaml (for the source URL and build layout) and emits
a draft spec to stdout. Output requires human review for %files and
description quality before committing to specs/.

Build types supported: ament_python, ament_cmake.

Usage:
    scripts/generate-spec.py <path-to-package-source> [options]

Examples:
    scripts/generate-spec.py build/ament_package > specs/ros-jazzy-ament-package.spec
    scripts/generate-spec.py build/ament_cmake_core_pkg/ament_cmake/ament_cmake_core
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    sys.stderr.write("ERROR: PyYAML required. pip install --user pyyaml\n")
    sys.exit(2)


DEFAULT_DISTRO = "jazzy"
DEFAULT_OS_VERSION = "44"
DEFAULT_PREFIX = "/opt/ros"
DEFAULT_PACKAGER_NAME = "Nick Schuetz"
DEFAULT_PACKAGER_EMAIL = "nschuetz@redhat.com"

LICENSE_MAP = {
    "Apache License 2.0": "Apache-2.0",
    "Apache License, Version 2.0": "Apache-2.0",
    "Apache 2.0": "Apache-2.0",
    "Apache-License-2.0": "Apache-2.0",
    "ASL 2.0": "Apache-2.0",
    "BSD-License": "BSD-3-Clause",
    "BSD": "BSD-3-Clause",
    "BSD 3-Clause": "BSD-3-Clause",
    "MIT-License": "MIT",
}


def spdx(license_str: str) -> str:
    s = license_str.strip()
    return LICENSE_MAP.get(s, s)


# Common spelling fixes applied to description text. rpmlint flags these as
# errors. They come from package.xml descriptions written by upstream authors.
DESCRIPTION_FIXES = [
    ("buildsystem", "build system"),
    ("funtionalities", "functionalities"),
]


def clean_description(desc: str, max_width: int = 75) -> str:
    """Apply spelling fixes and wrap to <max_width> chars per line."""
    import textwrap
    text = desc
    for old, new in DESCRIPTION_FIXES:
        text = text.replace(old, new)
    # Collapse internal whitespace runs to single spaces, then re-wrap.
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    wrapped: list[str] = []
    for p in paragraphs:
        p_clean = " ".join(p.split())
        wrapped.append(textwrap.fill(p_clean, width=max_width))
    return "\n\n".join(wrapped)


def rosdep_resolve(key: str, distro: str, os_version: str) -> Optional[list[str]]:
    """Return the list of system package names key resolves to, or None on failure."""
    try:
        r = subprocess.run(
            ["rosdep", "resolve", key, f"--os=fedora:{os_version}", f"--rosdistro={distro}"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        sys.stderr.write("ERROR: rosdep not on PATH. dnf install python3-rosdep\n")
        sys.exit(2)
    if r.returncode != 0:
        return None
    out_lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip() and not ln.startswith("#")]
    return out_lines or None


def resolve_deps(keys: list[str], distro: str, os_version: str) -> list[str]:
    """Resolve rosdep keys to deduplicated, sorted Fedora package names."""
    resolved = set()
    for key in keys:
        names = rosdep_resolve(key, distro, os_version)
        if names is None:
            sys.stderr.write(f"WARNING: rosdep could not resolve '{key}' on fedora:{os_version}\n")
            continue
        resolved.update(names)
    return sorted(resolved)


def parse_package_xml(path: Path) -> dict:
    tree = ET.parse(path)
    root = tree.getroot()

    pkg: dict = {
        "name": (root.findtext("name") or "").strip(),
        "version": (root.findtext("version") or "").strip(),
        "description": (root.findtext("description") or "").strip(),
        "license": (root.findtext("license") or "").strip(),
        "url": "",
    }

    # Homepage / URL: first <url> element
    url_elem = root.find("url")
    if url_elem is not None and url_elem.text:
        pkg["url"] = url_elem.text.strip()

    # Build type
    build_type = "ament_cmake"
    export = root.find("export")
    if export is not None:
        bt = export.find("build_type")
        if bt is not None and bt.text:
            build_type = bt.text.strip()
    pkg["build_type"] = build_type

    # Dependencies
    def collect(tag: str) -> list[str]:
        return [d.text.strip() for d in root.findall(tag) if d.text and d.text.strip()]

    pkg["buildtool_depends"] = collect("buildtool_depend")
    pkg["build_depends"] = collect("build_depend")
    pkg["depends"] = collect("depend")
    pkg["exec_depends"] = collect("exec_depend")
    pkg["test_depends"] = collect("test_depend")

    return pkg


def build_requires(pkg: dict, build_type: str, distro: str, os_version: str) -> list[str]:
    """Compute BuildRequires lines."""
    keys: list[str] = []
    keys += pkg["buildtool_depends"]
    keys += pkg["build_depends"]
    keys += pkg["depends"]
    keys += pkg["test_depends"]
    base = resolve_deps(keys, distro, os_version)

    # Always-on for our pipeline
    if build_type == "ament_python":
        always = [
            "python3-devel",
            "pyproject-rpm-macros",
            "python3-setuptools",
            "python3-pip",
            "python3-wheel",
        ]
    elif build_type == "ament_cmake":
        always = ["cmake", "python3-devel"]
    else:
        always = []

    return sorted(set(base + always))


def runtime_requires(pkg: dict, build_type: str, distro: str, os_version: str) -> list[str]:
    keys: list[str] = pkg["depends"] + pkg["exec_depends"]
    base = resolve_deps(keys, distro, os_version)
    if build_type == "ament_python":
        return sorted(set(base + ["python3"]))
    return sorted(set(base))


def render_python_spec(pkg: dict, cfg: dict, distro: str, prefix: str) -> str:
    name = pkg["name"]
    version = pkg["version"]
    name_dashed = name.replace("_", "-")
    license_spdx = spdx(pkg["license"])
    summary = f"ROS 2 {distro.capitalize()} {name}"
    desc = clean_description(pkg["description"] or summary)
    install_prefix = f"{prefix}/{distro}"

    source_url = cfg["source_url"].format(version=version)
    source_dir = cfg["source_dir"].format(version=version)

    brs = build_requires(pkg, "ament_python", distro, DEFAULT_OS_VERSION)
    rqs = runtime_requires(pkg, "ament_python", distro, DEFAULT_OS_VERSION)

    br_lines = "\n".join(f"BuildRequires:  {b}" for b in brs)
    rq_lines = "\n".join(f"Requires:       {r}" for r in rqs)

    return f"""%global ros_distro       {distro}
%global pkg_name         {name}
%global install_prefix   {install_prefix}

Name:           ros-%{{ros_distro}}-{name_dashed}
Version:        {version}
Release:        1%{{?dist}}
Summary:        {summary}

License:        {license_spdx}
{('URL:            ' + pkg['url']) if pkg['url'] else 'URL:            ' + cfg['source_url'].split('/archive/')[0]}
Source0:        {source_url}#/%{{pkg_name}}-%{{version}}.tar.gz

BuildArch:      noarch

{br_lines}

{rq_lines}

%global __provides_exclude_from ^%{{install_prefix}}/.*$
%global __requires_exclude_from ^%{{install_prefix}}/.*$

%description
{desc}

%prep
%autosetup -p1 -n {source_dir}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%{{python3}} -m pip install \\
    --root %{{buildroot}} \\
    --prefix %{{install_prefix}} \\
    --no-deps \\
    --no-build-isolation \\
    --no-warn-script-location \\
    --disable-pip-version-check \\
    %{{_pyproject_wheeldir}}/*.whl

%check
%pytest -v test

%files
%license LICENSE
%doc CHANGELOG.rst
# TODO: review the file list — generator emits a permissive glob and you may
# need to enumerate explicit paths to avoid conflicts with sibling packages.
%{{install_prefix}}/lib/python%{{python3_version}}/site-packages/%{{pkg_name}}/
%{{install_prefix}}/lib/python%{{python3_version}}/site-packages/%{{pkg_name}}-%{{version}}.dist-info/
%{{install_prefix}}/share/ament_index/resource_index/packages/%{{pkg_name}}
%{{install_prefix}}/share/%{{pkg_name}}/

%changelog
* {_today_rpm()} {DEFAULT_PACKAGER_NAME} <{DEFAULT_PACKAGER_EMAIL}> - {version}-1
- Initial Fedora COPR build for ROS 2 {distro.capitalize()}.
"""


def render_cmake_spec(pkg: dict, cfg: dict, distro: str, prefix: str) -> str:
    name = pkg["name"]
    version = pkg["version"]
    name_dashed = name.replace("_", "-")
    license_spdx = spdx(pkg["license"])
    summary = f"ROS 2 {distro.capitalize()} {name}"
    desc = clean_description(pkg["description"] or summary)
    install_prefix = f"{prefix}/{distro}"

    source_url = cfg["source_url"].format(version=version)
    source_dir = cfg["source_dir"].format(version=version)
    build_subdir = cfg.get("build_subdir")

    # Determine if package is noarch — pure CMake configuration packages are noarch;
    # packages that compile C/C++ are not. Default to noarch and let the user flip
    # if needed; CHANGELOG comment explains.
    noarch_line = "BuildArch:      noarch\n"

    brs = build_requires(pkg, "ament_cmake", distro, DEFAULT_OS_VERSION)
    rqs = runtime_requires(pkg, "ament_cmake", distro, DEFAULT_OS_VERSION)

    br_lines = "\n".join(f"BuildRequires:  {b}" for b in brs)
    rq_lines = "\n".join(f"Requires:       {r}" for r in rqs)

    if build_subdir:
        push = f"pushd {build_subdir}\n"
        pop = "popd\n"
        license_path = "LICENSE"
        changelog_path = f"{build_subdir}/CHANGELOG.rst"
    else:
        push = ""
        pop = ""
        license_path = "LICENSE"
        changelog_path = "CHANGELOG.rst"

    return f"""%global ros_distro       {distro}
%global pkg_name         {name}
%global install_prefix   {install_prefix}

Name:           ros-%{{ros_distro}}-{name_dashed}
Version:        {version}
Release:        1%{{?dist}}
Summary:        {summary}

License:        {license_spdx}
{('URL:            ' + pkg['url']) if pkg['url'] else 'URL:            ' + cfg['source_url'].split('/archive/')[0]}
Source0:        {source_url}#/{cfg['source_dir'].split('-')[0] if '-' in cfg['source_dir'] else name}-%{{version}}.tar.gz

{noarch_line}
{br_lines}

{rq_lines}

%global __provides_exclude_from ^%{{install_prefix}}/.*$
%global __requires_exclude_from ^%{{install_prefix}}/.*$

%description
{desc}

%prep
%autosetup -p1 -n {source_dir}

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{{install_prefix}}/lib/python%{{python3_version}}/site-packages${{PYTHONPATH:+:$PYTHONPATH}}
{push}%cmake \\
    -DCMAKE_INSTALL_PREFIX=%{{install_prefix}} \\
    -DAMENT_PREFIX_PATH=%{{install_prefix}} \\
    -DCMAKE_PREFIX_PATH=%{{install_prefix}} \\
    -DSETUPTOOLS_DEB_LAYOUT=OFF
%cmake_build
{pop}

%install
export PYTHONPATH=%{{install_prefix}}/lib/python%{{python3_version}}/site-packages${{PYTHONPATH:+:$PYTHONPATH}}
{push}%cmake_install
{pop}

%check
export PYTHONPATH=%{{install_prefix}}/lib/python%{{python3_version}}/site-packages${{PYTHONPATH:+:$PYTHONPATH}}
{push}%ctest
{pop}

%files
%license {license_path}
%doc {changelog_path}
# TODO: review the file list against the build's "Installing:" log lines; the
# generator emits the conventional ament_cmake set but specific packages may
# need additions or trimming.
%{{install_prefix}}/share/%{{pkg_name}}/
%{{install_prefix}}/share/ament_index/resource_index/packages/%{{pkg_name}}
%{{install_prefix}}/share/ament_index/resource_index/package_run_dependencies/%{{pkg_name}}
%{{install_prefix}}/share/ament_index/resource_index/parent_prefix_path/%{{pkg_name}}

%changelog
* {_today_rpm()} {DEFAULT_PACKAGER_NAME} <{DEFAULT_PACKAGER_EMAIL}> - {version}-1
- Initial Fedora COPR build for ROS 2 {distro.capitalize()}.
"""


def _today_rpm() -> str:
    """RPM %changelog date format: 'Day Mon DD YYYY'."""
    import datetime
    return datetime.date.today().strftime("%a %b %d %Y")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_dir", type=Path, help="Path to the ROS package source (containing package.xml)")
    p.add_argument("--config", type=Path, default=None, help="Path to packages.yaml")
    p.add_argument("--distro", default=DEFAULT_DISTRO, help=f"ROS distro (default: {DEFAULT_DISTRO})")
    p.add_argument("--prefix", default=DEFAULT_PREFIX, help=f"Install root prefix (default: {DEFAULT_PREFIX})")
    p.add_argument("--os-version", default=DEFAULT_OS_VERSION, help=f"Fedora version for rosdep (default: {DEFAULT_OS_VERSION})")
    args = p.parse_args()

    pkg_xml = args.source_dir / "package.xml"
    if not pkg_xml.is_file():
        sys.stderr.write(f"ERROR: no package.xml at {pkg_xml}\n")
        sys.exit(1)

    pkg = parse_package_xml(pkg_xml)

    config_path = args.config or Path(__file__).parent / "packages.yaml"
    with config_path.open() as f:
        all_cfg = yaml.safe_load(f)

    if pkg["name"] not in all_cfg:
        sys.stderr.write(f"ERROR: no entry for '{pkg['name']}' in {config_path}\n")
        sys.stderr.write("Add a stanza with source_url, source_dir, optional build_subdir.\n")
        sys.exit(1)

    cfg = all_cfg[pkg["name"]]

    if pkg["build_type"] == "ament_python":
        spec = render_python_spec(pkg, cfg, args.distro, args.prefix)
    elif pkg["build_type"] == "ament_cmake":
        spec = render_cmake_spec(pkg, cfg, args.distro, args.prefix)
    else:
        sys.stderr.write(f"ERROR: unsupported build_type '{pkg['build_type']}'\n")
        sys.exit(1)

    sys.stdout.write(spec)


if __name__ == "__main__":
    main()
