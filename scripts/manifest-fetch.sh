#!/usr/bin/env bash
# manifest-fetch.sh, refresh manifest.yaml pins from upstream rosdistro.

set -euo pipefail

DISTRO="${1:?usage: manifest-fetch.sh <distro>}"
ROSDISTRO_RAW="https://raw.githubusercontent.com/ros/rosdistro/master/${DISTRO}/distribution.yaml"

echo "TODO: manifest-fetch.sh is a scaffold."
echo "Steps to implement:"
echo "  1. curl -fsSL $ROSDISTRO_RAW -o /tmp/distribution.yaml"
echo "  2. yq merge with current manifest.yaml, preserving:"
echo "       - direct[] entries (kept as authoritative scope list)"
echo "       - metapackages[] (locally composed)"
echo "     replacing each .version with the upstream release tag."
echo "  3. For each transitive[] entry, look up version from upstream's"
echo "     release/$DISTRO/<package>/<version> tag."
echo "  4. Write back to manifest.yaml; emit a diff for review."
echo "  5. Update generated_at timestamp."
