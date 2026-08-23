# 共通Dev Container Feature

`agent-dev`は、Claude CodeとCodexを使う開発環境へ共通ツールと認証基盤を追加するDev Container Featureです。アプリケーション固有のランタイムや依存関係は各プロジェクトで管理します。

## 提供範囲

`agent-dev`は次を導入します。

- Node.js 22、GitHub CLI
- Claude Code / Codex CLIとVS Code拡張
- `vnzzzz/agent-skills`
- GitHub App認証用の`agent-github-auth`

各プロジェクトでは、アプリケーション固有のランタイム、依存関係、サービス、ポート、VS Code設定を管理します。GitHub Appの作成、権限、インストール先、秘密鍵もFeatureの管理対象外です。

インストール対象はDebian / Ubuntu系のDev Containerです。Dev Container Featureの仕様と作成方法は公式資料を参照してください。[^1][^2]

## 導入

`.devcontainer/devcontainer.json`からメジャーバージョンを参照します。

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

`.devcontainer-lock.json`もGitで管理すると、実際に利用するバージョンとdigestを固定できます。`agent-dev:1`は`2.x`へ自動移行しません。

GitHub Appによるエージェントごとの認証は[GitHub Appによるエージェント認証](github-agent-identity.md)を参照してください。認証情報の保管条件とセキュリティ境界は[SECURITY.md](../SECURITY.md)を正本とします。

## バージョン

FeatureとClaude Code / Codex CLIの既定バージョンは`src/agent-dev/devcontainer-feature.json`を正本とします。

- patch: 後方互換な修正、CLIのpatch更新
- minor: 後方互換な機能追加
- major: 利用側の変更が必要な破壊的変更

公開済みの特定バージョンは上書きしません。

## 開発とリリース

Featureの実装は`src/agent-dev/`、実コンテナを使うテストは`test/agent-dev/`にあります。

```bash
make validate
make test
```

リリース対象の変更ではFeatureのバージョンを更新し、PRで`feature-ci`と`security`が成功してからマージします。公開は`main`から`.github/workflows/release-feature.yml`を手動実行します。

リリースworkflowは、同じバージョンが未公開であることを確認できない場合は停止します。公開にはworkflow固有の`GITHUB_TOKEN`を使用します。

このリポジトリ自身のDev Containerは公開済み`agent-dev:1`を利用します。未公開バージョンを`.devcontainer-lock.json`へ先行反映しません。

## 参考資料

[^1]: [Dev Containers, Features](https://containers.dev/features)
[^2]: [Dev Containers, Authoring a Dev Container Feature](https://containers.dev/guide/author-a-feature)
