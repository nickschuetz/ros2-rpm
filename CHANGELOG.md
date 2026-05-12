# Changelog

All user-visible changes to the COPR packages live here. Per-spec `%changelog` entries are the audit trail for individual builds; this file summarizes the COPR-level "release" picture for humans.

The format roughly follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Maintenance tooling and CI hardening], 2026-05-11

No user-visible package changes. Project-side improvements that close the loop on drift detection, spec quality enforcement, SBOM validation, and PR pre-flight.

### Added

- **`scripts/verify-specs.py`** plus `verify-specs` CI job in [`lint.yml`](.github/workflows/lint.yml). Audits every spec for forbidden patterns, SPDX-valid License: fields, em-dashes, and `Patch%N:` references with valid DEP-3 metadata. Centralized `EXEMPTIONS` register covers the 11 specs that legitimately need `debug_package %{nil}` (vendor packages with empty debugsource; rclpy pybind11; python-qt-binding). Currently 0 errors and 65 `-devel` warnings across 163 specs. The `-devel` warnings can be promoted to fatal via `--devel-strict` once each spec is retrofitted.
- **`scripts/validate-sbom.py`** plus `sbom-validate` CI job. Asserts CycloneDX shape on every emitted SBOM. CI self-tests the validator with both a known-good and known-bad fixture so regressions surface even when no fresh RPMs are available.
- **`scripts/bump.py`** for fast-path version bumps. Reads `rosdistro/jazzy/distribution.yaml`, edits `Version:` + `Source0:` + prepends `%changelog`, runs `verify-specs.py` as a guard. Modes: single-package, explicit version, `--all-behind` to drain the weekly drift report. `--commit` produces a conventional commit.
- **`.github/workflows/spec-dry-build.yml`** (new). PR-only, triggers when `specs/**` changes. For up to 3 changed specs: `rpmspec -P`, `spectool -g`, `rpmbuild -bs`, and `dnf builddep --assumeno` against Fedora 44 + hellaenergy/ros2. Catches Source0 / BR breakage before the COPR build cycle.
- **`.github/workflows/drift-check.yml`** (new). Weekly Sunday 08:00 UTC. Opens / updates one sticky issue (`upstream-drift` label) when packages are behind rosdistro; closes it with a "fully caught up" comment when drift returns to zero. Self-bootstraps the labels.
- **`specs/patches/` scaffold** with [`README.md`](specs/patches/README.md) documenting the file naming convention (`<package>/NNNN-short-name.patch`) and required DEP-3 headers (Description, Origin, Forwarded, Last-Update). Verifier rejects `Patch%N:` lines that point at non-existent files or files missing DEP-3 metadata. No patches carried today; infrastructure is in place if the rviz2 deferral becomes blocking.
- **[`docs/MAINTENANCE.md`](docs/MAINTENANCE.md)** (new). Contributor reference for every script and CI workflow, with routine workflows (bump, add-package, carry-patch, investigate-failed-CI) documented end-to-end.

### Fixed

- **`actions/checkout@v4` → `@v6`** across every workflow. Eliminates the GitHub-flagged Node 20 deprecation; runner will force Node 24 in June 2026.
- **`upstream-issues.yml` label-bootstrap latent bug**: workflow would have failed the first time a tracked item closed because `upstream-tracker` / `maintenance` labels didn't exist. Self-bootstrap step added; same pattern as `drift-check.yml`.
- **`upstream-drift.yml` removed** as a duplicate of the new `drift-check.yml`. The pre-existing daily-cron variant ran under a different sticky-issue label (`drift` vs `upstream-drift`); deleting it avoids dual-tracking.
- **SPDX normalization**: `LGPL-3.0` → `LGPL-3.0-only` in `ros-jazzy-ros-desktop.spec`'s `License:` aggregate and in every doc that shows the SPDX expression (README, SCOPE, ARCHITECTURE, ADR 0006, ADR 0011, CHANGELOG). Conceptual references to "LGPL-3.0 obligations" or the license family stay as-is.
- **Em-dash sweep**: 147 spec files plus a handful of docs / scripts / ADRs / workflow files had U+2014 characters from generator-emitted strings or hand-written prose. Fixed at the source in `generate-spec.py` (three offending strings: "no LICENSE", "tests skipped", "Message package") and mechanically replaced space-bounded U+2014 with ", " across the rest. The lone surviving instance is the `EM_DASH` pattern literal inside `verify-specs.py`, which has to stay as the actual character so the verifier can search for it.

