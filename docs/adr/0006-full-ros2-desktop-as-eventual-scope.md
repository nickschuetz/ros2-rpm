# ADR 0006: Full `ros-jazzy-desktop`-equivalent as eventual scope; minimal subset is Phase 1

- **Status**: Accepted
- **Date**: 2026-05-07
- **Supersedes**: ADR 0001 in part (minimal subset becomes Phase 1, not the terminal scope)

## Context

ADR 0001 scoped this COPR to ~70 packages — what the O3DE ROS 2 Gem directly consumes — for maintenance reasons. Reconsidering against the broader Fedora community: a typical Fedora robotics developer wants to write nodes, visualize with `rviz2`, debug with `rqt_*`, run launch files, and simulate via Gazebo bridges. The minimal subset serves only embedded message-passing use cases.

State of ROS 2 on Fedora as of 2026-05:
- `packages.ros.org` ships RHEL 9 RPMs only; the Python 3.9/3.11 binaries do not work on Fedora 44's Python 3.14.
- `tavie/ros2` and similar community COPRs are single-maintainer hobby projects with partial coverage that trails Fedora releases.
- `morxa/rosfed` was archived 2024-11-01 (ROS 1 only).
- Fedora's main repos ship no ROS 2.

The "where do I get ROS 2 on Fedora" question has no good answer today. Whoever lands a maintained, current, full Jazzy COPR for Fedora 44+ fills a real community gap.

## Decision

**Eventual scope: full `ros-jazzy-desktop`-equivalent** — approximately 320 packages, including `rviz2`, `rqt_*`, navigation stacks, common visualization, and alternative RMW implementations.

**Delivery: phased.**

### Phase 1 — pipeline proving ground

~70 packages (the original ADR 0001 scope). Ships first. Validates the bloom + rosdep + Python-3.14 patch chain on a small surface where licensing stays clean (`Apache-2.0 AND BSD-3-Clause`) and time-to-first-build is short.

### Phase 2 — `ros-jazzy-desktop` equivalent

~250 additional packages. Ships once Phase 1 has demonstrated the pipeline works in production.

### Phase 2 entry gate

All of these must hold before Phase 2 work begins:

1. Phase 1 has shipped at least one stable build of every Phase 1 package across all 8 chroot/arch pairs.
2. Phase 1 build matrix has been green for 30+ continuous days.
3. The CVE-feed pipeline has demonstrably triggered at least one rebuild for a Fedora-system-dep CVE without manual intervention.
4. Source pin sync from rosdistro is automated (no `version: TBD` placeholders requiring manual resolution).
5. Maintainer has bandwidth for ~1 day/week steady-state load (vs. Phase 1's ~4 hrs/week).

## Consequences

**Positive**:
- Fills a real Fedora-community gap. The COPR becomes useful to nearly every Fedora ROS 2 user, not only O3DE consumers.
- Aligns with how every other Linux distro packages ROS 2 — sets expectations correctly.
- Justifies long-term maintenance investment with a proportionally larger user base.
- Phased delivery hedges against project failure: Phase 1 ships something useful even if Phase 2 stalls.

**Negative**:
- ~5× maintenance load in Phase 2 vs. Phase 1 (~1 day/week vs. ~4 hrs/week).
- License aggregate becomes heterogeneous: `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0` (Qt/rviz2), possibly `AND EPL-2.0` (Cyclone DDS). README/COPR/CITATION must disclose accurately. Downstream redistributors who bundle binaries face additional obligations — they handle this, not us.
- Build matrix scales linearly with package count.

**Neutral**:
- Phase 1 work is not wasted; it is the explicit foundation for Phase 2.
- O3DE consumers see no functional change — `ros-jazzy-ros-base` keeps its current shape across both phases.

## Compatibility with O3DE licensing

O3DE is Apache-2.0. ROS 2 components reach O3DE via dynamic linking through the ROS 2 Gem at runtime. The standard packaging model — O3DE RPM declares `Requires: ros-jazzy-rclcpp` etc. as runtime deps, not vendored sources — keeps each RPM's license clean. Dynamic linking across stable ABI boundaries to LGPL-3.0/EPL-2.0 libraries does not make either party a derivative work of the other, and is the standard practice for Linux distro packaging of mixed-license stacks (Fedora itself ships Apache-licensed apps that link against LGPL Qt).

Downstream redistributors who *bundle* binary distributions face additional obligations from the heterogeneous aggregate; that is their concern, handled at their distribution layer, not by this COPR.
