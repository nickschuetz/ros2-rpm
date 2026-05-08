# Packaging lessons learned

A durable record of the gotchas, blockers, and fixes encountered while packaging ROS 2 Jazzy for Fedora. Saved here so future-you (or future contributors) don't have to rediscover them by inspecting build logs in COPR.

Organized by category. When a new gotcha shows up that bit hard enough to lose an hour to, add it here with the failure mode and the fix.

## RPM spec gotchas

### `foonathan_memory_vendor` installs to `lib64/`, not `lib/`

**Symptom**: `librmw_fastrtps_cpp.so` fails to dlopen `libfoonathan_memory-0.7.3.so` at runtime.

**Why**: Fedora's `GNUInstallDirs` puts 64-bit shared libraries in `${CMAKE_INSTALL_PREFIX}/lib64` by default. Every other ROS package in `/opt/ros/jazzy/` lands in `lib/`, so the runtime loader path doesn't include `lib64/`.

**Why the obvious fix fails**: `foonathan_memory_vendor`'s outer `CMakeLists.txt` builds the upstream `foonathan/memory` library via `ExternalProject`. Passing `-DCMAKE_INSTALL_LIBDIR=lib` to the outer `cmake` doesn't propagate through `ExternalProject_Add`'s `CMAKE_ARGS` list (only specific keys like `BUILD_SHARED_LIBS`, `CMAKE_BUILD_TYPE` get explicitly forwarded; `CMAKE_INSTALL_LIBDIR` does not).

**Fix**: Patch `CMakeLists.txt` during `%prep` to inject `-DCMAKE_INSTALL_LIBDIR=lib` into the inner ExternalProject's `CMAKE_ARGS`:

```spec
%prep
%autosetup -p1 -n foonathan_memory_vendor-release-...
sed -i 's|^    -DCMAKE_INSTALL_PREFIX=|    -DCMAKE_INSTALL_LIBDIR=lib\n    -DCMAKE_INSTALL_PREFIX=|' CMakeLists.txt
```

Then update `%files` to reference `lib/` not `lib64/`.

### Vendor packages produce empty `debugsourcefiles.list`

**Symptom**: Build fails at end with `error: Empty %files file ... debugsourcefiles.list`.

**Why**: Vendor packages that wrap an `ExternalProject` (foonathan_memory_vendor, console_bridge_vendor, libyaml_vendor, spdlog_vendor, tinyxml2_vendor, tango_icons_vendor, ament_cmake_vendor_package, pybind11_vendor, python_qt_binding) build the upstream library outside RPM's reach. RPM's `find-debuginfo` can't locate source files for the staged libs.

**Fix**: `%global debug_package %{nil}` near the top of the spec.

### `rclpy` ships a small pybind11 C extension and trips the same debuginfo issue

**Symptom**: Same empty debugsourcefiles.list as vendor packages.

**Why**: rclpy is a Python package with a single C extension built via pybind11. The `.so` lands inside `site-packages/rclpy/`, not at `/opt/ros/jazzy/lib/`. RPM's debuginfo logic can't extract debug source for it cleanly.

**Fix**: Same as vendors, plus drop the bogus `lib/lib%{pkg_name}.so*` glob from `%files`:

```spec
%global debug_package %{nil}
# ...
# rclpy ships pybind11 extension inside site-packages, not lib/lib*.so
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}-py%{python3_version}.egg-info/
```

### Library naming doesn't always match package name

The generator's default `%files` glob is `%{install_prefix}/lib/lib%{pkg_name}.so*`. Several packages don't follow that convention:

| Package | Actual library name(s) |
|---|---|
| `rclcpp_components` | `libcomponent_manager.so*` (also ships executables under `lib/rclcpp_components/`) |
| `rmw_dds_common` | `librmw_dds_common.so*` (the message-package generator path missed this) |
| `tracetools` | `libtracetools.so*` plus `libtracetools_status.so*` plus `lib/tracetools/` helper binary |
| `tf2_ros` | `libtf2_ros.so*` plus `libstatic_transform_broadcaster_node.so*` plus `lib/tf2_ros/` for CLI binaries (buffer_server, static_transform_publisher, tf2_echo, tf2_monitor) |
| `demo_nodes_cpp` | per-tutorial `lib<demo>_library.so` (talker_library, listener_library, etc.) plus `lib/demo_nodes_cpp/` executables; **no** `libdemo_nodes_cpp.so` |
| `cyclonedds` | upstream Eclipse layout: `libddsc.so`, `libcycloneddsidl.so`, `libdds_security_*.so`, plus `bin/idlc`, `bin/ddsperf`. Use a local mock `--rebuild` of the spec to capture the exact `-- Installing:` log. |

