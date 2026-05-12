# Maintenance

Reference for the scripts and CI workflows that keep `hellaenergy/ros2` healthy between manual COPR builds. User-facing install instructions live in the [README](../README.md); this document is for the person bumping versions, reviewing PRs, and reading nightly drift reports.

## Local scripts

| Script | Purpose |
|---|---|
| [`scripts/bump.py`](../scripts/bump.py) | Fast-path version bumps. Edits `Version:`, `Source0:`, and prepends a `%changelog` entry to match `rosdistro/jazzy/distribution.yaml`. |
| [`scripts/verify-specs.py`](../scripts/verify-specs.py) | Audits every spec against the standards in CLAUDE.md / ADR 0005. Forbidden patterns, SPDX-valid License: fields, no em-dashes, patches/ DEP-3 metadata. |
| [`scripts/validate-sbom.py`](../scripts/validate-sbom.py) | CycloneDX shape validator. Asserts `bomFormat == "CycloneDX"`, `specVersion` is a string, `components` is a list. |
| [`scripts/check-upstream.py`](../scripts/check-upstream.py) | Compares local spec versions against `rosdistro/jazzy/distribution.yaml`. Reports drift in Markdown or JSON. |
| [`scripts/check-upstream-issues.py`](../scripts/check-upstream-issues.py) | Reads the Open section of [`UPSTREAM-ISSUES.md`](UPSTREAM-ISSUES.md) and queries the GitHub API for each tracked item. Reports closures. |
| [`scripts/smoke-test.sh`](../scripts/smoke-test.sh) | End-to-end install validation. 22 checks covering setup.bash, rclpy, rclcpp build, ros2cli, demos, gazebo_msgs. |
| [`scripts/build-one.sh`](../scripts/build-one.sh) | Local-only build of a single spec end-to-end (SRPM + mock). |
| [`scripts/publish.sh`](../scripts/publish.sh) | Generate, build, validate, and publish one package end-to-end. |
| [`scripts/sbom.sh`](../scripts/sbom.sh) | Generate (and validate) CycloneDX SBOMs from a mock result dir. |
| [`scripts/generate-spec.py`](../scripts/generate-spec.py) | Render an RPM spec from a ROS 2 package source. Used when a new package enters the build set. |
| [`scripts/postprocess-spec.sh`](../scripts/postprocess-spec.sh) | Apply our transformations to a `bloom-generate rosrpm` output. |
| [`scripts/manifest-fetch.sh`](../scripts/manifest-fetch.sh) | Refresh `manifest.yaml` pins from upstream rosdistro. |

## CI workflows

| Workflow | Trigger | What it does |
|---|---|---|
| [`lint.yml`](../.github/workflows/lint.yml) | push, PR | rpmlint, license-check (legacy SPDX shortname rejection), forbidden-patterns (grep), verify-specs (full audit), sbom-validate (CycloneDX self-test). |
| [`spec-dry-build.yml`](../.github/workflows/spec-dry-build.yml) | PR (only when specs/ changes) | For up to 3 changed specs: rpmspec parse, spectool fetch, rpmbuild SRPM, dnf builddep --assumeno against Fedora 44 + hellaenergy/ros2. Catches Source0 / BR breakage before the COPR build cycle. |
| [`build.yml`](../.github/workflows/build.yml) | push, PR | Matrix-build dry-run on all 6 chroot/arch pairs. |
| [`smoke-test.yml`](../.github/workflows/smoke-test.yml) | push, PR, daily 06:00 UTC | Installs `ros-base` + extras on a fresh Fedora 44 container and runs `scripts/smoke-test.sh -v`. |
| [`drift-check.yml`](../.github/workflows/drift-check.yml) | weekly (Sunday 08:00 UTC), push to relevant paths | Runs `scripts/check-upstream.py`. Opens / updates a single sticky issue labeled `upstream-drift` when packages are behind; closes it with a "fully caught up" comment when drift returns to zero. |
| [`upstream-issues.yml`](../.github/workflows/upstream-issues.yml) | nightly 08:00 UTC | Runs `scripts/check-upstream-issues.py`. Posts to a sticky issue labeled `upstream-tracker` when at least one tracked item has closed. |

Both `drift-check` and `upstream-issues` self-bootstrap their labels on first run, so a fresh fork or rebuild needs no manual setup.

## Routine workflows

### Bump a single drifted package

```bash
# See what the weekly drift workflow saw:
python3 scripts/check-upstream.py

# Bump one:
scripts/bump.py rclcpp                  # uses upstream version
scripts/bump.py rclcpp 28.1.19          # explicit pin
scripts/bump.py --dry-run rclcpp        # preview the diff first
scripts/bump.py --commit rclcpp         # bump + git commit

# Drain the entire drift report:
scripts/bump.py --all-behind --commit
```

