#!/usr/bin/env bash
set -Eeuo pipefail

claude --version | grep -F '2.1.227'
codex --version | grep -F '0.147.0'
gh --version >/dev/null
git --version
jq --version
make --version >/dev/null
shellcheck --version >/dev/null
unzip -v >/dev/null
zip -v >/dev/null

[[ "${CLAUDE_CONFIG_DIR:-}" == "/var/lib/agentic-dev/claude" ]]
[[ "${CODEX_HOME:-}" == "/var/lib/agentic-dev/codex" ]]
[[ "${GH_CONFIG_DIR:-}" == "/var/lib/agentic-dev/gh" ]]
[[ -w /var/lib/agentic-dev/claude ]]
[[ -w /var/lib/agentic-dev/codex ]]
[[ -w /var/lib/agentic-dev/gh ]]
[[ -x /usr/local/share/agentic-dev/post-create.sh ]]

printf 'agent-dev Feature validation passed.\n'
