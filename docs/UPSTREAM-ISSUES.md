# Upstream issues we're watching

A live tracking list of upstream issues and PRs in projects this COPR depends on. When something blocks Phase 1 / Phase 2 work and the right fix lives outside this repo, it gets recorded here with a link, the package(s) it gates, and the current status.

The list is checked manually before each Phase milestone, and we'll add a CI workflow to scan it nightly once the COPR has steady-state maintenance churn.

## Open

### `rviz_ogre_vendor` fails on Fedora 44 / CMake 4.x

- **Project**: [`ros2/rviz`](https://github.com/ros2/rviz)
- **Issue**: [#1637](https://github.com/ros2/rviz/issues/1637) (opened 2025-12-04 by @zumbi)
- **PR with fix**: [#1708](https://github.com/ros2/rviz/pull/1708) (opened by @ahcorde, awaiting merge from @mjcarroll)
- **Our comment**: [#1708 comment](https://github.com/ros2/rviz/pull/1708#issuecomment-4408710231) (confirmed Fedora 44 reproduction, +1'd the merge)
- **Blocks**: P-4 rviz2 chain in this COPR (`rviz_ogre_vendor` is the first vendor build in the rviz2 chain).
- **What lands when fixed**: `rviz_ogre_vendor` builds cleanly under CMake 4.x by adding `-DCMAKE_POLICY_VERSION_MINIMUM=3.20` to the inner ExternalProject's CMAKE_ARGS. After the next `release/jazzy/rviz_ogre_vendor/...` bloom tag, this COPR can resume P-4.

### `rviz_assimp_vendor` fails on Fedora 44 / GCC 15.1.1 (`-Werror=unused-but-set-variable`)

- **Project**: [`ros2/rviz`](https://github.com/ros2/rviz)
- **Issue we filed**: [#1730](https://github.com/ros2/rviz/issues/1730) (filed 2026-05-08 by @nickschuetz)
- **Blocks**: P-4 rviz2 chain in this COPR (`rviz_assimp_vendor` is the second vendor build).
- **Workaround proposed in the issue**: extend `ASSIMP_CXX_FLAGS` in `rviz_assimp_vendor/CMakeLists.txt` to include `-Wno-error=unused-but-set-variable` (and defensively `-Wno-error=array-bounds` and `-Wno-error=dangling-reference`). Real upstream fix belongs in [`assimp/assimp`](https://github.com/assimp/assimp): drop the dead `qu` variable in `code/AssetLib/MS3D/MS3DLoader.cpp:639`, or stop unconditionally adding `-Werror`.
- **Status**: awaiting maintainer response on whether they want a PR with the proposed approach or prefer a different fix.

## Closed (kept for history)

_None yet._

## Maintenance

- **When a blocker is fixed upstream**: move the entry to "Closed" with the close date and the bloom-release tag where the fix landed.
- **When a new blocker shows up**: add it under "Open" before deferring the work in CHANGELOG. Don't bury upstream blockers in spec comments; they belong here.
- **What goes in this file vs `CHANGELOG.md`**: this file lists the live upstream surface we're tracking. CHANGELOG records what we shipped and when. They cross-reference each other.
- **What goes in this file vs `docs/SCOPE.md`**: SCOPE describes intended scope and side effects of deferrals (user-facing). UPSTREAM-ISSUES.md is the maintainer's punch list for unblocking those deferrals (contributor-facing).

## Automation

- [`scripts/check-upstream-issues.py`](../scripts/check-upstream-issues.py) reads this file's "Open" section, queries the GitHub API for each linked issue / PR, and reports any that have closed.
- [`.github/workflows/upstream-issues.yml`](../.github/workflows/upstream-issues.yml) runs that script nightly at 08:00 UTC. When at least one tracked item has closed, the workflow opens (or updates) a single canonical tracking issue with label `upstream-tracker,maintenance` so the deferral can be revisited.
