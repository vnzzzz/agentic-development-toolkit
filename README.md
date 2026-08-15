# Agentic Development Toolkit

Claude Code / Codex を利用する複数project向けに、共通のDev Container Featureを提供するrepositoryです。

各consumer repositoryは自身をVS Code workspace / Git rootとして直接開き、project固有runtimeやserviceだけを`.devcontainer/devcontainer.json`で定義します。このrepositoryはconsumer projectを`repos/`配下へcloneする親workspaceではありません。

## 提供するもの

- `src/agent-dev/`: 共通Dev Container Featureの正本
- `test/agent-dev/`: Featureの実container test
- `.github/workflows/feature-ci.yml`: metadata / shell / 実container検証
- `.github/workflows/release-feature.yml`: GHCRへのrelease
- `docs/dev-container-feature.md`: Featureの責務、利用方法、認証境界、release手順

`agent-dev`はNode.js 22、GitHub CLI、Claude Code、Codex、共通CLI、認証状態の永続化、`vnzzzz/agent-skills` Plugin bootstrapを提供します。Python、Go、database、port、project固有extensionなどはconsumer repositoryの責務です。

## 利用方法

初回release後は、consumer repositoryから次のように参照します。

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

consumer repositoryでは`.devcontainer-lock.json`をcommitし、解決したFeature versionとdigestを固定します。

## 開発

Feature authoring用の`.devcontainer/`は、このrepository自身のbootstrapに必要なNode.js、GitHub CLI、Dev Container CLIだけを提供します。配布対象の`agent-dev` Featureを自己参照しません。

静的検証:

```bash
make validate
```

Dockerが利用できる環境での実container test:

```bash
make test
```

CIでは`devcontainer features test`により、Featureのinstall、Agent CLI、`agent-skills` Plugin bootstrap、認証volumeの書き込み可能性まで検証します。

## Release

Feature versionは`src/agent-dev/devcontainer-feature.json`のSemVerで管理します。releaseは`main`から`release-feature` workflowを手動実行し、GHCRへpublishします。

```text
ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev
```

詳細は[共通Dev Container Feature](docs/dev-container-feature.md)と[セキュリティポリシー](SECURITY.md)を参照してください。
