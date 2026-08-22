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

# The auth library is GitHub.com-only and must not accept an inherited API host.
export AGENT_GITHUB_API_URL=https://example.invalid
# shellcheck source=/dev/null
source /usr/local/lib/agent-dev/github-auth-lib.sh
[[ $AGENT_GITHUB_API_URL == https://api.github.com ]]

agent_github_set_repo_full_name 'vnzzzz/example-repo'
[[ $AGENT_GITHUB_REPO_OWNER == vnzzzz ]]
[[ $AGENT_GITHUB_REPO_NAME == example-repo ]]
[[ $AGENT_GITHUB_REPO_FULL_NAME == vnzzzz/example-repo ]]
if (agent_github_set_repo_full_name 'vnzzzz/example/repo') >/dev/null 2>&1; then
  echo 'ERROR: repository parser accepted a multi-segment repository path.' >&2
  exit 1
fi

# Plain HTTP origins are intentionally rejected before any credential is used.
tmp_repo=$(mktemp -d)
trap 'rm -rf "$tmp_repo"' EXIT
git -C "$tmp_repo" init -q
git -C "$tmp_repo" remote add origin http://github.com/vnzzzz/example-repo.git
if (cd "$tmp_repo" && agent_github_current_repo) >/dev/null 2>&1; then
  echo 'ERROR: insecure HTTP GitHub origin was accepted.' >&2
  exit 1
fi
rm -rf "$tmp_repo"
trap - EXIT

agent-github-auth configure claude 123456 >/dev/null
profile_dir="$HOME/.config/agent-dev/github-apps/claude"
config_path="$profile_dir/config.json"
[[ -f $config_path ]]
[[ $(jq -r '.app_id' "$config_path") == 123456 ]]
if jq -e 'has("app_slug")' "$config_path" >/dev/null; then
  echo 'ERROR: GitHub App slug must be derived from authenticated App metadata, not stored in profile config.' >&2
  exit 1
fi

# App activation refuses ambient caller credentials before trying the private key.
ambient_output=$(GH_TOKEN=human-test-token agent-github-auth claude -- true 2>&1 || true)
grep -q 'ambient GitHub credential is set in GH_TOKEN' <<<"$ambient_output"

# Profile directories and private keys must not be symlink escapes.
symlink_target=$(mktemp -d)
ln -s "$symlink_target" "$HOME/.config/agent-dev/github-apps/symlink-profile"
if agent-github-auth configure symlink-profile 123456 >/dev/null 2>&1; then
  echo 'ERROR: symlinked GitHub App profile directory was accepted.' >&2
  exit 1
fi
rm "$HOME/.config/agent-dev/github-apps/symlink-profile"
rm -rf "$symlink_target"

# Re-check every path component during load: replacing a configured profile
# directory with a symlink after configure must still fail closed.
profile_backup=$(mktemp -d)
profile_redirect=$(mktemp -d)
rmdir "$profile_backup"
mv "$profile_dir" "$profile_backup"
cp -a "$profile_backup/." "$profile_redirect/"
ln -s "$profile_redirect" "$profile_dir"
if (agent_github_load_profile claude) >/dev/null 2>&1; then
  echo 'ERROR: profile load accepted a symlink inserted after configuration.' >&2
  exit 1
fi
rm "$profile_dir"
mv "$profile_backup" "$profile_dir"
rm -rf "$profile_redirect"

key_target=$(mktemp)
chmod 0600 "$key_target"
ln -s "$key_target" "$profile_dir/private-key.pem"
if (agent_github_validate_private_key "$profile_dir/private-key.pem") >/dev/null 2>&1; then
  echo 'ERROR: symlinked GitHub App private key was accepted.' >&2
  exit 1
fi
rm "$profile_dir/private-key.pem" "$key_target"

if agent-github-auth claude -- true >/dev/null 2>&1; then
  echo 'ERROR: GitHub App auth must fail closed when the private key is not configured.' >&2
  exit 1
fi

# curl configuration must never precede the library's security options. A fake
# curl verifies that -q is the first option supplied by the shared helper.
fake_bin=$(mktemp -d)
cat >"$fake_bin/curl" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "${1:-}"
EOF
chmod 0755 "$fake_bin/curl"
[[ $(PATH="$fake_bin:$PATH" agent_github_curl --version) == -q ]]
rm -rf "$fake_bin"

# Credential helper only returns the process-local token for the exact frozen
# GitHub.com repository path. Missing path, another repo, or Enterprise host
# must not receive a credential.
export AGENT_GITHUB_PROFILE=claude
export AGENT_GITHUB_REPOSITORY=vnzzzz/example-repo
export AGENT_GITHUB_GIT_TOKEN=test-installation-token
credential=$(printf 'protocol=https\nhost=github.com\npath=vnzzzz/example-repo.git\n\n' | agent-github-credential get)
grep -q '^username=x-access-token$' <<<"$credential"
grep -q '^password=test-installation-token$' <<<"$credential"
[[ -z $(printf 'protocol=https\nhost=github.com\n\n' | agent-github-credential get) ]]
[[ -z $(printf 'protocol=https\nhost=github.com\npath=vnzzzz/other-repo.git\n\n' | agent-github-credential get) ]]
[[ -z $(printf 'protocol=https\nhost=ghe.example\npath=vnzzzz/example-repo.git\n\n' | agent-github-credential get) ]]
unset AGENT_GITHUB_PROFILE AGENT_GITHUB_REPOSITORY AGENT_GITHUB_GIT_TOKEN

# Keep these invariants visible in the installed wrappers. Live token behavior is
# covered by the merge-precondition E2E in Issue #32.
grep -Fq 'mktemp -d' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'GH_CONFIG_DIR=' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'GH_HOST=github.com' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'GH_REPO=' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'GH_PROMPT_DISABLED=1' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'trap cleanup EXIT' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'trap cleanup EXIT' /usr/local/lib/agent-dev/auth-bin/git
grep -Fq 'auth status --json hosts' /usr/local/bin/agent-github-auth
grep -Fq 'repo_http_url=' /usr/local/bin/agent-github-auth
grep -Fq 'agent_github_curl --fail' /usr/local/lib/agent-dev/github-auth-lib.sh
grep -Fq "command curl -q --proto '=https'" /usr/local/lib/agent-dev/github-auth-lib.sh

printf 'agent-dev Feature validation passed.\n'
