# Architecture

This document describes the architecture of the `ros2-rpm` packaging project, the surfaces, the pipeline, and how the moving parts fit together. For scope and license policy, see [`SCOPE.md`](SCOPE.md). For the dep-ordered build pipeline, see [`build-order.md`](build-order.md). For decision rationale, see [`adr/`](adr/).

## The two surfaces

There are exactly two public surfaces, and they are kept in lockstep:

```
  GitHub (source of truth)              COPR (build + distribution)
  ─────────────────────────             ───────────────────────────
  github.com/nickschuetz/ros2-rpm   →   copr.fedorainfracloud.org/coprs/hellaenergy/ros2

  - spec files (specs/*.spec)              - chroot matrix (3 distros × 2 arches = 6)
  - generator (scripts/*)                  - signed RPMs
  - per-package config (packages.yaml)     - per-build SBOM
  - local patches (specs/patches/)         - public package index
  - rosdep override (build/local-...)
  - documentation (docs/, README.md)
  - ADRs (docs/adr/)
  - CI (lint + verify-specs + sbom-validate +
        spec-dry-build + smoke-test +
        drift-check + upstream-issues + build matrix)
```

A user installs from COPR; a contributor reads the GitHub repo. Each artifact in COPR is reproducible from the GitHub source: the spec file is in `specs/`, the package version is recorded by the `Version:` and `Release:` fields, and the source archive is a fixed `bloom-release` tarball pinned in `Source0:`.

## The build pipeline

Any package goes through the same five stages. The generator handles 1-3 mechanically; stage 4 is handled by RPM/mock/COPR; stage 5 is COPR's createrepo + signing.

```
   ┌──────────────────────────────────────────────────────────┐
   │ 1. Source acquisition                                    │
   │    - bloom-release tag in ros2-gbp/<repo>-release        │
   │    - tarball cached in build/SOURCES/<pkg>-<ver>.tar.gz  │
   └──────────────────────────────────────────────────────────┘
                         ↓
   ┌──────────────────────────────────────────────────────────┐
   │ 2. Spec generation (scripts/generate-spec.py)            │
   │    - read package.xml                                    │
   │    - resolve <*_depend> via rosdep                       │
   │      (with build/local-rosdep-jazzy.yaml override)       │
   │    - pick template by build_type                         │
   │      (ament_python | ament_cmake | cmake)                │
   │    - detect message package, ament_python_install_       │
   │      package, install(DIRECTORY include), install(       │
   │      TARGETS|PROGRAMS), entry_points                     │
   │    - SPDX-normalize License:                             │
   │    - emit %prep / %build / %install / %check / %files    │
   └──────────────────────────────────────────────────────────┘
                         ↓
   ┌──────────────────────────────────────────────────────────┐
   │ 3. SRPM build (rpmbuild -bs)                             │
   │    - assembles %{name}-%{version}-%{release}.src.rpm     │
   │      with the spec + source tarball.                     │
   └──────────────────────────────────────────────────────────┘
                         ↓
   ┌──────────────────────────────────────────────────────────┐
   │ 4. Binary build                                          │
   │    - LOCAL: mock --rebuild on fedora-44-x86_64           │
   │      (validates against pulled deps from COPR)           │
   │    - REMOTE: copr-cli build → COPR builds across all     │
   │      6 chroot/arch pairs in parallel.                    │
   └──────────────────────────────────────────────────────────┘
                         ↓
   ┌──────────────────────────────────────────────────────────┐
   │ 5. Publish                                               │
   │    - COPR signs RPMs with project key                    │
   │    - createrepo updates repo metadata                    │
   │    - users `dnf copr enable hellaenergy/ros2`            │
   │    - downstream COPRs (o3de-dependencies) list us        │
   │      as a runtime External Repository.                   │
   └──────────────────────────────────────────────────────────┘
```

`scripts/publish.sh` is the wrapper that runs steps 1-4 against any package by name. `scripts/build-one.sh` is the local-only variant (1-3 + local mock).

