# Upgrading

Procedures for moving between ROS 2 distros and Fedora / CentOS Stream releases.

## ROS 2 distro transitions

ROS 2 distros are not API-compatible. A user moving from Jazzy to Lyrical replaces the entire `/opt/ros/jazzy` install path with `/opt/ros/lyrical`. This COPR ships parallel package trees per distro, so the transition is install-side-by-side, then uninstall the old.

### Adding a new distro to the COPR

Gated by the readiness checklist tracked in the pinned GitHub issue (see `CLAUDE.md` → Distro lifecycle policy). Summary of the steps:

1. Pin the [tracking issue](https://github.com/nickschuetz/ros2-rpm/issues) for the new distro.
2. When all checklist items hold, cut a `<distro>` branch in the repo.
3. Run the bloom-rpm pipeline against the new branch's manifest.
4. Validate on all 8 chroot/arch pairs in CI.
5. Add the new distro's chroots to the COPR (no chroot additions before CI is green).
6. Update README's "Supported targets" table.
7. Announce in the COPR project description.

### Sunsetting an EOL distro

When upstream EOLs a distro (e.g., Jazzy → May 2029):

1. Open a tracking issue 90 days before EOL.
2. README banner: "Jazzy will be removed from this COPR on YYYY-MM-DD."
3. On EOL day: drop the distro's chroots from `copr-cli modify`, archive the branch.
4. Do not carry past EOL — security posture depends on Fedora's CVE pipeline still covering deps that the EOL'd distro pinned.

## Fedora N → N+1 rebuild

When a new Fedora release ships:

1. Add `fedora-N+1-x86_64` and `fedora-N+1-aarch64` chroots in COPR.
2. Run the full build matrix on the new chroot. Common breakage:
   - **Python ABI**: Fedora bumps Python every release. `%pyproject_*` macros handle most of this; `rclpy` and ament_python may need patches.
   - **CMake major-version bumps**: F44 ships CMake 4.0; later releases may bring breaking changes. Bump `cmake_minimum_required(...)` in any patched-upstream config.
   - **Soname drift**: `tinyxml2`, `console_bridge`, `libyaml`, `spdlog`, `pybind11`, `boost` — rebuild deps will resolve most cases automatically; track explicit pins where they exist.
3. Once green, drop the EOL'd Fedora release (typically N-2). Fedora supports the latest two releases.

## CentOS Stream 10 → Stream 11 (future)

When Stream 11 emerges (likely 2027–2028 based on RHEL release cadence):

1. Add `centos-stream-11-x86_64` and `centos-stream-11-aarch64` chroots.
2. Expect a bigger jump in baseline tooling than Fedora N→N+1: glibc, gcc, Python all move further.
3. Stream 10 retirement aligns with RHEL 10 EOL. Carry both during overlap.

## RPM 4.19 → RPM 6 spec migration

Specs are written to the RPM 4.19 floor for portability. RPM 6.0-only macros are guarded behind `%if 0%{?fedora} >= 43`. When Stream 10 EOLs and only Stream 11+ remains:

1. Drop the `%if 0%{?fedora} >= 43` guards if Stream 11 also ships RPM 6+.
2. Adopt v6 package format if COPR supports it across the surviving chroots.
3. Switch to the native `%generate_sbom` macro (if Fedora has shipped one by then) and drop the `syft`-in-`%install` workaround. Capture the migration in an ADR.
