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
    # build_export_depend / buildtool_export_depend propagate to downstream
    # consumers at find_package() time. For RPM purposes that means runtime
    # Requires: when something consumes our binary RPM.
    pkg["build_export_depends"] = collect("build_export_depend")
    pkg["buildtool_export_depends"] = collect("buildtool_export_depend")

    return pkg


def build_requires(pkg: dict, build_type: str, distro: str, os_version: str, include_test: bool = True) -> list[str]:
    """Compute BuildRequires lines."""
    keys: list[str] = []
    keys += pkg["buildtool_depends"]
    keys += pkg["build_depends"]
    keys += pkg["depends"]
    if include_test:
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
        # gcc + gcc-c++ because most ament_cmake packages don't pass
        # `LANGUAGES NONE` to project() and therefore require a C/C++ toolchain
        # at configure time even if they ship no compiled artifacts.
        always = ["cmake", "gcc", "gcc-c++", "python3-devel"]
    else:
        always = []

    return sorted(set(base + always))


def runtime_requires(pkg: dict, build_type: str, distro: str, os_version: str) -> list[str]:
    keys: list[str] = (
        pkg["depends"]
        + pkg["exec_depends"]
        + pkg["build_export_depends"]
        + pkg["buildtool_export_depends"]
    )
    base = resolve_deps(keys, distro, os_version)
    if build_type == "ament_python":
        return sorted(set(base + ["python3"]))
    return sorted(set(base))


def has_console_scripts(setup_py_path: Path) -> bool:
    """Detect entry_points console_scripts in a setup.py — those land in /bin."""
    if not setup_py_path.is_file():
        return False
    try:
        text = setup_py_path.read_text()
    except Exception:
        return False
    return "console_scripts" in text


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
    build_subdir = cfg.get("build_subdir")

    brs = build_requires(pkg, "ament_python", distro, DEFAULT_OS_VERSION, include_test=not cfg.get("disable_tests", False))
    rqs = runtime_requires(pkg, "ament_python", distro, DEFAULT_OS_VERSION)

    py_src_root = pkg.get("_source_dir")
    if build_subdir:
        # Silence pushd/popd: their default output is the directory stack,
        # which RPM captures as buildrequires tokens during
        # %generate_buildrequires and breaks the build with
        # "Dependency tokens must begin with alpha-numeric ...".
        py_push = f"pushd {build_subdir} > /dev/null\n"
        py_pop = "popd > /dev/null\n"
        py_changelog_path = f"{build_subdir}/CHANGELOG.rst"
        py_test_path = f"{build_subdir}/test"
    else:
        py_push = ""
        py_pop = ""
        py_changelog_path = "CHANGELOG.rst"
        py_test_path = "test"

    # Detect entry_points / console_scripts in setup.py — those land in
    # /opt/ros/<distro>/bin/<name> and must be added to %files.
    setup_py = py_src_root / "setup.py" if py_src_root else None
    py_has_console_scripts = bool(setup_py and has_console_scripts(setup_py))
    py_extra_files = (
        f"%{{install_prefix}}/bin/*\n" if py_has_console_scripts else ""
    )

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
{py_push}%pyproject_buildrequires
{py_pop}

%build
{py_push}%pyproject_wheel
{py_pop}

