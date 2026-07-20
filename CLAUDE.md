# Repository instructions

This parent workspace develops portable Agent Skills and exposes local child repositories to both Claude Code and Codex.

- `skills/*` contains ignored local child repositories; the parent tracks only the directory documentation.
- A child Skill's canonical distributable source is `skills/<repository>/skill/`.
- `.claude/skills/` and `.agents/skills/` contain generated symlinks only.
- Keep parent workspace logic generic. Child tests, dependencies, fixtures, CI, manifests, and releases remain in the child repository.
- Parent tests and CI must pass when no local Skills are present.
- Preserve non-root execution and isolated authentication volumes in the Dev Container.
- Do not use permission-bypass flags, mount host credential directories, or mount the Docker socket.
- Do not commit local Skill directories, generated links, local agent state, API keys, tokens, or build output.

Before completion run:

```bash
make test
make audit
```

When changing Skill discovery or links, also run `make validate` and `make link-skills`.
