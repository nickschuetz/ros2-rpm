# Related Work

This page documents the broader Fedora-ROS packaging ecosystem so contributors and downstream users understand where this repo fits, and importantly, where it does **not** fit.

## Open Robotics official Fedora packages (the production path)

**For production use, this is the answer.** Open Robotics publishes official ROS 2 RPMs for Fedora starting with **Lyrical Luth** (the 2026 LTS). The install guide is [Installing on RHEL / Fedora (RPM packages)](https://docs.ros.org/en/lyrical/Get-Started/Installation/RHEL-Install-RPMs.html); the packages come from `packages.ros.org` through the official `ros2-release` package. They are:

- Vendor-supported by Open Robotics with the same tooling and SLA as their `packages.ros.org` RHEL builds.
- CVE-tracked and security-advisory-eligible.
- The recommended install path for any robotics fleet, regulated environment, or product shipping ROS 2 on Fedora.

**Status as of 2026-10-28** (re-check before quoting): the Lyrical docs list Fedora (amd64) as a supported binary platform, but the released `ros2` tier for Fedora 43 and 44 holds only the bootstrap packages (`ros2-release`, `ros-build-essential`, `ros-dev-tools`, `bloom-rpm-macros`). The Lyrical package set itself (about 2900 package names) is in the `ros2-testing` tier for Fedora 43 x86_64 only. There is no aarch64 build and no Fedora 44 or 45 Lyrical build yet. To re-check, fetch `http://packages.ros.org/ros2/fedora/<ver>/<arch>/repodata/repomd.xml` (and the `ros2-testing` equivalent), follow its `primary.xml` entry and count `ros-lyrical-*` names, or watch the status page linked from the install guide.

This repo (`hellaenergy/ros2`) **does not compete with that effort**. ADR 0010 captures the pivot: as soon as we learned Open Robotics was taking this on, we cancelled the Phase 2 desktop expansion and dropped the Phase 3 main-repo aspiration. This repo is intentionally a development-only sandbox for ROS 2 on Fedora, useful only until the official Lyrical packages cover the targets it covers: current Fedora releases (44, 45, rawhide), aarch64, and CentOS Stream 10.

If you are reading this because you landed on the COPR page looking for a production solution: **use Open Robotics's Lyrical packages where they cover your platform** (Fedora 43 x86_64 today), or the `packages.ros.org` RHEL builds in a RHEL container. Do not deploy `hellaenergy/ros2` to production.

## Fedora Robotics SIG (Fedora-main-repo effort)

The [Fedora Robotics SIG](https://gitlab.com/fedora/sigs/robotics) is pursuing FHS-compliant ROS packaging for Fedora main repositories on a separate, longer timeline than Open Robotics's third-party RPM channel. Their work is complementary to both Open Robotics's official packages and to this development-only COPR.

- **ROS 2 install docs:** https://docs.fedoraproject.org/en-US/robotics-sig/ros2/
- **Group homepage:** https://gitlab.com/fedora/sigs/robotics
- **Discussion / mailing:** https://discussion.fedoraproject.org/tag/robotics-sig
- **Meetings:** Every other Thursday, 16:00 UTC, https://calendar.fedoraproject.org/SIGs/

### SIG packaging projects

- **`fedros`**, https://gitlab.com/fedora/sigs/robotics/src/fedros
  Newer Python toolchain. Reads rosdistro, parses every package's `package.xml`, builds a dependency graph, and generates `.spec` files modeled on bloom output. Conceptually identical to `scripts/generate-spec.py` in this repo. Last meaningful update: late 2024.
- **`rosfed`**, https://gitlab.com/fedora/sigs/robotics/src/rosfed
  Older Jinja-template based generator. Backs the community COPR `saypaul/ros`. Still functional; `fedros` is positioned as the successor.
- **`o3de`, `o3de-dependencies`, `o3de-demos`, `physx`, etc.**, https://gitlab.com/groups/fedora/sigs/robotics/rpms, the SIG also packages O3DE's runtime and engine dependencies, which dovetails with the parallel `o3de-rpm` repo.

### Where this repo and the SIG diverge

| | This repo (`hellaenergy/ros2`) | Fedora Robotics SIG |
|---|---|---|
| **Status** | Development-only sandbox for Jazzy | Long-horizon FHS-compliant Fedora-main effort |
| **Install layout** | `/opt/ros/jazzy/` (upstream ROS 2 convention) | Targets FHS (`/usr/lib64/...`) for Fedora main eligibility |
| **Distribution channel** | Third-party COPR | Fedora main repos (eventually) |
| **Production posture** | None claimed; defers to Open Robotics's Lyrical | None yet; aiming at Fedora's normal review/QA gates |
| **Scope** | Phase 1 minimal subset + Phase 2 dev-sandbox (~160 packages); rviz2 chain deferred | Full ROS, eventually |

### Coordination

The SIG has called out concrete pain points that affect us too, `python3-flake8-docstrings` deprecation in Fedora 41+, EPEL 10 build-dep gaps, asimp packaging blockers. We hit the same issues (we work around the EPEL gap with per-chroot `additional_repos`). Cross-pollination is welcome:

- Open an issue in the SIG tracker (https://gitlab.com/fedora/sigs/robotics/fedora-robotics-sig/-/issues) when this repo discovers a fix that's relevant upstream.
- Mirror useful packaging patches between repos (Apache/BSD content can move freely).
- Show up to a meeting before opening any large coordination effort.

[`scripts/smoke-test.sh`](../scripts/smoke-test.sh) is intentionally source-agnostic: it works against any `/opt/ros/jazzy/` install regardless of where the RPMs came from (this COPR, the SIG's RPMs at the install-docs URL above, or `packages.ros.org`'s RHEL builds run in a RHEL 9 container). PR [#3](https://github.com/nickschuetz/ros2-rpm/pull/3) (by SIG contributor [@odra](https://github.com/odra)) is what made the foonathan-memory check cross-source friendly.

## Upstream ROS RPM packaging

- **`packages.ros.org` RHEL builds**, https://docs.ros.org/en/jazzy/Installation/RHEL-Install-RPMs.html. Built against RHEL 9 with Python 3.9; do not run cleanly on Fedora's Python 3.14 ABI. Today they are the production path on RHEL; with Lyrical the same channel extends to Fedora (see the first section above for what is published so far).
- **bloom-rpm generator**, https://github.com/ros-infrastructure/bloom/tree/master/bloom/generators/rpm. The upstream tool that produces bloom's RHEL spec output. Both `fedros` and this repo use bloom's output as a starting point and post-process it for Fedora compatibility.

## Why "yet another COPR" was the right call (briefly)

In the window between "no Fedora-native ROS 2 today" and "Open Robotics ships official Fedora packages with Lyrical for the platforms you run," it is useful to have a development-grade ROS 2 on Fedora available. That window is what `hellaenergy/ros2` covers. Once the official Lyrical packages cover current Fedora releases and aarch64, this repo's value drops sharply, by design.

If you have any ROS COPR enabled before installing from `hellaenergy/ros2`, disable it first or expect file conflicts. All ROS COPRs install under `/opt/ros/jazzy/`, so a mixed install will fight at the filesystem level.