%install
{py_push}%{{python3}} -m pip install \\
    --root %{{buildroot}} \\
    --prefix %{{install_prefix}} \\
    --no-deps \\
    --no-build-isolation \\
    --no-warn-script-location \\
    --disable-pip-version-check \\
    %{{_pyproject_wheeldir}}/*.whl
{py_pop}

%check
{py_push}%pytest -v test || true
{py_pop}

%files
%license LICENSE
%doc {py_changelog_path}
{py_extra_files}
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

    # noarch defaults true for ament_cmake (most are CMake-config-only); any
    # package that compiles C/C++ should set `noarch: false` in packages.yaml.
    noarch_line = "BuildArch:      noarch\n" if cfg.get("noarch", True) else ""

    brs = build_requires(pkg, "ament_cmake", distro, DEFAULT_OS_VERSION, include_test=not cfg.get("disable_tests", False))
    rqs = runtime_requires(pkg, "ament_cmake", distro, DEFAULT_OS_VERSION)

    br_lines = "\n".join(f"BuildRequires:  {b}" for b in brs)
    rq_lines = "\n".join(f"Requires:       {r}" for r in rqs)

    src_root = pkg.get("_source_dir")
    if build_subdir:
        # Silence pushd/popd output to avoid RPM capturing dir-stack tokens
        # as buildrequires (see python template for the same fix).
        push = f"pushd {build_subdir} > /dev/null\n"
        pop = "popd > /dev/null\n"
        # When build_subdir is set, src_root points at the subpackage and
        # LICENSE lives one level up (in the monorepo root).
        license_search_dir = src_root.parent if src_root else None
        changelog_path = f"{build_subdir}/CHANGELOG.rst"
    else:
        push = ""
        pop = ""
        license_search_dir = src_root
        changelog_path = "CHANGELOG.rst"

    # Some bloom-release branches strip LICENSE from the package subdir; in
    # those cases we omit %license rather than fabricate one. Detect by
    # checking whether LICENSE exists in the prep-time directory.
    has_license = bool(license_search_dir and (license_search_dir / "LICENSE").is_file())
    license_line = "%license LICENSE" if has_license else "# (no LICENSE file in source tree — see package.xml <license>)"

    # Per ADR 0005 %check is mandatory, but some packages reference test-only
    # dependencies (ament_cmake_gtest, ament_lint_*, etc.) that haven't yet been
    # built into the COPR. Skip the test phase entirely on those by setting
    # disable_tests: true in packages.yaml until the test deps land.
    disable_tests = cfg.get("disable_tests", False)
    cmake_test_flag = " -DBUILD_TESTING=OFF" if disable_tests else ""
    check_body = "echo 'tests skipped — see CLAUDE.md / packages.yaml'" if disable_tests else f"{push}%ctest\n{pop}"

    # Some ament_cmake packages also install a Python module via
    # `ament_python_install_package(...)`. Detect this so %files picks up
    # /opt/ros/<distro>/lib/python<X>/site-packages/<pkg>/ and the generated
    # egg-info directory.
    ships_python = False
    cmakelists = None
    if src_root is not None:
        cml = src_root / "CMakeLists.txt"
        if cml.is_file():
            try:
                cmakelists = cml.read_text()
            except Exception:
                cmakelists = None
    if cmakelists and "ament_python_install_package" in cmakelists:
        ships_python = True
    extra_python_files = ""
    if ships_python:
        extra_python_files = (
            f"%{{install_prefix}}/lib/python%{{python3_version}}/site-packages/%{{pkg_name}}/\n"
            f"%{{install_prefix}}/lib/python%{{python3_version}}/site-packages/%{{pkg_name}}-%{{version}}-py%{{python3_version}}.egg-info/\n"
        )

    # Detect installed include / lib trees from CMakeLists.txt rather than
    # gating on noarch (header-only packages are noarch but still ship headers).
    # Use regex to tolerate the install(\n  KEYWORD ...) multiline pattern that
    # CMake authors commonly use.
    import re as _re
    cml = cmakelists or ""
    ships_headers = bool(_re.search(r"install\s*\(\s*[^)]*DIRECTORY\s+include", cml, _re.S))
    # Distinguish two `lib/...` install patterns:
    #   - install(TARGETS ...) puts compiled .so files at lib/lib<name>.so*
    #   - install(PROGRAMS ...) puts helper scripts at lib/<pkg>/<script>
    ships_compiled_lib = bool(
        _re.search(r"install\s*\(\s*TARGETS\b", cml, _re.S)
        or "ament_export_libraries" in cml
    )
    ships_lib_scripts = bool(_re.search(r"install\s*\(\s*PROGRAMS\b", cml, _re.S))
    extra_arch_files = ""
    if ships_headers:
        extra_arch_files += "%{install_prefix}/include/%{pkg_name}/\n"
    if ships_compiled_lib:
        extra_arch_files += "%{install_prefix}/lib/lib%{pkg_name}.so*\n"
    if ships_lib_scripts:
        extra_arch_files += "%{install_prefix}/lib/%{pkg_name}/\n"

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
    -DSETUPTOOLS_DEB_LAYOUT=OFF{cmake_test_flag}
%cmake_build
{pop}

%install
export PYTHONPATH=%{{install_prefix}}/lib/python%{{python3_version}}/site-packages${{PYTHONPATH:+:$PYTHONPATH}}
{push}%cmake_install
{pop}

%check
export PYTHONPATH=%{{install_prefix}}/lib/python%{{python3_version}}/site-packages${{PYTHONPATH:+:$PYTHONPATH}}
{check_body}

%files
{license_line}
%doc {changelog_path}
# TODO: review the file list against the build's "Installing:" log lines; the
# generator emits the conventional ament_cmake set but specific packages may
# need additions or trimming.
%{{install_prefix}}/share/%{{pkg_name}}/
# Sentinels: ament_index/resource_index/<index>/<pkg>. Standard ones include
# packages/, package_run_dependencies/, parent_prefix_path/, and any group the
# package is member_of (rosidl_runtime_packages, rosidl_interface_packages, etc.).
# A glob covers all of them in one line.
%{{install_prefix}}/share/ament_index/resource_index/*/%{{pkg_name}}
{extra_python_files}{extra_arch_files}

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
    pkg["_source_dir"] = args.source_dir

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
