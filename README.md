# Agentic Development Toolkit

Claude CodeとCodexを利用する複数projectへ、共通のDev Container Featureを配布するrepositoryです。

各consumer repositoryは自身をVS Code workspace / Git rootとして直接開きます。このrepositoryはconsumer sourceを配下へcloneして管理する親workspaceではありません。

## Scope

`agent-dev`は次を提供します。

- Node.js 22とGitHub CLI
- versionを固定したClaude Code / Codex CLI
- `git`、`jq`、`make`、`shellcheck`、`unzip`、`zip`などの共通CLI
- Claude Code / Codex / GitHub CLIの認証状態を保持するnamed volume
- Claude Code / CodexのVS Code extension
- public `vnzzzz/agent-skills` Pluginのbootstrap

Python、Go、database、port、project固有dependencyやextensionはconsumer repositoryで定義します。

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

consumer repositoryでは`.devcontainer-lock.json`をcommitし、解決したFeature versionとdigestを固定します。`agent-dev`の詳細な利用契約は[共通Dev Container Feature](docs/dev-container-feature.md)を参照してください。

## Authoring workflow

このrepository自身の`.devcontainer/`はFeature authoring用の最小環境です。未releaseの`agent-dev`を自己参照せず、`src/`と`test/`を直接検証します。

```bash
make validate
make test
```

`make validate`はmetadata、shell、CLI version整合、release version guardのtestを検証します。`make test`はさらに`devcontainer features test`で実containerへFeatureを導入します。

## Release

Feature versionは`src/agent-dev/devcontainer-feature.json`のSemVerで管理します。release前にversionを更新し、`main`から`release-feature` workflowを手動実行します。

workflowは同じexact versionがGHCRに存在する場合、またはGHCRの照会結果を判定できない場合に失敗します。既存versionを上書きしません。

```text
ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev
```

## Repository layout

```text
src/agent-dev/                 Featureの配布物
test/agent-dev/                実container test
scripts/check-release-version.sh  release前のversion検証
.github/workflows/             CI / security / release
docs/dev-container-feature.md  consumer / version / releaseの詳細
```

## Supporting documents

- Featureの利用・version・release: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- trust boundaryとcredential: [SECURITY.md](SECURITY.md)
- repository変更時の制約: [AGENTS.md](AGENTS.md)
