# ADR 0002: Separate `hellaenergy/ros2` COPR rather than bundling into `hellaenergy/o3de-dependencies`

- **Status**: Accepted
- **Date**: 2026-05-07

## Context

[`hellaenergy/o3de-dependencies`](https://copr.fedorainfracloud.org/coprs/hellaenergy/o3de-dependencies) is the runtime-deps COPR for [`o3de-rpm`](https://github.com/nickschuetz/o3de-rpm). The natural question: should ROS 2 packages live inside that COPR, or in a separate `hellaenergy/ros2` COPR listed as an External Repository?

## Decision

**Separate `hellaenergy/ros2` COPR.** `hellaenergy/o3de-dependencies` declares it as an External Repository; users enabling the o3de-deps COPR transparently pick up ROS 2 packages.

## Consequences

**Positive**:
- Independent release cadences: ROS 2 distros (annual LTS) move on a different timeline than Fedora (6 months) and O3DE (its own cycle). Decoupled COPRs avoid forced-rebuild storms.
- Reusability: Fedora users wanting ROS 2 without O3DE can enable just `hellaenergy/ros2`. They are not forced to pull O3DE-specific runtime deps.
- License hygiene: the aggregate `License:` field on `hellaenergy/ros2` stays scoped to the ROS 2 package set, easing SBOM generation and downstream audit.
- Scope hygiene: `hellaenergy/o3de-dependencies` keeps its identity as "things the O3DE engine specifically needs that aren't already in Fedora/RPMFusion."
- Distinct contributor on-ramps: ROS 2 packagers from the Fedora Robotics SIG or community can target `hellaenergy/ros2` without learning the O3DE side.

**Negative**:
- Two COPR projects to maintain instead of one.
- Users who only learn about `o3de-dependencies` need the External Repository link to reach ROS 2 — handled by COPR's metadata.

**Neutral**:
- The user experience is identical: `dnf copr enable hellaenergy/o3de-dependencies` automatically also enables `hellaenergy/ros2` once we wire the External Repositories field.
