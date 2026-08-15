# ADR 0002: Support standalone and collection Skill source repositories

- Status: Accepted; amended by ADR 0003
- Date: 2026-08-14

## Context

ADR 0001 established a parent workspace that keeps Agent Skill source outside the parent Git history and exposes one canonical source to both Claude Code and Codex.

The original implementation assumed one Skill per child repository at `skills/<repository>/skill/SKILL.md`. A new shared repository, `agent-skills`, instead acts as a collection containing multiple reusable Skills at `skills/<skill-name>/SKILL.md`.

Replacing the standalone model with a collection-only model would discard useful support for Skills that need independent repositories, histories, dependencies, tests, and release processes. Special-casing `agent-skills` would also make the parent workspace depend on one concrete repository.

## Decision

1. Treat the local placement unit as a source repository rather than a Skill and rename the parent-local placement directory from `skills/` to `repos/`.
2. Support two repository layouts:
   - standalone: `repos/<repository>/skill/SKILL.md`
   - collection: `repos/<repository>/skills/<skill-name>/SKILL.md`
3. Keep the existing standalone repository template.
4. Discover every Skill in both layouts and generate `.claude/skills/<name>` and `.agents/skills/<name>` links directly to the actual Skill root.
5. Require the standalone repository directory or collection Skill directory to match the Skill `name` as applicable.
6. Reject repository-root `SKILL.md`, repositories containing both `skill/` and `skills/`, incomplete Skill directories, and duplicate Skill names across all local repositories.
7. Keep zero local source repositories as a valid parent state. An explicitly created but empty collection `skills/` directory is also valid.
8. Keep mutable development source repositories ignored by the parent Git repository and do not make them submodules.
9. Keep parent automation limited to discovery, cross-repository validation, link generation, the Dev Container, parent tests, documentation, and parent security controls.
10. Do not hard-code `agent-skills`; collection support is a generic repository capability.

ADR 0003 extends the workspace to Plugin marketplace repositories and separates direct Skill authoring from native Plugin distribution validation. The direct-link decision above continues to apply to standalone and collection repositories, not Plugin repository Skills.

## Consequences

- The workspace can develop a standalone Skill repository and a multi-Skill collection in the same environment.
- Repository identity and Skill identity are separate concepts for collection repositories.
- Claude Code and Codex continue consuming the same underlying Skill source without copies for direct-authoring repository layouts.
- Parent validation catches name collisions across standalone and collection sources before link generation.
- Existing local working copies under the old `skills/` placement must be moved or re-cloned under `repos/`.
- A source repository that has neither a supported standalone nor collection layout is treated as a configuration error rather than silently ignored.
- Pinning a reviewed shared revision for the parent workspace's own normal consumption remains a separate concern from mutable development working copies.

## Alternatives

### Collection repositories only

Rejected because standalone repositories remain useful for Skills with independent lifecycle, dependencies, tests, or distribution needs.

### Keep `skills/` as the parent placement directory

Rejected because the directory would contain repositories, some of which themselves contain a `skills/` collection. `repos/` makes the ownership unit explicit and avoids ambiguous paths such as `skills/agent-skills/skills/...`.

### Special-case `agent-skills`

Rejected because the workspace should support a repository shape, not one repository name or URL.

### Convert mutable development repositories to submodules

Rejected for the same reason as ADR 0001: the parent does not need to pin mutable development working copies. A future fixed consumer copy may use a pinning mechanism independently.