## [O3DE Gem coverage closed: gazebo_msgs added], 2026-05-08

Added `ros-jazzy-gazebo-msgs` (BSD-3-Clause, message-only). Closes the only optional dep that the [O3DE ROS 2 Gem](https://github.com/o3de/o3de-extras/tree/development/Gems/ROS2) had a `find_package(... QUIET)` for. With this in place, the Gem's optional `ContactSensor` and `ROS2 Spawner` components can be enabled at build time alongside the rest of the Gem.

Caveat, upstream EOL trajectory: the package is slated for removal in ROS 2 Kilted Kaiju per upstream comments in the Gem's CMakeLists. This COPR's scope sunsets at Jazzy EOL anyway (per ADR 0010), so we ship it for the Jazzy lifetime. Post-Jazzy users targeting Kilted+ will need an alternative path for those Gem components.

License is permissive; no new ADR required (BSD-3-Clause is already in the COPR's aggregate via `ros-jazzy-ros-base`). The package is a standalone opt-in; not Required: by `ros-jazzy-ros-base` or `ros-jazzy-ros-desktop`.

## [Phase 2, dev-sandbox expansion live], 2026-05-08

[ADR 0011](docs/adr/0011-phase-2-dev-sandbox-expansion.md) reopened a smaller Phase 2 (the developer-tooling slice of `ros-jazzy-desktop`) the same day as the development-only pivot. Most of the planned scope shipped that day. Production positioning unchanged: still development-only, disclaimer banner unchanged.

### Added

- **launch infrastructure**: `osrf_pycommon`, `launch`, `launch_xml`, `launch_yaml`, `launch_testing`, `launch_ros`.
- **lifecycle backfill** (originally deferred from Phase 1): `lifecycle_msgs`, `rcl_lifecycle`, `rclcpp_lifecycle`, `rclpy`, `pybind11_vendor`.
- **`ros2cli` + per-domain plugins**: `ros2cli`, `ros2pkg`, `ros2run`, `ros2node`, `ros2topic`, `ros2service`, `ros2interface`, `ros2action`, `ros2lifecycle`, `ros2param`, `ros2component`.
- **rqt + plugins** (Fedora-only, Stream 10 lacks Qt5 build deps): `qt_gui`, `qt_gui_cpp`, `qt_gui_py_common`, `qt_dotgraph`, `python_qt_binding`, `pluginlib`, `tinyxml2_vendor`, `tango_icons_vendor`, `rqt`, `rqt_gui`, `rqt_gui_cpp`, `rqt_gui_py`, `rqt_graph`, `rqt_topic`, `rqt_console`, `rqt_publisher`, `rqt_action`, `rqt_plot`, `rqt_service_caller`. Adds **LGPL-3.0-only** to the COPR's license aggregate (Qt5).
- **demo nodes**: `example_interfaces`, `demo_nodes_cpp`, `demo_nodes_py`.
- **Cyclone DDS chain** (`cyclonedds`, `rmw_cyclonedds_cpp`): live across all 6 chroot/arch pairs. Built against system libs with `-DENABLE_SHM=OFF` (skips the iceoryx shared-memory transport which Fedora doesn't package); standard sockets transport is sufficient for development. Adds **EPL-2.0** to the COPR's license aggregate. Verified end-to-end: `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp /opt/ros/jazzy/lib/demo_nodes_cpp/talker` publishes successfully.

### Metapackage

- **New `ros-jazzy-ros-desktop`**, published. License: `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0-only` honestly disclosed. Pulls in `ros-base` plus launch + ros2cli + rqt + demo_nodes. **rviz2 NOT included**, see "Deferred" below.
- `ros-jazzy-ros-core` and `ros-jazzy-ros-base` continue to be **permissive-only**. Installing those still yields only Apache-2.0 / BSD-3-Clause content.

### Build matrix caveat for Phase 2 GUI packages

Phase 2 GUI surface (qt_gui_core, python_qt_binding, rqt + plugins) builds successfully on the **4 Fedora chroots** (`fedora-44` + `fedora-rawhide` × `x86_64` + `aarch64`) but **fails on CentOS Stream 10** because Stream 10 doesn't ship `python3-sip-devel` and other Qt5 build dependencies. Stream 10 users get `ros-jazzy-ros-base` and the headless launch / ros2cli / demo packages; for visualization on Stream 10, use a Fedora chroot.

### Deferred (will revisit when blockers clear or upstream patches land)

- **rviz2 chain**: `rviz_ogre_vendor`, `rviz_assimp_vendor`, `rviz_rendering`, `rviz_common`, `rviz_default_plugins`, `rviz2`. Two upstream blockers, both now tracked in [`docs/UPSTREAM-ISSUES.md`](docs/UPSTREAM-ISSUES.md):
  - `rviz_ogre_vendor`: Ogre's bundled CMake config has `cmake_minimum_required` below 3.5, which CMake 4.x (Fedora 44+) rejects. Fix is in flight upstream as [ros2/rviz#1708](https://github.com/ros2/rviz/pull/1708) (awaiting merge); we [confirmed the workaround on Fedora 44](https://github.com/ros2/rviz/pull/1708#issuecomment-4408710231).
  - `rviz_assimp_vendor`: Assimp's CMake adds `-Werror` to the build flags via its own `target_compile_options`, ordered after our `-Wno-error` override. Filed as [ros2/rviz#1730](https://github.com/ros2/rviz/issues/1730) with a proposed `ASSIMP_CXX_FLAGS` extension; awaiting maintainer direction before sending the PR.
- `rcl_action_lifecycle`, `rclcpp_lifecycle_interface`, navigation stacks, simulation bridges: all out of scope per ADR 0011.

### Out of scope (per ADR 0011)

`nav2_*`, `ros2control`, simulation bridges, deployment tooling. Production-shaped surfaces; users belong on Open Robotics's official Lyrical packages.

## [Project pivot, development-only], 2026-05-08

After Phase 1 minimal subset shipped, the project was repositioned as **development-only**. Open Robotics is taking on official Fedora support starting with Lyrical Luth (the 2026 LTS); this COPR is no longer attempting to be the long-term Fedora ROS 2 distribution.

### Changed

- README, COPR description + instructions, GitHub repo description, CITATION.cff abstract, and `docs/RELATED-WORK.md` all updated to carry the **"Not the official ROS 2 packages for Fedora"** disclaimer and to point users at Open Robotics's upcoming Lyrical packages for production.
- `docs/SCOPE.md`, Phase 2 (full `ros-jazzy-desktop` equivalent) marked **cancelled**; Phase 3 (Fedora main repo) marked **dropped**. Phase 1 minimal subset was framed as the final scope at the moment of this entry; later the same day, ADR 0011 reopened a *smaller* dev-sandbox Phase 2 (see the next entry above).
- `CLAUDE.md`, production-grade compliance language stripped; "STIG-adjacent" pitch removed; CVE-feed automation downgraded from required to optional. Added a **mandatory sync rule** that COPR description + instructions must be updated in the same change-window as any README / SCOPE / RELATED-WORK update.
- Added [ADR 0010](docs/adr/0010-project-pivot-to-development-only.md) capturing the full pivot rationale. ADR 0001 and ADR 0006 carry retroactive notes.

### Why

- Open Robotics will deliver the production-grade equivalent for Lyrical, with vendor support and CVE tracking. Continuing to expand this COPR would duplicate that effort.
- Without the disclaimer, users were at risk of deploying a development-grade COPR to production.

### Unchanged

- Phase 1 packages keep shipping, they are appropriate for development workflows.
- Build hardening, license cleanliness, SBOM emission per build all retained because they are good engineering hygiene.
- All 6 chroot/arch pairs (Fedora 44 / rawhide / CentOS Stream 10 × x86_64 + aarch64) continue to build on every change.

## [Phase 1 minimal subset], 2026-05-08

The pipeline-proving release. Everything needed to compile and run a basic `rclcpp` ROS 2 application on Fedora 44 / Fedora rawhide / CentOS Stream 10, both `x86_64` and `aarch64`.

### Added, direct consumers (the leaves users ask for)

- `ros-jazzy-rclcpp`, ROS 2 client library for C++.
- `ros-jazzy-tf2`, `ros-jazzy-tf2-msgs`, `ros-jazzy-tf2-ros`, coordinate frame transform stack.
- `ros-jazzy-std-msgs`, `ros-jazzy-geometry-msgs`, `ros-jazzy-sensor-msgs`, `ros-jazzy-nav-msgs`, `ros-jazzy-trajectory-msgs`, `ros-jazzy-action-msgs`, `ros-jazzy-service-msgs`, common message packages.
- `ros-jazzy-ackermann-msgs`, `ros-jazzy-vision-msgs`, `ros-jazzy-control-msgs`, robotics-domain message packages.
- `ros-jazzy-message-filters`, `ros-jazzy-rclcpp-action`, `ros-jazzy-rclcpp-components`, `ros-jazzy-class-loader`, extension points used by clients.

### Added, metapackages

- `ros-jazzy-ros-core`, minimal runtime: rclcpp + RMW (Fast DDS) + core message foundations + components/actions.
- `ros-jazzy-ros-base`, recommended default: ros-core + tf2 + the ten Phase 1 message packages.

### Added, middleware

- `ros-jazzy-rmw`, `ros-jazzy-rmw-implementation`, `ros-jazzy-rmw-implementation-cmake`, `ros-jazzy-rmw-dds-common`, middleware abstraction.
- `ros-jazzy-rmw-fastrtps-cpp`, `ros-jazzy-rmw-fastrtps-dynamic-cpp`, `ros-jazzy-rmw-fastrtps-shared-cpp`, Fast DDS RMW implementation (Phase 1 default).
- `ros-jazzy-fastrtps`, `ros-jazzy-fastcdr`, `ros-jazzy-fastrtps-cmake-module`, `ros-jazzy-foonathan-memory-vendor`, Fast DDS itself.

### Added, rosidl chain

Full rosidl message-generation chain: `rosidl_typesupport_interface`, `rosidl_pycommon`, `rosidl_adapter`, `rosidl_runtime_c/cpp`, `rosidl_parser`, `rosidl_cli`, `rosidl_cmake`, `rosidl_generator_c/cpp/py/type_description`, `rosidl_typesupport_introspection_c/cpp`, `rosidl_typesupport_c/cpp`, `rosidl_typesupport_fastrtps_c/cpp`, `rosidl_dynamic_typesupport`, `rosidl_dynamic_typesupport_fastrtps`, `rosidl_core_generators/runtime`, `rosidl_default_generators/runtime`, `rosidl_typesupport_fastrtps_*`. Plus `builtin_interfaces`, `rcl_interfaces`, `rosgraph_msgs`, `statistics_msgs`, `composition_interfaces`, `unique_identifier_msgs`, `service_msgs`, `type_description_interfaces`.

### Added, utility libraries + ament_cmake stack

- `ros-jazzy-ament-package`, `ros-jazzy-ament-cmake-*` (full ament_cmake_core / ament_cmake / 16+ extension modules), the build-system family.
- `ros-jazzy-rcutils`, `ros-jazzy-rcpputils`, `ros-jazzy-rpyutils`, `ros-jazzy-tracetools`.
- `ros-jazzy-rcl`, `ros-jazzy-rcl-action`, `ros-jazzy-rcl-yaml-param-parser`, `ros-jazzy-rcl-logging-interface`, `ros-jazzy-rcl-logging-spdlog`.
- `ros-jazzy-libstatistics-collector`, `ros-jazzy-ament-index-cpp`, `ros-jazzy-ament-index-python`.

### Added, vendor packages (system-lib wrappers)

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

- Python 3.14 (Fedora 44 / rawhide) and Python 3.12 (Stream 10) supported via `%{python3_pkgversion}` macros, no per-distro spec forks.
- License: every package in default metapackages carries `Apache-2.0` or `BSD-3-Clause`, no LGPL / EPL / MPL pulls into `ros-jazzy-ros-base`. Phase 2 will introduce a heterogeneous license aggregate honestly disclosed in metapackage License: fields.
- Install layout: `/opt/ros/jazzy/` (per upstream ROS 2 convention; not FHS, see [ADR 0007](docs/adr/0007-install-location-opt-ros-jazzy.md) and [docs/RELATED-WORK.md](docs/RELATED-WORK.md) for why this is intentional vs the Fedora Robotics SIG's main-repo effort).

### Known limitations

- `ros-jazzy-rcl-lifecycle`, `ros-jazzy-rclcpp-lifecycle` deferred. Both depend on `lifecycle_msgs` which is not yet packaged. May be filled in if a development user needs them; otherwise Open Robotics's Lyrical packages will cover this surface.
- `rmw_cyclonedds_cpp` and `rmw_connextdds` (the other two RMW implementations in the upstream `rmw_implementation_packages` group) are not packaged; `rmw_implementation`'s Requires is patched to depend only on `rmw_fastrtps_cpp`. Will not be added, those belong on Open Robotics's official packages.
- COPR signing fingerprint placeholder in README, to be replaced with the real fingerprint after the first signed build.
