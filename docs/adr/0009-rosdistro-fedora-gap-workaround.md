# ADR 0009: Local rosdep override for the rosdistro Fedora-gap

- **Status**: Accepted
- **Date**: 2026-05-08

## Context

When a downstream packager builds a ROS 2 package that depends on another ROS package (e.g., `builtin_interfaces` depends on `rosidl_core_generators`), `bloom-generate rosrpm` invokes `rosdep` to translate the ROS package name into the system package name for the target OS.

For OSes listed in `rosdistro/jazzy/distribution.yaml`'s `release_platforms`, rosdep auto-generates these mappings. **Fedora is not in that list.** Consequence:

- `rosdep resolve ament_package --os=fedora:44 --rosdistro=jazzy` returns "no rosdep rule".
- `bloom-generate rosrpm` then prompts the user interactively to confirm the missing mapping. In a non-TTY environment (CI, scripted builds, generator pipeline) this fails with `(25, 'Inappropriate ioctl for device')`.

## Decision

Maintain `build/local-rosdep-jazzy.yaml` as a local rosdep override file mapping every ROS package we build to its `ros-jazzy-<dashed-name>` Fedora RPM. Loaded into rosdep via `/etc/ros/rosdep/sources.list.d/30-local-ros2-rpm.list`.

```yaml
ament_package:
  fedora:
    dnf:
      packages: [ros-jazzy-ament-package]
ament_cmake_core:
  fedora:
    dnf:
      packages: [ros-jazzy-ament-cmake-core]
# ... one entry per package ...
```

Every PR that adds a new package to `manifest.yaml` / `packages.yaml` must add a corresponding entry to the local override.

## Why not fix it upstream

- Adding Fedora to `rosdistro/jazzy/distribution.yaml`'s `release_platforms` would require Open Robotics to commit to running upstream Fedora RPM builds in their CI, a decision they have repeatedly declined for resource reasons.
- Even if accepted upstream, the change wouldn't reach our builds for weeks (rosdistro has a controlled release cadence).
- The override is ~30 lines of YAML per package, trivial to maintain.
- A long-term Phase 3 effort (Fedora main repo inclusion, see [ADR 0007](0007-install-location-opt-ros-jazzy.md)) would naturally include upstreaming this metadata.

## Consequences

**Positive**:
- bloom-generate runs cleanly in our pipeline without TTY prompts.
- rosdep correctly resolves cross-package deps to our `ros-jazzy-*` RPM names.
- No upstream patches required.

**Negative**:
- Each new package requires a manual override entry (one-line, trivial).
- Out-of-band tooling that reaches for rosdep without our override file (e.g., a fresh checkout running `bloom-generate` directly) won't have the mappings. Document the override file's role prominently in the README.

**Neutral**:
- The override file is the single source of truth for our package naming. When a new package's spec is generated, the rosdep override entry MUST exist or BuildRequires for that name will be missing from the generated spec.

## Process

When adding a new package N:

1. Add stanza to `scripts/packages.yaml` with `source_url`, `source_dir`, etc.
2. Add stanza to `build/local-rosdep-jazzy.yaml` mapping `N` → `ros-jazzy-<dashed-N>`.
3. Run `rosdep update` to refresh the cache.
4. Run `scripts/publish.sh N`, generator now resolves N's deps correctly.

The lint workflow does not currently enforce step 2 (no automated check that every `packages.yaml` entry has a matching rosdep override). Future improvement: add a CI check in `.github/workflows/lint.yml` that diffs the two files and fails on mismatch.
