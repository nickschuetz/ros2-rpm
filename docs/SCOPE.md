# Scope

What is in scope for this COPR, what is out, and why. Changes to this file require a PR with reviewer sign-off and a corresponding ADR for any boundary shift.

The package set is delivered in **two phases**, with **Phase 3** as an aspirational separate-effort target. See [ADR 0006](adr/0006-full-ros2-desktop-as-eventual-scope.md) and [ADR 0007](adr/0007-install-location-opt-ros-jazzy.md).

## Phase 1 — current shipping scope

The package set required by the [O3DE ROS 2 Gem](https://github.com/o3de/o3de-extras/tree/development/Gems/ROS2) and adjacent embedded-robotics workloads — approximately 70 packages. Pipeline proving ground for Phase 2.

### Phase 1 direct consumers

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

### Phase 1 transitive dependencies (representative; full list in `manifest.yaml`)

- `rcl`, `rclcpp_components`, `rmw`, `rmw_implementation`, `rmw_fastrtps_cpp`
- `rosidl_*` and `ament_*` build tooling
- Fast DDS, Fast CDR, foonathan_memory
- `tinyxml2`, `console_bridge`, `libyaml`, `spdlog`, `pybind11` — linked from system Fedora packages, never vendored

### Phase 1 metapackages

- `ros-jazzy-ros-core` — core libraries and runtime, mirrors upstream's `ros_core`.
- `ros-jazzy-ros-base` — `ros_core` plus the ten direct consumers above. Recommended default install during Phase 1.

## Phase 2 — `ros-jazzy-desktop` equivalent (eventual)

Approximately 320 packages — full upstream `ros-jazzy-desktop` composition: `rviz2` (visualization), `rqt_*` (debugger and tooling suite), navigation stacks, alternative RMW implementations, common visualization deps. License aggregate becomes heterogeneous (`Apache-2.0 AND BSD-3-Clause AND LGPL-3.0`, plus `EPL-2.0` if Cyclone DDS is shipped).

Phase 2 entry gate (all must hold):

1. Phase 1 has shipped at least one stable build of every package across all 8 chroot/arch pairs.
2. Phase 1 build matrix has been green for 30+ continuous days.
3. CVE-feed pipeline has demonstrably triggered at least one rebuild for a Fedora-system-dep CVE without manual intervention.
4. Source pin sync from rosdistro is automated.
5. Maintainer bandwidth confirmed for ~1 day/week steady-state.

## Phase 3 — Fedora main-repo inclusion (aspirational, separate effort)

FHS install layout (`/usr/lib64/ros2-jazzy/...`) and submission to Fedora main. Pursued only after upstream ROS 2 itself supports `CMAKE_INSTALL_PREFIX`-driven installs without hardcoded `/opt/ros/$DISTRO`. Not undertaken via local patches in this repo. See ADR 0007.

## Out of scope (across all phases)

- **Anything not on Fedora's [allowed-licenses list](https://docs.fedoraproject.org/en-US/legal/allowed-licenses/).** No exceptions.
- **GPL/AGPL transitively-licensed components.**
- **Vendored copies of libraries that Fedora ships.** System linking only — this is what makes Fedora's CVE pipeline cover transitive deps.
- **Demos, tutorials, example data packages.** Have value but typical Fedora packaging convention is to drop or split these from the runtime metapackage.

## Boundary rules

These hold in every phase:

1. **Each spec accurately declares its license.** No aggregation hiding.
2. **Phase 1 metapackages stay permissive-only.** During Phase 1, no LGPL/EPL/MPL package is `Requires:`-pulled by `ros-jazzy-ros-core` or `ros-jazzy-ros-base`. Phase 2 relaxes this to match upstream metapackage composition honestly.
3. **No bundled forks of system libraries.** Fedora-shipped libs are linked, never vendored.
4. **Any package adding a license type not previously seen in the COPR triggers an ADR.**
5. **Any addition of >5 transitive deps in a single PR triggers an ADR** (full-desktop-creep guard during Phase 1).

## Consumers

- **Primary**: [`o3de-rpm`](https://github.com/nickschuetz/o3de-rpm) via its runtime-deps COPR [`hellaenergy/o3de-dependencies`](https://copr.fedorainfracloud.org/coprs/hellaenergy/o3de-dependencies), which lists `hellaenergy/ros2` as a runtime External Repository.
- **Phase 1 secondary**: any Fedora 44+ or CentOS Stream 10 user wanting a permissive ROS 2 Jazzy core install without enabling the RHEL-targeted upstream RPMs.
- **Phase 2 secondary**: any Fedora 44+ or Stream 10 user wanting a complete ROS 2 desktop install on Fedora-family without using a RHEL container.
