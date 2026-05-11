# Local patches carried in this COPR

When upstream is broken on Fedora and we don't want to wait for the fix to land
in a new bloom-release tag, the patch lives here. Each patch is referenced by
its containing spec via `Patch%N:` and applied at `%autosetup -p1` time.

Carrying a patch is an explicit trust-signal decision (we ship something
different from what upstream packages today). Use sparingly. Prefer waiting
for upstream merge unless waiting is materially blocking work. Every patch
carried here should also be tracked in `docs/UPSTREAM-ISSUES.md` with the
upstream issue/PR link.

## File naming

```
specs/patches/<package>/NNNN-short-kebab-name.patch
```

- `<package>`: the upstream package name (no `ros-jazzy-` prefix).
- `NNNN`: 4-digit sequence, starting at `0001`. Sequence is per-package.
- `short-kebab-name`: 2-4 words describing the intent.

Example: `specs/patches/rviz_ogre_vendor/0001-cmake-policy-minimum-3.20.patch`

## Required header (DEP-3 format)

Every patch file MUST begin with a DEP-3 header block before the diff. Four
fields are required and validated by `scripts/verify-specs.py`:

```
Description: <one-line summary>
 <optional multi-line elaboration, indented by one space>
Origin: <upstream PR URL, or "backport" / "vendor-specific">
Forwarded: <upstream PR URL, "no" with reason, or "not-needed" with reason>
Last-Update: <YYYY-MM-DD when the patch was last refreshed against upstream>
Bug: <optional upstream issue URL>
---
<unified diff body>
```

The four required headers (`Description`, `Origin`, `Forwarded`, `Last-Update`)
make the patch self-documenting: anyone reading the file knows what it does,
where it came from, whether upstream knows about it, and how stale it is.

`verify-specs.py` will reject any spec whose `Patch%N:` references a file
missing one of these headers. This is enforced in CI.

## When upstream merges the fix

1. Check the upstream PR/issue closed (the nightly `upstream-issues` workflow
   posts a sticky issue when this happens).
2. Drop the `Patch%N:` line from the spec.
3. Delete the patch file from `specs/patches/<package>/`.
4. Re-pin `scripts/packages.yaml` to the upstream merge tag (or the next
   bloom-release that contains it).
5. Update `docs/UPSTREAM-ISSUES.md`: move the entry from Open to Closed with
   the close date.
6. Add a `%changelog` entry to the spec: "Dropped local patch NNNN; upstream
   merged in <tag>."
7. Re-run `scripts/smoke-test.sh` to confirm.

## Currently carried

_None._

When the first patch lands, list it here as: `<package>` / `NNNN-name.patch` /
upstream PR URL / date carried from.
