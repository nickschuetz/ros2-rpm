# ADR 0007: Install to `/opt/ros/jazzy` for COPR; defer FHS layout to a separate Phase 3 effort

- **Status**: Accepted
- **Date**: 2026-05-07

## Context

Two install-layout conventions are in tension:

- **Upstream ROS 2**: installs under `/opt/ros/$DISTRO`. Used by `bloom-rpm`, every Debian release of ROS 2, every community Fedora COPR (`tavie/ros2`, `techtasie/ros2`), and the install instructions every ROS 2 user has internalized. Supports clean side-by-side multi-distro installs.
- **Fedora main-repo policy**: [packaging guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_filesystem_layout) forbid `/opt`. Apps must follow FHS, `/usr/lib64`, `/usr/include`, `/usr/share`. COPRs are exempt as third-party repositories.

The user's stated long-term goal includes Fedora main inclusion. The question is whether to bend the COPR's layout toward FHS now or stay on `/opt`.

## Decision

**Two-track approach.**

1. **COPR uses `/opt/ros/jazzy`.** Spec files use `%global ros_install_prefix /opt/ros/%{ros_distro}` and reference `%{ros_install_prefix}/...` everywhere, the layout is centralized to a single macro per spec.
2. **Fedora main inclusion is a separate, longer-term Phase 3 effort**, not pursued by carrying FHS-rebasing patches in this repo. The honest path is upstream-first: get ROS 2 itself to honor `CMAKE_INSTALL_PREFIX` (REP-class proposal + CMake config refactor), then submit FHS-compliant packages to Fedora.
3. **Reject** "patch every spec in this repo to install under `/usr/lib64/ros2-jazzy/`." This would diverge from every other ROS 2 distro packaging, balloon maintenance, and almost certainly fail the "minimal upstream divergence" review test in Fedora itself.

## Consequences

**Positive**:
- Matches user expectations from Ubuntu / Debian / existing community Fedora COPRs.
- `bloom-rpm` works without divergent patches; CI complexity stays bounded.
- Side-by-side distro installs (Jazzy + Lyrical) are clean, distinct `/opt/ros/<distro>` trees.
- Single macro change per spec if/when Phase 3 begins; per-conditional handling is straightforward.

**Negative**:
- Blocks Fedora main inclusion under current Fedora rules. The `/opt` exemption only applies to COPR.
- Phase 3 may not happen for years. Be honest with users that "in Fedora main" is aspirational.

**Neutral**:
- Fedora's `redhat-rpm-config` hardening flags apply path-independently, `/opt` does not weaken security posture.
- This decision aligns with how `tavie/ros2`, `techtasie/ros2`, and every Debian-based ROS 2 distribution is laid out.

## Phase 3 readiness signals (informational)

These would make Phase 3 viable; they are not gates we control.

- Upstream ROS 2 accepts a REP enabling FHS-style installs (CMake configs honor `CMAKE_INSTALL_PREFIX`, setup scripts work without hardcoded `/opt/ros/...` paths).
- A maintained reference Fedora package set (Fedora SIG, this repo's Phase 3 branch, or community) demonstrates the FHS layout works end-to-end with the upstream-supported install machinery.
- Fedora's review queue has bandwidth for ROS 2 (several hundred packages would need individual reviews).

When all three hold, open an ADR proposing a Phase 3 branch with an alternative install prefix.
