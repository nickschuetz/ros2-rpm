"""Shared distro configuration for the multi-distro ros2-rpm tree.

One place to answer "where does distro X's stuff live and which COPR does it
publish to." Import this from every script that walks specs or talks to COPR
so adding a third distro later is a one-line change to DISTROS below.

Layout this module assumes (see ADR 0012):
    specs/<distro>/*.spec
    specs/<distro>/patches/
    distros/<distro>/packages.yaml
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Distros this repo builds, flagship first by convention. The flagship is the
# current LTS and is where new development is focused; others are maintenance.
DISTROS: tuple[str, ...] = ("lyrical", "jazzy")
FLAGSHIP = "lyrical"


def spec_dir(distro: str) -> Path:
    return REPO_ROOT / "specs" / distro


def packages_yaml(distro: str) -> Path:
    return REPO_ROOT / "distros" / distro / "packages.yaml"


def rosdistro_url(distro: str) -> str:
    return f"https://raw.githubusercontent.com/ros/rosdistro/master/{distro}/distribution.yaml"


def copr_project(distro: str) -> str:
    """hellaenergy/ros2 always tracks the flagship; others get a -<distro> suffix.

    See ADR 0012, COPR layout option A. At the next LTS transition the flagship
    moves and the outgoing distro inherits its `ros2-<name>` project.
    """
    return "hellaenergy/ros2" if distro == FLAGSHIP else f"hellaenergy/ros2-{distro}"


def spec_path(distro: str, pkg: str) -> Path:
    """Spec file path for a rosdep-key package name (underscores become dashes)."""
    return spec_dir(distro) / f"ros-{distro}-{pkg.replace('_', '-')}.spec"


def distro_from_spec_name(spec_name: str) -> str | None:
    """Parse the distro out of a `ros-<distro>-<pkg>` spec name (no extension)."""
    parts = spec_name.split("-")
    if len(parts) >= 3 and parts[0] == "ros" and parts[1] in DISTROS:
        return parts[1]
    return None


def all_spec_files(distros: tuple[str, ...] = DISTROS):
    """Yield (distro, Path) for every spec across the requested distros."""
    for d in distros:
        sd = spec_dir(d)
        if sd.is_dir():
            for spec in sorted(sd.glob("*.spec")):
                yield d, spec