For routine version syncs that only change `Version:` and `Source0:` (no dep shifts), `scripts/bump.py` short-circuits the pipeline: it reads `rosdistro/jazzy/distribution.yaml`, edits the spec in place, prepends a `%changelog` entry, and runs `scripts/verify-specs.py` as a guard. Pair with `scripts/check-upstream.py` (or the weekly `drift-check` workflow's sticky issue) to know which packages need bumping. See [`MAINTENANCE.md`](MAINTENANCE.md) for the full tooling reference.

## The four spec patterns

Every upstream ROS 2 package falls into one of four shapes. The generator emits four corresponding spec templates:

| Pattern | Build system | Examples | %install style |
|---|---|---|---|
| **ament_python** | setup.py (PEP 517) | `ament_package`, `rosidl_pycommon`, `ament_index_python` | `%pyproject_buildrequires` + `%pyproject_wheel` + `pip install --root --prefix=/opt/ros/<distro>` (legacy `%py3_install` is forbidden by ADR 0005) |
| **ament_cmake** | CMake + ament_package() | All `ament_cmake_*`, `rosidl_*`, all message packages, `rclcpp` | `%cmake` with `-DCMAKE_INSTALL_PREFIX=/opt/ros/<distro>` and a full set of `INCLUDE_INSTALL_DIR`/`LIB_INSTALL_DIR`/etc. overrides so packages using `GNUInstallDirs` honor the prefix |
| **cmake** (plain) | CMake (no ament_package) | `foonathan_memory_vendor`, `fastcdr`, `fastrtps`, `rmw` | Same as ament_cmake but no `share/ament_index/resource_index/<group>/<pkg>` sentinels in `%files` |
| **vendor (ExternalProject)** | CMake `ExternalProject_Add` | `foonathan_memory_vendor` | Above plus `%global debug_package %{nil}` (find-debuginfo can't see ExternalProject sources). `%files` is hand-curated for whatever the bundled upstream installs |

Beyond the build pattern, the generator also detects:

- **Message packages** (have `msg/`/`srv/`/`action/` subdir): emit per-typesupport `.so` glob (`lib%{pkg_name}__rosidl_*.so`), `/include/<pkg>/`, and Python `site-packages` bindings + egg-info.
- **Python entry_points / console_scripts**: emit `/bin/*` in `%files`.
- **install(DIRECTORY include)**: emit `/include/<pkg>/` in `%files`.
- **install(TARGETS) / ament_export_libraries**: emit `/lib/lib<pkg>.so*`.
- **install(PROGRAMS)**: emit `/lib/<pkg>/` (helper scripts).
- **ament_python_install_package(...)**: emit Python `site-packages/<pkg>/` + egg-info.
- **Missing LICENSE / CHANGELOG** (some bloom-release branches strip them): emit a comment instead of a broken `%license`/`%doc`.

## Subpackage split

Every library spec produces the conventional Fedora subpackage set so users install only what they need and downstream consumers get the right CMake / pkg-config surface for their phase of work:

| Subpackage | Contents |
|---|---|
| `ros-jazzy-<pkg>` | Runtime: `.so.*`, executables, runtime data files. |
| `ros-jazzy-<pkg>-devel` | Headers (`.h` / `.hpp`), CMake config (`*-config.cmake`), pkg-config (`*.pc`), unversioned `.so` symlink. Mandatory for any package that ships headers or CMake config. |
| `ros-jazzy-<pkg>-debuginfo` | Stripped debug symbols. Auto-generated by `find-debuginfo`; never disabled. |
| `ros-jazzy-<pkg>-debugsource` | Build sources for the debugger. Auto-generated alongside `-debuginfo`. |

Variants by package type:

- **Pure-Python packages** (`rclpy`, `ament_python`, etc.) use `python3-<pkg>` for Python files + C extensions. No `-devel` (Python lacks a separate dev surface in this style). `-debuginfo` / `-debugsource` still auto-generate for any C extension components.
- **Message-only packages** (`std_msgs`, `geometry_msgs`) put generated typesupport `.so.*` and IDL data in the runtime subpackage; generated headers and CMake config land in `-devel`. Both subpackages are mandatory even though message packages are sometimes treated as "pure interface."
- **Header-only libraries** ship headers + CMake config in `-devel`. The runtime subpackage may be empty or a stub for `Requires:` flow purposes.

The `-devel` subpackage mandate is enforced as a warning by `scripts/verify-specs.py` today (every spec currently lacks one); it can be promoted to fatal via `--devel-strict` once the retrofit is complete. See [`MAINTENANCE.md`](MAINTENANCE.md).

## Install layout

All RPMs install under `/opt/ros/<distro>/`. This matches every other ROS 2 distribution (Ubuntu/Debian, packages.ros.org RHEL, RoboStack, openSUSE) and is what `bloom-generate rosrpm` emits by default. See [ADR 0007](adr/0007-install-location-opt-ros-jazzy.md) for the rationale and Phase 3 plan for FHS-compliant paths.

```
/opt/ros/jazzy/
├── bin/                             # entry-point scripts (rosidl, fast-discovery-server, ...)
├── include/<pkg>/<pkg>/             # C/C++ headers (note doubled subpath for messages)
├── lib/                             # C/C++ shared libraries
│   ├── lib<pkg>.so*                 # standard libs
│   ├── lib<msgpkg>__rosidl_*.so     # message-package per-typesupport variants
│   └── python<X>/site-packages/     # Python modules (ament_python_install_package)
│       └── <pkg>/
├── share/<pkg>/                     # CMake config, package.xml, generated message defs
└── share/ament_index/resource_index/
    ├── packages/<pkg>               # sentinel: this package is installed
    ├── package_run_dependencies/<pkg>
    ├── parent_prefix_path/<pkg>
    └── <group>/<pkg>                # member_of_group sentinels
                                     # (rosidl_runtime_packages, rosidl_interface_packages, ...)
```

## Dependency model

ROS 2's package boundaries are fine-grained on purpose (see [ADR 0008](adr/0008-mirror-upstream-package-boundaries.md)). One upstream `package.xml` = one RPM. The dependency graph follows package.xml's `<*_depend>` declarations, with one important nuance: the `<buildtool_export_depend>` and `<build_export_depend>` tags become RPM `Requires:` lines because consumers need those packages installed at *their* build time when they `find_package(...)` the producer.

```
     ┌──────────────────────────────────────────┐
     │ <buildtool_depend> → BuildRequires       │
     │ <build_depend>     → BuildRequires       │
     │ <depend>           → BuildRequires       │
     │                      and Requires        │
     │ <exec_depend>      → Requires            │
     │ <test_depend>      → BuildRequires       │
     │                     (skipped if          │
     │                      disable_tests:true) │
     │ <buildtool_export_depend> → Requires     │
     │ <build_export_depend>     → Requires     │
     └──────────────────────────────────────────┘
```

The dep graph is realized as the tier list in [`build-order.md`](build-order.md): tiers are topological levels, packages in the same tier can build in parallel, tiers must build sequentially.

## The rosdistro-Fedora gap

`rosdep`'s mapping from a ROS package name (e.g., `ament_package`) to an OS-specific RPM name (e.g., `ros-jazzy-ament-package`) is auto-generated by upstream `rosdistro` for OSes listed in `jazzy/distribution.yaml`'s `release_platforms`. Fedora is not listed there. We work around this with `build/local-rosdep-jazzy.yaml`, a local override mapping every package we ship to its `ros-jazzy-<dashed>` Fedora RPM name. See [ADR 0009](adr/0009-rosdistro-fedora-gap-workaround.md).

```
   bloom-generate / rosdep                Fedora Repo
   ──────────────────────                 ───────────
   "ament_package"   ──┐                   ros-jazzy-ament-package
                       │
                       ├──→ build/local-rosdep-jazzy.yaml
                       │    (Fedora-specific overrides; we maintain this)
                       │
   ros/rosdistro     ──┘
   (upstream; Fedora gap)
```

## Phase plan

```
   Phase 1 (live)        ───►  Phase 2 (live, modulo rviz2)            ╳ Phase 3 (dropped)
   minimal subset                dev sandbox                              FHS / Fedora main
   ~85 packages                  + rqt + ros2cli + Cyclone DDS            see ADR 0010
   /opt/ros/jazzy/                + launch + demo_nodes + lifecycle
                                  + ros-jazzy-ros-desktop metapackage
                                  ⚠ rviz2 chain deferred (upstream blockers)
```

- **Phase 1** (live): minimal subset, `rclcpp`, common message packages, Fast DDS, `tf2_ros`. License-clean (`Apache-2.0 AND BSD-3-Clause`). See [`SCOPE.md`](SCOPE.md) for the package list.
- **Phase 2** (live except rviz2): the developer-tooling slice of `ros-jazzy-desktop`, rqt suite, ros2cli, alternate Cyclone DDS RMW, launch family, demo_nodes, lifecycle backfill, plus the `ros-jazzy-ros-desktop` metapackage with the heterogeneous `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0-only AND EPL-2.0` aggregate. **rviz2 chain is deferred** pending upstream patches for Ogre's CMake-policy floor and Assimp's bundled `-Werror`; see [`SCOPE.md` → "rviz2 deferral side effects"](SCOPE.md#rviz2-deferral-side-effects). See [ADR 0011](adr/0011-phase-2-dev-sandbox-expansion.md).
- **Phase 3** (dropped): Fedora main-repo inclusion was originally aspirational; dropped in [ADR 0010](adr/0010-project-pivot-to-development-only.md). Production distribution is now Open Robotics's lane via their official Lyrical packages.

## CI / publishing flow

```
  contributor              GitHub                                COPR
       │                     │                                    │
       │ git push / open PR  │                                    │
       ├────────────────────►│                                    │
       │                     │                                    │
       │                     │ workflow: lint (per push/PR)       │
       │                     │   ├─ rpmlint                       │
       │                     │   ├─ license-check (legacy SPDX)   │
       │                     │   ├─ forbidden-patterns (grep)     │
       │                     │   ├─ verify-specs (full audit)     │
       │                     │   └─ sbom-validate (CycloneDX)     │
       │                     │                                    │
       │                     │ workflow: spec-dry-build (PR only) │
       │                     │   on PRs that touch specs/, runs   │
       │                     │   rpmspec -P, spectool -g,         │
       │                     │   rpmbuild -bs, dnf builddep on    │
       │                     │   up to 3 changed specs.           │
       │                     │                                    │
       │                     │ workflow: build (per push/PR)      │
       │                     │   matrix-build dry-run on all 6    │
       │                     │   chroot/arch pairs.               │
       │                     │                                    │
       │                     │ workflow: smoke-test (per push/PR  │
       │                     │   + daily 06:00 UTC). Installs     │
       │                     │   ros-base on fresh Fedora 44,     │
       │                     │   exercises all 22 checks.         │
       │                     │                                    │
       │                     │ workflow: drift-check (Sun 08:00)  │
       │                     │   diffs local pins vs rosdistro;   │
       │                     │   updates a sticky issue in place. │
       │                     │                                    │
       │                     │ workflow: upstream-issues (daily)  │
       │                     │   queries tracked GH issues/PRs,   │
       │                     │   pings when one closes.           │
       │                     │                                    │
       │ copr-cli build      │                                    │
       ├───────────────────────────────────────────────────────► │
       │                     │                                    │
       │                     │                                    │ build all 6
       │                     │                                    │ chroot/arch
       │                     │                                    │ in parallel
       │                     │                                    │
       │                     │                                    │ sign + publish
       │                     │                                    │
       │ ◄────────────────────────────────────────────────────── │
       │   user dnf copr enable hellaenergy/ros2                  │
```

The CI on GitHub does *not* publish to COPR, that's an explicit `copr-cli build` action by the maintainer. CI's job is to fail PRs that would publish broken specs and to surface drift / upstream-blocker movement between manual builds. See [`MAINTENANCE.md`](MAINTENANCE.md) for the per-workflow knob descriptions.

## What's not here (and why)

- **No bundled forks of system libs.** `tinyxml2`, `console_bridge`, `libyaml`, `spdlog`, `pybind11`, `boost`, `asio`, `openssl`, `gtest` come from Fedora's base repos. This makes Fedora's CVE pipeline cover transitive deps automatically. See [SCOPE.md](SCOPE.md) "Boundary rules".
- **Cyclone DDS shipped in Phase 2, not Phase 1.** Default RMW remains Fast DDS (Apache-2.0). Cyclone DDS (EPL-2.0) is a Phase 2 alternate RMW per ADR 0011; users opt in by setting `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` and installing `ros-jazzy-rmw-cyclonedds-cpp`. `ros-jazzy-ros-base` does not pull EPL-2.0 content.
- **No ament_lint family.** `ament_lint_*` are test-only deps. We pass `disable_tests: true` per package, which strips them from `BuildRequires`. The trade-off: no upstream lint runs at build time. Phase 2 may revisit.
- **No FHS layout in Phase 1/2.** `/opt/ros/<distro>/` matches every other distro; FHS is a Phase 3 separate effort (ADR 0007), and Phase 3 itself was dropped per ADR 0010.
- **rviz2 chain not shipped.** Two upstream blockers: `rviz_ogre_vendor` (CMake 4.x policy floor, [ros2/rviz#1708](https://github.com/ros2/rviz/pull/1708)) and `rviz_assimp_vendor` (Fedora's stricter GCC + bundled `-Werror`, [ros2/rviz#1730](https://github.com/ros2/rviz/issues/1730)). The patch-carry infrastructure is in place at [`specs/patches/`](../specs/patches/README.md) if the deferral becomes blocking; current decision is to wait for upstream merges.
