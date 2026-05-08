# Build order

This is the dependency-ordered build pipeline. Tiers must be built sequentially (each depends on the previous); within a tier, packages are independent and could build in parallel.

The order is derived from `package.xml` `<*_depend>` declarations. New packages are added to this document as they enter the build set.

## Phase 1 minimal subset — current build order

```
T-A  Foundation Python tooling
     ├─ ament_package          (pure-Python)
     │
T-B  ament_cmake stack (no compilation, mostly CMake macros)
     ├─ ament_cmake_core
     ├─ ament_cmake_export_definitions
     ├─ ament_cmake_export_dependencies
     ├─ ament_cmake_export_include_directories
     ├─ ament_cmake_export_interfaces
     ├─ ament_cmake_export_libraries
     ├─ ament_cmake_export_link_flags
     ├─ ament_cmake_export_targets
     ├─ ament_cmake_gen_version_h
     ├─ ament_cmake_include_directories
     ├─ ament_cmake_libraries
     ├─ ament_cmake_python
     ├─ ament_cmake_target_dependencies
     ├─ ament_cmake_test
     ├─ ament_cmake_version
     ├─ ament_cmake_gtest
     ├─ ament_cmake_gmock
     ├─ ament_cmake_pytest
     ├─ ament_cmake          (umbrella metapackage)
     ├─ ament_cmake_ros      (umbrella + Requires for the test framework family)
     │
T-C  Utility libs (compiled C/C++)
     ├─ rcutils              (C utilities)
     ├─ rcpputils            (C++ utilities)
     ├─ ament_index_python   (Python — ament_index lookups)
     ├─ python_cmake_module  (CMake helper for finding system Python)
     ├─ rpyutils             (Python helpers used at code-gen time)
     │
T-D  rosidl chain (the IDL toolchain)
     ├─ rosidl_typesupport_interface     (header-only)
     ├─ rosidl_pycommon                  (Python)
     ├─ rosidl_adapter                   (Python)
     ├─ rosidl_runtime_c                 (compiled lib)
     ├─ rosidl_runtime_cpp               (header-only)
     ├─ rosidl_parser                    (Python)
     ├─ rosidl_cli                       (Python; ships /bin/rosidl)
     ├─ rosidl_cmake                     (CMake macros)
     ├─ rosidl_generator_c               (Python generator)
     ├─ rosidl_generator_cpp             (Python generator)
     ├─ rosidl_generator_py              (Python generator)
     ├─ rosidl_generator_type_description
     ├─ rosidl_typesupport_introspection_c   (compiled lib)
     ├─ rosidl_typesupport_introspection_cpp (compiled lib)
     ├─ rosidl_typesupport_c             (compiled lib)
     ├─ rosidl_typesupport_cpp           (compiled lib)
     ├─ rosidl_dynamic_typesupport       (compiled lib)
     │
T-E  Fast DDS chain (the default RMW)
     ├─ foonathan_memory_vendor          (vendor: ExternalProject)
     ├─ fastcdr                          (compiled C++ lib)
     ├─ fastrtps                         (compiled C++ DDS)
     ├─ fastrtps_cmake_module            (CMake helper)
     ├─ rmw                              (middleware abstraction)
     ├─ rosidl_typesupport_fastrtps_c    (compiled lib)
     ├─ rosidl_typesupport_fastrtps_cpp  (compiled lib)
     │
T-F  Code-gen umbrellas
     ├─ rosidl_core_generators           (metapackage)
     ├─ rosidl_core_runtime              (metapackage)
     ├─ rosidl_default_generators        (metapackage)
     ├─ rosidl_default_runtime           (metapackage)
     │
T-G  Message foundation
     ├─ builtin_interfaces               ← first message package
     │
T-H  Tier-1 messages (depend only on builtin_interfaces / no msg deps)
     ├─ service_msgs
     ├─ std_msgs
     ├─ unique_identifier_msgs
     │
T-I  Tier-2 messages
     ├─ action_msgs       (needs service_msgs + unique_identifier_msgs)
     ├─ geometry_msgs     (needs std_msgs)
     ├─ ackermann_msgs    (needs std_msgs)
     ├─ trajectory_msgs   (needs std_msgs + builtin_interfaces)
     │
T-J  Tier-3 messages
     ├─ sensor_msgs       (needs std_msgs + geometry_msgs)
     ├─ nav_msgs          (needs std_msgs + geometry_msgs)
     ├─ vision_msgs       (needs std_msgs + geometry_msgs)
     │
T-K  Tier-4 messages
     ├─ control_msgs      (needs action_msgs + sensor_msgs + trajectory_msgs + ...)
     │
T-L  Direct ROS 2 client API
     ├─ rcl, rclcpp, tf2_ros, ...      (Phase 1 endpoint)
     │
T-M  Convenience metapackages
     ├─ ros-jazzy-ros-core
     └─ ros-jazzy-ros-base
```

