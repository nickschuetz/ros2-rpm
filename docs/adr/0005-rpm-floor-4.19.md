# ADR 0005: RPM 4.19 portability floor; opportunistic RPM 6.0 features behind guards

- **Status**: Accepted
- **Date**: 2026-05-07

## Context

The user's stated goal: "build with the latest version of RPM that Fedora 44 supports natively, take advantage of all the latest features and spec best practices." Reality:

- Fedora 44 ships **RPM 6.0** (introduced in Fedora 43).
- CentOS Stream 10 ships **RPM 4.19.1.1**.
- The COPR build matrix targets both.

Picking RPM 6.0 features unguarded breaks Stream 10. Refusing all RPM 6.0 features wastes available capability on Fedora.

## Decision

- **Floor**: RPM 4.19. All spec patterns must build unguarded on 4.19+.
- **Opportunistic**: RPM 6.0-only features (`%{span:...}`, `%{xdg:...}`) are permitted only inside `%if 0%{?fedora} >= 43` guards.
- **v6 package format**: do not opt in. F44 still emits v4 packages by default; v4 emission preserves Stream 10 portability.
- **Mandatory modern macros (4.19+)**: SPDX `License:`, `%autosetup -p1`, `%cmake`/`%cmake_build`/`%cmake_install`/`%ctest`, `%pyproject_*` for Python (not `%py3_*`), `%generate_buildrequires`, `%check`, `%license` and `%doc` distinction, `BuildRequires: pkgconfig(...)`.
- **Forbidden patterns** (drop on sight): `Group:`, `BuildRoot:`, `%clean`, `%defattr(...)`, `%setup` + numbered `%patch`, `%py3_build`/`%py3_install`, legacy license shortnames, hardcoded `%{__cmake}`, `%pyproject_buildrequires -w`.

## Consequences

**Positive**:
- One spec source builds on F44/F45/Fxxx + Stream 10 with minimal `%if` clutter.
- Modern, audit-friendly spec patterns throughout.
- Reproducible builds via `source_date_epoch_from_changelog` (default in Fedora).

**Negative**:
- A handful of Fedora-only conveniences require guards.
- Future Stream 10 EOL will simplify this — but that's years away.

**Neutral**:
- This floor matches the broader Fedora packaging community's practice for cross-EL/Fedora specs in 2026.
