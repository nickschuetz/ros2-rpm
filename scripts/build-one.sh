#!/usr/bin/env bash
# build-one.sh — build a single spec end-to-end (SRPM + mock) for one chroot.
#
# Usage:
#   scripts/build-one.sh <spec-name-without-extension> [chroot]
#
# Examples:
#   scripts/build-one.sh ros-jazzy-ament-package
#   scripts/build-one.sh ros-jazzy-ament-package fedora-44-aarch64
#
# Expects:
#   - specs/<name>.spec to exist
#   - The corresponding source tarball already in build/SOURCES/
#
# Output:
#   - build/SRPMS/<name>-<version>-<release>.src.rpm
#   - build/mock-results/<name>-...rpm
#   - rpmlint pass against the .rpmlintrc filter

set -euo pipefail

SPEC_NAME="${1:?usage: build-one.sh <spec-name> [chroot]}"
CHROOT="${2:-fedora-44-x86_64}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPEC="$REPO_ROOT/specs/${SPEC_NAME}.spec"
BUILD="$REPO_ROOT/build"
SOURCES="$BUILD/SOURCES"
SRPMS="$BUILD/SRPMS"
RESULTS="$BUILD/mock-results"

if [ ! -f "$SPEC" ]; then
    echo "ERROR: $SPEC not found" >&2
    exit 1
fi

mkdir -p "$SOURCES" "$SRPMS" "$RESULTS"

echo "==> Building SRPM for $SPEC_NAME"
rpmbuild -bs \
    --define "_topdir $BUILD" \
    --define "_sourcedir $SOURCES" \
    --define "_srcrpmdir $SRPMS" \
    "$SPEC"

SRPM=$(ls -t "$SRPMS"/${SPEC_NAME}-*.src.rpm | head -1)
echo "==> SRPM: $SRPM"

# Use the direct pulp URL — download.copr.fedorainfracloud.org now redirects
# to packages.redhat.com/api/pulp-content, and mock's dnf doesn't always
# follow the redirect when fetching repodata.
COPR_REPO="https://packages.redhat.com/api/pulp-content/public-copr/hellaenergy/ros2/$CHROOT/"

echo "==> mock --rebuild on $CHROOT (with hellaenergy/ros2 COPR enabled)"
sg mock -c "mock -r '$CHROOT' \
    --addrepo='$COPR_REPO' \
    --resultdir='$RESULTS' \
    '$SRPM'"

echo "==> rpmlint with project filter"
rpmlint --rpmlintrc "$REPO_ROOT/.rpmlintrc" "$RESULTS"/*.rpm

echo "==> done; results in $RESULTS"
