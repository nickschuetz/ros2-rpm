# ADR 0010, Project pivot to development-only; Lyrical official is OR's responsibility

**Status:** Accepted (2026-05-08). Amended same day by **ADR 0011** which reopens Phase 2 in a narrower form (dev-sandbox expansion of `ros-jazzy-desktop`, not the original ~320-package full desktop). The development-only positioning, the disclaimer-everywhere rule, and the production-deferral to Open Robotics all remain in force. Only the "Phase 2 cancelled" portion of this ADR is narrowed.

## Context

When this repo started, no upstream-supported ROS 2 RPM build existed for Fedora. Open Robotics's `packages.ros.org` shipped RHEL 9 RPMs only, incompatible with Fedora's Python 3.14 ABI. The Fedora Robotics SIG was working on a long-horizon Fedora-main-repo packaging effort but had no near-term shipping path. The original project goal (per ADR 0001 and ADR 0006) was therefore to:

1. Ship a Phase 1 minimal subset of ROS 2 Jazzy as a third-party COPR for Fedora 44+ and CentOS Stream 10, then
2. Expand to a Phase 2 `ros-jazzy-desktop`-equivalent build, then
3. Possibly attempt Fedora-main-repo inclusion (Phase 3) at some point.

That trajectory presumed this repo (and the Fedora Robotics SIG) would be the only shipping paths for ROS 2 on Fedora for the foreseeable future.

## Update

Open Robotics is taking on official Fedora support starting with **Lyrical Luth** (the 2026 LTS). The official packages will be supported, CVE-tracked, and will be the recommended path for any production use of ROS 2 on Fedora.

This changes the role of this repo entirely. We are no longer filling a multi-year gap, we are providing a stop-gap development sandbox for Jazzy on Fedora until the official Lyrical packages arrive. After that, the official packages take over.

## Decision

**This repo is now development-only.** All public-facing copy, project metadata, and per-package descriptions must communicate this clearly. The full set of changes:

1. **Scope**:
   - Phase 1 minimal subset stays (it's already shipped and useful for development).
   - **Phase 2 (full `ros-jazzy-desktop` equivalent) is cancelled.** Per ADR 0006's revised note. Reason: Open Robotics will deliver the production-grade equivalent for Lyrical; expanding this repo's surface no longer serves users.
   - **Phase 3 (Fedora main repo inclusion) is dropped.** That path was already aspirational; it is now Open Robotics's lane (or the Fedora Robotics SIG's, on a separate timeline).
2. **Disclaimer**: every public surface (README, COPR description, COPR instructions, GitHub repo description, CITATION.cff abstract) must carry a prominent "**Not the official ROS 2 packages for Fedora**" notice and a pointer to the upcoming Open Robotics Lyrical packages.
3. **Production-grade claims are dropped**:
   - The "STIG-adjacent posture for CentOS Stream 10" pitch in `docs/SECURITY.md` is replaced with a plain statement that no production-deployment claim is being made.
   - The CVE-feed automation roadmap (drift-tracking, OSV scanning) is downgraded from required to optional. If implemented at all, it serves the maintainer's curiosity, not a user-facing SLA.
4. **Per-package install messaging**: `%description` blocks should not promise long-term support. Spec-file changes for this are not retroactive, new specs and any spec touched in a future PR pick up the reframe.
5. **Distro lifecycle policy**:
   - Adding a Lyrical chroot here is **no longer a goal**. When the official Open Robotics Lyrical packages ship, users should switch to those. This COPR's chroots stay frozen at the Phase 1 build matrix (Fedora 44 / Fedora rawhide / CentOS Stream 10 × x86_64 + aarch64) for Jazzy only.
   - The COPR's lifetime past Jazzy EOL (May 2029) is **left open**, could be retired entirely, frozen as a historical archive, or extended to track a later development distro. To be decided closer to the date in a follow-up ADR. No commitment today.

## What stays the same

- The technical pipeline (`scripts/generate-spec.py`, `bloom-rpm` post-processing, COPR build flow) is still useful infrastructure and remains in place.
- Phase 1 packages keep shipping, they are appropriate for development workflows.
- Build hardening flags, license cleanliness, SBOM emission per build, all retained because they are good engineering hygiene, not because we are claiming production posture.
- All eight chroot/arch pairs continue to build on every change. Dropping aarch64 or Stream 10 would only churn CI for no gain.

## Why this matters

Without this pivot, two harmful outcomes were likely:

1. **Users would deploy this COPR to production**, expecting vendor support that does not exist. The disclaimer plus the "use Open Robotics for production" pointer eliminates that confusion.
2. **Maintenance load would balloon** as Phase 2 added ~250 additional packages on the path to a desktop equivalent that Open Robotics is about to ship anyway. Cancelling Phase 2 saves an estimated 1 day/week of steady-state maintenance.

## Consequences

- Reduces this repo's ambitions but increases its honesty.
- Decouples this repo from the Fedora Robotics SIG's main-repo effort, they were always on a different timeline; the official Lyrical packages from Open Robotics now establish the "real" path that both efforts ultimately defer to.
- README, CLAUDE.md, SCOPE.md, RELATED-WORK.md, CITATION.cff, COPR description, GitHub description, CHANGELOG: all updated in the same change-window as this ADR.
- ADR 0001 (minimal subset scope) and ADR 0006 (full desktop as eventual scope) carry retroactive notes pointing here. They are not deleted because they explain the historical reasoning.
