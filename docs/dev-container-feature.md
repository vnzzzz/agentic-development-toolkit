# 共通Dev Container Feature

`agent-dev`は、Claude CodeやCodexを使う開発環境へ既存ツールと認証設定を共通構成で導入するDev Container Featureです。プロジェクト固有のランタイムや依存関係は各プロジェクトで管理します。

## 提供範囲

### ツール

| 導入対象 | 現在の指定 | バージョン方針 | 備考 |
|---|---|---|---|
| Node.js | `22` | 22系の最新版 | `node:1` Featureから導入[^3] |
| GitHub CLI | `latest` | ビルド時点の最新版 | `github-cli:1` Featureから導入[^4] |
| Claude Code CLI | `2.1.229` | 完全固定 | `claudeCodeVersion`で上書き可能 |
| Codex CLI | `0.147.0` | 完全固定 | `codexVersion`で上書き可能 |
| Claude Code VS Code拡張 | `anthropic.claude-code` | 未固定 | Marketplace版を利用[^5] |
| ChatGPT VS Code拡張 | `openai.chatgpt` | 未固定 | Marketplace版を利用[^5] |
| [vnzzzz/agent-skills](https://github.com/vnzzzz/agent-skills) | 既定ブランチ | 未固定 | post-create時点の内容をClaude Code / Codexへ導入 |
| 基本ツール | OSパッケージリポジトリ | 未固定 | `git`、`curl`、`jq`、`make`、`openssl`、`shellcheck`、`unzip`、`zip`等 |

Claude Code / Codex CLIの既定値は`src/agent-dev/devcontainer-feature.json`を正本とし、インストール時に指定バージョンとの一致を確認します。

### 認証関連

| 機能 | 内容 |
|---|---|
| `agent-github-auth` | GitHub Appを使ってGitHub操作とcommitのAuthor / Committerをエージェント単位で分離 |
| 認証用ボリューム | Claude Code、Codex、GitHub CLIの認証領域を分離 |
| GitHub App設定領域 | エージェントごとのGitHub App設定を分離 |

認証情報の保存方式や寿命を含むセキュリティ境界は[SECURITY.md](../SECURITY.md)を正本とします。GitHub Appの設定方法は[GitHub Appによるエージェント認証](github-agent-identity.md)を参照してください。

### バージョン固定の範囲

`.devcontainer-lock.json`は`agent-dev`と依存Featureのバージョン、digestを固定します。Featureのインストール時に外部から解決するツール、post-createで取得する`vnzzzz/agent-skills`、VS Code Marketplaceの拡張機能は固定しません。[^6]

`agent-dev:1`は`2.x`へ自動移行しません。

対象はDebian / Ubuntu系のDev Containerです。Dev Container Featureの仕様は公式資料を参照してください。[^1][^2]

## 導入

`.devcontainer/devcontainer.json`の`features`に追加します。

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

## 更新

Dev Containers CLIで確認・更新します。

```bash
devcontainer outdated
devcontainer upgrade
```

更新後は`.devcontainer-lock.json`の差分を確認し、Dev Containerを再ビルドします。

## agent-devのバージョン

`agent-dev`はSemVerで管理します。

- patch: 後方互換な修正、CLIのpatch更新
- minor: 後方互換な機能追加
- major: 利用側の変更が必要な破壊的変更

公開済みの特定バージョンは上書きしません。

<a id="release-workflow"></a>

## 開発とリリース

実装は`src/agent-dev/`、実コンテナを使うテストは`test/agent-dev/`にあります。

```bash
make validate
make test
```

リリース対象の変更ではFeatureのバージョンを更新し、`feature-ci`と`security`が成功してからマージします。公開は`main`から`.github/workflows/release-feature.yml`を手動実行します。

リリースworkflowは、同一バージョンが未公開と確認できない場合は停止します。公開にはworkflow固有の`GITHUB_TOKEN`を使用します。

このリポジトリ自身のDev Containerは公開済み`agent-dev:1`を利用し、未公開バージョンを`.devcontainer-lock.json`へ先行反映しません。

## 参考資料

[^1]: [Dev Container Specification, Features](https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-features.md)
[^2]: [Dev Containers, Authoring a Dev Container Feature](https://containers.dev/guide/author-a-feature)
[^3]: [Dev Containers Features, Node.js](https://github.com/devcontainers/features/tree/main/src/node)
[^4]: [Dev Containers Features, GitHub CLI](https://github.com/devcontainers/features/tree/main/src/github-cli)
[^5]: [Visual Studio Code, Supporting Remote Development](https://code.visualstudio.com/api/advanced-topics/remote-extensions)
[^6]: [Dev Container Specification, Lockfiles](https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-lockfile.md)
