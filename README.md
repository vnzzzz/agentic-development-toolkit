# Agentic Development Toolkit

Claude CodeとCodexを使う開発環境を共通化するためのDev Container Feature `agent-dev`を提供するリポジトリです。

`agent-dev`を導入すると、Claude Code / Codex CLI、GitHub CLI、共通スキル、GitHub App認証用のコマンドなどをDev Containerへまとめて導入できます。アプリケーション固有のランタイムや依存関係、サービス設定は各プロジェクト側で管理します。

## プロジェクトで利用する

`.devcontainer/devcontainer.json`の`features`に`agent-dev`を追加します。

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:bookworm",
  "features": {
    "ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev:1": {}
  },
  "remoteUser": "vscode"
}
```

`.devcontainer-lock.json`もGitで管理することで、利用するFeatureのバージョンとdigestを固定できます。導入方法やバージョン管理の詳細は[共通Dev Container Feature](docs/dev-container-feature.md)を参照してください。

## GitHub操作をエージェントごとに分ける

Claude CodeやCodexからGitHubへ書き込む際、個人のGitHubアカウントとは別に、エージェント専用のGitHub Appを使うことができます。`agent-github-auth`を利用すると、GitHub上の操作主体とGit commitのAuthor / CommitterをGitHub App botへ揃えられます。

設定方法、必要な権限、認証情報の扱い、Rulesetとの組み合わせは[GitHub Agent identity](docs/github-agent-identity.md)を参照してください。

## ドキュメント

- 導入方法、バージョン管理、更新、リリース: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- GitHub Appによるエージェントごとの操作主体の分離: [docs/github-agent-identity.md](docs/github-agent-identity.md)
- 認証情報とセキュリティ境界: [SECURITY.md](SECURITY.md)
- このリポジトリの変更ルール: [AGENTS.md](AGENTS.md)
