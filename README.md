# ros2-rpm

> **Not the official ROS 2 packages for Fedora.**
>
> This is a **development-only** package set. Open Robotics is taking on official Fedora support starting with **Lyrical Luth** (the 2026 LTS). For production deployments, robotics fleets, or any work that needs vendor-supported, CVE-tracked, official ROS 2 builds, use Open Robotics's official Fedora packages when those land.
>
> This COPR exists for developers who want to compile and experiment against ROS 2 Jazzy on Fedora 44+ today, before the official Lyrical packages ship. See [ADR 0010](docs/adr/0010-project-pivot-to-development-only.md) and [`docs/RELATED-WORK.md`](docs/RELATED-WORK.md).

Development-only ROS 2 Jazzy minimal subset (~85 packages — `rclcpp`, `tf2_ros`, common message packages, `rmw_fastrtps_cpp` + Fast DDS, transitive deps), built for **Fedora 44+** and **CentOS Stream 10** on **x86_64** and **aarch64**, distributed via the Fedora COPR [`hellaenergy/ros2`](https://copr.fedorainfracloud.org/coprs/hellaenergy/ros2).

## Scope

Two phases, both development-only. The disclaimer at the top of this README applies to both.

### Phase 1 — minimal subset (live)

~85 packages: `rclcpp`, `tf2_ros`, common message packages (`std_msgs`, `sensor_msgs`, `geometry_msgs`, `nav_msgs`, `tf2_msgs`, `trajectory_msgs`, `ackermann_msgs`, `vision_msgs`, `control_msgs`), `rmw_fastrtps_cpp` + Fast DDS, plus the metapackages `ros-jazzy-ros-core` and `ros-jazzy-ros-base`. Built on `fedora-44`, `fedora-rawhide`, `centos-stream-10` × `x86_64` + `aarch64`. License-clean: only `Apache-2.0` and `BSD-3-Clause`.

### Phase 2 — dev-sandbox expansion (in progress)

Per [ADR 0011](docs/adr/0011-phase-2-dev-sandbox-expansion.md), Phase 2 expands the development sandbox so developers can visualize, debug, and test their code locally on Fedora — without forcing a hop to a RHEL container. Phase 2 is **smaller than the originally-planned ~320-package full desktop** (the originally-cancelled Phase 2 in [ADR 0010](docs/adr/0010-project-pivot-to-development-only.md)) — only the developer-tooling slice. Adds the `ros-jazzy-ros-desktop` metapackage with a heterogeneous license aggregate honestly disclosed.

Included:
- `rviz2` + plugin chain (visualization).
- `rqt` + key plugins (`rqt_graph`, `rqt_topic`, `rqt_console`, `rqt_publisher`, `rqt_service_caller`, `rqt_action`, `rqt_plot`).
- `ros2cli` and per-domain CLI tools (`ros2pkg`, `ros2node`, `ros2topic`, `ros2service`, `ros2interface`, `ros2action`, `ros2lifecycle`, `ros2param`, `ros2component`, `ros2run`).
- `rmw_cyclonedds_cpp` + `cyclonedds` as alternate RMW (adds `EPL-2.0`).
- `launch` family (`launch`, `launch_ros`, `launch_xml`, `launch_yaml`).
- `demo_nodes_cpp` and `demo_nodes_py` for end-to-end environment verification.

Explicitly **not** in Phase 2 dev-sandbox: full `nav2_*` navigation, `ros2control`, simulation bridges, deployment tooling. Those are production-shaped surfaces and belong on Open Robotics's official Lyrical packages.

Full scope and per-package status in [`docs/SCOPE.md`](docs/SCOPE.md). Dependency-ordered build pipeline in [`docs/build-order.md`](docs/build-order.md).

### Sunset

When upstream Open Robotics EOLs Jazzy (May 2029), this COPR sunsets. By then, users should already be on Open Robotics's official Lyrical (or later) Fedora packages.

## Quickstart

```bash
sudo dnf copr enable hellaenergy/ros2
sudo dnf install ros-jazzy-ros-base
source /opt/ros/jazzy/setup.bash
```

For a single package:

```bash
sudo dnf install ros-jazzy-rclcpp
```

## Supported targets

| Distro | Architectures |
|---|---|
| Fedora 44 | x86_64, aarch64 |
| Fedora rawhide | x86_64, aarch64 |
| CentOS Stream 10 | x86_64, aarch64 |

Stream 10 chroots additionally pull EPEL 10 for ROS build deps not in Stream 10's base / AppStream / CRB. The Stream 10 chroots are convenient build targets — **not** a production-deployment pitch.

## Install location

Packages install to `/opt/ros/jazzy/` per upstream ROS 2 convention. Setup environment via `source /opt/ros/jazzy/setup.bash` (or enable `/etc/profile.d/ros-jazzy.sh` for opt-in shell-wide loading). See [ADR 0007](docs/adr/0007-install-location-opt-ros-jazzy.md).

## License posture

Default metapackages `ros-jazzy-ros-core` and `ros-jazzy-ros-base` contain only **Apache-2.0** and **BSD-3-Clause** content. Installing either never pulls in non-permissive code — that path stays clean by design.

`ros-jazzy-ros-desktop` (the Phase 2 dev-sandbox metapackage) declares its actual aggregate honestly: `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0` (Qt via `rviz2`/rqt) and `AND EPL-2.0` if Cyclone DDS is included. Installing it is an explicit opt-in to the heterogeneous license aggregate.

All non-permissive packages link dynamically against system libraries (LGPL-3.0 / EPL-2.0 obligations). Full scope and per-license-type policy: [`docs/SCOPE.md`](docs/SCOPE.md).

## Subpackages

Every library package produces:

- `ros-jazzy-<pkg>` — runtime libs (`.so.*`), executables, runtime data
- `ros-jazzy-<pkg>-devel` — headers, CMake config, pkg-config (mandatory for libraries with headers)
- `ros-jazzy-<pkg>-debuginfo` and `ros-jazzy-<pkg>-debugsource` — auto-generated debug info

Pure-Python packages use `python3-<pkg>` instead of the runtime/devel split. Message-only packages still produce `-devel` subpackages for the generated headers and CMake config.

## Engineering hygiene

These are practices applied because they are good engineering, not because this COPR is making production-grade SLA claims (it isn't — see the disclaimer at the top):

- Built with Fedora's hardening flags (`_FORTIFY_SOURCE=3`, full RELRO, PIE, stack-clash protection, CFI) inherited from `redhat-rpm-config`.
- System libraries linked rather than vendored.
- CycloneDX SBOM published per build at `%{_datadir}/doc/<package>/sbom.cdx.json`.
- COPR repo metadata and packages are signed by the COPR project key. Fingerprint: _to be filled in after first build_.

For production deployments, do not rely on this COPR — use Open Robotics's official Fedora Lyrical packages once they ship.

Vulnerability disclosure: [`docs/SECURITY.md`](docs/SECURITY.md).

## Related work

The [Open Robotics official Fedora packages](https://docs.ros.org/) (starting with Lyrical, the 2026 LTS) are the production-grade path for ROS 2 on Fedora. The [Fedora Robotics SIG](https://gitlab.com/fedora/sigs/robotics) (whose `fedros` / `rosfed` projects use a similar bloom-spec approach) is working separately on Fedora-main-repo inclusion on a longer timeline. This COPR is narrower than either: a development-only sandbox for Jazzy on Fedora until the official Lyrical packages arrive. See [`docs/RELATED-WORK.md`](docs/RELATED-WORK.md) for the full landscape.

## Validating your install

After installing, run [`scripts/smoke-test.sh`](scripts/smoke-test.sh) to verify your install is functional. It checks: package presence, `setup.bash` activation, Python `import rclpy`, a tiny `rclcpp` C++ build + run, `ros2 topic list`, and demo_nodes_cpp talker. No root, no GUI, ~20 seconds.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/nickschuetz/ros2-rpm/main/scripts/smoke-test.sh)
```

Full documentation: [`docs/SMOKE-TEST.md`](docs/SMOKE-TEST.md).

## Documentation

- [`CHANGELOG.md`](CHANGELOG.md) — COPR-level release history (per-spec `%changelog` is the per-package audit trail).
- [`docs/SMOKE-TEST.md`](docs/SMOKE-TEST.md) — install validation, what each check does, common failure modes.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — pipeline overview, the four spec patterns, install layout, dependency model, CI/publishing flow.
- [`docs/SCOPE.md`](docs/SCOPE.md) — phased scope policy, in/out lists, package boundaries.
- [`docs/build-order.md`](docs/build-order.md) — dependency-ordered build pipeline, build patterns the generator handles, and known edge cases.
- [`docs/UPGRADING.md`](docs/UPGRADING.md) — upgrade procedures across ROS 2 distros and Fedora releases.
- [`docs/SECURITY.md`](docs/SECURITY.md) — vulnerability handling, watchlist, disclosure.
- [`docs/RELATED-WORK.md`](docs/RELATED-WORK.md) — the broader Fedora-ROS packaging ecosystem.
- [`docs/adr/`](docs/adr/) — architecture decision records (read these before opening scope-changing PRs).

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
