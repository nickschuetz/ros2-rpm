# ADR 0014, O3DE Gem dependency metapackage on Lyrical; Lyrical becomes the O3DE target from 26.10

**Status:** Proposed (2026-10-16). Builds on **ADR 0002** (separate ROS 2 COPR from `o3de-dependencies`), **ADR 0003** (permissive-only default metapackages), **ADR 0011** (dev sandbox slice) and **ADR 0012** (Lyrical flagship, Jazzy maintenance). Inherits the development-only posture and disclaimer-everywhere rule from **ADR 0010**.

## Context

The O3DE ROS 2 Gems in `o3de-extras` (ROS2, ROS2Sensors, ROS2Controllers, SimulationInterfaces) link against ROS 2 packages through `target_depends_on_ros2_packages()`. As of `o3de-extras` development 39bc2c28 (2026-08-24) the full set is: `rclcpp`, `rclcpp_action`, `builtin_interfaces`, `std_msgs`, `geometry_msgs`, `sensor_msgs`, `nav_msgs`, `tf2_ros`, `ackermann_msgs`, `vision_msgs`, `control_msgs`, `simulation_interfaces`, plus `gazebo_msgs` behind the optional `WITH_GAZEBO_MSGS` switch. ROS2RobotImporter also needs SDFormat, which O3DE fetches as its own prebuilt package, not from ROS.

Until now this repo pointed O3DE at Jazzy, because the Gems needed `gazebo_msgs` and only Jazzy releases it. Three facts changed that:

1. `o3de-extras` builds against Lyrical since o3de/o3de-extras#1061 (merged 2026-06-17), and that commit is on `stabilization/26100`, the branch that pairs with O3DE 26.10. It is not on `main` (the 26.05 line).
2. `gazebo_msgs` is optional in the Gems, and rosdistro has no Lyrical release of it (`gazebo_ros_pkgs` is absent from `lyrical/distribution.yaml`), so a Lyrical build simply leaves the Gazebo-message components off.
3. The only gap in `hellaenergy/ros2` was `simulation_interfaces`, which rosdistro releases for Lyrical at 2.1.0; the Gems support 2.1.0 since o3de/o3de-extras#1044.

Open Robotics's official Fedora packages currently cover Fedora 43 only, so for Fedora 44+ and CentOS Stream 10 this COPR is the only RPM source for these packages.

## Decision

1. **Add `simulation_interfaces` to Lyrical.** It is an Apache-2.0 interface package (messages, services, actions) depending only on packages already shipped; it is not a simulation bridge, so it is inside the ADR 0011 scope.
2. **Add the `ros-lyrical-o3de-gem-deps` metapackage.** It `Requires:` exactly the Gem link set above (minus `gazebo_msgs`), `ros-core`, the workspace setup packages and the Fast DDS RMW, and `Recommends:` the ros2 CLI verbs (`ros2cli`, `ros2topic`, `ros2node`, `ros2service`, `ros2run`, `ros2launch`, `ros2interface`, `ros2param`, `ros2action`). Its aggregate License stays `Apache-2.0 AND BSD-3-Clause`.
3. **Lyrical is the O3DE target from 26.10 on; Jazzy stays the target for O3DE 26.05.** No Jazzy twin of the metapackage for now; one can be added later without a new ADR if 26.05 users ask for it.
4. **No COPR runtime-dependency wiring.** `o3de-rpm` points at the metapackage with a weak dependency and documents `dnf copr enable hellaenergy/ros2`; enabling an O3DE COPR does not enable the ROS 2 COPR. This keeps ADR 0002's separation while leaving its "External Repository" wiring, which was never configured, unimplemented on purpose: most O3DE users do not use ROS 2.
5. **Rebuild all 26 existing Lyrical interface packages against `rosidl_typesupport_fastrtps` 3.9.7, with `Release:` bumped.** Found while testing this ADR: since 3.9.6 the generated Fast DDS type support calls `cdr_serialize_with_endpoint` on nested types, the 2026-09-29 sync moved the generator from 3.9.5 to 3.9.7 without rebuilding the interface packages, and `simulation_interfaces` (the first interface package built after it) therefore failed to link against `builtin_interfaces` and `geometry_msgs`. A local rebuild of that chain fixed it. The Release bump is needed so installed systems pick up the rebuilt libraries. Smoke test section 8 now checks for the symbol; see `docs/PACKAGING-LESSONS.md`.

## What stays the same

- Development-only; the "Not the official ROS 2 packages for Fedora" disclaimer is in the metapackage `%description` too.
- `ros-lyrical-ros-base` and `ros-lyrical-ros-core` are unchanged.
- The Gems themselves are not packaged here; they come from `o3de-extras` and are built per project.

## Consequences

- One command installs everything an O3DE project with the ROS 2 Gems needs: `sudo dnf copr enable hellaenergy/ros2 && sudo dnf install ros-lyrical-o3de-gem-deps`.
- The metapackage list must be re-checked when the Gems' `target_depends_on_ros2_packages()` calls change; the check is a grep over `Gems/*/Code/CMakeLists.txt` in `o3de-extras`.
- `CLAUDE.md`, `README.md`, `docs/SCOPE.md` and both COPR descriptions are updated in the same change-window to say Lyrical (not Jazzy) is the O3DE target from 26.10.
