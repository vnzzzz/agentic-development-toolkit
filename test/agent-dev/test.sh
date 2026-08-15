#!/usr/bin/env bash
set -Eeuo pipefail

claude --version | grep -F '2.1.227'
codex --version | grep -F '0.147.0'
gh --version | head -n 1
git --version
jq --version
make --version | head -n 1
shellcheck --version | head -n 2
unzip -v | head -n 1
zip -v | head -n 2

[[ "${CLAUDE_CONFIG_DIR:-}" == "/var/lib/agentic-dev/claude" ]]
[[ "${CODEX_HOME:-}" == "/var/lib/agentic-dev/codex" ]]
[[ "${GH_CONFIG_DIR:-}" == "/var/lib/agentic-dev/gh" ]]
[[ -x /usr/local/share/agentic-dev/post-create.sh ]]

printf 'agent-dev Feature validation passed.\n'
