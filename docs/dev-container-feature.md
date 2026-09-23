# Shared Dev Container Feature

[日本語](dev-container-feature.ja.md)

`agent-dev` is a Dev Container Feature that installs existing tools and authentication configuration in a shared setup for development environments using Claude Code and Codex. Project-specific runtimes and dependencies remain in each consumer project.

## Scope

### Tools

| Installed component | Current setting | Version policy | Notes |
|---|---|---|---|
| Node.js | `22` | Latest in the 22 series | Installed from the `node:1` Feature[^3] |
| GitHub CLI | `latest` | Latest at build time | Installed from the `github-cli:1` Feature[^4] |
| Claude Code CLI | `2.1.229` | Fully pinned | Can be overridden with `claudeCodeVersion` |
| Codex CLI | `0.147.0` | Fully pinned | Can be overridden with `codexVersion` |
| Claude Code VS Code extension | `anthropic.claude-code` | Unpinned | Uses the Marketplace version[^5] |
| ChatGPT VS Code extension | `openai.chatgpt` | Unpinned | Uses the Marketplace version[^5] |
| [vnzzzz/agent-skills](https://github.com/vnzzzz/agent-skills) | Default branch | Unpinned | Installed for Claude Code / Codex at post-create time |
| Base tools | OS package repository | Unpinned | `git`, `curl`, `jq`, `make`, `openssl`, `shellcheck`, `unzip`, `zip`, and others |

`src/agent-dev/devcontainer-feature.json` is canonical for the default Claude Code / Codex CLI versions. Installation verifies that the installed versions match the configured values.

### Authentication

| Feature | Description |
|---|---|
| `agent-github-auth` | Uses GitHub Apps to separate GitHub operations and commit Author / Committer identities by Agent |
| Authentication volumes | Separates authentication state for Claude Code, Codex, and GitHub CLI |
| GitHub App configuration | Separates GitHub App configuration by Agent |

[SECURITY.md](../SECURITY.md) is canonical for security boundaries, including credential storage and lifetime. See [GitHub App authentication for agents](github-agent-identity.md) for GitHub App configuration.

### What the lockfile pins

`.devcontainer-lock.json` pins versions and digests for `agent-dev` and dependent Features. It does not pin tools resolved externally during Feature installation, `vnzzzz/agent-skills` fetched during post-create, or extensions from the VS Code Marketplace.[^6]

`agent-dev:1` does not automatically move to `2.x`.

The supported target is Debian / Ubuntu-based Dev Containers. See the official documentation for the Dev Container Feature specification.[^1][^2]

## Installation

Add the Feature to `features` in `.devcontainer/devcontainer.json`.

```json
{
  "name": "example-project",
  "image": "mcr.microsoft.com/devcontainers/base:bookworm",
  "features": {
    "ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev:1": {}
  },
  "remoteUser": "vscode"
}
```

## Updating

Use the Dev Containers CLI to inspect and apply updates.

```bash
devcontainer outdated
devcontainer upgrade
```

After updating, review the `.devcontainer-lock.json` diff and rebuild the Dev Container.

## agent-dev versioning

`agent-dev` follows SemVer.

- patch: backward-compatible fixes and CLI patch updates
- minor: backward-compatible feature additions
- major: breaking changes that require consumer changes

Published exact versions are never overwritten.

<a id="release-workflow"></a>

## Development and release

Implementation lives under `src/agent-dev/`; real-container tests live under `test/agent-dev/`.

```bash
make validate
make test
```

For release-bearing changes, update the Feature version and merge only after `feature-ci` and `security` succeed. Publishing is performed by manually running `.github/workflows/release-feature.yml` from `main`.

The release workflow stops if it cannot confirm that the exact version is unpublished. Publishing uses the workflow-specific `GITHUB_TOKEN`.

This repository's own Dev Container uses the published `agent-dev:1` and does not point `.devcontainer-lock.json` at an unpublished version.

## References

[^1]: [Dev Container Specification, Features](https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-features.md)
[^2]: [Dev Containers, Authoring a Dev Container Feature](https://containers.dev/guide/author-a-feature)
[^3]: [Dev Containers Features, Node.js](https://github.com/devcontainers/features/tree/main/src/node)
[^4]: [Dev Containers Features, GitHub CLI](https://github.com/devcontainers/features/tree/main/src/github-cli)
[^5]: [Visual Studio Code, Supporting Remote Development](https://code.visualstudio.com/api/advanced-topics/remote-extensions)
[^6]: [Dev Container Specification, Lockfiles](https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-lockfile.md)
