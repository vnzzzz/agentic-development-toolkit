DEVCONTAINER_CLI_VERSION ?= 0.88.0
BASE_IMAGE ?= mcr.microsoft.com/devcontainers/base:bookworm

.PHONY: validate test

validate:
	jq -e . src/agent-dev/devcontainer-feature.json >/dev/null
	bash -n src/agent-dev/install.sh src/agent-dev/post-create.sh test/agent-dev/test.sh
	shellcheck src/agent-dev/install.sh src/agent-dev/post-create.sh test/agent-dev/test.sh
	test "$$(jq -r '.dependencies["@anthropic-ai/claude-code"]' package.json)" = "$$(jq -r '.options.claudeCodeVersion.default' src/agent-dev/devcontainer-feature.json)"
	test "$$(jq -r '.dependencies["@openai/codex"]' package.json)" = "$$(jq -r '.options.codexVersion.default' src/agent-dev/devcontainer-feature.json)"

test: validate
	devcontainer features test -f agent-dev -i $(BASE_IMAGE) .
