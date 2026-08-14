# Repository instructions

This parent repository provides a workspace for independently managed Agent Skill source repositories used by Claude Code and Codex.

## Boundaries

- Treat `repos/*` as ignored local source repositories; the parent tracks only `repos/README.md` and an optional `repos/.gitkeep`.
- Support both standalone repositories at `repos/<repository>/skill/SKILL.md` and collection repositories at `repos/<repository>/skills/<skill-name>/SKILL.md`.
- Treat `.claude/skills/` and `.agents/skills/` as generated discovery links; never edit linked copies.
- Keep parent workspace logic generic. Do not hard-code `agent-skills` or another concrete source repository.
- The parent owns the Dev Container, shared discovery tooling, standalone repository template, parent tests, documentation, and parent CI.
- Each source repository owns its Skill files, tests, dependencies, fixtures, security review, release process, and CI.
- Do not add credentials, host SSH mounts, Docker socket mounts, cloud credential mounts, or permissive agent flags.
- Do not weaken validation or security checks merely to make a failing check pass.
- Prefer the Agent Skills open format. Agent-specific frontmatter is allowed only when documented and harmless to the other agent.
- Do not add submodules for mutable development repositories. Pinning review済み shared revisions for workspace consumption is a separate concern.

## Required checks

Run before completion:

```bash
make test
make audit
```

When changing local Skill discovery or link generation, also run:

```bash
make validate
make link-skills
```
