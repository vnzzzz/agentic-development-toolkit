# ADR 0001: Parent workspace with independent local Skill repositories

- Status: Accepted
- Date: 2026-07-20

## Context

The development environment must support Claude Code and Codex without making either agent's discovery directory the canonical Skill source. Each Skill must also be able to gain its own Git history, CI, dependencies, fixtures, and release process.

The parent repository must remain usable immediately after clone, when no child Skill repositories exist. Tracking provisional child contents in the parent would blur ownership and complicate later extraction. Requiring submodules now would add clone and update operations before the parent needs to pin child commits.

## Decision

1. Use `skills/` as a local workspace for independent child repositories.
2. Ignore `skills/*` in the parent, except `skills/README.md` and an optional `.gitkeep`.
3. Put each child repository's distributable Skill at `skills/<repository>/skill/SKILL.md`.
4. Generate relative links from `.claude/skills/` and `.agents/skills/` to the same child `skill/` directory.
5. Treat zero local Skills as a valid parent state. Validation, linking, diagnosis, tests, and CI must succeed in that state.
6. Limit parent automation to the Dev Container, discovery tooling, templates, parent tests, documentation, and parent security settings.
7. Keep child dependencies, tests, fixtures, demos, manifests, releases, distribution artifacts, CI, and Dependabot in each child repository.
8. Do not use Git submodules now. Reconsider them only if the parent later needs to pin reviewed child commits reproducibly.

## Consequences

- A fresh parent clone contains no Skill implementation and still passes its checks.
- Local child repositories can be created or cloned without changing the parent index.
- Claude Code and Codex consume one agent-neutral Skill source without duplicated copies.
- Parent CI uses temporary fixtures to test discovery behavior and never runs local child automation.
- Child repositories must be initialized, committed, published, tested, and released independently.
- The parent does not record which child commit happens to be checked out locally.

## Alternatives

### Git submodules now

Deferred because there is no current requirement to pin child commits and no child remote is assumed. Submodules remain an option when reproducible parent-to-child version selection becomes necessary.

### Git subtree

Not selected because bidirectional history synchronization adds operational work and keeps child content in the parent history.

### Track all Skills in the parent monorepo

Not selected because it prevents a clean ownership boundary and makes later independent histories and releases harder.

### Duplicate Skill files in agent discovery directories

Rejected because copies drift and can apply fixes to only one agent's version.
