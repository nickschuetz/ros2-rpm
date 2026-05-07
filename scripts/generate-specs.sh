#!/usr/bin/env bash
# generate-specs.sh — produce RPM spec files from manifest.yaml.
#
# For each entry in manifest.yaml, this script:
#   1. Fetches the upstream tarball at the pinned version.
#   2. Runs `bloom-generate rosrpm` to produce a spec.
#   3. Post-processes the spec to enforce repo conventions:
#        - SPDX License: expression
#        - %autosetup, %cmake macros
#        - %check enabled
#        - %install hook for syft -> %{_datadir}/doc/<name>/sbom.cdx.json
#
# This script is currently a scaffold. Real implementation requires:
#   - python3-bloom installed (dnf install python3-bloom)
#   - rosdep keys for Fedora 44 / Stream 10 (may need upstream PRs)
#   - yq for parsing manifest.yaml

set -euo pipefail

SPEC_DIR="${1:?usage: generate-specs.sh <output-spec-dir>}"
mkdir -p "$SPEC_DIR/generated"

echo "TODO: generate-specs.sh is a scaffold."
echo "Steps to implement:"
echo "  1. Parse manifest.yaml (yq '.direct + .transitive | .[]')."
echo "  2. For each pkg: git clone --depth 1 --branch \$version \$repo"
echo "  3. cd into clone; bloom-generate rosrpm"
echo "  4. Move generated spec to $SPEC_DIR/generated/"
echo "  5. Post-process per ADR 0005 (SPDX, %autosetup, %cmake, %pyproject_*, %check, %license)."
echo "  6. Inject SBOM hook per ADR 0004."
