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
  echo 'ERROR: GitHub App slug must not be stored in profile config.' >&2
  exit 1
fi

ambient_output=$(GH_TOKEN=human-test-token agent-github-auth claude -- true 2>&1 || true)
grep -q 'ambient GitHub credential is set in GH_TOKEN' <<<"$ambient_output"

symlink_target=$(mktemp -d)
ln -s "$symlink_target" "$HOME/.config/agent-dev/github-apps/symlink-profile"
if agent-github-auth configure symlink-profile 123456 >/dev/null 2>&1; then
  echo 'ERROR: symlinked GitHub App profile directory was accepted.' >&2
  exit 1
fi
rm "$HOME/.config/agent-dev/github-apps/symlink-profile"
rm -rf "$symlink_target"

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

fake_bin=$(mktemp -d)
cat >"$fake_bin/curl" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "${1:-}"
EOF
chmod 0755 "$fake_bin/curl"
[[ $(PATH="$fake_bin:$PATH" agent_github_curl --version) == -q ]]
rm -rf "$fake_bin"

export AGENT_GITHUB_PROFILE=claude
export AGENT_GITHUB_REPOSITORY=vnzzzz/example-repo
ghe_host_output=$(/usr/local/lib/agent-dev/auth-bin/gh api --hostname tenant.ghe.com /user 2>&1 || true)
grep -q 'refuses non-github.com --hostname target' <<<"$ghe_host_output"
ghe_repo_output=$(/usr/local/lib/agent-dev/auth-bin/gh repo view -R tenant.ghe.com/example/repo 2>&1 || true)
grep -q 'refuses non-github.com repository host' <<<"$ghe_repo_output"
ghe_short_host_output=$(/usr/local/lib/agent-dev/auth-bin/gh auth status -h tenant.ghe.com 2>&1 || true)
grep -q 'refuses non-github.com -h target' <<<"$ghe_short_host_output"
ghe_joined_host_output=$(/usr/local/lib/agent-dev/auth-bin/gh auth status -htenant.ghe.com 2>&1 || true)
grep -q 'refuses non-github.com -h target' <<<"$ghe_joined_host_output"
auth_token_output=$(/usr/local/lib/agent-dev/auth-bin/gh auth token 2>&1 || true)
grep -q 'gh auth token is disabled in GitHub App session' <<<"$auth_token_output"
unset AGENT_GITHUB_PROFILE AGENT_GITHUB_REPOSITORY

# Authenticated Git must reject alternate Human credential sources before minting.
header_repo=$(mktemp -d)
git -C "$header_repo" init -q
git -C "$header_repo" config --local \
  'http.https://github.com/vnzzzz/example-repo.git/info/refs.extraHeader' \
  'Authorization: human-test-token'
header_output=$(AGENT_GITHUB_PROFILE=claude \
  AGENT_GITHUB_REPOSITORY=vnzzzz/example-repo \
  /usr/local/lib/agent-dev/auth-bin/git -C "$header_repo" \
  ls-remote https://github.com/vnzzzz/example-repo.git 2>&1 || true)
grep -q 'refuses configured Git HTTP Authorization extraHeader' <<<"$header_output"
git -C "$header_repo" config --unset-all \
  'http.https://github.com/vnzzzz/example-repo.git/info/refs.extraHeader'

git -C "$header_repo" config --local \
  'credential.https://github.com/vnzzzz/example-repo.git.helper' \
  '!human-helper'
helper_output=$(AGENT_GITHUB_PROFILE=claude \
  AGENT_GITHUB_REPOSITORY=vnzzzz/example-repo \
  /usr/local/lib/agent-dev/auth-bin/git -C "$header_repo" \
  ls-remote https://github.com/vnzzzz/example-repo.git 2>&1 || true)
grep -q 'refuses configured Git credential helper' <<<"$helper_output"
git -C "$header_repo" config --unset-all \
  'credential.https://github.com/vnzzzz/example-repo.git.helper'

cli_header_output=$(AGENT_GITHUB_PROFILE=claude \
  AGENT_GITHUB_REPOSITORY=vnzzzz/example-repo \
  /usr/local/lib/agent-dev/auth-bin/git -C "$header_repo" \
  -c 'http.https://github.com/vnzzzz/example-repo.git/info/refs.extraHeader=Authorization: human-test-token' \
  ls-remote https://github.com/vnzzzz/example-repo.git 2>&1 || true)
grep -q 'refuses configured Git HTTP Authorization extraHeader' <<<"$cli_header_output"

embedded_url_output=$(AGENT_GITHUB_PROFILE=claude \
  AGENT_GITHUB_REPOSITORY=vnzzzz/example-repo \
  /usr/local/lib/agent-dev/auth-bin/git -C "$header_repo" \
  push https://human:human-test-token@github.com/vnzzzz/example-repo.git HEAD 2>&1 || true)
grep -q 'refuses HTTP Git URLs with embedded credentials' <<<"$embedded_url_output"

git -C "$header_repo" remote add origin https://github.com/vnzzzz/example-repo.git
git -C "$header_repo" remote set-url --push origin \
  https://human:human-test-token@github.com/vnzzzz/example-repo.git
remote_url_output=$(AGENT_GITHUB_PROFILE=claude \
  AGENT_GITHUB_REPOSITORY=vnzzzz/example-repo \
  /usr/local/lib/agent-dev/auth-bin/git -C "$header_repo" push origin HEAD 2>&1 || true)
grep -q 'refuses HTTP Git URLs with embedded credentials' <<<"$remote_url_output"
git -C "$header_repo" remote set-url --push origin https://github.com/vnzzzz/example-repo.git

git -C "$header_repo" config alias.publish push
alias_output=$(AGENT_GITHUB_PROFILE=claude \
  AGENT_GITHUB_REPOSITORY=vnzzzz/example-repo \
  /usr/local/lib/agent-dev/auth-bin/git -C "$header_repo" publish origin HEAD 2>&1 || true)
grep -q "Git alias 'publish' is not supported in GitHub App session" <<<"$alias_output"
git -C "$header_repo" config --unset alias.publish
rm -rf "$header_repo"

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

grep -Fq 'mktemp -d' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'GH_CONFIG_DIR=' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'GH_HOST=github.com' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'GH_REPO=' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'GH_PROMPT_DISABLED=1' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'assert_github_com_command_target' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'assert_safe_git_credentials' /usr/local/lib/agent-dev/auth-bin/git
grep -Fq 'assert_safe_git_urls' /usr/local/lib/agent-dev/auth-bin/git
grep -Fq 'assert_not_git_alias' /usr/local/lib/agent-dev/auth-bin/git
grep -Fq 'trap cleanup EXIT' /usr/local/lib/agent-dev/auth-bin/gh
grep -Fq 'trap cleanup EXIT' /usr/local/lib/agent-dev/auth-bin/git
grep -Fq 'auth status --json hosts' /usr/local/bin/agent-github-auth
grep -Fq 'agent_github_curl --fail' /usr/local/lib/agent-dev/github-auth-lib.sh
grep -Fq "command curl -q --proto '=https'" /usr/local/lib/agent-dev/github-auth-lib.sh

printf 'agent-dev Feature validation passed.\n'
