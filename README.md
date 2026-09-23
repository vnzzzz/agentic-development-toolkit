# Agentic Development Toolkit

[日本語](README.ja.md)

This repository maintains the `agent-dev` Dev Container Feature, which standardizes development environments that use Claude Code and Codex.

`agent-dev` installs and configures Claude Code / Codex CLI, GitHub CLI, [vnzzzz/agent-skills](https://github.com/vnzzzz/agent-skills), GitHub App authentication commands, and related tooling in a shared Dev Container setup. Project-specific runtimes, dependencies, and service configuration remain in each consumer project.

## Use in a project

Add `agent-dev` to `features` in `.devcontainer/devcontainer.json`.

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:bookworm",
  "features": {
    "ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev:1": {}
  },
  "remoteUser": "vscode"
}
```

To pin the Feature version and digest, also commit `.devcontainer-lock.json`. See [Shared Dev Container Feature](docs/dev-container-feature.md) for the installed components and versioning policy.

## Separate GitHub identities by agent

GitHub writes from Claude Code or Codex can use dedicated GitHub Apps instead of a personal account. `agent-github-auth` aligns the GitHub actor and the Git commit Author / Committer with the same App bot.

See [GitHub App authentication for agents](docs/github-agent-identity.md) for configuration, permissions, credentials, and Ruleset guidance.

## Documentation

- Installed components, versioning policy, updates, and releases: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- Separate GitHub identities for agents with GitHub Apps: [docs/github-agent-identity.md](docs/github-agent-identity.md)
- Credentials and security boundaries: [SECURITY.md](SECURITY.md)
- Rules for changing this repository: [AGENTS.md](AGENTS.md)
