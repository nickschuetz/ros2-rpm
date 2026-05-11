#!/usr/bin/env python3
"""verify-specs.py — codify what good looks like for ros2-rpm specs.

Walks specs/*.spec and asserts every spec conforms to the standards in
CLAUDE.md (and ADR 0005). Default mode fails on forbidden patterns,
invalid SPDX, em-dashes, and missing patch metadata. Pass
--devel-strict to additionally enforce the -devel subpackage mandate
(currently warn-only because no spec ships a -devel yet; that's the
known gap CLAUDE.md flags as "checked in PR review until a verifier
script exists").

Usage:
    scripts/verify-specs.py                              # default
    scripts/verify-specs.py --devel-strict               # promote devel to fatal
    scripts/verify-specs.py --json                       # machine output
    scripts/verify-specs.py specs/ros-jazzy-foo.spec ... # check a subset
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = REPO_ROOT / "specs"
PATCHES_DIR = SPEC_DIR / "patches"

EM_DASH = "—"

# Forbidden patterns. Each entry: (pattern_regex, human_reason).
# Order matches CLAUDE.md "Patterns to drop on sight" and "Forbidden settings".
FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    (r"^Group:",                  "obsolete Group: tag"),
    (r"^BuildRoot:",              "obsolete BuildRoot: tag"),
    (r"^%clean\b",                "obsolete %clean section"),
    (r"^%defattr\b",              "obsolete %defattr(...) — RPM handles defaults"),
    (r"^%py3_build\b",            "%py3_build deprecated; use %pyproject_wheel"),
    (r"^%py3_install\b",          "%py3_install deprecated; use raw pip with %{_pyproject_wheeldir}"),
    (r"%\{__cmake\}",             "hardcoded %{__cmake}; use %cmake / %cmake_build / %cmake_install"),
    (r"%pyproject_buildrequires\s+-w",
                                  "%pyproject_buildrequires -w deprecated 2025; drop the -w flag"),
    (r"^%setup\s+-q\b",           "%setup -q with numbered patches forbidden; use %autosetup -p1"),
    (r"^%global\s+debug_package\s+%\{nil\}",
                                  "debug_package %{nil} disables debuginfo; forbidden per CLAUDE.md"),
    (r"^%global\s+_enable_debug_packages\s+0",
                                  "_enable_debug_packages 0 disables debuginfo; forbidden per CLAUDE.md"),
    (r"^%global\s+_without_check\s+1",
                                  "_without_check 1 disables %check; forbidden per CLAUDE.md"),
    (r"^%doc\s+LICENSE\b",        "%doc LICENSE is wrong; use %license LICENSE"),
]

# Fedora-approved SPDX tokens we have actively decided to ship. Anything
# else trips the verifier and forces a human decision (likely an ADR).
APPROVED_SPDX_TOKENS = {
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "MIT",
    "ISC",
    "Zlib",
    "BSL-1.0",
    "EPL-2.0",
    "MPL-2.0",
    "LGPL-2.1-only",
    "LGPL-2.1-or-later",
    "LGPL-3.0-only",
    "LGPL-3.0-or-later",
    "CC0-1.0",
}

DEP3_REQUIRED_HEADERS = {"Description", "Origin", "Forwarded", "Last-Update"}


@dataclass
class Finding:
    spec: Path
    line: int | None
    rule: str
    severity: str
    message: str


@dataclass
class Result:
    findings: list[Finding] = field(default_factory=list)

    def add(self, **kw) -> None:
        self.findings.append(Finding(**kw))

    def has_fatal(self) -> bool:
        return any(f.severity == "error" for f in self.findings)


def spdx_tokenize(license_expr: str) -> list[str]:
    """Split a Fedora SPDX expression into leaf tokens for membership check.

    Handles parens and the AND/OR/WITH operators. We strip everything that
    isn't a leaf; "Apache-2.0 AND (BSD-3-Clause OR MIT)" returns
    ["Apache-2.0", "BSD-3-Clause", "MIT"].
    """
    s = re.sub(r"[()]", " ", license_expr)
    parts = re.split(r"\s+(?:AND|OR|WITH)\s+", s)
    return [p.strip() for p in parts if p.strip()]


# Centralized exemption register: spec name -> set of rule-id strings the spec
# is allowed to violate. Every entry must point to a documented reason
# (CLAUDE.md, an ADR, or PACKAGING-LESSONS.md). Keep this list small and
# auditable; if an exemption category grows past five entries, write an ADR
# that either lifts the rule or moves the exception into the codified design.
EXEMPTIONS: dict[str, set[str]] = {
    # Vendor packages: external sources built via ExternalProject. Debug
    # extraction either finds nothing (pure CMake-config) or produces an
    # empty -debuginfo; suppressing keeps the build clean rather than
    # shipping an empty debug RPM. See PACKAGING-LESSONS.md.
    "ros-jazzy-foonathan-memory-vendor.spec": {"debug_package-nil"},
    "ros-jazzy-tinyxml2-vendor.spec":         {"debug_package-nil"},
    "ros-jazzy-console-bridge-vendor.spec":   {"debug_package-nil"},
    "ros-jazzy-libyaml-vendor.spec":          {"debug_package-nil"},
    "ros-jazzy-pybind11-vendor.spec":         {"debug_package-nil"},
    "ros-jazzy-spdlog-vendor.spec":           {"debug_package-nil"},
    "ros-jazzy-tango-icons-vendor.spec":      {"debug_package-nil"},
    "ros-jazzy-rviz-ogre-vendor.spec":        {"debug_package-nil"},
    "ros-jazzy-rviz-assimp-vendor.spec":      {"debug_package-nil"},
    # rclpy ships its pybind11 extension inside site-packages, not under
    # /lib/lib*.so; the standard debuginfo scan finds nothing and produces
    # an empty subpackage. See PACKAGING-LESSONS.md.
    "ros-jazzy-rclpy.spec":                   {"debug_package-nil"},
    # python_qt_binding is pure-Python Qt glue, no compiled artifacts;
    # debugsource list is empty.
    "ros-jazzy-python-qt-binding.spec":       {"debug_package-nil"},
}

# Map each FORBIDDEN_PATTERNS regex to a short rule-id for the exemption
# register. Order matches FORBIDDEN_PATTERNS.
FORBIDDEN_PATTERN_IDS = [
    "group-tag", "buildroot-tag", "clean-section", "defattr",
    "py3-build", "py3-install", "raw-cmake", "pyproject-w-flag",
    "setup-q-with-patches", "debug_package-nil", "enable-debug-packages-zero",
    "without-check", "doc-license-mismatch",
]


def check_forbidden_patterns(spec_path: Path, text: str, result: Result) -> None:
    exempt = EXEMPTIONS.get(spec_path.name, set())
    for lineno, line in enumerate(text.splitlines(), start=1):
        for (pattern, reason), rule_id in zip(FORBIDDEN_PATTERNS, FORBIDDEN_PATTERN_IDS):
            if re.search(pattern, line):
                if rule_id in exempt:
                    continue
                result.add(spec=spec_path, line=lineno, rule="forbidden-pattern",
                           severity="error", message=f"{reason}: {line.strip()!r}")


def check_em_dashes(spec_path: Path, text: str, result: Result) -> None:
    for lineno, line in enumerate(text.splitlines(), start=1):
        if EM_DASH in line:
            result.add(spec=spec_path, line=lineno, rule="em-dash",
                       severity="error",
                       message=f"em-dash (U+2014) found; replace per project rule: {line.strip()!r}")


def check_spdx_license(spec_path: Path, text: str, result: Result) -> None:
    m = re.search(r"^License:\s+(.+?)\s*$", text, re.MULTILINE)
    if not m:
        result.add(spec=spec_path, line=None, rule="missing-license",
                   severity="error", message="no License: field")
        return
    expr = m.group(1)
    tokens = spdx_tokenize(expr)
    unknown = [t for t in tokens if t not in APPROVED_SPDX_TOKENS]
    if unknown:
        result.add(spec=spec_path, line=None, rule="spdx-token",
                   severity="error",
                   message=(f"License: {expr!r} contains unapproved SPDX token(s) "
                            f"{unknown!r}; either fix the spelling or add to "
                            f"APPROVED_SPDX_TOKENS via an ADR"))


def check_patch_references(spec_path: Path, text: str, result: Result) -> None:
    """Every Patch%N: <file> must have specs/patches/<file> with DEP-3 headers."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        m = re.match(r"^Patch\d+:\s+(\S+)", line)
        if not m:
            continue
        patch_name = m.group(1)
        patch_path = PATCHES_DIR / patch_name
        if not patch_path.is_file():
            result.add(spec=spec_path, line=lineno, rule="patch-missing-file",
                       severity="error",
                       message=f"Patch references {patch_name!r} but specs/patches/{patch_name} does not exist")
            continue
        head = patch_path.read_text(errors="replace").split("\n---", 1)[0]
        present = {h for h in DEP3_REQUIRED_HEADERS if re.search(rf"^{h}:", head, re.MULTILINE)}
        missing = DEP3_REQUIRED_HEADERS - present
        if missing:
            result.add(spec=spec_path, line=lineno, rule="patch-dep3-headers",
                       severity="error",
                       message=(f"specs/patches/{patch_name} missing DEP-3 header(s) "
                                f"{sorted(missing)!r}"))


