# Repository instructions

This parent repository provides a workspace for independently managed Agent Skill repositories used by Claude Code and Codex.

## Boundaries

- Treat `skills/*` as ignored local child repositories; the parent tracks only `skills/README.md` and an optional `skills/.gitkeep`.
- Keep each child Skill's distributable source under `skills/<repository>/skill/`.
- Treat `.claude/skills/` and `.agents/skills/` as generated discovery links; never edit linked copies.
- The parent owns the Dev Container, shared discovery tooling, templates, parent tests, documentation, and parent CI.
- Each child owns its Skill files, tests, dependencies, fixtures, security review, release process, and CI.
- Do not add credentials, host SSH mounts, Docker socket mounts, cloud credential mounts, or permissive agent flags.
- Do not weaken validation or security checks merely to make a failing check pass.
- Prefer the Agent Skills open format. Agent-specific frontmatter is allowed only when documented and harmless to the other agent.
- Do not add submodules unless the parent has an explicit requirement to pin reviewed child commits.

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
