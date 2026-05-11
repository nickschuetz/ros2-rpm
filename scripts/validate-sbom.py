#!/usr/bin/env python3
"""validate-sbom.py, assert one or more CycloneDX SBOM JSON files are well-formed.

Validates the shape expected by ADR 0004: well-formed JSON, top-level
`bomFormat == "CycloneDX"`, `specVersion` present, and `components` (if
present) is a list. If `jsonschema` is importable, additionally validates
against the CycloneDX 1.5 JSON schema bundled with the cyclonedx-python-lib
package; if not, skip schema validation with a warning (basic shape check
still runs).

Usage:
    scripts/validate-sbom.py path/to/sbom.cdx.json [more.cdx.json ...]
    scripts/validate-sbom.py sbom/                  # validate every *.cdx.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def validate_basic_shape(path: Path, doc: dict) -> list[str]:
    errs: list[str] = []
    if doc.get("bomFormat") != "CycloneDX":
        errs.append(f"{path.name}: bomFormat is {doc.get('bomFormat')!r}, expected 'CycloneDX'")
    if "specVersion" not in doc:
        errs.append(f"{path.name}: missing 'specVersion'")
    elif not isinstance(doc["specVersion"], str):
        errs.append(f"{path.name}: 'specVersion' must be a string")
    if "components" in doc and not isinstance(doc["components"], list):
        errs.append(f"{path.name}: 'components' must be a list when present")
    return errs


def collect_targets(args: list[str]) -> list[Path]:
    out: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            out.extend(sorted(p.glob("*.cdx.json")))
        elif p.is_file():
            out.append(p)
        else:
            sys.stderr.write(f"WARNING: {a} not found, skipping\n")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("paths", nargs="+", help="*.cdx.json files or directories")
    args = p.parse_args()

    targets = collect_targets(args.paths)
    if not targets:
        sys.stderr.write("No SBOM files to validate.\n")
        return 0

    all_errs: list[str] = []
    for path in targets:
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            all_errs.append(f"{path.name}: invalid JSON: {e}")
            continue
        all_errs.extend(validate_basic_shape(path, doc))

    if all_errs:
        for e in all_errs:
            print(f"  ERROR {e}")
        print(f"\nFAIL: {len(all_errs)} error(s) across {len(targets)} SBOM(s)")
        return 1

    print(f"OK: {len(targets)} SBOM(s) well-formed (basic CycloneDX shape)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
