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

## Authoring workflow

このrepository自身の`.devcontainer/`はFeature authoring用の最小環境です。未releaseの`agent-dev`を自己参照せず、`src/`と`test/`を直接検証します。

```bash
make validate
make test
```

## Release

Featureは`main`からGitHub Actionsでreleaseします。手順とrelease contractは[共通Dev Container Feature](docs/dev-container-feature.md#release-workflow)を参照してください。

## Repository layout

```text
src/agent-dev/                    Featureの配布物
test/agent-dev/                   実container test
scripts/check-release-version.sh  release前のversion検証
.github/workflows/                CI / security / release
docs/dev-container-feature.md     consumer / version / releaseの正本
```

## Supporting documents

- Featureの利用・version・release: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- trust boundaryとcredential: [SECURITY.md](SECURITY.md)
- repository変更時の制約: [AGENTS.md](AGENTS.md)
