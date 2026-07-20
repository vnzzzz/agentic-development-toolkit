#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

python3 -m venv .venv
.venv/bin/python scripts/skill_workspace.py link

cat <<'MESSAGE'
Local Python environment created.
Run:
  source .venv/bin/activate
  make test

Claude Code and Codex CLI are not installed by this script. Local Skill
repositories own their dependency installation and tests.
MESSAGE
