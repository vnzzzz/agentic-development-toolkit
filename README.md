# Agentic Development Toolkit

Claude CodeとCodexを利用するprojectへ、共通Dev Container Feature `agent-dev`を配布するrepositoryです。consumer repositoryは自身をVS Code workspace / Git rootとして直接開きます。

## Consumer

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:bookworm",
  "features": {
    "ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev:1": {}
  },
  "remoteUser": "vscode"
}
```

`.devcontainer-lock.json`をcommitし、Feature更新も通常のcode changeとしてreviewします。利用方法とversioningは[共通Dev Container Feature](docs/dev-container-feature.md)を参照してください。

Claude / CodexのGitHub writeをHumanから分離する場合は、AgentごとのGitHub Appと`agent-github-auth`を利用します。詳細は[GitHub Agent identity](docs/github-agent-identity.md)を参照してください。

## Authoring

repository自身は公開済み`agent-dev:1`を利用し、編集中の`src/agent-dev/`を自己参照しません。

```bash
make validate
make test
```

Feature sourceは`src/agent-dev/`、実container testは`test/agent-dev/`です。releaseは`main`からGitHub Actionsで行います。

## Documents

- Feature contract: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- GitHub Agent identity: [docs/github-agent-identity.md](docs/github-agent-identity.md)
- trust boundary: [SECURITY.md](SECURITY.md)
- repository変更規則: [AGENTS.md](AGENTS.md)
