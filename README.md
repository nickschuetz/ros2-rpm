# ros2-rpm

ROS 2 Jazzy RPMs for **Fedora 44+** and **CentOS Stream 10**, built on **x86_64** and **aarch64**, scoped to what the [Open 3D Engine (O3DE)](https://o3de.org) ROS 2 Gem and adjacent embedded-robotics workloads consume. Distributed via the Fedora COPR [`hellaenergy/ros2`](https://copr.fedorainfracloud.org/coprs/hellaenergy/ros2).

This is **not** a full ROS 2 desktop distribution. It is a curated minimal subset (~70 packages) — `rclcpp`, the common message packages, `rmw_fastrtps_cpp` + Fast DDS, and their transitive dependencies. There is no `rviz2`, no `rqt`, no demo nodes. If you need full desktop ROS 2 on RHEL/EL, use [packages.ros.org](https://docs.ros.org/en/jazzy/Installation/RHEL-Install-RPMs.html) on RHEL 9 instead.

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

## Scope and license posture

Default metapackages (`ros-jazzy-ros-core`, `ros-jazzy-ros-base`) contain only **Apache-2.0** and **BSD-3-Clause** content. Installing a metapackage never pulls in non-permissive code.

Individual packages in this COPR may carry other open-source-compatible licenses (EPL-2.0, LGPL-3.0, MPL-2.0). When such packages exist, they are standalone — users install them explicitly and accept the additional obligations. See each package's `License:` field.

Full scope rules: [`docs/SCOPE.md`](docs/SCOPE.md).

## Security

- Built with Fedora's hardening flags (`_FORTIFY_SOURCE=3`, full RELRO, PIE, stack-clash protection, CFI).
- System libraries linked rather than vendored — Fedora's CVE pipeline covers transitive deps.
- CycloneDX SBOM published per build at `%{_datadir}/doc/<package>/sbom.cdx.json`.
- COPR repo metadata and packages are signed by the COPR project key. Fingerprint: _to be filled in after first build_.

Vulnerability disclosure: [`docs/SECURITY.md`](docs/SECURITY.md).

## Documentation

- [`docs/SCOPE.md`](docs/SCOPE.md) — what is in vs out of scope and why.
- [`docs/UPGRADING.md`](docs/UPGRADING.md) — upgrade notes between ROS 2 distros and Fedora releases.
- [`docs/SECURITY.md`](docs/SECURITY.md) — vulnerability handling, watchlist, disclosure.
- [`docs/adr/`](docs/adr/) — architecture decision records.

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
