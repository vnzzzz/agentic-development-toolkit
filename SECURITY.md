# Security Policy

[日本語](SECURITY.ja.md)

Because `agent-dev` handles credentials, it is intended for use only with trusted repositories. Code running as the same user inside an authenticated container can access credentials readable by that user.

## Invariants

- Do not include credentials, tokens, or authenticated configuration in Feature source, test fixtures, or GHCR artifacts.
- Do not bind mount host credential directories, SSH directories, or the Docker socket.
- Keep authentication state for Claude Code, Codex, and the human GitHub CLI separate.
- Do not reuse a human PAT or human `gh auth` credentials for an Agent identity.
- Use a dedicated GitHub App for each Agent that performs GitHub writes.
- Do not store GitHub App private keys in the workspace, repository, GHCR artifacts, or named volumes.
- Do not persist Installation Tokens to disk or credential stores.
- Users must configure GitHub App permissions and installation repository scope with least privilege.

## Credential storage

Authentication state for Claude Code, Codex, and the human GitHub CLI is isolated in per-Dev-Container named volumes.

```text
agentic-dev-claude-${devcontainerId}
agentic-dev-codex-${devcontainerId}
agentic-dev-gh-${devcontainerId}
```

Named volumes are not secret vaults. Any principal that can control the same Docker daemon can access the volumes, so the Docker daemon is part of the trust boundary and the Agent Container does not mount the Docker socket.

To discard authentication state, delete the container and the corresponding volumes, and revoke sessions or tokens at the provider when necessary.

## GitHub Agent identity

Place each GitHub App private key at the following container-local path.

```text
~/.config/agent-dev/github-apps/<profile>/private-key.pem
```

Private keys are intentionally lost when the Dev Container is rebuilt. Credential directories must be mode `0700`; configuration files and private keys must be mode `0600` and owned by the current user. Symlinks, including symlinks in intermediate path components, are rejected.

An `agent-github-auth` session fails closed to guarantee the following:

- Issue an Installation Token scoped only to the repository active at session start.
- Do not coexist with ambient GitHub tokens or saved human `gh auth` accounts.
- Use temporary configuration for `gh`, and reject explicit targets other than `github.com` before issuing a token.
- Before issuing a token, reject authenticated Git operations when another Authorization header or credential helper is active.
- Do not fall back to GitHub SSH or interactive credential prompts.
- GitHub App API requests use HTTPS only and do not read user curl configuration.

These controls prevent accidental credential misuse; they do not sandbox processes running as the same user. Because an Agent process can read its private key, the GitHub App installation scope is the final repository boundary if the private key is compromised. Runtime token repository scope is defense in depth.

See [GitHub Agent identity](docs/github-agent-identity.md) for usage and GitHub App permissions.

## Release supply chain

- Pin the default Claude Code / Codex CLI versions.
- Install Node.js and GitHub CLI from official Dev Container Features.
- Pin external GitHub Actions to full commit SHAs.
- Release workflows use only `contents: read` and `packages: write`, and do not use personal PATs.
- Treat each published exact Feature version as immutable.

[Shared Dev Container Feature](docs/dev-container-feature.md#release-workflow) is canonical for release behavior.

## Authoring boundary

The repository's own `.devcontainer/` uses only a published Feature and does not self-reference the Feature source under development. Do not add Docker socket mounts or privileged settings to the distributed Feature for real-container tests.

## Reporting

Do not paste credentials or confidential source into Issues. Share only the minimum information required to reproduce a problem and output with sensitive data removed.

## Supporting documents

- Feature contract: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- GitHub Agent identity: [docs/github-agent-identity.md](docs/github-agent-identity.md)
- Repository change rules: [AGENTS.md](AGENTS.md)
