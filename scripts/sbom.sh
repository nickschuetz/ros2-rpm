#!/usr/bin/env bash
# sbom.sh — generate CycloneDX SBOMs for built RPMs in a result dir.
#
# Per ADR 0004, the canonical place for an SBOM is INSIDE each RPM at
# %{_datadir}/doc/<name>/sbom.cdx.json. This script is the fallback /
# audit helper that re-extracts SBOMs from already-built RPMs into a
# flat directory for cross-package inspection.

set -euo pipefail

RESULT_DIR="${1:?usage: sbom.sh <mock-result-dir>}"
OUT_DIR="${SBOM_OUT:-sbom}"

if ! command -v syft >/dev/null 2>&1; then
    echo "syft not installed. dnf install syft (or pull from upstream)." >&2
    exit 1
fi

mkdir -p "$OUT_DIR"

shopt -s nullglob
rpms=("$RESULT_DIR"/*.rpm)
if [ ${#rpms[@]} -eq 0 ]; then
    echo "No RPMs in $RESULT_DIR/ — nothing to inspect."
    exit 0
fi

for rpm in "${rpms[@]}"; do
    name=$(rpm -qp --queryformat '%{NAME}' "$rpm")
    syft "$rpm" -o cyclonedx-json="$OUT_DIR/${name}.cdx.json"
    echo "wrote $OUT_DIR/${name}.cdx.json"
done
