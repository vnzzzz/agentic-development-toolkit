#!/usr/bin/env bash
set -Eeuo pipefail

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

rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn.sources
apt-get update
apt-get install -y --no-install-recommends \
  file \
  git \
  jq \
  make \
  shellcheck \
  unzip \
  zip
rm -rf /var/lib/apt/lists/*

npm config set update-notifier false
npm install --global \
  "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
  "@openai/codex@${CODEX_VERSION}"

remote_user=${_REMOTE_USER:-${_CONTAINER_USER:-root}}
if ! id "$remote_user" >/dev/null 2>&1; then
  echo "ERROR: Dev Container remote user '$remote_user' does not exist." >&2
  exit 1
fi
remote_group=$(id -gn "$remote_user")

install -d -m 0700 \
  /var/lib/agentic-dev/claude \
  /var/lib/agentic-dev/codex \
  /var/lib/agentic-dev/gh
chown -R "$remote_user:$remote_group" /var/lib/agentic-dev

install -d -m 0755 /usr/local/share/agentic-dev
install -m 0755 post-create.sh /usr/local/share/agentic-dev/post-create.sh

claude --version
codex --version
gh --version | head -n 1
