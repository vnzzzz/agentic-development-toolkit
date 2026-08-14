# Repository instructions

This parent repository provides a workspace for independently managed Agent Skill source repositories used by Claude Code and Codex.

## Boundaries

- Treat `repos/*` as ignored local source repositories; the parent tracks only `repos/README.md` and an optional `repos/.gitkeep`.
- Support both standalone repositories at `repos/<repository>/skill/SKILL.md` and collection repositories at `repos/<repository>/skills/<skill-name>/SKILL.md`.
- Treat `.claude/skills/` and `.agents/skills/` as generated discovery links for mutable local development sources; never edit linked copies.
- Keep source-repository discovery logic generic. Do not special-case a concrete repository in `skill_workspace.py`.
- The workspace itself consumes the reusable public `vnzzzz/agent-skills` collection through its Codex / Claude Code Plugin package. Plugin bootstrap may name that package explicitly, but must not enumerate its individual Skills or depend on `skills/<name>` paths.
- Do not use a git submodule or fixed shared copy for workspace consumption. The Dev Container installs the latest public Plugin after installing both agent CLIs.
- The parent owns the Dev Container, Plugin bootstrap, shared discovery tooling, standalone repository template, parent tests, documentation, and parent CI.
- Each source repository owns its Skill files, tests, dependencies, fixtures, security review, release process, and CI.
- Do not add credentials, host SSH mounts, Docker socket mounts, cloud credential mounts, or permissive agent flags.
- Public GitHub Plugin installation must not require GitHub credentials; only outbound HTTPS is assumed.
- Do not weaken validation or security checks merely to make a failing check pass.
- Prefer the Agent Skills open format. Agent-specific metadata is allowed only as a thin distribution adapter over shared Skill content.

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
