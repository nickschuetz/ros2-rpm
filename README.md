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

Lyrical currently ships the **minimal headless set**: `rclcpp`, `rclpy`, the common message packages (`std_msgs`, `sensor_msgs`, `geometry_msgs`, `nav_msgs`, `tf2_msgs`, `control_msgs`, and more), Fast DDS as the RMW, `tf2_ros`, and the `ros-lyrical-ros-core` / `ros-lyrical-ros-base` metapackages. The developer sandbox (`rqt`, `ros2cli`, `launch`, demo nodes, Cyclone DDS) is available today on the Jazzy maintenance COPR and is being ported to Lyrical.

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
| Dev tooling (rqt, ros2cli, launch, demo_nodes, Cyclone DDS) **(Jazzy today)** | `ros-jazzy-ros-desktop` |
| O3DE Gem optional ContactSensor + Spawner support **(Jazzy)** | `ros-jazzy-gazebo-msgs` |
| Cyclone DDS as your RMW **(Jazzy today)** | `ros-jazzy-rmw-cyclonedds-cpp`, then `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` |

Setup environment is sourced per-session via `source /opt/ros/<distro>/setup.bash`. To enable shell-wide loading, opt in by sourcing `/etc/profile.d/ros-<distro>.sh` from your login shell. Packages install to `/opt/ros/<distro>/`; see [ADR 0007](docs/adr/0007-install-location-opt-ros-jazzy.md) for why.

## Supported targets

Both COPRs build the same matrix:

| Distro | x86_64 | aarch64 |
|---|---|---|
| Fedora 44 | ✓ | ✓ |
| Fedora rawhide | ✓ | ✓ |
| CentOS Stream 10 (with EPEL 10) | ✓ | ✓ |

The CentOS Stream 10 chroots are convenient build targets, **not** a production-deployment pitch. Stream 10 also lacks Qt5 build deps, so the Jazzy `rqt` family is Fedora-chroot-only; install `ros-jazzy-ros-desktop` from a Fedora chroot if you want the GUI tooling.

## Known limitations

- **`rviz2` (3D visualizer) is not packaged** on either COPR. Tracked upstream blockers include [ros2/rviz#1708](https://github.com/ros2/rviz/pull/1708) (Ogre / CMake 4.x) and [ros2/rviz#1730](https://github.com/ros2/rviz/issues/1730) (Assimp / Fedora's stricter GCC). On Jazzy, `rqt` works for non-3D debugging (graph, topic echo, console, plot). For 3D today, run a RHEL 9 container with [packages.ros.org's RPMs](https://docs.ros.org/en/jazzy/Installation/RHEL-Install-RPMs.html) or wait for Open Robotics's Lyrical packages. Full impact analysis: [`docs/SCOPE.md`](docs/SCOPE.md).
- **`nav2_*`, `ros2control`, simulation bridges** are out of scope. Production-shaped surfaces; users belong on Open Robotics's Lyrical packages once they ship.
- **Long-term posture is undecided.** Upstream EOLs Jazzy in May 2029. Whether the Jazzy COPR sunsets, freezes as a historical archive, or is retired once the official Lyrical packages ship is a future-ADR decision; see [`docs/UPGRADING.md`](docs/UPGRADING.md#approaching-upstream-eol).

## License

Each package carries its own SPDX `License:` field. The default metapackages (`ros-<distro>-ros-core`, `ros-<distro>-ros-base`) ship only **Apache-2.0** and **BSD-3-Clause** content. The optional `ros-jazzy-ros-desktop` metapackage opts in to a heterogeneous aggregate (`Apache-2.0 AND BSD-3-Clause AND LGPL-3.0-only AND EPL-2.0`) honestly disclosed in its `License:` field. All non-permissive packages link dynamically against system libraries. Full policy: [`docs/SCOPE.md`](docs/SCOPE.md). The repo itself is Apache-2.0 ([`LICENSE`](LICENSE)).

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
