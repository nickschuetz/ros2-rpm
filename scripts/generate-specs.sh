#!/usr/bin/env bash
# generate-specs.sh, produce RPM spec files from manifest.yaml.
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

echo "generate-specs.sh, scaffolded, not fully wired yet."
echo
echo "Working flow today (manual):"
echo "  1. mkdir -p build && cd build"
echo "  2. git clone --depth 1 --branch release/jazzy/<pkg>/<version>-1 \\"
echo "       https://github.com/ros2-gbp/<pkg>-release <pkg>"
echo "  3. cd <pkg> && bloom-generate rosrpm --ros-distro jazzy"
echo "  4. ../../scripts/postprocess-spec.sh rpm/template.spec"
echo "  5. Manually finish the spec: %py3_* -> %pyproject_*, %check, %files,"
echo "     Source0, BuildArch. Reference: specs/ros-jazzy-ament-package.spec."
echo "  6. cp rpm/template.spec ../../specs/ros-jazzy-<pkg-dashed>.spec"
echo "  7. Download Source0 tarball into build/SOURCES/"
echo "  8. ../../scripts/build-one.sh ros-jazzy-<pkg-dashed>"
echo
echo "TODO: automate steps 2-7 in this script as patterns repeat across more"
echo "packages. The first hand-walkthrough (ament_package) is committed under"
echo "specs/ as the canonical example."
