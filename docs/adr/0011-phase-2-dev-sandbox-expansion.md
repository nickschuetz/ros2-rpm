# ADR 0011 — Phase 2: dev-sandbox expansion of `ros-jazzy-desktop` content

**Status:** Accepted (2026-05-08)

## Context

ADR 0010 (the development-only pivot, accepted earlier the same day) cancelled the originally-planned Phase 2 expansion to a full `ros-jazzy-desktop` equivalent on the reasoning that Open Robotics's upcoming official Lyrical packages will deliver that production-grade surface. That reasoning is still correct for the **production** trajectory.

But the development-only sandbox itself is genuinely improved by some of what `ros-jazzy-desktop` adds. A developer working on a ROS 2 Jazzy node on Fedora today wants to:

- Visualize topics, frames, and pointclouds (`rviz2`).
- Inspect the node graph and topic activity (`rqt`, `rqt_graph`, `rqt_topic`, `rqt_console`).
- Run demo nodes to verify their RMW + transport + message stack is working end-to-end.
- Test against alternate RMW implementations (Cyclone DDS) before deploying to whatever RMW the production environment uses.

Without those, the development sandbox is "good enough to build against" but not "good enough to actually develop on." Forcing developers to either (a) wait for Open Robotics's Lyrical packages or (b) hop to a RHEL container to get `rviz2` is poor UX for the population this repo exists to serve.

## Decision

**Phase 2 is reopened — as a dev-sandbox expansion, not a production trajectory.** ADR 0010's development-only positioning stays in force. This ADR amends rather than reverses ADR 0010.

Concretely:

1. **Disclaimer is unchanged.** Every public surface (README, COPR description + instructions, GitHub repo description, CITATION.cff, per-package `%description`) continues to carry the **"Not the official ROS 2 packages for Fedora"** banner and the pointer to Open Robotics's upcoming Lyrical packages.
2. **Production claims still forbidden.** No CVE SLA, no STIG-adjacent posture, no vendor-support framing. Phase 2 packages are subject to the same engineering-hygiene-not-SLA rule as Phase 1.
3. **Open Robotics is still the production path.** Phase 2 dev-sandbox does not compete with their official Lyrical packages — when those ship, users move to them. This COPR sunsets when Jazzy EOLs.

### Phase 2 dev-sandbox scope

The Phase 2 set is **smaller than the originally-cancelled ~320-package full desktop**. It is the developer-tooling slice — what a developer needs to inspect, visualize, and debug their own code on Fedora today.

- **Visualization**: `rviz2` and its plugin dependencies, `rviz_common`, `rviz_default_plugins`, `rviz_rendering`, `rviz_visual_testing_framework` (skip the test framework for runtime — only needed for `%check`).
- **rqt suite (debug GUIs)**: `rqt`, `rqt_gui`, `rqt_gui_cpp`, `rqt_gui_py`, `rqt_graph`, `rqt_topic`, `rqt_console`, `rqt_publisher`, `rqt_service_caller`, `rqt_action`, `rqt_plot`. Skip the lifecycle/diagnostic plugins for now (they need additional infrastructure that isn't in Phase 1).
- **Alternate RMW**: `rmw_cyclonedds_cpp` and `cyclonedds`. Adds `EPL-2.0` to the COPR's license aggregate. Documented honestly per ADR 0003.
- **Demo nodes (development verification)**: `demo_nodes_cpp`, `demo_nodes_py`, `example_interfaces`. These run the canonical "talker/listener" pair developers use to confirm their environment is healthy.
- **Launch + utilities**: `launch`, `launch_ros`, `launch_xml`, `launch_yaml`, `launch_testing` if they aren't already in Phase 1. (Many of these will be — verify against `manifest.yaml` before adding to `packages.yaml`.)
- **`ros2cli` and core CLI tools**: `ros2cli`, `ros2pkg`, `ros2run`, `ros2node`, `ros2topic`, `ros2service`, `ros2interface`, `ros2action`, `ros2lifecycle`, `ros2param`, `ros2component`. The `ros2 ...` command-line surface developers actually use.

### Explicitly NOT in Phase 2 dev-sandbox

- Full `ros-jazzy-desktop`'s navigation stack (`nav2_*`). Production-shaped feature; developers building against it should target the production environment's official packages.
- `ros2control` family. Production hardware-control surface.
- `gazebo` / `ros_gz_*` simulation bridges. Large dep surface; covered separately by the upstream Gazebo Fedora packages.
- Any package whose only purpose is the production deployment workflow (release tooling, deployment helpers).

If a developer needs one of those, they can request it as a one-off PR with justification — but the default answer is "use Open Robotics's Lyrical packages when those ship" or "spin up a RHEL container."

### Metapackage policy under Phase 2

To preserve the license-clean default install path:

- `ros-jazzy-ros-core` and `ros-jazzy-ros-base` stay permissive-only. Their `Requires:` lines never name a non-permissive package. `EPL-2.0` (Cyclone DDS) does not enter these.
- A new metapackage `ros-jazzy-ros-desktop` is added when Phase 2 lands. Its License: field declares the heterogeneous aggregate honestly: `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0` (Qt via rviz2) and `EPL-2.0` if Cyclone DDS is included.
- All non-permissive Phase 2 packages link dynamically against system libraries (LGPL-3.0 / EPL-2.0 obligation). Static linking forbidden.

### Package-set ordering

Phase 2 builds on Phase 1's already-shipping ament_cmake / rosidl / rcl / rclcpp / messaging foundation. The new dependency tiers will be added to `docs/build-order.md` as they materialize. Approximate top-level order:

1. **Cyclone DDS** chain (alternate RMW): `cyclonedds`, `rmw_cyclonedds_cpp`, plus the `cyclonedds-cmake-module` if upstream ships one.
2. **Launch** chain: `launch`, `launch_ros`, `launch_xml`, `launch_yaml`, `launch_testing`.
3. **ros2cli** chain: `ros2cli` and the per-domain CLI plugins (`ros2pkg`, `ros2node`, etc.).
4. **rqt** core: `qt_gui`, `qt_gui_cpp`, `qt_gui_py_common`, `qt_dotgraph`, then `rqt_gui`, `rqt_gui_cpp`, `rqt_gui_py`.
5. **rqt** plugins.
6. **rviz** core: `rviz_ogre_vendor`, `rviz_assimp_vendor`, `rviz_common`, `rviz_rendering`, `rviz_default_plugins`, `rviz2`.
7. **demo_nodes**: `example_interfaces`, then `demo_nodes_cpp` and `demo_nodes_py`.

Each tier ships across all 6 chroot/arch pairs before moving to the next.

## Why this is amend, not revert

ADR 0010's decision was driven by the production trajectory ("OR will deliver this for Lyrical"). That decision is correct and remains. ADR 0011 narrows the cancellation to "production-trajectory Phase 2 cancelled" and reopens "dev-sandbox-trajectory Phase 2." Public-facing copy continues to direct production users to Open Robotics. Internal scope expands to make the development experience reasonable.

## Consequences

- README, COPR description + instructions, GitHub repo description, CHANGELOG, SCOPE.md, RELATED-WORK.md updated in the same change-window as this ADR — per the sync rule in CLAUDE.md.
- ADR 0006 (full desktop as eventual scope) stays cancelled; ADR 0011's scope is intentionally smaller than that.
- ADR 0010 carries a retroactive note pointing to ADR 0011 as the dev-sandbox amendment.
- No reversal of any technical infrastructure: same generator, same publish flow, same chroot matrix, same license invariants.
