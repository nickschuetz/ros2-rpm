# Smoke test

After installing from the [`hellaenergy/ros2`](https://copr.fedorainfracloud.org/coprs/hellaenergy/ros2) COPR, run [`scripts/smoke-test.sh`](../scripts/smoke-test.sh) to verify your install is functional.

It is a **user** smoke test, not a developer regression suite — it doesn't run upstream test suites, doesn't measure performance, and doesn't try to reach a public DDS network. It checks that:

- The packages installed where they were supposed to.
- `source /opt/ros/jazzy/setup.bash` produces a usable shell environment.
- `import rclpy` works (Python bindings).
- A trivial `rclcpp` C++ program can compile against the install and run.
- `ros2` CLI commands work (if `ros-jazzy-ros2cli` is installed).
- A canonical talker actually publishes (if `ros-jazzy-demo-nodes-cpp` is installed).

It runs on Fedora 44+ and CentOS Stream 10 with the [supported chroot/arch matrix](../README.md#supported-targets). It does not require root.

## Quickstart

```bash
# 1. Enable the COPR and install ros-base.
sudo dnf copr enable -y hellaenergy/ros2
sudo dnf install -y ros-jazzy-ros-base

# 2. (Optional) Add the ros2 CLI and demo nodes for fuller coverage.
sudo dnf install -y ros-jazzy-ros2cli ros-jazzy-ros2node ros-jazzy-ros2topic \
                    ros-jazzy-demo-nodes-cpp

# 3. Run the smoke test.
curl -fsSL https://raw.githubusercontent.com/nickschuetz/ros2-rpm/main/scripts/smoke-test.sh \
    | bash
```

Expected output (with all optional packages installed): **20 passed, 0 failed**.

If you cloned the repo locally:

```bash
git clone https://github.com/nickschuetz/ros2-rpm.git
cd ros2-rpm
bash scripts/smoke-test.sh
```

Add `-v` to see the underlying command output for each check:

```bash
bash scripts/smoke-test.sh -v
```

## What each section checks

### 1. Install presence (5 checks)

Verifies the RPM install actually placed files where this COPR claims:

- `ros-jazzy-ros-base` is registered in the RPM database.
- `/opt/ros/jazzy/setup.bash` exists (sourced by the next section).
- `librclcpp.so*` is at `/opt/ros/jazzy/lib/`.
- `libfoonathan_memory*.so` is at `/opt/ros/jazzy/lib/` — **not** `lib64/`. (Fedora's `GNUInstallDirs` defaults to `lib64/` for 64-bit binaries; the COPR explicitly forces `lib/` to keep the runtime loader path consistent with every other ROS lib in the prefix.)
- A `site-packages/rclpy/` directory exists for some installed Python version (Fedora ships 3.14 on F44; Stream 10 ships 3.12).

If any of these fail, the rest of the test is skipped — there's nothing useful to test against.

### 2. Environment activation (3 checks)

Sources `setup.bash` in a subshell and confirms it actually populates the environment:

- `ROS_DISTRO=jazzy`
- `AMENT_PREFIX_PATH` contains `/opt/ros/jazzy`
- `PATH` includes `/opt/ros/jazzy/bin`

If `setup.bash` exists but doesn't set these, `ros_workspace` is broken.

### 3. Python bindings — rclpy (5 checks, optional)

Skipped if `ros-jazzy-rclpy` isn't installed (it's pulled in by `ros-jazzy-ros-base ≥ 0.13.1`).

- `import rclpy` succeeds.
- `import std_msgs.msg` and constructing a `String` succeeds.
- Same for `geometry_msgs.msg.Twist` and `sensor_msgs.msg.Imu`.
- Round-trip lifecycle: `rclpy.init()` → `create_node` → `destroy_node` → `rclpy.shutdown()`.

The last check exercises the actual middleware (Fast DDS) initialization path without needing a peer.

### 4. C++ rclcpp build + run (3 checks, optional)

Skipped if `cmake` or `g++` aren't on PATH.

- Generates a 6-line `rclcpp` program in a temp dir, runs `cmake` against it with `CMAKE_PREFIX_PATH=/opt/ros/jazzy`.
- Builds it.
- Runs the binary; expects clean exit.

This is the most stringent check in the suite — it exercises the CMake config files, the ament_target_dependencies macro, the linker against `librclcpp.so` and its transitive deps, and the runtime middleware load.

### 5. ros2 CLI (3 checks, optional)

Skipped if `ros-jazzy-ros2cli` isn't installed.

- `which ros2` resolves to `/opt/ros/jazzy/bin/ros2`.
- `ros2 --help` runs and exits 0.
- `ros2 topic list` (5-second timeout) returns at least the daemon topic `/rosout`. (Skipped further if `ros-jazzy-ros2topic` isn't installed.)

### 6. Demo nodes — publish path (1 check, optional)

Skipped if `ros-jazzy-demo-nodes-cpp` isn't installed.

- Runs `/opt/ros/jazzy/lib/demo_nodes_cpp/talker` for 3 seconds, greps the output for `Hello World`. Confirms the publisher is actually reaching DDS — i.e. that `rmw_fastrtps_cpp` loaded its dependencies cleanly at runtime.

## What it doesn't cover

This test is intentionally narrow:

- **No upstream ROS 2 test suite.** Each spec runs `%check` during build and we ship `disable_tests: true` for development builds; users running the upstream pytest / gtest suite is out of scope here.
- **No GUI checks** (rqt, rviz2). The smoke test runs in a headless shell. If you installed `ros-jazzy-ros-desktop` and want to validate visualization, run `ros2 run rqt_graph rqt_graph` manually after `source /opt/ros/jazzy/setup.bash`.
- **No multi-host networking checks.** A real DDS deployment spans multiple hosts; that's an integration test, not a smoke test.
- **No security / signing verification.** When the COPR project key is wired in, README will document `gpg --verify` of `repodata`.
- **No performance regressions.** Use `ros2 topic hz` against a known publisher for that.
- **No coverage of Cyclone DDS or the rviz2 chain** — both are Phase 2 work [deferred](../CHANGELOG.md) at the time of writing.

## Failure modes you might see

| Symptom | Probable cause |
|---|---|
| `ros-jazzy-ros-base RPM installed: FAIL` | COPR not enabled, or you ran `dnf install` for a single sub-package without the metapackage. |
| `/opt/ros/jazzy/setup.bash exists: FAIL` | `ros-jazzy-ros-workspace` is missing — bug in this COPR. Open an issue. |
| `libfoonathan_memory*.so present (not lib64): FAIL` | You're running an old `ros-jazzy-foonathan-memory-vendor` (Release: 1). Run `sudo dnf upgrade ros-jazzy-foonathan-memory-vendor` and re-test. |
| `import rclpy: FAIL` with `ModuleNotFoundError` | `ros-jazzy-rclpy` not installed. `sudo dnf install ros-jazzy-rclpy`. |
| `rclcpp run: FAIL` with `failed to load any RMW implementations` | Missing `ros-jazzy-rmw-fastrtps-cpp` or it can't dlopen its deps. Re-check the foonathan check above. |
| `ros2 topic list: FAIL` with timeout | Likely a multicast / firewall block, not a packaging issue. Set `ROS_LOCALHOST_ONLY=1` and re-test. |
| All `ros2` checks: SKIP | You only installed `ros-jazzy-ros-base`. To get `ros2`, also install `ros-jazzy-ros2cli`. |

For anything unexpected, re-run with `-v` and attach the output to an [issue](https://github.com/nickschuetz/ros2-rpm/issues/new).

## CI

The smoke test is run automatically on every PR via `.github/workflows/smoke-test.yml` against the published COPR contents on a Fedora 44 container. PRs that break the smoke test against `ros-jazzy-ros-base` are blocked from merging.
