#!/usr/bin/env bash
# build-srpm.sh — build SRPMs from spec files.
#
# Reads specs from $1, writes SRPMs to $2.

set -euo pipefail

SPEC_DIR="${1:?usage: build-srpm.sh <spec-dir> <srpm-dir>}"
SRPM_DIR="${2:?usage: build-srpm.sh <spec-dir> <srpm-dir>}"

mkdir -p "$SRPM_DIR"

if ! compgen -G "$SPEC_DIR/*.spec" > /dev/null && \
   ! compgen -G "$SPEC_DIR/generated/*.spec" > /dev/null; then
    echo "No specs in $SPEC_DIR/ — nothing to build."
    exit 0
fi

# Build SRPMs via rpmbuild -bs. Sources expected to be under SOURCES/ relative
# to %{_topdir}; bloom-generated specs include source URLs.
for spec in "$SPEC_DIR"/*.spec "$SPEC_DIR"/generated/*.spec; do
    [ -f "$spec" ] || continue
    rpmbuild -bs \
        --define "_topdir $(pwd)" \
        --define "_sourcedir $(pwd)/sources" \
        --define "_srcrpmdir $SRPM_DIR" \
        --define "_specdir $SPEC_DIR" \
        "$spec"
done

echo "SRPMs in $SRPM_DIR:"
ls -1 "$SRPM_DIR"
