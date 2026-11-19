#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CLAUDE_CODE_VERSION=${CLAUDECODEVERSION:?claudeCodeVersion is required}
CODEX_VERSION=${CODEXVERSION:?codexVersion is required}

if [[ $(id -u) -ne 0 ]]; then
  echo "ERROR: agent-dev Feature installation must run as root." >&2
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "ERROR: agent-dev currently supports Debian/Ubuntu-based Dev Container images only." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: Node.js and npm are required. The Node Dev Container Feature dependency did not install correctly." >&2
  exit 1
fi
if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI is required. The GitHub CLI Dev Container Feature dependency did not install correctly." >&2
  exit 1
fi

apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  file \
  git \
  jq \
  make \
  openssl \
  shellcheck \
  unzip \
  zip
rm -rf /var/lib/apt/lists/*

# The Node Feature installs nvm's global npm prefix for the remote user.
# Installing the CLIs as root leaves root-owned packages that the user cannot
# replace when Codex/Claude runs npm install --global to update itself.
remote_user=${_REMOTE_USER:-${_CONTAINER_USER:-root}}
if ! id "$remote_user" >/dev/null 2>&1; then
  echo "ERROR: Dev Container remote user '$remote_user' does not exist." >&2
  exit 1
fi
remote_group=$(id -gn "$remote_user")
remote_home=$(getent passwd "$remote_user" | cut -d: -f6)
if [[ -z "$remote_home" ]]; then
  echo "ERROR: cannot resolve home directory for Dev Container remote user '$remote_user'." >&2
  exit 1
fi

if ! command -v runuser >/dev/null 2>&1; then
  echo "ERROR: runuser is required to install agent CLIs as the Dev Container remote user." >&2
  exit 1
fi

run_as_remote_user() {
  # Preserve NVM's shared nvm-group write access when Dev Containers remaps
  # the remote user's UID/GID at container creation on Linux.
  runuser -u "$remote_user" -- env HOME="$remote_home" PATH="$PATH" \
    bash -c 'umask 0002; exec "$@"' bash "$@"
}

npm_global_prefix=$(run_as_remote_user npm prefix --global)
npm_global_root=$(run_as_remote_user npm root --global)
if [[ -z "$npm_global_prefix" || -z "$npm_global_root" ]] ||
   ! run_as_remote_user test -w "$npm_global_prefix/bin" ||
   ! run_as_remote_user test -w "$npm_global_root"; then
  echo "ERROR: npm global prefix must be writable by '$remote_user': $npm_global_prefix" >&2
  echo "Check that the Node Feature and agent-dev use the same remote user." >&2
  exit 1
fi

run_as_remote_user npm config set update-notifier false
run_as_remote_user npm install --global \
  "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
  "@openai/codex@${CODEX_VERSION}"

claude_version_output=$(run_as_remote_user claude --version)
codex_version_output=$(run_as_remote_user codex --version)
claude_installed_version=${claude_version_output%% *}
codex_version_rest=${codex_version_output#* }
codex_installed_version=${codex_version_rest%% *}

if [[ "$CLAUDE_CODE_VERSION" != latest && "$claude_installed_version" != "$CLAUDE_CODE_VERSION" ]]; then
  echo "ERROR: expected Claude Code ${CLAUDE_CODE_VERSION}, got: ${claude_version_output}" >&2
  exit 1
fi
if [[ "$CODEX_VERSION" != latest && "$codex_installed_version" != "$CODEX_VERSION" ]]; then
  echo "ERROR: expected Codex ${CODEX_VERSION}, got: ${codex_version_output}" >&2
  exit 1
fi

install -d -m 0700 \
  /var/lib/agentic-dev/claude \
  /var/lib/agentic-dev/codex \
  /var/lib/agentic-dev/gh
chown -R "$remote_user:$remote_group" /var/lib/agentic-dev

mkdir -p \
  "$remote_home/.config/agent-dev/github-apps/claude" \
  "$remote_home/.config/agent-dev/github-apps/codex"
chmod 0700 \
  "$remote_home/.config/agent-dev" \
  "$remote_home/.config/agent-dev/github-apps" \
  "$remote_home/.config/agent-dev/github-apps/claude" \
  "$remote_home/.config/agent-dev/github-apps/codex"
chown -R "$remote_user:$remote_group" "$remote_home/.config/agent-dev"

real_gh=$(command -v gh)
real_git=$(command -v git)
install -d -m 0755 \
  /usr/local/share/agentic-dev \
  /usr/local/lib/agent-dev/real-bin \
  /usr/local/lib/agent-dev/auth-bin
ln -sfn "$real_gh" /usr/local/lib/agent-dev/real-bin/gh
ln -sfn "$real_git" /usr/local/lib/agent-dev/real-bin/git

install -m 0755 "$SCRIPT_DIR/post-create.sh" /usr/local/share/agentic-dev/post-create.sh
install -m 0644 "$SCRIPT_DIR/github-auth-lib.sh" /usr/local/lib/agent-dev/github-auth-lib.sh
install -m 0755 "$SCRIPT_DIR/agent-github-auth" /usr/local/bin/agent-github-auth
install -m 0755 "$SCRIPT_DIR/agent-github-credential" /usr/local/bin/agent-github-credential
install -m 0755 "$SCRIPT_DIR/auth-bin/gh" /usr/local/lib/agent-dev/auth-bin/gh
install -m 0755 "$SCRIPT_DIR/auth-bin/git" /usr/local/lib/agent-dev/auth-bin/git

printf '%s\n' "$claude_version_output"
printf '%s\n' "$codex_version_output"
gh --version | head -n 1
