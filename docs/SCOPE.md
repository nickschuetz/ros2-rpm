# Scope

What is in scope for this COPR, what is out, and why. Changes to this file require a PR with reviewer sign-off and a corresponding ADR for any boundary shift.

## In scope

The package set required by the [O3DE ROS 2 Gem](https://github.com/o3de/o3de-extras/tree/development/Gems/ROS2) and adjacent embedded-robotics workloads — approximately 70 packages.

### Direct consumers
- `rclcpp`
- `builtin_interfaces`
- `std_msgs`
- `sensor_msgs`
- `nav_msgs`
- `geometry_msgs`
- `tf2_ros`
- `ackermann_msgs`
- `vision_msgs`
- `control_msgs`

### Transitive dependencies (representative; see `manifest.yaml` for the full list)
- `rcl`, `rclcpp_components`, `rmw`, `rmw_implementation`, `rmw_fastrtps_cpp`
- `rosidl_*` and `ament_*` build tooling
- Fast DDS, Fast CDR, foonathan_memory
- `tinyxml2`, `console_bridge`, `libyaml`, `spdlog`, `pybind11` (linked from system Fedora packages, not bundled)

### Convenience metapackages
- `ros-jazzy-ros-core` — core libraries and runtime, mirrors upstream's `ros_core`.
- `ros-jazzy-ros-base` — `ros_core` plus the ten direct consumers above. This is the recommended default install.

## Out of scope

Hard out-of-scope; do not propose adding without an ADR.

- **`rviz2`, `rqt_*`** — full desktop tools. Pull in Qt (LGPL-3.0) and a substantial dep tail. Users wanting visualization should layer them in separately, not from this COPR.
- **`gazebo_*` bridges, `ros_gz_*`** — out of scope; Gazebo packaging is itself a project.
- **`navigation2`, `moveit2`** — application stacks; downstream concerns.
- **Anything bringing GPL/AGPL-licensed transitive deps.**
- **Demo nodes, examples, tutorials packages.** They have value but they are not what O3DE consumes.
- **`rmw_cyclonedds_cpp`** — *currently* out of scope. Adding it expands the License aggregate (Cyclone DDS is EPL-2.0). Allowed only as a standalone non-metapackage entry under the License Policy in CLAUDE.md, with an ADR. Not in the initial release.

## Boundary rules

1. **Default metapackages stay permissive-only** (`Apache-2.0` and `BSD-3-Clause`). No exceptions.
2. **Initial release ships permissive-only.** Non-permissive standalone packages are added on demand, with ADRs, after launch.
3. **No bundled forks of system libraries.** If Fedora ships it, link against it. This is what makes Fedora's CVE pipeline cover us.
4. **Any package that grows the dep tail by more than ~5 transitive deps** triggers an ADR — full-desktop creep is the failure mode to avoid.

## Consumers

- Primary: [`o3de-rpm`](https://github.com/nickschuetz/o3de-rpm) via its runtime-deps COPR [`hellaenergy/o3de-dependencies`](https://copr.fedorainfracloud.org/coprs/hellaenergy/o3de-dependencies), which lists `hellaenergy/ros2` as an External Repository.
- Secondary: any Fedora 44+ or CentOS Stream 10 user wanting a permissive ROS 2 Jazzy install without enabling RHEL-targeted upstream RPMs.
