# Architecture

This document describes the architecture of the `ros2-rpm` packaging project — the surfaces, the pipeline, and how the moving parts fit together. For scope and license policy, see [`SCOPE.md`](SCOPE.md). For the dep-ordered build pipeline, see [`build-order.md`](build-order.md). For decision rationale, see [`adr/`](adr/).

## The two surfaces

There are exactly two public surfaces, and they are kept in lockstep:

```
  GitHub (source of truth)              COPR (build + distribution)
  ─────────────────────────             ───────────────────────────
  github.com/nickschuetz/ros2-rpm   →   copr.fedorainfracloud.org/coprs/hellaenergy/ros2

  - spec files (specs/*.spec)              - chroot matrix (4 distros × 2 arches = 8)
  - generator (scripts/*)                  - signed RPMs
  - per-package config (packages.yaml)     - per-build SBOM
  - rosdep override (build/local-...)      - public package index
  - documentation (docs/, README.md)
  - ADRs (docs/adr/)
  - CI (lint + matrix-build dry-run)
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
   │    - LOCAL: mock --rebuild on fedora-44-x86_64            │
   │      (validates against pulled deps from COPR)           │
   │    - REMOTE: copr-cli build → COPR builds across all     │
   │      8 chroot/arch pairs in parallel.                    │
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

`rosdep`'s mapping from a ROS package name (e.g., `ament_package`) to an OS-specific RPM name (e.g., `ros-jazzy-ament-package`) is auto-generated by upstream `rosdistro` for OSes listed in `jazzy/distribution.yaml`'s `release_platforms`. Fedora is not listed there. We work around this with `build/local-rosdep-jazzy.yaml` — a local override mapping every package we ship to its `ros-jazzy-<dashed>` Fedora RPM name. See [ADR 0009](adr/0009-rosdistro-fedora-gap-workaround.md).

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

- **Phase 1** (live): minimal subset — `rclcpp`, common message packages, Fast DDS, `tf2_ros`. License-clean (`Apache-2.0 AND BSD-3-Clause`). See [`SCOPE.md`](SCOPE.md) for the package list.
- **Phase 2** (live except rviz2): the developer-tooling slice of `ros-jazzy-desktop` — rqt suite, ros2cli, alternate Cyclone DDS RMW, launch family, demo_nodes, lifecycle backfill, plus the `ros-jazzy-ros-desktop` metapackage with the heterogeneous `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0 AND EPL-2.0` aggregate. **rviz2 chain is deferred** pending upstream patches for Ogre's CMake-policy floor and Assimp's bundled `-Werror`; see [`SCOPE.md` → "rviz2 deferral side effects"](SCOPE.md#rviz2-deferral-side-effects). See [ADR 0011](adr/0011-phase-2-dev-sandbox-expansion.md).
- **Phase 3** (dropped): Fedora main-repo inclusion was originally aspirational; dropped in [ADR 0010](adr/0010-project-pivot-to-development-only.md). Production distribution is now Open Robotics's lane via their official Lyrical packages.

## CI / publishing flow

```
  contributor              GitHub                COPR
       │                     │                     │
       │ git push            │                     │
       ├────────────────────►│                     │
       │                     │                     │
       │                     │ workflow: lint      │
       │                     │ (rpmlint, forbidden │
       │                     │  patterns)          │
       │                     │                     │
       │                     │ workflow: build     │
       │                     │ (matrix-build       │
       │                     │  dry-run on all 8   │
       │                     │  chroot/arch pairs) │
       │                     │                     │
       │ copr-cli build      │                     │
       ├──────────────────────────────────────────►│
       │                     │                     │
       │                     │                     │ build all 8
       │                     │                     │ chroot/arch
       │                     │                     │ in parallel
       │                     │                     │
       │                     │                     │ sign + publish
       │                     │                     │
       │ ◄──────────────────────────────────────── │
       │   user dnf copr enable                    │
       │   hellaenergy/ros2                        │
```

The CI on GitHub does *not* publish to COPR — that's an explicit `copr-cli build` action by the maintainer. CI's job is to fail PRs that would publish broken specs (lint, forbidden-pattern check, matrix-build dry-run).

## What's not here (and why)

- **No bundled forks of system libs.** `tinyxml2`, `console_bridge`, `libyaml`, `spdlog`, `pybind11`, `boost`, `asio`, `openssl`, `gtest` come from Fedora's base repos. This makes Fedora's CVE pipeline cover transitive deps automatically. See [SCOPE.md](SCOPE.md) "Boundary rules".
- **No Cyclone DDS in Phase 1.** Default RMW is Fast DDS. Cyclone DDS is EPL-2.0 (different license aggregate), so it's deferred until a deliberate License-policy decision (ADR 0003).
- **No ament_lint family.** `ament_lint_*` are test-only deps. We pass `disable_tests: true` per package, which strips them from `BuildRequires`. The trade-off: no upstream lint runs at build time. Phase 2 may revisit.
- **No FHS layout in Phase 1/2.** `/opt/ros/<distro>/` matches every other distro; FHS is a Phase 3 separate effort (ADR 0007).
