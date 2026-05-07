# ADR 0008: Mirror upstream ROS 2 package boundaries 1:1; do not bundle into monolithic RPMs

- **Status**: Accepted
- **Date**: 2026-05-07

## Context

A typical Fedora user's intuition is that one logical "thing" maps to one RPM (often with a `-devel` companion). Looking at this COPR, they will see ~30+ packages just to reach a single message library:

- `ros-jazzy-ament-package`
- `ros-jazzy-ament-cmake-core`
- `ros-jazzy-ament-cmake`
- `ros-jazzy-ament-cmake-export-definitions`
- `ros-jazzy-ament-cmake-export-dependencies`
- `ros-jazzy-ament-cmake-export-include-directories`
- `ros-jazzy-ament-cmake-export-interfaces`
- `ros-jazzy-ament-cmake-export-libraries`
- `ros-jazzy-ament-cmake-export-link-flags`
- `ros-jazzy-ament-cmake-export-targets`
- `ros-jazzy-ament-cmake-gen-version-h`
- `ros-jazzy-ament-cmake-include-directories`
- `ros-jazzy-ament-cmake-libraries`
- `ros-jazzy-ament-cmake-python`
- `ros-jazzy-ament-cmake-target-dependencies`
- `ros-jazzy-ament-cmake-test`
- `ros-jazzy-ament-cmake-version`
- (rosidl_*, ament_lint_*, ...)

This volume is unusual against most Fedora packaging norms. The natural question is: why not bundle several upstream packages into one RPM?

## Decision

**One upstream ROS package = one RPM. No bundling, no merging, no convenience metapackages that obscure the upstream boundary.**

The only metapackages we ship are upstream-defined (`ros-jazzy-ros-core`, `ros-jazzy-ros-base`, `ros-jazzy-desktop` in Phase 2) — and those are pure `Requires:` aggregators with no content of their own.

## Why fine-grained matches upstream ROS

ROS 2's fundamental unit is the package — every directory with a `package.xml` is its own thing with:

- Independent semantic version
- Independent dependency graph
- Independent CMake `find_package()` surface
- Independent maintainer / release cadence (in principle; in practice many ship together)

Consumers genuinely use them individually:

- `find_package(ament_cmake_export_libraries REQUIRED)` pulls in only the macros for exporting library targets, not the whole ament_cmake stack.
- A pure-message package depends on `rosidl_default_runtime` but not `rosidl_typesupport_cpp` if it doesn't want C++ bindings.
- Embedded users frequently install `ros-jazzy-rclcpp` and a few message packages without ever touching `rqt_*` or visualization deps — that minimalism is only possible because each piece is a separate package.

Bundling several upstream packages into one RPM would:

- Force users who want one piece to pull all of it.
- Break the `find_package()` consumption pattern (consumers expect to find each component independently).
- Diverge from every other Linux distro's ROS packaging (Ubuntu/Debian via bloom, RHEL via packages.ros.org, openSUSE, RoboStack on conda) — making this COPR an outlier and reducing predictability for users coming from those ecosystems.

## Why this is unusual to traditional Fedora users

Most established Fedora packages are monolithic — `boost-devel` ships all of Boost's headers, `qt6-qtbase-devel` ships all the Qt core dev surface. The exceptions are ecosystems where upstream is itself granular:

- Python on Fedora: one RPM per upstream PyPI package (`python3-requests`, `python3-numpy`, `python3-pytest`, ...).
- Node.js on Fedora: similarly one RPM per upstream npm package when packaged.
- Rust crates as RPMs: one RPM per crate.

ROS 2 is in the same family as those: an ecosystem where upstream's atomic unit is a small, self-contained package, and the tooling around it (`find_package`, `ament_index`, `colcon`) treats each one as a first-class entity. We follow that convention because diverging from it costs more in user surprise and tooling friction than it saves in maintenance time.

## Tooling implication

`bloom-generate rosrpm` (Open Robotics' supplied generator) emits one spec per upstream package. Our `scripts/generate-spec.py` follows the same model. Both approaches fit the upstream structure; combining packages would require us to write a wholly different generator and then maintain it forever as upstream evolves.

## Consequences

**Positive**:
- Users coming from Ubuntu / Debian / packages.ros.org find familiar package names (`ros-jazzy-rclcpp` is searchable, expected, and matches every other distribution's RPM/Deb).
- `dnf install ros-jazzy-<one-package>` pulls only what's needed — predictable closure.
- Per-package CVE tracking, per-package version pins, per-package source pins all map cleanly.
- Easy to upstream into Fedora main repos in Phase 3 because the structure already matches `bloom-generate`'s expected output.

**Negative**:
- ~30+ specs to reach the first message package; ~70 specs for the Phase 1 minimal subset; ~320 for Phase 2 desktop. Significantly more package count than typical Fedora work.
- Per-package COPR build slot consumption is real — each new package = 6 chroot builds.

**Neutral**:
- Upstream-managed metapackages (`ros-jazzy-ros-core`, `ros-jazzy-ros-base`) provide convenient bulk-install entry points for users who don't want to think about granularity. They give us the convenience of bundling for users without requiring us to merge upstream packages.

## Alternatives considered

- **Bundle by feature**: e.g., one `ros-jazzy-ament-cmake-bundle` containing all ament_cmake_*. Rejected — breaks `find_package()` granularity, requires hand-written `Provides:` aliases for every upstream package name, and forces users into all-or-nothing installs.
- **Bundle the ament_cmake monorepo into one RPM**: similar problems plus would conflate independent `package.xml` boundaries, making spec maintenance harder when upstream releases individual packages.
- **Subpackages within one spec**: `Name: ros-jazzy-ament-cmake-stack` with `%package -n ros-jazzy-ament-cmake-core`, etc. Technically possible but `bloom-generate`'s output doesn't fit this model and we'd lose the auto-generated specs benefit. Rejected on tooling-friction grounds.
