# ADR 0001: Minimal subset scope

- **Status**: Accepted
- **Date**: 2026-05-07

## Context

ROS 2 Jazzy publishes ~320 packages in `ros-jazzy-desktop`, ~140 in `ros-jazzy-ros-base`, ~50 in `ros-jazzy-ros-core`. Maintaining a downstream RPM build of the full desktop install is a part-time job in perpetuity for one maintainer. The primary consumer of this COPR is the O3DE ROS 2 Gem, which directly references only ten packages and pulls in roughly 60–80 transitive deps total.

Upstream ros.org publishes RPMs for RHEL 9, but not Fedora and not CentOS Stream 10. Existing community Fedora COPRs (`tavie/ros2`, `techtasie/ros2`) trail releases and are single-maintainer hobby projects. There is no maintained Jazzy COPR for Fedora 44+ and Stream 10 today.

## Decision

Scope this COPR to the **O3DE-minimal subset** — approximately 70 packages — rather than the full desktop install.

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
