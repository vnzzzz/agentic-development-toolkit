# 共通Dev Container Feature

`agent-dev`は、Claude CodeとCodexを使う開発環境へ共通ツールと認証基盤を追加するDev Container Featureです。アプリケーション固有のランタイムや依存関係は各プロジェクトで管理します。

## 提供範囲

| 提供物 | 現在の指定 | バージョン方針 | 備考 |
|---|---|---|---|
| Node.js | `22` | 22系を利用。exact versionは固定しない | `node:1` Featureから導入[^3] |
| GitHub CLI | `latest` | build時のlatest | `github-cli:1` Featureから導入[^4] |
| Claude Code CLI | `2.1.229` | exact固定 | `claudeCodeVersion`で上書き可能 |
| Codex CLI | `0.147.0` | exact固定 | `codexVersion`で上書き可能 |
| Claude Code VS Code拡張 | `anthropic.claude-code` | version未固定 | Marketplace版を利用[^5] |
| ChatGPT VS Code拡張 | `openai.chatgpt` | version未固定 | Marketplace版を利用[^5] |
| [agent-skills](https://github.com/vnzzzz/agent-skills) | 既定branch | version未固定 | post-create時に取得してClaude Code / Codexへ導入 |
| `agent-github-auth` | `agent-dev`に同梱 | Feature versionに追従 | GitHub App認証用コマンド |

Claude Code / Codex CLIの既定値は`src/agent-dev/devcontainer-feature.json`を正本とし、install時に指定versionと実際のversionが一致することを確認します。

`.devcontainer-lock.json`は`agent-dev`と依存Featureのversion / digestを固定します。一方、依存Featureがbuild時に解決するツール、post-createで取得する`agent-skills`、VS Code Marketplaceから入る拡張機能までは固定しません。[^6]

GitHub Appの作成、権限、インストール先、秘密鍵はFeatureの管理対象外です。認証情報の扱いは[GitHub Appによるエージェント認証](github-agent-identity.md)と[SECURITY.md](../SECURITY.md)を参照してください。

インストール対象はDebian / Ubuntu系のDev Containerです。

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

`.devcontainer-lock.json`もGitで管理すると、利用するFeature artifactをversion / digestで固定できます。`agent-dev:1`は`2.x`へ自動移行しません。

## 更新

利用中のFeatureを更新する場合は、Dev Containers CLIで確認・更新します。

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
[^3]: [Dev Containers Features, Node.js](https://github.com/devcontainers/features/tree/main/src/node)
[^4]: [Dev Containers Features, GitHub CLI](https://github.com/devcontainers/features/tree/main/src/github-cli)
[^5]: [Visual Studio Code, Supporting Remote Development](https://code.visualstudio.com/api/advanced-topics/remote-extensions)
[^6]: [Visual Studio Code, Dev Container Feature lockfile](https://code.visualstudio.com/updates/v1_118#_dev-container-feature-lockfile)
