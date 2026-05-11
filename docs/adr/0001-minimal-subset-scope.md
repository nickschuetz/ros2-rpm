# ADR 0001: Minimal subset scope

- **Status**: Accepted as the project's final scope (after the 2026-05-08 development-only pivot, see ADR 0010). Originally framed as Phase 1 of a phased plan; ADR 0006 (Phase 2 expansion) is now cancelled and ADR 0010 makes this minimal subset the project's permanent scope.
- **Date**: 2026-05-07
- **Realization note (2026-05-08)**: Phase 1 minimal subset shipped, ~85 packages live across all 6 chroot/arch pairs. The "~70 packages" estimate undercounted by ~15 due to the rosidl chain expanding more than expected. See [`docs/build-order.md`](../build-order.md) for the realized dependency tiers.
- **Pivot note (2026-05-08)**: Open Robotics is taking on official Fedora support starting with Lyrical Luth. ADR 0010 makes this minimal subset the project's final scope (no Phase 2, no Phase 3) and reframes the entire repo as development-only.

## Context

ROS 2 Jazzy publishes ~320 packages in `ros-jazzy-desktop`, ~140 in `ros-jazzy-ros-base`, ~50 in `ros-jazzy-ros-core`. Maintaining a downstream RPM build of the full desktop install is a part-time job in perpetuity for one maintainer. The primary consumer of this COPR is the O3DE ROS 2 Gem, which directly references only ten packages and pulls in roughly 60–80 transitive deps total.

Upstream ros.org publishes RPMs for RHEL 9, but not Fedora and not CentOS Stream 10. Existing community Fedora COPRs (`tavie/ros2`, `techtasie/ros2`) trail releases and are single-maintainer hobby projects. There is no maintained Jazzy COPR for Fedora 44+ and Stream 10 today.

## Decision

Scope this COPR to the **O3DE-minimal subset**, approximately 70 packages, rather than the full desktop install.

Initial in-scope packages: `rclcpp`, `builtin_interfaces`, `std_msgs`, `sensor_msgs`, `nav_msgs`, `geometry_msgs`, `tf2_ros`, `ackermann_msgs`, `vision_msgs`, `control_msgs`, plus their transitive deps including `rmw_fastrtps_cpp` + Fast DDS.

Deliberately out: `rviz2`, `rqt_*`, `gazebo_*` bridges, `navigation2`, `moveit2`, demos, examples.

## Consequences

**Positive**:
- Maintenance load is bounded; one maintainer can sustain it.
- License story stays clean (`Apache-2.0 AND BSD-3-Clause` aggregate).
- Build matrix is tractable across 8 chroot/arch pairs.
- Clear scope statement makes contributor onboarding straightforward.

**Negative**:
- Users wanting `rviz2` or full desktop must source it elsewhere.
- A second COPR or an upstream-RPM-on-container path is needed for those use cases.

**Neutral**:
- Future expansion via standalone packages (per ADR 0003) remains possible without renegotiating scope.