`bump.py` runs `verify-specs.py` on every modified spec as a guard. If verification fails, review the diff before committing.

### Add a new package

1. Add an entry to [`scripts/packages.yaml`](../scripts/packages.yaml) with `source_url`, `source_dir`, optional `build_subdir`.
2. Download the source: bloom-release tarball, then run `scripts/generate-spec.py <source-dir>` to emit a draft spec.
3. Hand-finish the `%files` section against the actual install layout (`mock --shell` if you need to introspect).
4. `scripts/build-one.sh ros-jazzy-<pkg>` to local-build, then `copr-cli build hellaenergy/ros2 build/SRPMS/...` for the matrix build.
5. Update [`SCOPE.md`](SCOPE.md), [`build-order.md`](build-order.md), and [`CHANGELOG.md`](../CHANGELOG.md).

### Carry an upstream patch locally

Used when an upstream blocker is days-or-more from merging and the deferral has become blocking. See [`specs/patches/README.md`](../specs/patches/README.md) for the file naming convention and required DEP-3 header set. The verifier rejects `Patch%N:` lines that point at non-existent files or files missing DEP-3 metadata.

When the upstream PR finally merges:
1. The nightly `upstream-issues` workflow opens a sticky tracker issue.
2. Drop the `Patch%N:` line from the spec, delete the patch file, re-pin `packages.yaml`.
3. Update `UPSTREAM-ISSUES.md` (move entry from Open to Closed) and `CHANGELOG.md`.
4. Re-run `scripts/smoke-test.sh`.

### Investigate a failed CI run

| Failure | Likely cause | Where to look |
|---|---|---|
| `verify-specs` fails | New forbidden pattern or em-dash crept in | Re-run locally: `python3 scripts/verify-specs.py` |
| `spec-dry-build` fails on `dnf builddep` | New BR doesn't resolve on Fedora 44 + hellaenergy/ros2 | Either the BR needs packaging too, or the rosdep mapping is wrong (see [ADR 0009](adr/0009-rosdistro-fedora-gap-workaround.md)) |
| `spec-dry-build` fails on `spectool -g` | Source0 URL is broken (typo, upstream tag deleted, etc.) | Check the bloom-release tag exists |
| `smoke-test` fails after `dnf install` | Either a packaging regression or upstream Fedora broke a dep | Run smoke-test locally with `-v` to see which check failed |
| `sbom-validate` fails | syft output shape changed (rare) | Inspect the failing fixture; `validate-sbom.py` has both positive and negative self-tests in CI |

### Local sanity before pushing

```bash
python3 scripts/verify-specs.py
python3 scripts/check-upstream.py | head -10
bash scripts/smoke-test.sh                 # ~20s, requires installed ros-base
```

## Watching the project's pulse

- **Issues labeled `upstream-drift`**: weekly drift reports. Decide which to bump.
- **Issues labeled `upstream-tracker`**: a tracked upstream issue / PR closed; deferral can be revisited.
- **`docs/UPSTREAM-ISSUES.md`**: the manually-curated source of truth for what the workflows watch. Edit this when you start tracking something new or want to stop tracking something resolved.

## Documentation sync rule (mandatory)

Per [CLAUDE.md](../CLAUDE.md) (the project's source-of-truth instructions), when README, project scope, supported chroots, or the disclaimer text change, **the COPR description and instructions must be updated in the same change-window** via:

```bash
copr-cli modify --description '...' --instructions '...' hellaenergy/ros2
gh repo edit nickschuetz/ros2-rpm --description '...'
```

PRs that change the README's user-visible copy without also updating both remote surfaces should be rejected. The COPR `Homepage` and `Contact` fields are not exposed by `copr-cli`; set those via the COPR web UI or the API (`copr.v3.Client.project_proxy.edit(homepage=..., contact=...)`).

## Project rules at a glance

- **No em-dashes** anywhere in project prose (verifier enforces in specs; sed-replace if they sneak into docs/scripts).
- **No AI / Claude attribution** in any committed artifact (no `Co-Authored-By` lines, no "generated by" footers, no AI-mention comments).
- **No bundled forks of system libs** Fedora ships.
- **Per-spec License: must be SPDX-valid** against the list in `scripts/verify-specs.py`'s `APPROVED_SPDX_TOKENS`. Adding a new token requires an ADR.
- **`-devel` subpackage mandate** for any package shipping headers / CMake config / pkg-config (currently a verifier warning; `--devel-strict` promotes to fatal once the retrofit is done).
