# Scope

What is in scope for this COPR, what is out, and why. Changes to this file require a PR with reviewer sign-off and a corresponding ADR for any boundary shift.

The package set is delivered in **two phases**, with **Phase 3** as an aspirational separate-effort target. See [ADR 0006](adr/0006-full-ros2-desktop-as-eventual-scope.md) and [ADR 0007](adr/0007-install-location-opt-ros-jazzy.md).

## Phase 1 — current shipping scope

The package set required by the [O3DE ROS 2 Gem](https://github.com/o3de/o3de-extras/tree/development/Gems/ROS2) and adjacent embedded-robotics workloads — approximately 70 packages. Pipeline proving ground for Phase 2.

For the realized dependency-ordered build pipeline (ament_cmake stack → utility libs → rosidl chain → Fast DDS chain → message foundation → tier-1/2/3/4 messages → client APIs), see [`docs/build-order.md`](build-order.md).

### Phase 1 direct consumers (the O3DE-targeted leaves)

- `rclcpp` ✓ (live)
- `builtin_interfaces` ✓ (live)
- `std_msgs` ✓ (live)
- `sensor_msgs` ✓ (live)
- `nav_msgs` ✓ (live)
- `geometry_msgs` ✓ (live)
- `tf2_ros` ✓ (live)
- `ackermann_msgs` ✓ (live)
- `vision_msgs` ✓ (live)
- `control_msgs` ✓ (live)

### Phase 1 transitive dependencies (representative; full list in `manifest.yaml`)

- **Build tooling**: full `ament_cmake_*` family, `python_cmake_module`, `ament_index_python`.
- **Utility libs**: `rcutils`, `rcpputils`, `rpyutils`.
- **rosidl chain**: `rosidl_typesupport_interface`, `rosidl_pycommon`, `rosidl_adapter`, `rosidl_runtime_c/cpp`, `rosidl_parser`, `rosidl_cli`, `rosidl_cmake`, `rosidl_generator_c/cpp/py/type_description`, `rosidl_typesupport_introspection_c/cpp`, `rosidl_typesupport_c/cpp`, `rosidl_typesupport_fastrtps_c/cpp`, `rosidl_dynamic_typesupport`, `rosidl_core_generators/runtime`, `rosidl_default_generators/runtime`.
- **Middleware**: `rmw`, `rmw_fastrtps_cpp` (Phase 1 default RMW).
- **Fast DDS chain**: `foonathan_memory_vendor` (vendor wrapper), `fastcdr`, `fastrtps`, `fastrtps_cmake_module`.
- **System libs (linked from Fedora)**: `tinyxml2`, `console_bridge`, `libyaml`, `spdlog`, `pybind11`, `asio`, `openssl`. Never vendored.

### Phase 1 metapackages

- `ros-jazzy-ros-core` — core libraries and runtime, mirrors upstream's `ros_core`.
- `ros-jazzy-ros-base` — `ros_core` plus the ten direct consumers above. Recommended default install during Phase 1.

## Phase 2 — cancelled (ADR 0010)

Originally planned: ~320-package full `ros-jazzy-desktop` equivalent. **Cancelled on 2026-05-08.** Open Robotics is taking on official Fedora support starting with Lyrical Luth, which will deliver this surface as part of the production-grade vendor packages. Continuing to build it here would duplicate that effort. The Phase 2 entry-gate criteria are kept in the historical ADR (0006) as context but are not active.

## Phase 3 — dropped (ADR 0010)

Originally aspirational: Fedora-main-repo inclusion via FHS layout. **Dropped on 2026-05-08.** Production distribution is now Open Robotics's lane. The Fedora Robotics SIG continues a separate FHS-rebasing effort on its own timeline; see [`RELATED-WORK.md`](RELATED-WORK.md).

## Out of scope (across all phases)

- **Anything not on Fedora's [allowed-licenses list](https://docs.fedoraproject.org/en-US/legal/allowed-licenses/).** No exceptions.
- **GPL/AGPL transitively-licensed components.**
- **Vendored copies of libraries that Fedora ships.** System linking only — this is what makes Fedora's CVE pipeline cover transitive deps.
- **Demos, tutorials, example data packages.** Have value but typical Fedora packaging convention is to drop or split these from the runtime metapackage.

## Boundary rules

1. **Each spec accurately declares its license.** No aggregation hiding.
2. **Metapackages stay permissive-only.** No LGPL/EPL/MPL package is `Requires:`-pulled by `ros-jazzy-ros-core` or `ros-jazzy-ros-base`.
3. **No bundled forks of system libraries.** Fedora-shipped libs are linked, never vendored.
4. **Any package adding a license type not previously seen in the COPR triggers an ADR.**
5. **Any addition of >5 transitive deps in a single PR triggers an ADR** (scope-creep guard).
6. **No expansion beyond Phase 1.** ADR 0010 closed Phase 2 / Phase 3. Adding packages outside the minimal subset requires either a new ADR overturning 0010 or a clear bugfix justification (e.g. an existing Phase 1 package needs a missing transitive dep packaged).

## Consumers

- **Primary**: developers compiling and experimenting against ROS 2 Jazzy on Fedora 44+ or CentOS Stream 10 today, ahead of Open Robotics's official Lyrical Fedora packages.
- **Secondary**: [`o3de-rpm`](https://github.com/nickschuetz/o3de-rpm) via its runtime-deps COPR [`hellaenergy/o3de-dependencies`](https://copr.fedorainfracloud.org/coprs/hellaenergy/o3de-dependencies), which lists `hellaenergy/ros2` as a runtime External Repository for development integration testing.

**Not a consumer**: any production deployment, robotics fleet, or regulated environment. Those users belong on Open Robotics's official Fedora packages once they ship.
