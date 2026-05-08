# Related Work

This repo is one of several ROS-on-Fedora packaging efforts. We aren't reinventing the wheel — we're building a focused, narrowly-scoped slice of it. This page documents the ecosystem honestly so contributors and downstream users understand the landscape.

## Fedora Robotics SIG

The [Fedora Robotics SIG](https://gitlab.com/fedora/sigs/robotics) is the official Fedora-organized effort to bring robotics software to Fedora. Their goals overlap significantly with this repo, and their project is the right long-term home for ROS in Fedora's main repositories.

- **Group homepage:** https://gitlab.com/fedora/sigs/robotics
- **Discussion / mailing:** https://discussion.fedoraproject.org/tag/robotics-sig
- **Meetings:** Every other Thursday, 16:00 UTC — https://calendar.fedoraproject.org/SIGs/

### SIG packaging projects

- **`fedros`** — https://gitlab.com/fedora/sigs/robotics/src/fedros
  Newer Python toolchain. Reads rosdistro, parses every package's `package.xml`, builds a dependency graph, and generates `.spec` files modeled on bloom output. Conceptually identical to `scripts/generate-spec.py` in this repo. Last meaningful update: late 2024.
- **`rosfed`** — https://gitlab.com/fedora/sigs/robotics/src/rosfed
  Older Jinja-template based generator. Backs the community COPR `saypaul/ros`. Still functional; `fedros` is positioned as the successor.
- **`o3de`, `o3de-dependencies`, `o3de-demos`, `physx`, etc.** — https://gitlab.com/groups/fedora/sigs/robotics/rpms — the SIG also packages O3DE's runtime and engine dependencies, which dovetails with the parallel `o3de-rpm` repo.

### Why `hellaenergy/ros2` exists alongside the SIG's effort

The two efforts have **non-overlapping immediate goals** and the contrast is honest, not adversarial:

| | This repo (`hellaenergy/ros2`) | Fedora Robotics SIG |
|---|---|---|
| **Install layout** | `/opt/ros/jazzy/` (matches upstream ROS 2 convention) | Aimed at FHS (`/usr/lib64/...`) for Fedora main-repo eligibility |
| **Distribution channel** | Third-party COPR (now), permanent COPR (later) | Fedora main repos (long-horizon) |
| **Scope** | Phase 1: ~70 packages (rclcpp, message tier, Fast DDS, tf2). Phase 2: full `ros-jazzy-desktop` equivalent. | Full ROS, eventually Fedora-blessed |
| **Priority** | Ship something working for O3DE + embedded robotics, fast | Get ROS into Fedora main repo cleanly, slowly |
| **Maintainer time investment** | ~4 hrs/week steady-state Phase 1 | Volunteer SIG cadence |
| **Patch-tolerance for upstream ROS** | Carry small patches to ship | Push patches upstream first |

In practice this means:

- If you need ROS 2 Jazzy on Fedora **today** and are happy with `/opt/ros/jazzy/`, this COPR is the path.
- If you want ROS 2 in `dnf install` from the official repos and are willing to wait years for upstream FHS-friendliness, the SIG's effort is the path.
- If the SIG's `fedros`-driven COPR eventually offers what this one does and broader, **this repo will defer to it** — see [ADR 0006](adr/0006-full-ros2-desktop-as-eventual-scope.md) for the Phase 2/3 outlook.

### Coordination

The SIG has called out specific concrete pain points that affect us too — `python3-flake8-docstrings` deprecation in Fedora 41+, EPEL 10 build-dep gaps, asimp packaging blockers. These are tracked in their meeting notes and BZ tickets. We hit some of the same issues (we work around the EPEL gap with per-chroot `additional_repos`). Cross-pollination is welcome:

- Open an issue in the SIG tracker (https://gitlab.com/fedora/sigs/robotics/fedora-robotics-sig/-/issues) when this repo discovers a fix that's relevant upstream.
- Mirror useful packaging patches between repos (apache/BSD content can move freely).
- Show up to a meeting before opening any large coordination effort.

## Upstream ROS RPM packaging

- **`packages.ros.org` RHEL builds** — https://docs.ros.org/en/jazzy/Installation/RHEL-Install-RPMs.html. Built against RHEL 9 with Python 3.9; do not run cleanly on Fedora's Python 3.14 ABI. This is the gap this repo fills for Fedora users.
- **bloom-rpm generator** — https://github.com/ros-infrastructure/bloom/tree/master/bloom/generators/rpm. The upstream tool that produces bloom's RHEL spec output. Both `fedros` and this repo use bloom's output as a starting point and post-process it for Fedora compatibility.

## Why "yet another COPR" is acceptable

Multiple Fedora COPRs for ROS exist (`saypaul/ros`, `tavie/ros2`, this one, occasional one-offs). Each has a different posture. As long as each COPR documents its scope, install layout, and license posture honestly — and warns users about cross-COPR conflicts when they enable more than one — this is fine and doesn't dilute the SIG's main-repo effort.

If you have any ROS COPR enabled before installing from `hellaenergy/ros2`, disable it first or expect file conflicts.
