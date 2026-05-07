# COPR "Custom" build method entrypoint.
#
# COPR invokes `make srpm outdir=$resultdir` in this directory when a
# build is triggered (web UI, webhook, or `copr-cli build-package`).
# This Makefile is responsible for producing one or more SRPMs in
# $outdir; COPR then schedules per-chroot rebuilds.
#
# Build environment:
#   - Fedora-based mock chroot (the "source build root" — distinct from
#     the per-package build chroots).
#   - $outdir is set by COPR; do not assume.
#   - Network access available during this stage.

PACKAGE ?=

.PHONY: srpm

srpm:
	@if [ -z "$(outdir)" ]; then echo "outdir not set" >&2; exit 1; fi
	@dnf install -y --setopt=install_weak_deps=False \
		git make rpm-build python3-bloom python3-rosdep \
		redhat-rpm-config
	# TODO: real pipeline:
	#   1. cd to repo root (`..` from .copr/).
	#   2. make manifest-fetch    # ensure pins are current
	#   3. make specs PACKAGE=$(PACKAGE)
	#   4. make srpms PACKAGE=$(PACKAGE)
	#   5. cp SRPMS/*.src.rpm $(outdir)/
	@echo "TODO: wire bloom-rpm pipeline. Until then, COPR builds will be no-ops."
	@mkdir -p "$(outdir)"
