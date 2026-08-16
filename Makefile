BASE_IMAGE ?= mcr.microsoft.com/devcontainers/base:bookworm

SHELL_SCRIPTS := \
	src/agent-dev/install.sh \
	src/agent-dev/post-create.sh \
	scripts/check-release-version.sh \
	test/agent-dev/test.sh \
	test/release-version-check.sh

.PHONY: validate test

validate:
	jq -e . src/agent-dev/devcontainer-feature.json >/dev/null
	bash -n $(SHELL_SCRIPTS)
	shellcheck $(SHELL_SCRIPTS)
	bash test/release-version-check.sh

test: validate
	devcontainer features test -f agent-dev -i $(BASE_IMAGE) .
