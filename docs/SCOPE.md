# Scope

What is in scope for this COPR, what is out, and why. Changes to this file require a PR with reviewer sign-off and a corresponding ADR for any boundary shift.

The package set is delivered in **two phases**, with **Phase 3** as an aspirational separate-effort target. See [ADR 0006](adr/0006-full-ros2-desktop-as-eventual-scope.md) and [ADR 0007](adr/0007-install-location-opt-ros-jazzy.md).

## Phase 1, current shipping scope

The package set required by the [O3DE ROS 2 Gem](https://github.com/o3de/o3de-extras/tree/development/Gems/ROS2) and adjacent embedded-robotics workloads, approximately 70 packages. Pipeline proving ground for Phase 2.

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

- `ros-jazzy-ros-core`, core libraries and runtime, mirrors upstream's `ros_core`.
- `ros-jazzy-ros-base`, `ros_core` plus the ten direct consumers above. Recommended default install during Phase 1.

## Phase 2, dev-sandbox expansion (ADR 0011)

After ADR 0010 cancelled the originally-planned ~320-package full `ros-jazzy-desktop` (production trajectory), [ADR 0011](adr/0011-phase-2-dev-sandbox-expansion.md) **reopened Phase 2 as a smaller dev-sandbox expansion** so developers can visualize, debug, and test their code locally on Fedora. The dev-only positioning is unchanged; the disclaimer banner stays on every public surface; Open Robotics remains the production path for Lyrical.

### Phase 2, what's live (Fedora chroots only, see Stream 10 caveat below)

- **rqt suite**: `rqt`, `rqt_gui`, `rqt_gui_cpp`, `rqt_gui_py`, `rqt_graph`, `rqt_topic`, `rqt_console`, `rqt_publisher`, `rqt_service_caller`, `rqt_action`, `rqt_plot`. Underlying Qt foundation: `qt_gui`, `qt_gui_cpp`, `qt_gui_py_common`, `qt_dotgraph`, `python_qt_binding`, `pluginlib`, `tinyxml2_vendor`, `tango_icons_vendor`.
- **Alternate RMW**: `rmw_cyclonedds_cpp` and `cyclonedds`. Adds `EPL-2.0` to the COPR's license aggregate.
- **`ros2cli` suite**: `ros2cli`, `ros2pkg`, `ros2run`, `ros2node`, `ros2topic`, `ros2service`, `ros2interface`, `ros2action`, `ros2lifecycle`, `ros2param`, `ros2component`. Plus `rosidl_runtime_py`, `ament_copyright` (transitive runtime deps).
- **Launch infrastructure**: `launch`, `launch_ros`, `launch_xml`, `launch_yaml`, `launch_testing`, `osrf_pycommon`.
- **Lifecycle backfill** (originally deferred from Phase 1): `lifecycle_msgs`, `rcl_lifecycle`, `rclcpp_lifecycle`, `rclpy`, `pybind11_vendor`.
- **Demo nodes**: `demo_nodes_cpp`, `demo_nodes_py`, `example_interfaces` for environment verification.
- **O3DE Gem optional dep**: `gazebo_msgs` (BSD-3-Clause, opt-in). Enables the [O3DE ROS 2 Gem](https://github.com/o3de/o3de-extras/tree/development/Gems/ROS2)'s optional `ContactSensor` and `ROS2 Spawner` components. Not pulled in by `ros-jazzy-ros-base` or `ros-jazzy-ros-desktop`; users install explicitly when they want those Gem features. Upstream is slated for removal in Kilted Kaiju, so post-Jazzy users will need an alternative path for these specific components.

### Phase 2 metapackage

- **`ros-jazzy-ros-desktop`**, License: `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0` (Qt5 via the rqt suite). Pulls in `ros-jazzy-ros-base` plus the Phase 2 surface. Users explicitly opt in to the heterogeneous license aggregate by installing this metapackage. **Does not include rviz2**, see deferral note below.

### Phase 2 build matrix caveat

The Qt5-dependent packages (qt_gui_core, python_qt_binding, rqt + plugins) build successfully on the **4 Fedora chroots** (`fedora-44` + `fedora-rawhide` × `x86_64` + `aarch64`) but fail on **CentOS Stream 10** because Stream 10 doesn't ship `python3-sip-devel` and other Qt5 build deps. Stream 10 users get `ros-jazzy-ros-base` + the headless launch / ros2cli / demo packages; for visualization on Stream 10, run `rqt` from a Fedora chroot.

<a name="rviz2-deferral-side-effects"></a>
### rviz2 deferral, side effects

`rviz2` (and its chain: `rviz_ogre_vendor`, `rviz_assimp_vendor`, `rviz_rendering`, `rviz_common`, `rviz_default_plugins`) is **not packaged**. Two upstream blockers identified during Phase 2 P-4:

| Package | Blocker |
|---|---|
| `rviz_ogre_vendor` | Ogre 14.x's vendored CMake config has `cmake_minimum_required` below CMake 4.x's hard floor. Fedora 44 ships CMake 4.x. Workaround `-DCMAKE_POLICY_VERSION_MINIMUM=3.5` was tried but Ogre's build hit further issues; needs upstream attention or a real CMake-policy patch. |
| `rviz_assimp_vendor` | Assimp's bundled CMakeLists adds `-Werror` via its own `target_compile_options`, ordered after our spec's `-Wno-error` override and Fedora's stricter GCC warnings (`-Wunused-but-set-variable` on `MS3DLoader.cpp`). Fixing this requires either an upstream patch or replacing the vendored ExternalProject with system `assimp-devel`. |

System library substitution doesn't help: Fedora's `ogre-devel` is **1.9.x**, not the **14.x** rviz needs. Fedora's `assimp-devel` is **6.x**, newer than rviz's vendored 5.x with API differences.

**What you lose without rviz2:**

- **No 3D visualization.** Point clouds, robot models (URDF), TF frame trees, occupancy grids, navigation costmaps, marker arrays, none of these can be visualized. rviz2 is the canonical 3D visualizer in ROS 2.
- **No camera image rendering.** `sensor_msgs/Image` topics can't be displayed live; you can echo metadata via `ros2 topic echo /image_raw` but not see the pixels.
- **Most tutorials become read-only at the visualization step.** Many ROS 2 tutorials end with "now look at the result in rviz2." You can run the launch files; you just can't see the output.
- **SLAM, localization, and navigation development is significantly harder.** These workflows are visual-feedback driven; debugging without a 3D viewer of the map / pose / plan is painful.
- **Robot model debugging is harder.** Verifying URDF/Xacro frames or joint states without `rviz2 -d robot.rviz` means relying on `tf2_echo`/`tf2_monitor` text output.

**What still works without rviz2:**

- **rqt for non-3D debugging.** `rqt_graph` shows the node/topic graph; `rqt_topic` echoes any topic into a Qt list; `rqt_console` aggregates `/rosout` log messages with severity filtering; `rqt_plot` plots scalar message fields over time. None of these need rviz2 or Ogre.
- **All headless workflows.** Writing nodes, testing message passing, integration tests via `launch_testing`, performance measurement via `ros2 topic hz`, none touch rviz2.
- **CLI inspection.** `ros2 topic list / echo / hz / info`, `ros2 node list / info`, `ros2 service list / call`, `ros2 param list / get / set`, `ros2 interface show`, full coverage.

**Workarounds if you need 3D visualization today:**

- Run a RHEL 9 container with [packages.ros.org's ROS 2 Jazzy RPMs](https://docs.ros.org/en/jazzy/Installation/RHEL-Install-RPMs.html), those ship rviz2 against RHEL 9's older Ogre.
- Forward your DDS topics to a separate workstation with rviz2 already installed (set `ROS_DOMAIN_ID` consistently and ensure firewall allows DDS multicast).
- Wait for Open Robotics's official Lyrical packages, which the project pivoted to deferring this surface to (per [ADR 0010](adr/0010-project-pivot-to-development-only.md)).

**When this deferral closes:**

When upstream `rviz_ogre_vendor` and `rviz_assimp_vendor` accept patches for the CMake 4.x and `-Werror` issues (or when this repo gains the bandwidth to carry those patches locally), the rviz2 chain rebuilds against the existing P-3 foundation in days. Tracked but not committed; the dev-only positioning means waiting is acceptable.

The two upstream tickets we're watching are listed in [`docs/UPSTREAM-ISSUES.md`](UPSTREAM-ISSUES.md): the Ogre fix is in flight as [ros2/rviz#1708](https://github.com/ros2/rviz/pull/1708), and the Assimp blocker was filed as [ros2/rviz#1730](https://github.com/ros2/rviz/issues/1730).

### Phase 2 explicitly out of scope (per ADR 0011)

- Full `nav2_*` navigation stack, production-shaped.
- `ros2control` family, production hardware-control surface.
- Simulation bridges (`ros_gz_*`, etc.), large dep surface, separate Gazebo Fedora packaging effort.
- Any package whose only purpose is a production deployment workflow.

Adding any of those requires a new ADR overriding 0011.

## Phase 3, dropped (ADR 0010)

Originally aspirational: Fedora-main-repo inclusion via FHS layout. **Dropped on 2026-05-08.** Production distribution is now Open Robotics's lane. The Fedora Robotics SIG continues a separate FHS-rebasing effort on its own timeline; see [`RELATED-WORK.md`](RELATED-WORK.md).

## Out of scope (across all phases)

- **Anything not on Fedora's [allowed-licenses list](https://docs.fedoraproject.org/en-US/legal/allowed-licenses/).** No exceptions.
- **GPL/AGPL transitively-licensed components.**
- **Vendored copies of libraries that Fedora ships.** System linking only, this is what makes Fedora's CVE pipeline cover transitive deps.
- **Demos, tutorials, example data packages.** Have value but typical Fedora packaging convention is to drop or split these from the runtime metapackage.

## Boundary rules

1. **Each spec accurately declares its license.** No aggregation hiding.
2. **Default metapackages stay permissive-only.** No LGPL/EPL/MPL package is `Requires:`-pulled by `ros-jazzy-ros-core` or `ros-jazzy-ros-base`. `ros-jazzy-ros-desktop` declares its heterogeneous aggregate honestly.
3. **No bundled forks of system libraries.** Fedora-shipped libs are linked, never vendored.
4. **All non-permissive (LGPL/EPL/MPL) content links dynamically.** Static linking is forbidden.
5. **Any package adding a license type not previously seen in the COPR triggers an ADR.** (LGPL-3.0 and EPL-2.0 are anchored by ADR 0011 for Phase 2; new types still need ADRs.)
6. **Any addition of >5 transitive deps in a single PR triggers an ADR** (scope-creep guard).
7. **No expansion beyond Phase 1 + Phase 2 dev-sandbox.** Phase 2 is bounded by ADR 0011. Adding navigation stacks, simulation bridges, or production deployment tooling requires a new ADR overriding 0011.

## Consumers

- **Primary**: developers compiling and experimenting against ROS 2 Jazzy on Fedora 44+ or CentOS Stream 10 today, ahead of Open Robotics's official Lyrical Fedora packages.
- **Secondary**: [`o3de-rpm`](https://github.com/nickschuetz/o3de-rpm) via its runtime-deps COPR [`hellaenergy/o3de-dependencies`](https://copr.fedorainfracloud.org/coprs/hellaenergy/o3de-dependencies), which lists `hellaenergy/ros2` as a runtime External Repository for development integration testing.

**Not a consumer**: any production deployment, robotics fleet, or regulated environment. Those users belong on Open Robotics's official Fedora packages once they ship.
