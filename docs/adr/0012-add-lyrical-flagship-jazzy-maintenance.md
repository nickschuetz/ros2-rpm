# ADR 0012, Add Lyrical alongside Jazzy; Lyrical becomes the flagship, Jazzy moves to maintenance

**Status:** Accepted (2026-05-27). Reverses the "adding a Lyrical chroot is no longer a goal" clause of **ADR 0010** (section 5, Distro lifecycle policy). Amends **ADR 0007** (install location) by making the install prefix switchable so an FHS build is possible without a rewrite. The development-only positioning, the disclaimer-everywhere rule, and the production-deferral to Open Robotics from ADR 0010 all remain in force for both distros.

## Context

ADR 0010 set this repo's scope to Jazzy only, on the expectation that Open Robotics's official Fedora packages for Lyrical Luth (the 2026 LTS) would arrive and take over the production path. That expectation still holds: Open Robotics remains the production answer, and nothing in this ADR competes with that.

What changed is timing. The official Lyrical packages are not yet available, and a development-grade ROS 2 Lyrical on Fedora is useful in the interim, for the same reason the Jazzy sandbox was useful before it: developers want to compile and experiment against the current LTS on Fedora today. This ADR extends the existing stop-gap posture from one distro to two. It does not change the posture itself.

## Decision

1. **Maintain both Jazzy and Lyrical concurrently, both development-only.**
   - Lyrical is the **flagship** (the current LTS, the recommended distro for new development).
   - Jazzy moves to **maintenance** (version bumps and build fixes continue; it is no longer where new effort is focused).
   - Both remain development-only. The "Not the official ROS 2 packages for Fedora" disclaimer applies to both, on every public surface.

2. **Lyrical is ROS 2, not "ROS 3."** Package prefix `ros-lyrical-*`, default install prefix `/opt/ros/lyrical`, mirroring the Jazzy convention exactly. No naming or layout invention.

3. **Source layout: directory-per-distro in the existing `ros2-rpm` repo.** The repo is not renamed (a distro-specific name would be inaccurate for a two-distro repo, and a rename cascades through every metadata surface). Specs live under `specs/<distro>/`, per-distro manifests under `distros/<distro>/packages.yaml`, and `scripts/` plus `.github/workflows/` are made distro-aware so one tooling fix lands for both distros at once. Branch-per-distro was rejected because it forces CI, scripts, and docs to diverge and be kept in sync by cherry-pick.

4. **COPR layout: option A.** `hellaenergy/ros2` becomes the Lyrical (flagship) project. A new `hellaenergy/ros2-jazzy` project holds Jazzy (maintenance). Convention going forward: `hellaenergy/ros2` always tracks the current flagship distro, and an outgoing distro moves to `ros2-<name>` at the next LTS transition. No COPR forking is used; with no established external user base, projects are created fresh and populated by CI rebuilds. The CentOS Stream 10 per-chroot EPEL `additional_repos` must be re-applied to every new project, or Stream 10 builds fail to install build dependencies.

5. **Keep specs FHS-convertible (Fedora-friendly insurance).** The install prefix becomes switchable behind a build conditional (`%bcond fedora_fhs`): the default stays `/opt/ros/<distro>` for the COPR, and an FHS (`/usr`) build is a one-line flip. This keeps every spec liftable into Fedora dist-git for a possible future Fedora-main bid, or as a reference implementation, without a rewrite. FHS and Fedora-main inclusion remain aspirational and Fedora-Robotics-SIG-coordinated, not a near-term deliverable. This is the one place ADR 0010's "Phase 3 dropped" stance is softened: the door is kept open structurally, but no inclusion work is committed.

## What stays the same

- **Development-only for both distros.** Open Robotics's official packages remain the production path. No production-grade claims (no STIG/CERT/OWASP, no CVE-tracked SLA, no vendor support).
- The disclaimer banner, the license policy (permissive-default metapackages, accurate per-package SPDX, no aggregation hiding), the no-bundled-libs rule, hardening flags, `%check`, debuginfo, and SBOM emission all carry over unchanged to Lyrical.
- The technical pipeline (`generate-spec.py`, bloom post-processing, COPR build flow) is reused; it only gains a distro dimension.
- Carried patches must still be filed upstream first with DEP-3 provenance. This matters more now, since Lyrical pulls newer upstream and will surface its own build blockers.

## Consequences

- Doubles the build matrix work in principle, but shared tooling keeps the maintenance cost sublinear; a fix to `generate-spec.py` or a workflow benefits both distros at once.
- `docs/SCOPE.md`, `docs/UPGRADING.md`, `README.md`, `CHANGELOG.md`, both COPR projects' descriptions and instructions, and the GitHub repo metadata are updated in the same change-window as this ADR, per the sync rule.
- ADR 0010 carries a note pointing here; it is not deleted, because it explains the historical single-distro reasoning that this ADR extends.
- The `o3de-dependencies` COPR's external-repository reference must point at whichever distro O3DE consumes, since `hellaenergy/ros2` now means Lyrical.
