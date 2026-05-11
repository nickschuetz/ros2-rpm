# Security

> **Development-only COPR.** Per [ADR 0010](adr/0010-project-pivot-to-development-only.md), this is not a production-grade package set. For production deployments with a vendor-supported security SLA, use Open Robotics's official Fedora packages (starting with Lyrical Luth) when those land. Do not deploy this COPR to any environment where you need timely CVE response.

## Reporting a vulnerability

Email **security@hellaenergy.studio** with details. Please do not open a public issue for unpatched vulnerabilities.

This is a best-effort development project, there is no committed SLA. Triage cadence is approximately:
- **48 hours** for critical CVEs (CVSS ≥ 9.0): acknowledged.
- **7 days** for high-severity CVEs (CVSS 7.0–8.9): acknowledged.
- **30 days** for medium / low: acknowledged.

A fix may follow if the maintainer has bandwidth. If you need guaranteed turnaround, you are on the wrong package set, see Open Robotics's official Fedora packages.

## Supported versions

Each ROS 2 distro is supported in this COPR while upstream Open Robotics supports it. Past upstream EOL, the COPR's posture is **undecided**, could be sunset, frozen as an archive, or extended on dev-only terms. Decision deferred to a follow-up ADR closer to the date; see [README → "Long-term posture"](../README.md#long-term-posture).

| ROS 2 distro | Upstream EOL | Our support |
|---|---|---|
| Jazzy Jalisco | May 2029 | Active |
| Lyrical Luth | (TBD per REP-2000) | Pending, see tracking issue |

## What this COPR claims about security

- Built with Fedora's hardening flags inherited from `redhat-rpm-config`: `_FORTIFY_SOURCE=3`, full RELRO, PIE, stack-clash protection, control-flow integrity.
- Dependencies link against system libraries provided by Fedora / CentOS Stream, no vendored copies of `tinyxml2`, `console_bridge`, `libyaml`, `spdlog`, `pybind11`, etc. CVEs in those deps flow to users via the OS's normal patch pipeline.
- Source pins are recorded per-package in `manifest.yaml` (commit SHA or git tag, never a moving branch). Builds are reproducible-build-friendly via `source_date_epoch_from_changelog`.
- A CycloneDX SBOM is generated at build time (via `syft` in `%install`) and shipped at `%{_datadir}/doc/<package>/sbom.cdx.json`. Subscribed CVE feeds:
  - `ros-security@lists.ros.org`
  - GitHub Security Advisories for every upstream repo in `manifest.yaml`
  - Fedora `security-announce` for transitive system dep CVEs

## What this COPR does NOT claim

- **Production readiness.** Per ADR 0010, this is a development-only sandbox.
- **Vendor support, SLA, or guaranteed CVE turnaround.** Use Open Robotics's official Fedora packages for that.
- **DISA STIG / CERT / OWASP / DSPM compliance.** None of those frameworks describe RPM packaging meaningfully, and this COPR makes no posture claim against any of them.

The CentOS Stream 10 chroots are convenient build targets for development testing, **not** a production-deployment pitch.

## Watchlist

These are the upstream sources whose security feeds we monitor. Any addition to `manifest.yaml` requires adding the corresponding feed here.

| Source | Feed |
|---|---|
| ROS 2 core | `ros-security@lists.ros.org`, GHSA |
| Fast DDS | https://github.com/eProsima/Fast-DDS/security/advisories |
| Fast CDR | https://github.com/eProsima/Fast-CDR/security/advisories |
| foonathan_memory | https://github.com/foonathan/memory/security/advisories |
| Fedora | `security-announce@lists.fedoraproject.org` |
| CentOS Stream | https://access.redhat.com/security/data |
