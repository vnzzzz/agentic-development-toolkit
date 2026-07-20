#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

package_version() {
  local package_name=$1
  node -e 'const p=require(process.argv[1]); const v=p.dependencies[process.argv[2]]; if (!v) process.exit(2); process.stdout.write(v)' \
    "$ROOT/package.json" "$package_name"
}

CLAUDE_CODE_VERSION=${CLAUDE_CODE_VERSION:-$(package_version '@anthropic-ai/claude-code')}
CODEX_VERSION=${CODEX_VERSION:-$(package_version '@openai/codex')}

npm config set update-notifier false
npm install --global \
  "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
  "@openai/codex@${CODEX_VERSION}"

claude --version
codex --version
