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
[[ -x /usr/local/lib/agent-dev/auth-bin/git ]]
[[ -x /usr/local/lib/agent-dev/real-bin/gh ]]
[[ -x /usr/local/lib/agent-dev/real-bin/git ]]
agent-github-auth --help >/dev/null

# shellcheck source=/dev/null
source /usr/local/lib/agent-dev/github-auth-lib.sh
agent_github_set_repo_full_name 'vnzzzz/example-repo'
[[ $AGENT_GITHUB_REPO_OWNER == vnzzzz ]]
[[ $AGENT_GITHUB_REPO_NAME == example-repo ]]
[[ $AGENT_GITHUB_REPO_FULL_NAME == vnzzzz/example-repo ]]

agent-github-auth configure claude 123456 >/dev/null
config_path="$HOME/.config/agent-dev/github-apps/claude/config.json"
[[ -f $config_path ]]
[[ $(jq -r '.app_id' "$config_path") == 123456 ]]
if jq -e 'has("app_slug")' "$config_path" >/dev/null; then
  echo 'ERROR: GitHub App slug must be derived from authenticated App metadata, not stored in profile config.' >&2
  exit 1
fi

if agent-github-auth claude -- true >/dev/null 2>&1; then
  echo 'ERROR: GitHub App auth must fail closed when the private key is not configured.' >&2
  exit 1
fi

printf 'agent-dev Feature validation passed.\n'
