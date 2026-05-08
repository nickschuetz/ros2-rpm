# Changelog

All user-visible changes to the COPR packages live here. Per-spec `%changelog` entries are the audit trail for individual builds; this file summarizes the COPR-level "release" picture for humans.

The format roughly follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Phase 2 reopened — dev-sandbox expansion] — 2026-05-08

Same day as the development-only pivot, [ADR 0011](docs/adr/0011-phase-2-dev-sandbox-expansion.md) reopened a smaller Phase 2 — the developer-tooling slice of `ros-jazzy-desktop` so visualization and debugging UX is reasonable on Fedora during the wait for Open Robotics's official Lyrical packages. Production positioning unchanged: still development-only, disclaimer banner unchanged.

### Planned Phase 2 additions

- `rviz2` + plugin chain (visualization). Adds **LGPL-3.0** to the COPR aggregate (Qt).
- `rqt` + key plugins (`rqt_graph`, `rqt_topic`, `rqt_console`, `rqt_publisher`, `rqt_service_caller`, `rqt_action`, `rqt_plot`).
- `ros2cli` suite (`ros2pkg`, `ros2node`, `ros2topic`, `ros2service`, `ros2interface`, `ros2action`, `ros2lifecycle`, `ros2param`, `ros2component`, `ros2run`).
- `rmw_cyclonedds_cpp` + `cyclonedds` as alternate RMW. Adds **EPL-2.0** to the COPR aggregate.
- `launch` family + `launch_testing`.
- `demo_nodes_cpp`, `demo_nodes_py` for environment verification.

### Metapackage

- **New**: `ros-jazzy-ros-desktop` with heterogeneous License: `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0` (and `AND EPL-2.0` if Cyclone DDS is shipped).
- `ros-jazzy-ros-core` and `ros-jazzy-ros-base` stay **permissive-only**. Users who run `dnf install ros-jazzy-ros-base` continue to get only Apache-2.0 / BSD-3-Clause content.

### Out of scope (per ADR 0011)

`nav2_*`, `ros2control`, simulation bridges, deployment tooling. Production-shaped surfaces; users belong on Open Robotics's official Lyrical packages.

## [Project pivot — development-only] — 2026-05-08

After Phase 1 minimal subset shipped, the project was repositioned as **development-only**. Open Robotics is taking on official Fedora support starting with Lyrical Luth (the 2026 LTS); this COPR is no longer attempting to be the long-term Fedora ROS 2 distribution.

### Changed

- README, COPR description + instructions, GitHub repo description, CITATION.cff abstract, and `docs/RELATED-WORK.md` all updated to carry the **"Not the official ROS 2 packages for Fedora"** disclaimer and to point users at Open Robotics's upcoming Lyrical packages for production.
- `docs/SCOPE.md` — Phase 2 (full `ros-jazzy-desktop` equivalent) marked **cancelled**; Phase 3 (Fedora main repo) marked **dropped**. Phase 1 minimal subset is the final scope.
- `CLAUDE.md` — production-grade compliance language stripped; "STIG-adjacent" pitch removed; CVE-feed automation downgraded from required to optional. Added a **mandatory sync rule** that COPR description + instructions must be updated in the same change-window as any README / SCOPE / RELATED-WORK update.
- Added [ADR 0010](docs/adr/0010-project-pivot-to-development-only.md) capturing the full pivot rationale. ADR 0001 and ADR 0006 carry retroactive notes.

### Why

- Open Robotics will deliver the production-grade equivalent for Lyrical, with vendor support and CVE tracking. Continuing to expand this COPR would duplicate that effort.
- Without the disclaimer, users were at risk of deploying a development-grade COPR to production.

### Unchanged

- Phase 1 packages keep shipping — they are appropriate for development workflows.
- Build hardening, license cleanliness, SBOM emission per build all retained because they are good engineering hygiene.
- All 6 chroot/arch pairs (Fedora 44 / rawhide / CentOS Stream 10 × x86_64 + aarch64) continue to build on every change.

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

All packages build on the full 6 chroot/arch matrix:

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

- `ros-jazzy-rcl-lifecycle`, `ros-jazzy-rclcpp-lifecycle` deferred. Both depend on `lifecycle_msgs` which is not yet packaged. May be filled in if a development user needs them; otherwise Open Robotics's Lyrical packages will cover this surface.
- `rmw_cyclonedds_cpp` and `rmw_connextdds` (the other two RMW implementations in the upstream `rmw_implementation_packages` group) are not packaged; `rmw_implementation`'s Requires is patched to depend only on `rmw_fastrtps_cpp`. Will not be added — those belong on Open Robotics's official packages.
- COPR signing fingerprint placeholder in README — to be replaced with the real fingerprint after the first signed build.
