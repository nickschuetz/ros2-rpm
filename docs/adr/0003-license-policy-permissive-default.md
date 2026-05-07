# ADR 0003: License policy — permissive default, opt-in non-permissive standalones

- **Status**: Accepted
- **Date**: 2026-05-07

## Context

The minimal subset (ADR 0001) is `Apache-2.0 AND BSD-3-Clause`. Some legitimate ROS 2 use cases want non-permissive packages — `rmw_cyclonedds_cpp` (transitively EPL-2.0 via Cyclone DDS) for QoS or interop reasons; `rviz2` (transitively LGPL-3.0 via Qt) for visualization. The question is how (or whether) to admit them.

Options considered:
- (a) Strict refusal — never include non-permissive packages.
- (b) Open inclusion via a single fat metapackage — silently expands the License aggregate.
- (c) Strict permissive default in metapackages, opt-in standalones for non-permissive.
- (d) Two separate COPRs (`-core` and `-extras`).

## Decision

**Option (c).** Default metapackages (`ros-jazzy-ros-core`, `ros-jazzy-ros-base`) ship only Apache-2.0 / BSD-3-Clause content. Their `Requires:` lines never name a non-permissive package. The aggregate License field stays permissive and never expands.

Non-permissive packages with compatible licenses (EPL-2.0, LGPL-3.0, MPL-2.0) may be added to the COPR as **standalone packages** users install explicitly. Each spec accurately declares its license. Adding any such package requires a follow-up ADR documenting:

- Real demand (not speculative).
- Specific license obligations imposed on downstream consumers.
- Verification that no Apache-2.0/BSD-3 package gains a transitive non-permissive dep as a side effect.
- README and CITATION.cff updates.

Initial release ships permissive-only.

## Consequences

**Positive**:
- A single COPR (no fragmentation between `-core` and `-extras`).
- `dnf install ros-jazzy-ros-base` cannot accidentally pull in copyleft.
- Downstream consumers (including O3DE) face zero new license obligations from default install.
- Non-permissive use cases remain reachable via explicit `dnf install <package>`.

**Negative**:
- Future contributors must understand the metapackage / standalone distinction. Documented in `docs/SCOPE.md` and `CLAUDE.md`.
- README must explain the split prominently; failure to do so risks user confusion when they discover non-permissive packages exist in the COPR.

**Neutral**:
- The discipline is the same as the minimal-subset principle (ADR 0001) applied to license scope rather than dep count.
