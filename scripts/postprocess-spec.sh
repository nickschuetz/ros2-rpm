#!/usr/bin/env bash
# postprocess-spec.sh — apply ros2-rpm transformations to a bloom-generated spec.
#
# bloom-generate rosrpm produces specs that are mostly modern but diverge from
# our ADR 0005 standards in specific ways. This script applies the universal
# transformations; package-specific work (Source0 URL, %files, %check body)
# still requires human review.
#
# What this DOES handle:
#   - License: SPDX normalization (`Apache License 2.0` -> `Apache-2.0`, etc.)
#
# What this does NOT yet handle (manual edits required per package):
#   - %py3_build / %py3_install replacement with %pyproject_buildrequires /
#     %pyproject_wheel + raw pip install (using --prefix=/opt/ros/<distro>)
#   - %check unconditional (drop %bcond_without tests guard)
#   - %files explicit paths including %license and %doc
#   - Source0 URL fixup (bloom emits a placeholder)
#   - BuildArch: noarch for ament_python and message packages
#
# When the next package goes through, broaden this script with the patterns
# that turn out to repeat. See specs/ros-jazzy-ament-package.spec for the
# canonical hand-tuned reference.

set -euo pipefail

SPEC="${1:?usage: postprocess-spec.sh <spec-file>}"

if [ ! -f "$SPEC" ]; then
    echo "ERROR: $SPEC not found" >&2
    exit 1
fi

# License: SPDX normalization. Bloom passes the package.xml <license> string
# through verbatim; Fedora requires SPDX expressions.
sed -i \
    -e 's|^License:[[:space:]]*Apache License 2\.0[[:space:]]*$|License:        Apache-2.0|' \
    -e 's|^License:[[:space:]]*Apache License, Version 2\.0[[:space:]]*$|License:        Apache-2.0|' \
    -e 's|^License:[[:space:]]*Apache 2\.0[[:space:]]*$|License:        Apache-2.0|' \
    -e 's|^License:[[:space:]]*Apache-License-2\.0[[:space:]]*$|License:        Apache-2.0|' \
    -e 's|^License:[[:space:]]*BSD-License[[:space:]]*$|License:        BSD-3-Clause|' \
    -e 's|^License:[[:space:]]*BSD[[:space:]]*$|License:        BSD-3-Clause|' \
    -e 's|^License:[[:space:]]*BSD 3-Clause[[:space:]]*$|License:        BSD-3-Clause|' \
    -e 's|^License:[[:space:]]*MIT-License[[:space:]]*$|License:        MIT|' \
    -e 's|^License:[[:space:]]*ASL 2\.0[[:space:]]*$|License:        Apache-2.0|' \
    "$SPEC"

echo "applied SPDX License normalization to $SPEC"
echo
echo "Manual edits still required:"
echo "  - Replace %py3_build/%py3_install with %pyproject_buildrequires /"
echo "    %pyproject_wheel + raw pip install (--prefix=%{install_prefix},"
echo "    using %{_pyproject_wheeldir} for wheel discovery)"
echo "  - Make %check unconditional; drop %bcond_without tests"
echo "  - Replace %files /opt/ros/<distro> with explicit per-file/per-dir entries"
echo "    including %license and %doc"
echo "  - Set Source0 to upstream GitHub tarball or release-repo URL"
echo "  - Add BuildArch: noarch for pure-Python and message-only packages"
echo "  - See specs/ros-jazzy-ament-package.spec for the canonical reference."
