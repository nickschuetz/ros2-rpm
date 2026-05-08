# Changelog

All user-visible changes to the COPR packages live here. Per-spec `%changelog` entries are the audit trail for individual builds; this file summarizes the COPR-level "release" picture for humans.

The format roughly follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning here tracks the COPR's Phase boundaries, not any single package's upstream version.

## [Phase 1 minimal subset] — 2026-05-08

The pipeline-proving release. Everything needed to compile and run a basic `rclcpp` ROS 2 application on Fedora 44 / Fedora rawhide / CentOS Stream 10, both `x86_64` and `aarch64`.

### Added — direct consumers (the leaves users ask for)

- `ros-jazzy-rclcpp` — ROS 2 client library for C++.
- `ros-jazzy-tf2`, `ros-jazzy-tf2-msgs`, `ros-jazzy-tf2-ros` — coordinate frame transform stack.
- `ros-jazzy-std-msgs`, `ros-jazzy-geometry-msgs`, `ros-jazzy-sensor-msgs`, `ros-jazzy-nav-msgs`, `ros-jazzy-trajectory-msgs`, `ros-jazzy-action-msgs`, `ros-jazzy-service-msgs` — common message packages.
- `ros-jazzy-ackermann-msgs`, `ros-jazzy-vision-msgs`, `ros-jazzy-control-msgs` — robotics-domain message packages.
- `ros-jazzy-message-filters`, `ros-jazzy-rclcpp-action`, `ros-jazzy-rclcpp-components`, `ros-jazzy-class-loader` — extension points used by clients.

### Added — metapackages

- `ros-jazzy-ros-core` — minimal runtime: rclcpp + RMW (Fast DDS) + core message foundations + components/actions.
- `ros-jazzy-ros-base` — recommended default: ros-core + tf2 + the ten Phase 1 message packages.

### Added — middleware

- `ros-jazzy-rmw`, `ros-jazzy-rmw-implementation`, `ros-jazzy-rmw-implementation-cmake`, `ros-jazzy-rmw-dds-common` — middleware abstraction.
- `ros-jazzy-rmw-fastrtps-cpp`, `ros-jazzy-rmw-fastrtps-dynamic-cpp`, `ros-jazzy-rmw-fastrtps-shared-cpp` — Fast DDS RMW implementation (Phase 1 default).
- `ros-jazzy-fastrtps`, `ros-jazzy-fastcdr`, `ros-jazzy-fastrtps-cmake-module`, `ros-jazzy-foonathan-memory-vendor` — Fast DDS itself.

### Added — rosidl chain

Full rosidl message-generation chain: `rosidl_typesupport_interface`, `rosidl_pycommon`, `rosidl_adapter`, `rosidl_runtime_c/cpp`, `rosidl_parser`, `rosidl_cli`, `rosidl_cmake`, `rosidl_generator_c/cpp/py/type_description`, `rosidl_typesupport_introspection_c/cpp`, `rosidl_typesupport_c/cpp`, `rosidl_typesupport_fastrtps_c/cpp`, `rosidl_dynamic_typesupport`, `rosidl_dynamic_typesupport_fastrtps`, `rosidl_core_generators/runtime`, `rosidl_default_generators/runtime`, `rosidl_typesupport_fastrtps_*`. Plus `builtin_interfaces`, `rcl_interfaces`, `rosgraph_msgs`, `statistics_msgs`, `composition_interfaces`, `unique_identifier_msgs`, `service_msgs`, `type_description_interfaces`.

### Added — utility libraries + ament_cmake stack

- `ros-jazzy-ament-package`, `ros-jazzy-ament-cmake-*` (full ament_cmake_core / ament_cmake / 16+ extension modules) — the build-system family.
- `ros-jazzy-rcutils`, `ros-jazzy-rcpputils`, `ros-jazzy-rpyutils`, `ros-jazzy-tracetools`.
- `ros-jazzy-rcl`, `ros-jazzy-rcl-action`, `ros-jazzy-rcl-yaml-param-parser`, `ros-jazzy-rcl-logging-interface`, `ros-jazzy-rcl-logging-spdlog`.
- `ros-jazzy-libstatistics-collector`, `ros-jazzy-ament-index-cpp`, `ros-jazzy-ament-index-python`.

### Added — vendor packages (system-lib wrappers)

- `ros-jazzy-libyaml-vendor`, `ros-jazzy-spdlog-vendor`, `ros-jazzy-console-bridge-vendor`, `ros-jazzy-ament-cmake-vendor-package`.
  All link dynamically against system libs; no static vendoring.

### Build matrix

All packages build on the full 8 chroot/arch matrix:

| Distro | x86_64 | aarch64 |
|---|---|---|
| Fedora 44 | ✓ | ✓ |
| Fedora rawhide | ✓ | ✓ |
| CentOS Stream 10 (with EPEL 10) | ✓ | ✓ |

### Compatibility notes

- Python 3.14 (Fedora 44 / rawhide) and Python 3.12 (Stream 10) supported via `%{python3_pkgversion}` macros — no per-distro spec forks.
- License: every package in default metapackages carries `Apache-2.0` or `BSD-3-Clause` — no LGPL / EPL / MPL pulls into `ros-jazzy-ros-base`. Phase 2 will introduce a heterogeneous license aggregate honestly disclosed in metapackage License: fields.
- Install layout: `/opt/ros/jazzy/` (per upstream ROS 2 convention; not FHS — see [ADR 0007](docs/adr/0007-install-location-opt-ros-jazzy.md) and [docs/RELATED-WORK.md](docs/RELATED-WORK.md) for why this is intentional vs the Fedora Robotics SIG's main-repo effort).

### Known limitations

- `ros-jazzy-rcl-lifecycle`, `ros-jazzy-rclcpp-lifecycle` deferred. Both depend on `lifecycle_msgs` which is not yet packaged. Tracked for a Phase 1.5 follow-up.
- `rmw_cyclonedds_cpp` and `rmw_connextdds` (the other two RMW implementations in the upstream `rmw_implementation_packages` group) are not packaged; `rmw_implementation`'s Requires is patched to depend only on `rmw_fastrtps_cpp`. Phase 2 will add Cyclone DDS (EPL-2.0).
- COPR signing fingerprint placeholder in README — to be replaced with the real fingerprint after the first signed build.

## [Unreleased] — Phase 2 → `ros-jazzy-desktop` equivalent

See [ADR 0006](docs/adr/0006-full-ros2-desktop-as-eventual-scope.md) for the entry gate. Packages will be added in dependency-ordered batches and each batch noted here on landing.