def check_devel_split(spec_path: Path, text: str, result: Result, strict: bool) -> None:
    """If main %files contains -devel content but no -devel subpackage exists, flag it."""
    has_devel_files = bool(re.search(r"^%files\s+devel\b", text, re.MULTILINE))
    if has_devel_files:
        return

    main_files_match = re.search(
        r"^%files\b(?!\s+\w)(.*?)(?=^%(?:files|changelog|package|prep|build|install|check)\b|\Z)",
        text, re.MULTILINE | re.DOTALL)
    if not main_files_match:
        return
    main_files = main_files_match.group(1)

    devel_indicators = []
    if re.search(r"/include\b", main_files) or "/include/" in main_files:
        devel_indicators.append("headers under include/")
    if re.search(r"\.cmake\b", main_files):
        devel_indicators.append("CMake config (*.cmake)")
    if re.search(r"\.pc\b", main_files):
        devel_indicators.append("pkg-config (*.pc)")

    if devel_indicators:
        severity = "error" if strict else "warning"
        result.add(spec=spec_path, line=None, rule="devel-split",
                   severity=severity,
                   message=(f"main %files ships {', '.join(devel_indicators)} "
                            f"but no '%files devel' subpackage exists "
                            f"(see CLAUDE.md 'Subpackage split policy')"))


