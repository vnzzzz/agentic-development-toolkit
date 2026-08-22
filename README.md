# Agentic Development Toolkit

Claude CodeとCodexを利用する複数projectへ、共通のDev Container Featureを配布するrepositoryです。

各consumer repositoryは自身をVS Code workspace / Git rootとして直接開きます。このrepositoryはconsumer sourceを配下へcloneして管理する親workspaceではありません。

`agent-dev`の提供範囲、consumer責務、versioning、update、release contractは[共通Dev Container Feature](docs/dev-container-feature.md)を正本とします。

## Consumer workflow

GHCRへ公開されたFeatureは、consumer側の`.devcontainer/devcontainer.json`から参照します。

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

consumer repositoryでは`.devcontainer-lock.json`をcommitします。詳細な利用手順は[共通Dev Container Feature](docs/dev-container-feature.md#consumer-workflow)を参照してください。

Claude / CodexのGitHub write identityをHumanから分離する場合は、AgentごとのGitHub Appと`agent-github-auth`を利用します。permissions、private key、token lifecycle、Ruleset前提は[GitHub Agent identity](docs/github-agent-identity.md)を参照してください。

## Authoring workflow

このrepository自身も公開済み`agent-dev:1`を利用します。`.devcontainer-lock.json`は開発環境として使う公開済みartifactを固定し、編集中の`src/agent-dev/`は自己参照しません。

```bash
make validate
make test
```

開発中Featureの検証とself-hosting環境の更新手順は[共通Dev Container Feature](docs/dev-container-feature.md#authoring-workflow)を参照してください。

## Release

Featureは`main`からGitHub Actionsでreleaseします。手順とrelease contractは[共通Dev Container Feature](docs/dev-container-feature.md#release-workflow)を参照してください。

## Repository layout

```text
src/agent-dev/                    Featureの配布物
test/agent-dev/                   実container test
scripts/check-release-version.sh  release前のversion検証
.github/workflows/                CI / security / release
docs/dev-container-feature.md     consumer / version / releaseの正本
docs/github-agent-identity.md     GitHub Agent identityの正本
```

## Supporting documents

- Featureの利用・version・release: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- GitHub Agent identity: [docs/github-agent-identity.md](docs/github-agent-identity.md)
- trust boundaryとcredential: [SECURITY.md](SECURITY.md)
- repository変更時の制約: [AGENTS.md](AGENTS.md)
