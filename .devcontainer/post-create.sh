#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

bash scripts/install-agent-clis.sh
if ! python scripts/skill_workspace.py link; then
  echo "Warning: local Skill validation or link generation failed; run 'make validate' after fixing the local Skill." >&2
fi

cat <<'MESSAGE'

Dev container is ready.

Claude Code:
  claude

Codex CLI:
  codex

Run `make doctor` to inspect the environment and `make test` to validate the
parent workspace. Each local Skill repository owns its dependencies and tests.
MESSAGE
