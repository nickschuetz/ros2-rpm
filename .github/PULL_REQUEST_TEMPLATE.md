## What

<!-- One or two sentences describing the change. -->

## Why

<!-- Reason for the change. Link issues / ADRs. -->

## Checklist

- [ ] If this PR adds, updates, or removes a packaged component, `manifest.yaml` is updated with new pins.
- [ ] If this PR adds a non-permissive (EPL/LGPL/MPL) package, an ADR has been added under `docs/adr/` and README + CITATION.cff are updated per ADR 0003.
- [ ] If this PR adds chroots, the readiness checklist in `CLAUDE.md` (Distro lifecycle policy) has been satisfied and a tracking issue exists.
- [ ] Spec files use SPDX license expressions, `%autosetup`, `%cmake`/`%cmake_build`/`%cmake_install`, `%pyproject_*` (where applicable), and `%check`. No `Group:`, `BuildRoot:`, `%clean`, `%defattr`, `%py3_*`, hardcoded `%{__cmake}`, or legacy license shortnames.
- [ ] CI build is green on all 8 chroot/arch pairs.
- [ ] `rpmlint` clean on changed specs (or new warnings explicitly justified).
- [ ] `%check` exercises upstream tests; not skipped.
