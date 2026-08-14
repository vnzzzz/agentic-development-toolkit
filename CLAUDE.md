# Repository instructions

This parent workspace develops portable Agent Skills and exposes local source repositories to both Claude Code and Codex.

- `repos/*` contains ignored local source repositories; the parent tracks only the directory documentation.
- A standalone repository exposes `repos/<repository>/skill/SKILL.md`.
- A collection repository exposes each `repos/<repository>/skills/<skill-name>/SKILL.md`.
- A Plugin marketplace repository exposes each `repos/<repository>/plugins/<plugin-name>/skills/<skill-name>/SKILL.md`.
- `.claude/skills/` and `.agents/skills/` contain generated symlinks only for mutable local development sources.
- Keep local source discovery generic; do not special-case a concrete repository in discovery code.
- The workspace itself consumes `vnzzzz/agent-skills` through the Codex / Claude Code Plugin package. Plugin bootstrap may name the package, but must not enumerate individual shared Skills or depend on provider-internal Skill paths.
- Do not introduce a fixed submodule copy for shared Plugin consumption; Dev Container creation installs the latest public Plugin after installing both CLIs.
- Source-repository tests, dependencies, fixtures, CI, manifests, and releases remain in that repository.
- Parent tests and CI must pass when no local source repositories are present.
- Preserve non-root execution and isolated authentication volumes in the Dev Container.
- Public GitHub Plugin installation must not require GitHub credentials.
- Do not use permission-bypass flags, mount host credential directories, or mount the Docker socket.
- Do not commit local source repositories, generated links, local agent state, API keys, tokens, or build output.

Before completion run:

```bash
make test
make audit
```

When changing Skill discovery or links, also run `make validate` and `make link-skills`.
