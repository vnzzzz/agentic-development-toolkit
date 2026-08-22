#!/usr/bin/env bash
set -Eeuo pipefail

claude --version >/dev/null
codex --version >/dev/null
gh --version >/dev/null
git --version
jq --version
make --version >/dev/null
shellcheck --version >/dev/null
unzip -v >/dev/null
zip -v >/dev/null
curl --version >/dev/null
openssl version >/dev/null

[[ "${CLAUDE_CONFIG_DIR:-}" == "/var/lib/agentic-dev/claude" ]]
[[ "${CODEX_HOME:-}" == "/var/lib/agentic-dev/codex" ]]
[[ "${GH_CONFIG_DIR:-}" == "/var/lib/agentic-dev/gh" ]]
[[ -w /var/lib/agentic-dev/claude ]]
[[ -w /var/lib/agentic-dev/codex ]]
[[ -w /var/lib/agentic-dev/gh ]]
[[ -x /usr/local/share/agentic-dev/post-create.sh ]]

command -v agent-github-auth >/dev/null
command -v agent-github-credential >/dev/null
[[ -r /usr/local/lib/agent-dev/github-auth-lib.sh ]]
[[ -x /usr/local/lib/agent-dev/auth-bin/gh ]]
[[ -x /usr/local/lib/agent-dev/real-bin/gh ]]
[[ -x /usr/local/lib/agent-dev/real-bin/git ]]
agent-github-auth --help >/dev/null

if agent-github-auth claude -- true >/dev/null 2>&1; then
  echo 'ERROR: GitHub App auth must fail closed when the profile/private key is not configured.' >&2
  exit 1
fi

printf 'agent-dev Feature validation passed.\n'
