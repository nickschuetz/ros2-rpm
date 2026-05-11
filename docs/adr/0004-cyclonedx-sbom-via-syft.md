# ADR 0004: CycloneDX SBOM via `syft` in `%install`

- **Status**: Accepted
- **Date**: 2026-05-07

## Context

The user wants per-build SBOMs for downstream supply-chain visibility. Two format candidates: CycloneDX and SPDX. Generation tooling and timing are also open.

RPM 6.0 (shipped in Fedora 43+) lays groundwork for built-in SBOM macros. Fedora 44 does not yet ship a `%generate_sbom` macro. Stream 10 ships RPM 4.19, well below the SBOM-macro work.

## Decision

- **Format**: CycloneDX. Reasons: native JSON output, well-supported tooling (`syft`, `cyclonedx-cli`), strong adoption in the OWASP ecosystem the user references.
- **Tool**: `syft` invoked in `%install` against the staged `%{buildroot}`.
- **Output path**: `%{_datadir}/doc/%{name}/sbom.cdx.json` per package, shipped as `%doc`.
- **Migration**: replace with the native `%generate_sbom` macro the moment Fedora ships a stable one.

## Consequences

**Positive**:
- Per-package SBOM that lives alongside the binary, queryable post-install.
- Tooling exists today on Fedora 44 and Stream 10 (both can `dnf install syft` from upstream).
- CycloneDX is the format most CVE-correlation tooling expects in 2026.

**Negative**:
- `syft` is an extra build-time dependency in every chroot; `BuildRequires: syft` everywhere.
- SBOM lives in the package not in the build manifest, slightly harder for aggregate auditing than a build-time export. Acceptable trade-off until Fedora's macro lands.

**Neutral**:
- Path is portable: when the native macro arrives, the spec change is local (drop the explicit `syft` invocation, drop the `BuildRequires: syft`, add `%generate_sbom`).
