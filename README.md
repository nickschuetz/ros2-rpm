# ros2-rpm

> **Not the official ROS 2 packages for Fedora.**
>
> This is a **development-only** package set. Open Robotics is taking on official Fedora support starting with **Lyrical Luth** (the 2026 LTS). For production deployments, robotics fleets, or any work that needs vendor-supported, CVE-tracked, official ROS 2 builds, use Open Robotics's official Fedora packages once those land.
>
> These COPRs exist for developers who want to compile and experiment against ROS 2 on **Fedora 44+** or **CentOS Stream 10** today, while the official packages are still in progress.

This repo builds two COPRs, both development-only:

| COPR | ROS 2 distro | Role | Package prefix | Install prefix |
|---|---|---|---|---|
| [`hellaenergy/ros2`](https://copr.fedorainfracloud.org/coprs/hellaenergy/ros2) | **Lyrical Luth** (2026 LTS) | Flagship | `ros-lyrical-*` | `/opt/ros/lyrical` |
| [`hellaenergy/ros2-jazzy`](https://copr.fedorainfracloud.org/coprs/hellaenergy/ros2-jazzy) | **Jazzy Jalisco** | Maintenance | `ros-jazzy-*` | `/opt/ros/jazzy` |

Pick Lyrical for new work; it tracks the current LTS. Jazzy stays available for existing Jazzy workspaces.

## Quickstart (Lyrical, flagship)

```bash
sudo dnf copr enable hellaenergy/ros2
sudo dnf install ros-lyrical-ros-base
source /opt/ros/lyrical/setup.bash
```

Verify the install (~20s, no root, no GUI):

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/nickschuetz/ros2-rpm/main/scripts/smoke-test.sh) lyrical
```

Lyrical ships the **minimal headless set** (`rclcpp`, `rclpy`, the common message packages such as `std_msgs`, `sensor_msgs`, `geometry_msgs`, `nav_msgs`, `tf2_msgs`, `control_msgs`, Fast DDS as the RMW, `tf2_ros`, and the `ros-lyrical-ros-core` / `ros-lyrical-ros-base` metapackages) plus the full **developer sandbox**: `rqt`, `ros2cli`, `launch`, demo nodes, the alternate Cyclone DDS RMW, and **`rviz2`**, all rolled up in the `ros-lyrical-ros-desktop` metapackage. The sandbox and `rviz2` build on Fedora 44 and CentOS Stream 10 (both arches); fedora-rawhide carries the headless set only (see [Supported targets](#supported-targets)).

```bash
sudo dnf install ros-lyrical-ros-desktop   # rqt + ros2cli + launch + rviz2 + Cyclone DDS + demos
```

## Quickstart (Jazzy, maintenance)

```bash
sudo dnf copr enable hellaenergy/ros2-jazzy
sudo dnf install ros-jazzy-ros-base
source /opt/ros/jazzy/setup.bash
```

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/nickschuetz/ros2-rpm/main/scripts/smoke-test.sh) jazzy
```

Jazzy includes the minimal subset plus a developer sandbox (`rqt`, `ros2cli`, `launch`, demo nodes, alternate Cyclone DDS RMW, `gazebo_msgs` for the O3DE Gem) via the `ros-jazzy-ros-desktop` metapackage.

## Common installs

Substitute `<distro>` with `lyrical` (from `hellaenergy/ros2`) or `jazzy` (from `hellaenergy/ros2-jazzy`).

| You want… | Install |
|---|---|
| Minimal headless dev (rclcpp + Fast DDS + tf2 + common messages) | `ros-<distro>-ros-base` |
| One specific package | `ros-<distro>-<pkg>` (e.g. `ros-lyrical-rclcpp`) |
| Dev tooling (rqt, ros2cli, launch, demo_nodes, Cyclone DDS, **rviz2 on Lyrical**) | `ros-<distro>-ros-desktop` |
| 3D visualization (`rviz2`) **(Lyrical, Fedora 44 + Stream 10)** | `ros-lyrical-rviz2` |
| O3DE Gem optional ContactSensor + Spawner support **(Jazzy)** | `ros-jazzy-gazebo-msgs` |
| Cyclone DDS as your RMW | `ros-<distro>-rmw-cyclonedds-cpp`, then `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` |

Setup environment is sourced per-session via `source /opt/ros/<distro>/setup.bash`. To enable shell-wide loading, opt in by sourcing `/etc/profile.d/ros-<distro>.sh` from your login shell. Packages install to `/opt/ros/<distro>/`; see [ADR 0007](docs/adr/0007-install-location-opt-ros-jazzy.md) for why.

## Supported targets

Both COPRs build the same matrix:

| Distro | x86_64 | aarch64 |
|---|---|---|
| Fedora 44 | ✓ | ✓ |
| Fedora rawhide | ✓ | ✓ |
| CentOS Stream 10 (with EPEL 10) | ✓ | ✓ |

The CentOS Stream 10 chroots are convenient build targets, **not** a production-deployment pitch.

Per-distro GUI / sandbox availability differs:

- **Lyrical**: the `rqt` family and `rviz2` use Qt6 and build on Fedora 44 **and** CentOS Stream 10 (both arches). They are **not** built on fedora-rawhide: the Ogre and Gazebo vendor packages download sources with `vcstool`, which is broken on rawhide's Python 3.14 (setuptools dropped `pkg_resources`). On rawhide, install `ros-lyrical-ros-base` (headless).
- **Jazzy**: the `rqt` family is built on the Fedora chroots only; Stream 10 lacks the Qt5 build deps (`python3-sip-devel`). Install `ros-jazzy-ros-desktop` from a Fedora chroot for the GUI tooling. Jazzy does not ship `rviz2` (see Known limitations).

## Known limitations

- **`rviz2` (3D visualizer):** packaged on **Lyrical** (Fedora 44 + CentOS Stream 10, both arches) via `ros-lyrical-rviz2` / `ros-lyrical-ros-desktop`; not built on fedora-rawhide (the Ogre/Gazebo vendor downloads use `vcstool`, broken on rawhide's Python 3.14). **Not packaged on Jazzy**: its Ogre and Assimp vendor builds hit [ros2/rviz#1708](https://github.com/ros2/rviz/pull/1708) (Ogre / CMake 4.x) and [ros2/rviz#1730](https://github.com/ros2/rviz/issues/1730) (Assimp / Fedora's stricter GCC); on Jazzy, `rqt` covers non-3D debugging (graph, topic echo, console, plot), or run a RHEL 9 container with [packages.ros.org's RPMs](https://docs.ros.org/en/jazzy/Installation/RHEL-Install-RPMs.html). Full impact analysis: [`docs/SCOPE.md`](docs/SCOPE.md).
- **`nav2_*`, `ros2control`, simulation bridges** are out of scope. Production-shaped surfaces; users belong on Open Robotics's Lyrical packages once they ship.
- **Long-term posture is undecided.** Upstream EOLs Jazzy in May 2029. Whether the Jazzy COPR sunsets, freezes as a historical archive, or is retired once the official Lyrical packages ship is a future-ADR decision; see [`docs/UPGRADING.md`](docs/UPGRADING.md#approaching-upstream-eol).

## License

Each package carries its own SPDX `License:` field. The default metapackages (`ros-<distro>-ros-core`, `ros-<distro>-ros-base`) ship only **Apache-2.0** and **BSD-3-Clause** content. The optional `ros-<distro>-ros-desktop` metapackages opt in to a heterogeneous aggregate, honestly disclosed in their `License:` field: `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0-only AND EPL-2.0` (LGPL-3.0 via Qt6 for the `rqt` suite and, on Lyrical, `rviz2`; EPL-2.0 via the Cyclone DDS RMW). All non-permissive packages link dynamically against system libraries. Full policy: [`docs/SCOPE.md`](docs/SCOPE.md). The repo itself is Apache-2.0 ([`LICENSE`](LICENSE)).

## Documentation

**For users**

- [`docs/SMOKE-TEST.md`](docs/SMOKE-TEST.md): what each install-validation check does, common failure modes.
- [`docs/UPGRADING.md`](docs/UPGRADING.md): distro transitions, Fedora N→N+1 rebuild notes, EOL plan.
- [`docs/SCOPE.md`](docs/SCOPE.md): exactly which packages are in / out / deferred, and why.

**For project context**

- [`CHANGELOG.md`](CHANGELOG.md): COPR-level release history.
- [`docs/SECURITY.md`](docs/SECURITY.md): vulnerability handling, watchlist, hardening posture, what these COPRs claim (and don't) about security.
- [`docs/RELATED-WORK.md`](docs/RELATED-WORK.md): the broader Fedora-ROS packaging ecosystem (Open Robotics's official Lyrical work, the Fedora Robotics SIG, packages.ros.org).
- [`docs/UPSTREAM-ISSUES.md`](docs/UPSTREAM-ISSUES.md): live tracking of upstream issues / PRs that block deferred work.
- [`docs/adr/`](docs/adr/): architecture decision records. [ADR 0010](docs/adr/0010-development-only-pivot.md) (development-only pivot) and [ADR 0012](docs/adr/0012-add-lyrical-flagship-jazzy-maintenance.md) (Lyrical flagship + Jazzy maintenance) are the load-bearing ones. Read these before opening scope-changing PRs.

**For contributors**

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): the pipeline, spec patterns, install layout, dependency model, CI/publishing flow.
- [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md): the maintenance scripts and CI workflows; bumping versions, carrying patches, reading drift reports.
- [`docs/build-order.md`](docs/build-order.md): dependency-ordered build pipeline, build patterns the generator handles, known edge cases.
- [`docs/PACKAGING-LESSONS.md`](docs/PACKAGING-LESSONS.md): RPM spec gotchas, generator gotchas, cross-distro gotchas, hidden runtime deps.

## Related work

- **[Open Robotics official Fedora packages](https://docs.ros.org/)** (production path): starting with Lyrical Luth (the 2026 LTS).
- **[Fedora Robotics SIG](https://gitlab.com/fedora/sigs/robotics)**: pursuing FHS-compliant ROS in Fedora's main repos via `fedros` / `rosfed` on a longer timeline.
- **[`packages.ros.org`](https://docs.ros.org/en/jazzy/Installation/RHEL-Install-RPMs.html)**: Open Robotics's existing RHEL 9 Jazzy RPMs, today's production path on RHEL.

These COPRs sit between those: a development-only sandbox for ROS 2 on Fedora until the official Lyrical packages arrive. See [`docs/RELATED-WORK.md`](docs/RELATED-WORK.md) for the full landscape.
