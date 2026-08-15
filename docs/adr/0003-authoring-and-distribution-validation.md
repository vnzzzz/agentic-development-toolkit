# ADR 0003: Separate mutable Skill authoring from distribution validation

- Status: Accepted
- Date: 2026-08-15

## Context

The workspace now handles three different concerns that look similar on disk but have different correctness requirements:

1. the workspace normally consumes shared reusable Skills from the public `vnzzzz/agent-skills` Plugin;
2. standalone and collection Skill repositories under `repos/` need a short feedback loop while their working trees are being edited;
3. Plugin repositories and script-bearing Skills must also prove that the actual distributable package works without relying on repository-only files or project-local discovery behavior.

Direct links from `.claude/skills/` and `.agents/skills/` to a mutable Skill root are useful for authoring because edits become visible without copying or packaging. They do not prove that a Plugin namespace, Plugin cache, packaged file set, or bundled resource resolution will behave the same way after distribution.

This distinction matters more for Skills that contain scripts, references, or assets. A Skill can work from a repository checkout while accidentally reading tests, fixtures, generated files, or sibling directories that are absent from the distributed Skill bundle.

Plugin repositories add another ambiguity. Exposing each Plugin Skill as a project-local direct link while an installed Plugin with the same capability is also present can make it unclear which source is active. It also removes Plugin namespacing from the authoring path.

## Decision

1. Keep three explicit modes:
   - normal Plugin consumption;
   - mutable direct authoring;
   - distribution validation.
2. Normal workspace consumption continues to install the public `vnzzzz/agent-skills` Plugin during Dev Container creation.
3. Direct authoring links are generated only for standalone and collection repositories:
   - `repos/<repository>/skill/<...>`;
   - `repos/<repository>/skills/<skill-name>/<...>`.
4. Plugin repository Skills remain discoverable and validated for metadata, layout, duplicate names, and Skill-root security boundaries, but are not linked into `.claude/skills/` or `.agents/skills/`.
5. Plugin repositories are tested through native Plugin mechanisms owned by the provider repository. For the shared `agent-skills` provider:
   - Claude Code may load the Plugin working tree with `--plugin-dir`;
   - Codex may switch the existing marketplace installation to a local marketplace source through the workspace bootstrap and then restore the public source.
6. The standalone repository template treats the complete `skill/` directory as the distributable bundle.
7. Template `make test` must validate an isolated copy of `skill/` before repository unit tests:
   - local Markdown links must remain inside the bundle and exist;
   - symlinks must not escape the Skill root;
   - bundled Python and shell scripts receive syntax checks from the isolated copy.
8. Generic distribution validation does not pretend to prove Skill-specific runtime behavior. Script-bearing Skill repositories must add representative integration tests that execute the distributed bundle against repository-owned fixtures.
9. Parent CI continues to validate only workspace infrastructure, generic discovery/link behavior, the standalone template, and shared Plugin integration. It must not clone or execute every child repository.
10. Each child repository remains an independent Git repository and owns its branches, commits, PRs, dependencies, tests, CI, security updates, versions, releases, and distribution artifacts.
11. `repos/*` remains ignored by the parent Git repository and is not converted to submodules.

## Consequences

- Standalone and collection Skills retain immediate working-tree feedback for Claude Code and Codex.
- Plugin working copies no longer create project-local Skill entries that can overlap ambiguously with installed Plugin capabilities.
- Native Plugin testing preserves the runtime properties that direct Skill links cannot model.
- Script-bearing standalone Skills gain a reusable distribution-boundary check without moving their tests or dependencies into the parent workspace.
- A passing parent CI does not imply that every local child Skill passes its own runtime tests; that remains intentionally delegated to each source repository.
- Child CI failures remain isolated from parent workspace infrastructure failures.
- The parent does not record local child revisions, so reproducibility of a child release is established by the child repository itself rather than by the parent workspace checkout.

## Alternatives

### Install every mutable Skill as a Plugin during editing

Rejected because standalone Skills do not require Plugin packaging and reinstalling on each edit creates a slower feedback loop than direct working-tree authoring.

### Direct-link Plugin Skills and also run Plugin validation later

Rejected as the default because it leaves an installed Plugin and unnamespaced project-local copies visible at the same time and makes source selection harder to reason about.

### Run all child CI from the parent workspace

Rejected because the parent does not own child dependencies, fixtures, runtime versions, or release lifecycles. Central execution would couple unrelated repositories and make parent CI depend on local source availability.

### Convert `repos/*` to Git submodules

Rejected because mutable development working copies do not need a parent-owned revision pin. Each child repository already provides the Git history needed to reproduce its own releases.

### Put tests and fixtures inside the distributable Skill bundle

Rejected as a generic requirement. Tests and fixtures are development assets unless the Skill actually needs them at runtime. Distribution validation should instead prove that runtime files remain inside the bundle while repository-only validation assets stay outside it.