**Fix**: hand-tune `%files` per package. The generator's default is a starting point, not a finish line.

### Pure-metapackage Python pkg with `packages=[]`

**Symptom**: `error: Directory not found: BUILDROOT/opt/ros/jazzy/lib/python3.14/site-packages/rqt`

**Why**: `rqt`'s `setup.py` has `packages=[]` (truly a metapackage). No site-packages dir is created.

**Fix**: drop the site-packages directory entry from `%files`, keep only the `dist-info`, ament_index sentinel, and `share/<pkg>/` entries.

### `setup.py` `data_files` patterns install outside site-packages

**Symptom**: `rqt_gui` installs `lib/rqt_gui/rqt_gui` (launcher script). `launch_testing` installs `lib/launch_testing/<example_proc.py>` test fixtures via:

```python
data_files=[
    ('lib/launch_testing', glob.glob('example_processes/**')),
],
```

**Fix**: add `%{install_prefix}/lib/%{pkg_name}/` to `%files`.

### Bloom-release tarballs sometimes strip `LICENSE`

**Symptom**: Build fails on `error: Could not open %files file: LICENSE: No such file or directory` if the spec uses `%license LICENSE`.

**Why**: `bloom-release` makes per-package source tarballs that don't always include the umbrella repo's LICENSE file. Some packages (gazebo_msgs, ament_cmake_test, etc.) end up without one.

**Fix**: the generator detects this and emits a comment instead of `%license`. If you ever hand-edit a spec, mirror that pattern:

```spec
# (no LICENSE file in source tree; see package.xml <license>)
%doc CHANGELOG.rst
```

## Generator gotchas

### `%pyproject_buildrequires` auto-injection

**Symptom**: build fails in `%prep` with `python3dist(launch)` or similar BR that won't resolve.

**Why**: When a spec `BuildRequires: pyproject-rpm-macros`, RPM auto-generates a `%generate_buildrequires` section that calls `%pyproject_buildrequires`, which reads `setup.py`'s `install_requires` and emits `python3dist(<name>)` BRs for every entry. ROS Python packages (`launch`, `ament_index_python`, etc.) live under `/opt/ros/jazzy/` and don't register `python3dist(...)` Provides, so those BRs are unresolvable.

**Fix**: patch `setup.py` during `%prep` to reduce `install_requires` to `['setuptools']` only. The runtime `Requires:` lines we generate already enforce the deps with proper RPM semantics:

```spec
python3 << 'PYEOF' || true
import re
p = "setup.py"
s = open(p).read()
s = re.sub(r"install_requires\s*=\s*\[[^\]]*\]", "install_requires=['setuptools']", s, flags=re.S)
open(p, "w").write(s)
PYEOF
```

### Don't put `%pyproject_buildrequires` literally in spec comments

**Symptom**: `%pyproject_buildrequires: error: argument REQUIREMENTS.TXT: can't open 'runs.': [Errno 2] No such file or directory`.

**Why**: RPM tries to expand `%pyproject_buildrequires` even inside a comment. The rest of the comment line (`runs. The full list...`) becomes its arguments.

**Fix**: refer to it as "the auto-generated buildrequires step" or "pyproject buildrequires" without the `%`.

### Rosdep key vs Fedora package name mismatches

**Symptom**: `dnf install` fails with `nothing provides python3-lark-parser`.

**Why**: Upstream `rosdep` python.yaml maps `python3-lark-parser` to itself (assuming Ubuntu). Fedora ships the package as `python3-lark`.

**Fix**: `DEP_REWRITES` table in the generator post-rewrites known mismatches:

```python
DEP_REWRITES = {
    "python3-lark-parser": "python3-lark",
}
```

