#!/usr/bin/env bash
set -Eeuo pipefail

MARKETPLACE_SOURCE=${AGENT_SKILLS_MARKETPLACE_SOURCE:-vnzzzz/agent-skills}
MARKETPLACE_NAME=agent-skills
PLUGIN_ID=agent-skills@agent-skills

install_for_codex() {
  codex plugin marketplace add "$MARKETPLACE_SOURCE" --json >/dev/null
  codex plugin marketplace upgrade "$MARKETPLACE_NAME" --json >/dev/null 2>&1 || true
  codex plugin remove "$PLUGIN_ID" --json >/dev/null 2>&1 || true
  codex plugin add "$PLUGIN_ID" --json >/dev/null
}

install_for_claude() {
  if ! claude plugin marketplace update "$MARKETPLACE_NAME" >/dev/null 2>&1; then
    claude plugin marketplace add "$MARKETPLACE_SOURCE" --scope user >/dev/null
  fi

  if ! claude plugin update "$PLUGIN_ID" --scope user >/dev/null 2>&1; then
    claude plugin install "$PLUGIN_ID" --scope user >/dev/null
  fi
}

command -v codex >/dev/null || {
  echo "ERROR: codex CLI is required before installing agent-skills Plugin." >&2
  exit 1
}
command -v claude >/dev/null || {
  echo "ERROR: claude CLI is required before installing agent-skills Plugin." >&2
  exit 1
}

install_for_codex
install_for_claude

printf 'agent-skills Plugin installed for Codex and Claude Code from %s.\n' "$MARKETPLACE_SOURCE"
