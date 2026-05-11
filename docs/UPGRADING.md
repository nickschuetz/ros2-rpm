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

### Approaching upstream EOL

Upstream Open Robotics EOLs Jazzy in May 2029. The COPR's posture past that date is **not yet decided**, see [README → "Long-term posture"](../README.md#long-term-posture). Three credible options when the time comes:

- **Sunset entirely.** Drop chroots, archive the branch, README banner pointing users to Open Robotics's then-current distro. Cleanest for users, but loses any historical-reproducibility value.
- **Freeze as a historical archive.** Stop publishing new builds, leave the existing RPMs reachable for users who need a known-good Jazzy snapshot for reproducing past development work.
- **Pivot to a later development distro.** If a near-future ROS 2 distro is on similar Fedora-on-Fedora footing and the maintainer is willing to do the work, replay this COPR's pipeline against that distro on dev-only terms.

The choice will be made via a follow-up ADR ~90 days before EOL based on usage telemetry, Open Robotics's published Fedora roadmap at that time, and maintainer bandwidth. Whichever path is chosen, security posture beyond EOL is **not** part of the commitment, Fedora's CVE pipeline only covers deps while the underlying Fedora release is in support.

Concrete mechanics regardless of path:

1. Open a tracking issue 90 days before upstream EOL with the decision questions above.
2. Update the README "Long-term posture" section with the chosen path and target date.
3. Sync the COPR description and instructions with the same wording (per the CLAUDE.md sync rule).
4. Execute the chosen path on/near EOL day.

## Fedora N → N+1 rebuild

When a new Fedora release ships:

1. Add `fedora-N+1-x86_64` and `fedora-N+1-aarch64` chroots in COPR.
2. Run the full build matrix on the new chroot. Common breakage:
   - **Python ABI**: Fedora bumps Python every release. `%pyproject_*` macros handle most of this; `rclpy` and ament_python may need patches.
   - **CMake major-version bumps**: F44 ships CMake 4.0; later releases may bring breaking changes. Bump `cmake_minimum_required(...)` in any patched-upstream config.
   - **Soname drift**: `tinyxml2`, `console_bridge`, `libyaml`, `spdlog`, `pybind11`, `boost`, rebuild deps will resolve most cases automatically; track explicit pins where they exist.
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