Add new entries when you find them. Local rosdep override in `build/local-rosdep-jazzy.yaml` doesn't help here because rosdep prefers the upstream key when both match.

### Spec regen overwrites hand-tuned `%files`

**Symptom**: After a version bump, several packages fail with mysterious "file not found" errors that were previously fixed.

**Why**: `scripts/generate-spec.py` regenerates the entire spec from `package.xml` + `CMakeLists.txt`. Hand-tuned `%files` sections (added in earlier iterations to match real install layouts) get overwritten.

**Fix**: re-apply the hand fixes after regen. The recurring offenders are:

- `rclpy`: `%global debug_package %{nil}` + drop `lib/lib%{pkg_name}.so*`.
- `rclcpp_components`: replace `lib/lib%{pkg_name}.so*` with `lib/libcomponent_manager.so*` + `lib/%{pkg_name}/`.
- `tf2_ros`: add `libstatic_transform_broadcaster_node.so*` + `lib/%{pkg_name}/`.
- `tracetools`: add `include/%{pkg_name}/` + `libtracetools_status.so*` + `lib/%{pkg_name}/`.
- `launch_testing`: add `lib/%{pkg_name}/` for the test fixtures.
- `rqt`: drop the site-packages directory entry.
- `demo_nodes_cpp`: replace `lib/lib%{pkg_name}.so*` with `lib/lib*_library.so*` + `lib/%{pkg_name}/`.

**Long-term fix wanted**: per-package `%files` overrides in `packages.yaml` so the generator preserves them. Not yet implemented.

## Cross-distro gotchas

### CentOS Stream 10 doesn't ship Qt5 build deps

**Symptom**: `qt_gui_core`, `python_qt_binding`, `rqt`, and downstream rqt plugins fail on Stream 10 chroots with `No matching package to install: 'python3-sip-devel'`.

**Why**: Stream 10 ships only a minimal Qt surface. `python3-sip-devel`, `qt5-qtbase-devel`, and several Qt5 dev packages aren't in BaseOS / AppStream / CRB / EPEL 10.

**Fix**: accept it. The Phase 2 GUI surface is intentionally Fedora-only. Stream 10 users can install `ros-jazzy-ros-base` (headless), `ros-jazzy-ros2cli`, and `ros-jazzy-demo-nodes-cpp`. Documented in `docs/SCOPE.md` "Phase 2 build matrix caveat" section.

### Stream 10 needs EPEL 10 for `rpmlint`, `mock`, `python3-flake8`

**Symptom**: Stream 10 chroot's `dnf install rpmlint mock` fails.

**Why**: Stream 10 base/AppStream/CRB don't include the Fedora ROS build-toolchain packages. They're in EPEL 10.

**Fix**: per-chroot `additional_repos` on the COPR project for Stream 10 chroots only. Set via:

```bash
copr-cli edit-chroot --repos https://dl.fedoraproject.org/pub/epel/10/Everything/\$basearch/ \
                     hellaenergy/ros2/centos-stream-10-x86_64
```

CI workflows install `epel-release` + `dnf config-manager --set-enabled crb` first when running on Stream 10.

### Fedora doesn't package `iceoryx`

**Symptom**: `cyclonedds` build fails at dep-resolution if you don't carefully exclude iceoryx.

**Why**: Cyclone DDS's optional shared-memory transport requires `iceoryx_binding_c`, `iceoryx_posh`, `iceoryx_hoofs`. Fedora doesn't ship any of them.

**Fix**: build with `-DENABLE_SHM=OFF` (default for Cyclone DDS anyway). Stub the iceoryx packages in `build/local-rosdep-jazzy.yaml` with empty `fedora: []` arrays so rosdep doesn't error trying to resolve them. Standard sockets transport is sufficient for development.

### Fedora's `assimp-devel` and `ogre-devel` don't match what rviz wants

**Symptom**: rviz2 chain build fails (separate blockers for each).

**Why**: Fedora ships `assimp-6.x` and `ogre-1.9.x`. rviz wants `assimp-5.x` (API differences) and `ogre-14.x` (completely different version). System library substitution doesn't help.

