# ADR 0013, Add Fedora 45 chroots; build matrix goes from 6 to 8 chroot/arch pairs

**Status:** Accepted (2026-08-25). Resolves the "Fedora 45 when it releases is a follow-up" clause in CLAUDE.md's Resolved-scope section, and satisfies the standing rule (CLAUDE.md, COPR metadata) that any chroot-set change requires an ADR. Builds on **ADR 0012** (Lyrical flagship / Jazzy maintenance) and inherits the development-only posture and disclaimer-everywhere rule from **ADR 0010**.

## Context

Fedora 45 branched from Rawhide in August 2026 (GA 2026-10-20), and Rawhide has rolled forward to Fedora 46. When F45 branched, COPR forked our existing Rawhide builds into the new `fedora-45-*` chroots: all 173 non-visual Lyrical packages came up `forked` (installable) on both arches with zero failures. That clean inheritance is the direct payoff of the July 2026 Rawhide Python 3.15 foundation rebuild: F45 ships Python 3.15, the same interpreter Rawhide carried when we rebuilt the noarch python foundation, the message/rclpy bindings, and the fmt-v11 spdlog ABI chain against it. Nothing new had to be built to bring F45 up.

Two prerequisites the earlier planning set for adding F45 are now met: (1) the py3.15 foundation rebuild is done, and (2) this ADR records the matrix change. This ADR ratifies the `fedora-45-*` chroot addition rather than proposing it after the fact only in tooling.

## Decision

1. **Add `fedora-45-x86_64` and `fedora-45-aarch64` to both COPR projects** (`hellaenergy/ros2` for Lyrical, `hellaenergy/ros2-jazzy` for Jazzy). The build matrix becomes **8 chroot/arch pairs**: `fedora-44`, `fedora-45`, `fedora-rawhide`, `centos-stream-10`, each on x86_64 + aarch64 (was 6).

2. **Keep `fedora-rawhide` on the matrix.** Now that Rawhide is F46, it serves as the early-warning canary for the next Python and system-library transitions, exactly the role that surfaced the py3.15 and fmt-v11 breakage months before F45 GA. F45 is the current supported Fedora target; F44 stays until it reaches end of life, at which point it is dropped in a follow-up (no ADR needed to drop an EOL chroot, only to add one).

3. **The deferred visual/vcstool chain stays deferred on `fedora-45` and `fedora-rawhide`.** The 9 packages `gz-cmake-vendor`, `gz-utils-vendor`, `gz-math-vendor`, `rviz-ogre-vendor`, `rviz-rendering`, `rviz-common`, `rviz-default-plugins`, `rviz2`, `ros-desktop`, plus `spdlog-vendor`, cannot build on py3.15 chroots until Fedora ships `python3-vcstool` for Python 3.15 (Fedora point of contact: FAS `cottsay`). This is an upstream-Fedora blocker, not a spec defect; these packages remain green on `fedora-44` and `centos-stream-10`.

4. **CentOS Stream 10 EPEL and signing conventions are unaffected.** F45 is a standard Fedora chroot; the per-chroot EPEL `additional_repos` requirement (ADR 0012, section 4) applies only to the Stream 10 chroots and is unchanged.

## What stays the same

- **Development-only for both distros.** Open Robotics's official Lyrical packages remain the production path. No production-grade claims. The "Not the official ROS 2 packages for Fedora" disclaimer applies on every public surface, F45 included.
- License policy, no-bundled-libs, hardening flags, `%check`, debuginfo, and SBOM emission carry over to the F45 builds unchanged.
- The per-chroot build driver (`scripts/copr-drive.py`) already handles an arbitrary chroot set (per-chroot success detection, ADR-era PRs #18/#19/#20), so no tooling change is needed to drive 8 chroots; drift catch-ups now refresh F45 automatically.

## Consequences

- Build-matrix work grows from 6 to 8 pairs. Cost stays sublinear: F45 inherits Rawhide-validated builds, and one spec fix lands across all chroots at once.
- `README.md` badges/supported-distros, `docs/SCOPE.md`, `docs/UPGRADING.md` (Fedora N to N+1 notes), and both COPR project descriptions/instructions are updated in the same change-window as this ADR, per the sync rule, to list Fedora 45 as a supported chroot.
- When F45 reaches GA on 2026-10-20 it is a first-class supported target, not a preview. Users on F45 install the same `ros-lyrical-ros-base` set as F44.
- The next transition (F46 branch, and whatever Python bump Rawhide takes next) is now a known, mechanical process: force the three stale classes (py-path python modules, message/rclpy bindings, and compiled deps ABI-stale against a moved system library such as fmt), then let the forked chroot inherit the result.
