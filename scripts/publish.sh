#!/usr/bin/env bash
# publish.sh — generate, build, validate, and publish one package end-to-end.
#
# Usage:
#   scripts/publish.sh <package_name> [<source_path>]
#
# - Auto-derives <source_path> from build/ament_cmake_full/ament_cmake-*/<package_name>
#   if not supplied (works for ament_cmake monorepo packages).
# - Generates spec via generate-spec.py.
# - Local mock build on fedora-44-x86_64 to catch errors fast.
# - Pushes to all 6 COPR chroots.
#
# Skips if specs/ros-jazzy-<dashed>.spec already exists (manual hand-tuned spec).

set -euo pipefail

PKG="${1:?usage: publish.sh <package_name> [<source_path>]}"
SOURCE_PATH="${2:-}"

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PKG_DASHED="${PKG//_/-}"
SPEC_NAME="ros-jazzy-${PKG_DASHED}"
SPEC="$REPO/specs/${SPEC_NAME}.spec"

# Auto-derive source path from ament_cmake monorepo layout.
if [ -z "$SOURCE_PATH" ]; then
    candidates=(
        "$REPO/build/ament_cmake_full/ament_cmake-"*/"$PKG"
        "$REPO/build/rosidl_pkgsrc/rosidl-"*/"$PKG"
        "$REPO/build/${PKG}_pkgsrc"/*
        "$REPO/build/$PKG"
        "$REPO/build/${PKG}_pkg"
    )
    for c in "${candidates[@]}"; do
        if [ -f "$c/package.xml" ]; then SOURCE_PATH="$c"; break; fi
    done
fi
if [ -z "${SOURCE_PATH:-}" ] || [ ! -f "$SOURCE_PATH/package.xml" ]; then
    echo "ERROR: could not locate source for $PKG. Pass <source_path> explicitly." >&2
    exit 1
fi

echo "==> $PKG"
echo "    source: $SOURCE_PATH"
echo "    spec:   $SPEC"

if [ -f "$SPEC" ]; then
    echo "    spec already exists — skipping generation (hand-tuned?)"
else
    echo "==> Generating spec"
    "$REPO/scripts/generate-spec.py" "$SOURCE_PATH" > "$SPEC"
fi

# Ensure the source tarball exists in build/SOURCES/ for rpmbuild.
VERSION=$(grep -E '^Version:' "$SPEC" | head -1 | awk '{print $2}')
PKGNAME_RAW=$(grep -E '^%global pkg_name' "$SPEC" | head -1 | awk '{print $3}')
SOURCE_URL=$(grep -E '^Source0:' "$SPEC" | head -1 | awk '{print $2}' | cut -d'#' -f1)
RAW_SOURCE_NAME=$(grep -E '^Source0:' "$SPEC" | head -1 | awk '{print $2}' | sed 's|.*#/||')
SOURCE_FILE="$REPO/build/SOURCES/${RAW_SOURCE_NAME//%\{version\}/$VERSION}"
SOURCE_FILE="${SOURCE_FILE//%\{pkg_name\}/$PKGNAME_RAW}"
if [ ! -f "$SOURCE_FILE" ]; then
    echo "==> Fetching source: $SOURCE_URL"
    mkdir -p "$REPO/build/SOURCES"
    curl -fsSL -o "$SOURCE_FILE" "$SOURCE_URL"
fi

echo "==> Local mock build (fedora-44-x86_64)"
"$REPO/scripts/build-one.sh" "$SPEC_NAME" >/dev/null
echo "    local build OK"

echo "==> Pushing to all 6 COPR chroots"
SRPM=$(ls -t "$REPO/build/SRPMS/${SPEC_NAME}-${VERSION}-"*.src.rpm | head -1)
copr-cli build \
    --chroot fedora-44-x86_64 \
    --chroot fedora-44-aarch64 \
    --chroot fedora-rawhide-x86_64 \
    --chroot fedora-rawhide-aarch64 \
    --chroot centos-stream-10-x86_64 \
    --chroot centos-stream-10-aarch64 \
    hellaenergy/ros2 "$SRPM" | tail -10

echo "==> $PKG: published"
