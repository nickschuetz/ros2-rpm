# Driver for the ros2-rpm pipeline.
#
# Most heavy lifting is delegated to scripts/ — this Makefile is the
# glue that ties them together and the canonical entry-point for both
# local development and CI.

.PHONY: help manifest-fetch specs srpms build-mock copr-upload lint sbom clean

DISTRO          ?= jazzy
CHROOT          ?= fedora-44-x86_64
COPR_PROJECT    ?= hellaenergy/ros2
SPEC_DIR        := specs
SRPM_DIR        := SRPMS
BUILD_DIR       := build

help:
	@echo "Targets:"
	@echo "  manifest-fetch   Pull fresh upstream pins from rosdistro/$(DISTRO) into manifest.yaml"
	@echo "  specs            Generate spec files from manifest.yaml into $(SPEC_DIR)/"
	@echo "  srpms            Build SRPMs from $(SPEC_DIR)/ into $(SRPM_DIR)/"
	@echo "  build-mock       Build SRPMs locally via mock (override CHROOT=...)"
	@echo "  copr-upload      Upload SRPMs to COPR project $(COPR_PROJECT)"
	@echo "  lint             Run rpmlint and forbidden-pattern checks on specs"
	@echo "  sbom             Generate CycloneDX SBOMs for built RPMs"
	@echo "  clean            Remove generated specs, SRPMs, and build artifacts"

manifest-fetch:
	@scripts/manifest-fetch.sh $(DISTRO)

specs:
	@scripts/generate-specs.sh $(SPEC_DIR)

srpms: specs
	@mkdir -p $(SRPM_DIR)
	@scripts/build-srpm.sh $(SPEC_DIR) $(SRPM_DIR)

build-mock: srpms
	@mkdir -p $(BUILD_DIR)
	@for srpm in $(SRPM_DIR)/*.src.rpm; do \
		mock -r $(CHROOT) --resultdir=$(BUILD_DIR)/$(CHROOT) "$$srpm" || exit 1; \
	done

copr-upload: srpms
	@for srpm in $(SRPM_DIR)/*.src.rpm; do \
		copr-cli build $(COPR_PROJECT) "$$srpm" || exit 1; \
	done

lint:
	@if compgen -G "$(SPEC_DIR)/*.spec" > /dev/null; then \
		rpmlint $(SPEC_DIR)/*.spec; \
	else \
		echo "No specs to lint."; \
	fi

sbom:
	@scripts/sbom.sh $(BUILD_DIR)/$(CHROOT)

clean:
	rm -rf $(SPEC_DIR)/generated/ $(SRPM_DIR) $(BUILD_DIR) sbom/