def verify_spec(spec_path: Path, devel_strict: bool) -> Result:
    result = Result()
    try:
        text = spec_path.read_text()
    except UnicodeDecodeError as e:
        result.add(spec=spec_path, line=None, rule="encoding",
                   severity="error", message=f"spec is not valid UTF-8: {e}")
        return result

    check_forbidden_patterns(spec_path, text, result)
    check_em_dashes(spec_path, text, result)
    check_spdx_license(spec_path, text, result)
    check_patch_references(spec_path, text, result)
    check_devel_split(spec_path, text, result, strict=devel_strict)
    return result


def render_text(results: dict[Path, Result]) -> str:
    lines: list[str] = []
    fatal = 0
    warn = 0
    clean = 0
    for spec, r in sorted(results.items()):
        if not r.findings:
            clean += 1
            continue
        lines.append(f"\n{spec.name}")
        for f in r.findings:
            tag = "ERROR" if f.severity == "error" else "WARN "
            loc = f":{f.line}" if f.line is not None else ""
            lines.append(f"  {tag} {f.rule}{loc}  {f.message}")
            if f.severity == "error":
                fatal += 1
            else:
                warn += 1
    lines.append("")
    lines.append(f"Summary: {clean} clean, {fatal} error(s), {warn} warning(s) across {len(results)} spec(s)")
    return "\n".join(lines)


def render_json(results: dict[Path, Result]) -> str:
    out = []
    for spec, r in sorted(results.items()):
        for f in r.findings:
            out.append({
                "spec": f.spec.name,
                "line": f.line,
                "rule": f.rule,
                "severity": f.severity,
                "message": f.message,
            })
    return json.dumps(out, indent=2)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("specs", nargs="*", help="spec files to check (default: specs/*.spec)")
    p.add_argument("--devel-strict", action="store_true",
                   help="Promote -devel subpackage warnings to errors.")
    p.add_argument("--json", action="store_true", help="Machine-readable output.")
    args = p.parse_args()

    if args.specs:
        targets = [Path(s) for s in args.specs]
    else:
        targets = sorted(SPEC_DIR.glob("*.spec"))

    if not targets:
        sys.stderr.write("No spec files to verify.\n")
        return 0

    results: dict[Path, Result] = {}
    for spec in targets:
        results[spec] = verify_spec(spec, devel_strict=args.devel_strict)

    if args.json:
        print(render_json(results))
    else:
        print(render_text(results))

    any_fatal = any(r.has_fatal() for r in results.values())
    return 1 if any_fatal else 0


if __name__ == "__main__":
    sys.exit(main())
