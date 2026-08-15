# Repository instructions

- The canonical distributable Agent Skill is the complete `skill/` directory; do not add a repository-root `SKILL.md`.
- Keep the Skill focused on one capability.
- Add deterministic scripts only where instructions are insufficient.
- Keep runtime scripts, references, and assets required by the Skill inside `skill/`; repository-only tests and fixtures may stay outside it.
- Do not make runtime behavior depend on repository-only files that will be absent after distribution.
- Document inputs, outputs, boundaries, failure handling, and security assumptions.
- Run `make test` before completion. It includes isolated distribution-bundle validation.