**Status**: deferred. Tracked in `docs/UPSTREAM-ISSUES.md` as ros2/rviz#1708 (Ogre, in flight) and ros2/rviz#1730 (Assimp, awaiting upstream response). See [`SCOPE.md` "rviz2 deferral"](SCOPE.md#rviz2-deferral-side-effects) for the side-effects analysis.

## Workspace activation

### `/opt/ros/jazzy/setup.bash` doesn't exist by default

**Symptom**: After `dnf install ros-jazzy-ros-base`, sourcing `/opt/ros/jazzy/setup.bash` fails because the file doesn't exist.

**Why**: The setup.bash file is generated by the `ros_workspace` package (which uses `ament_package`'s template-emitter). Without `ros_workspace` installed, individual packages have their own `local_setup.sh` files but nothing aggregates them.

**Fix**: `ros-jazzy-ros-base` Requires `ros-jazzy-ros-workspace` and `ros-jazzy-ros-environment`. Both were originally missing from Phase 1; backfilled when the smoke test caught it.

### `LD_LIBRARY_PATH` doesn't include `/opt/ros/jazzy/lib64`

**Symptom**: Before fixing the foonathan_memory_vendor lib64 issue, runtime dlopen fails.

**Why**: setup.bash adds `/opt/ros/jazzy/lib` to `LD_LIBRARY_PATH`, not `lib64`. Anything that lands in `lib64` is invisible to the loader.

**Fix**: ensure all ROS packages install to `lib/`, not `lib64/`. Either by passing `-DCMAKE_INSTALL_LIBDIR=lib` (works for most ament_cmake packages) or by sed-patching the inner ExternalProject's CMAKE_ARGS (foonathan_memory_vendor pattern).

## Hidden runtime dep gotchas

### `rclpy` not Required: by `ros-jazzy-ros-base`

**Symptom**: `import rclpy` fails after `dnf install ros-jazzy-ros-base`. Nobody can write Python ROS 2 code.

**Why**: Phase 1's `ros-base` metapackage was built before rclpy was packaged. After we backfilled rclpy + lifecycle_msgs + rcl_lifecycle + pybind11_vendor, we forgot to update ros-base's Requires.

**Fix**: bumped ros-base to 0.13.1 with rclpy + ros-workspace + ros-environment in the Requires list.

### `ros2cli` plugins have surprising hard runtime deps

- `ros2pkg` Requires `ament_copyright` (despite the lint-family naming suggesting it's a test dep).
- `ros2topic` and `ros2service` Require `rosidl_runtime_py`.

Both `ament_copyright` and `rosidl_runtime_py` had to be packaged as standalone additions to support ros2cli installs. Surfaced by the smoke test trying to `dnf install ros-jazzy-ros2pkg` and getting "nothing provides..." errors.

**Fix**: package the missing transitive deps and add to `packages.yaml`. The ros2cli plugins themselves don't need any new logic.

## Upstream blockers (with how we found and tracked them)

### `rviz_ogre_vendor` and CMake 4.x

Found by attempting to build the rviz2 chain on Fedora 44 (CMake 4.0.3). Searched `ros2/rviz` issues, found existing report (#1637) with PR (#1708) in flight by @ahcorde. Confirmed our Fedora 44 reproduction in the PR comments rather than filing a duplicate.

**Lesson**: search before filing. Even niche-looking issues often have someone already tracking them upstream.

### `rviz_assimp_vendor` and Fedora's stricter GCC

Found by attempting to build with the workaround for the Ogre blocker in place. Failed with `-Werror=unused-but-set-variable` on `MS3DLoader.cpp`. Searched `ros2/rviz` issues, found nothing matching. Filed as #1730 with reproduction, root cause analysis, proposed `rviz_assimp_vendor`-side workaround diff, and offer to send the PR.

**Lesson**: when filing upstream, make it easy to act on. Concrete diff suggestions get faster responses than "this is broken, please fix."

## When to stop

This file is a tax on future-you. It's worth paying when:
- A gotcha bit hard enough that future-you would lose ≥1 hour rediscovering the fix.
- The fix is non-obvious from the spec or build log alone.
- Multiple packages share the same root cause (capture once, reference from each spec).

Don't add entries for:
- Things obvious from the spec.
- One-off fixes that won't recur.
- Generic Linux / RPM / CMake knowledge (the upstream docs cover those).
