# ros2-rpm

ROS 2 Jazzy RPMs for **Fedora 44+** and **CentOS Stream 10**, built on **x86_64** and **aarch64**, distributed via the Fedora COPR [`hellaenergy/ros2`](https://copr.fedorainfracloud.org/coprs/hellaenergy/ros2).

The end state is a `ros-jazzy-desktop`-equivalent install path — filling the gap that no current Fedora-native ROS 2 distribution covers. (Upstream `packages.ros.org` ships RHEL 9 RPMs that don't run on Fedora's Python 3.13; existing community Fedora COPRs are partial / unmaintained.)

## Phased delivery

Delivered in two phases. Phase 1 is the current shipping scope; Phase 2 expands to full desktop.

### Phase 1 — current scope (~70 packages)

Pipeline proving ground: `rclcpp`, common message packages, `rmw_fastrtps_cpp` + Fast DDS, transitive deps. License-clean (`Apache-2.0 AND BSD-3-Clause`). Validates the bloom + rosdep + Python-3.13 patch chain on a small surface. Ships first.

### Phase 2 — `ros-jazzy-desktop` equivalent (~320 packages)

Full ROS 2 desktop: `rviz2`, `rqt_*`, navigation stacks, alternative RMW implementations. Adds heterogeneous license aggregate (Qt is LGPL-3.0; Cyclone DDS is EPL-2.0 if shipped). Ships once Phase 1 is stable across all 8 chroot/arch pairs for 30+ days. See [ADR 0006](docs/adr/0006-full-ros2-desktop-as-eventual-scope.md).

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

Fedora 45 will be added when it ships (planned October 2026).

## Install location

Packages install to `/opt/ros/jazzy/` per upstream ROS 2 convention. Setup environment via `source /opt/ros/jazzy/setup.bash` (or enable `/etc/profile.d/ros-jazzy.sh` for opt-in shell-wide loading).

This is the same layout used by `packages.ros.org`, Ubuntu, and every existing community Fedora COPR. It supports clean side-by-side multi-distro installs (e.g., Jazzy + Lyrical when Lyrical is added). Fedora main-repo inclusion would require FHS layout — that's tracked as a separate Phase 3 effort and is not pursued in this repo today. See [ADR 0007](docs/adr/0007-install-location-opt-ros-jazzy.md).

## Scope and license posture

In Phase 1, default metapackages (`ros-jazzy-ros-core`, `ros-jazzy-ros-base`) contain only **Apache-2.0** and **BSD-3-Clause** content. Installing a metapackage never pulls in non-permissive code.

Individual packages may carry other open-source-compatible licenses (EPL-2.0, LGPL-3.0, MPL-2.0). When such packages exist, they're standalone — install them explicitly and accept the corresponding obligations. See each package's `License:` field.

In Phase 2, metapackages will match upstream ROS 2 composition honestly — the aggregate license becomes `Apache-2.0 AND BSD-3-Clause AND LGPL-3.0` (Qt via rviz2) and possibly `AND EPL-2.0` (Cyclone DDS as alt RMW). All non-permissive components ship dynamically linked.

Full scope and policy: [`docs/SCOPE.md`](docs/SCOPE.md).

## Subpackages

Every library package produces:

- `ros-jazzy-<pkg>` — runtime libs (`.so.*`), executables, runtime data
- `ros-jazzy-<pkg>-devel` — headers, CMake config, pkg-config (mandatory for libraries with headers)
- `ros-jazzy-<pkg>-debuginfo` and `ros-jazzy-<pkg>-debugsource` — auto-generated debug info

Pure-Python packages use `python3-<pkg>` instead of the runtime/devel split. Message-only packages still produce `-devel` subpackages for the generated headers and CMake config.

## Security

- Built with Fedora's hardening flags (`_FORTIFY_SOURCE=3`, full RELRO, PIE, stack-clash protection, CFI).
- System libraries linked rather than vendored — Fedora's CVE pipeline covers transitive deps.
- CycloneDX SBOM published per build at `%{_datadir}/doc/<package>/sbom.cdx.json`.
- COPR repo metadata and packages are signed by the COPR project key. Fingerprint: _to be filled in after first build_.

Vulnerability disclosure: [`docs/SECURITY.md`](docs/SECURITY.md).

## Documentation

- [`docs/SCOPE.md`](docs/SCOPE.md) — phased scope policy, in/out lists, package boundaries.
- [`docs/UPGRADING.md`](docs/UPGRADING.md) — upgrade procedures across ROS 2 distros and Fedora releases.
- [`docs/SECURITY.md`](docs/SECURITY.md) — vulnerability handling, watchlist, disclosure.
- [`docs/adr/`](docs/adr/) — architecture decision records (read these before opening scope-changing PRs).

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