## Build patterns the generator handles

Four upstream patterns surfaced through Phase 1:

| Pattern | Example | Generator handling |
|---|---|---|
| **ament_python** | `ament_package`, `rosidl_pycommon`, `ament_index_python` | `%pyproject_buildrequires` + `%pyproject_wheel` + raw `pip install --prefix=/opt/ros/<distro>`. Detect `console_scripts` in `setup.py` → add `/bin/*` to `%files`. |
| **ament_cmake** | All ament_cmake_*, rosidl_*, message packages | `%cmake` with `-DCMAKE_INSTALL_PREFIX=/opt/ros/<distro>` + override of `INCLUDE_INSTALL_DIR` / `LIB_INSTALL_DIR` / etc. so packages using GNUInstallDirs honor the prefix. PYTHONPATH set in `%build`/`%install` so `find_package()` Python invocations see installed ROS Python modules. |
| **cmake** (plain) | `foonathan_memory_vendor`, `fastcdr`, `fastrtps`, `rmw` | Same as ament_cmake but no `ament_package()` so no ament_index sentinels in `%files`. |
| **vendor (ExternalProject)** | `foonathan_memory_vendor` | Above plus `%global debug_package %{nil}` (find-debuginfo can't see ExternalProject sources). Hand-curate `%files` for whatever the bundled upstream installs. |

## Build-time edge cases

These caught us during Phase 1; documented so future packages can avoid them:

- **`pushd`/`popd` inside `%generate_buildrequires`** writes the directory stack to stdout, which RPM captures as buildrequires tokens and aborts with `Dependency tokens must begin with alpha-numeric ...`. Always redirect: `pushd <dir> > /dev/null`.
- **`bloom-release` branches strip LICENSE** from per-package subtrees in some monorepos. Generator detects this and omits `%license` rather than fail.
- **`bloom-generate rosrpm` prompts interactively** when a rosdep key has no Fedora mapping. Solution: pre-populate `build/local-rosdep-jazzy.yaml` with our ROS package names so bloom never asks.
- **CHANGELOG.rst is sometimes missing** (`fastcdr`, `builtin_interfaces`). Detect and skip `%doc` accordingly.
- **`ament_cmake_ros-extras.cmake` unconditionally `find_package`s gmock/gtest/pytest.** Every consumer needs them as transitive `Requires:` even when not testing. Hand-injected into `ament_cmake_ros`'s spec.
- **COPR repo-metadata propagation lag** (~30–60s) and mock cache can hide just-published deps. `mock --scrub=cache` (or `--scrub=all`) clears it.
- **Source-filename collisions**: when multiple sub-packages share a monorepo (e.g., `rosidl_typesupport_c` + `_cpp`), the local cache filename must include `%{pkg_name}` to avoid one overwriting the other.
- **`ament_python_install_package(...)` in CMakeLists** = the package ships a Python module under `/opt/ros/<distro>/lib/python<X>/site-packages/<pkg>/`. Generator auto-detects.
- **Multi-typesupport message packages** install one `.so` per typesupport variant (`lib<pkg>__rosidl_generator_c.so`, `lib<pkg>__rosidl_typesupport_c.so`, `lib<pkg>__rosidl_typesupport_fastrtps_c.so`, `_introspection_c`, plus `_cpp` variants). Use a glob: `%{install_prefix}/lib/lib%{pkg_name}__rosidl_*.so`.

## Roadmap beyond messages

Once Phase 1's message set is complete, the remaining steps to a usable ROS 2 install are:

- **rcl** + **rclcpp** + **rclpy** — the client APIs
- **tf2** + **tf2_ros** — coordinate-frame transforms
- **ros2cli** + **ros2run/topic/service/action/...** — the `ros2` command-line tool
- **launch** + **launch_ros** — launch system
- **Convenience metapackages** (`ros-jazzy-ros-core`, `ros-jazzy-ros-base`) wrapping the above

Phase 2 (full `ros-jazzy-desktop`-equivalent) extends with `rviz2`, `rqt_*`, navigation/manipulation stacks, etc. — see [ADR 0006](adr/0006-full-ros2-desktop-as-eventual-scope.md).
