# Security

## Reporting a vulnerability

Email **security@hellaenergy.example** with details. _(Replace with a real address before flipping the repo public.)_ Please do not open a public issue for unpatched vulnerabilities.

We will acknowledge receipt within 5 business days and aim to issue a fixed build within:
- **48 hours** for critical CVEs (CVSS ≥ 9.0).
- **7 days** for high-severity CVEs (CVSS 7.0–8.9).
- **30 days** for medium / low.

## Supported versions

Each ROS 2 distro is supported in this COPR while upstream Open Robotics supports it. When upstream EOLs a distro, this COPR drops it within 30 days (see `docs/UPGRADING.md` → "Sunsetting an EOL distro").

| ROS 2 distro | Upstream EOL | Our support |
|---|---|---|
| Jazzy Jalisco | May 2029 | Active |
| Lyrical Luth | (TBD per REP-2000) | Pending — see tracking issue |

## What this COPR claims about security

- Built with Fedora's hardening flags inherited from `redhat-rpm-config`: `_FORTIFY_SOURCE=3`, full RELRO, PIE, stack-clash protection, control-flow integrity.
- Dependencies link against system libraries provided by Fedora / CentOS Stream — no vendored copies of `tinyxml2`, `console_bridge`, `libyaml`, `spdlog`, `pybind11`, etc. CVEs in those deps flow to users via the OS's normal patch pipeline.
- Source pins are recorded per-package in `manifest.yaml` (commit SHA or git tag, never a moving branch). Builds are reproducible-build-friendly via `source_date_epoch_from_changelog`.
- A CycloneDX SBOM is generated at build time (via `syft` in `%install`) and shipped at `%{_datadir}/doc/<package>/sbom.cdx.json`. Subscribed CVE feeds:
  - `ros-security@lists.ros.org`
  - GitHub Security Advisories for every upstream repo in `manifest.yaml`
  - Fedora `security-announce` for transitive system dep CVEs

## What this COPR does NOT claim

- **DISA STIG compliance.** There is no STIG for ROS 2; STIGs target full OS deployments. Users needing a STIG-attested chain should layer this COPR on RHEL 10 with the appropriate RHEL 10 STIG profile applied.
- **CERT, OWASP, or DSPM compliance.** Those frameworks address application code, web-application architecture, and data-security posture respectively — none describes RPM packaging.

For a STIG-adjacent posture, the recommended path is the **CentOS Stream 10** builds from this COPR plus standard RHEL 10 hardening on the host.

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
