# Agentic Development Toolkit

Claude CodeとCodexを使う開発環境を共通化するためのDev Container Feature `agent-dev`を提供するリポジトリです。

`agent-dev`を導入すると、Claude Code / Codex CLI、GitHub CLI、[agent-skills](https://github.com/vnzzzz/agent-skills)、GitHub App認証用のコマンドなどをDev Containerへまとめて導入できます。アプリケーション固有のランタイムや依存関係、サービス設定は各プロジェクト側で管理します。

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

`.devcontainer-lock.json`もGitで管理することで、利用するFeatureのバージョンとdigestを固定できます。提供されるツールとバージョン方針は[共通Dev Container Feature](docs/dev-container-feature.md)を参照してください。

## GitHub操作をエージェントごとに分ける

Claude CodeやCodexからGitHubへ書き込む際、個人のGitHubアカウントとは別に、エージェント専用のGitHub Appを使うことができます。`agent-github-auth`を利用すると、GitHub上の操作主体とGit commitのAuthor / CommitterをGitHub App botへ揃えられます。

設定方法、必要な権限、認証情報の扱い、Rulesetとの組み合わせは[GitHub Appによるエージェント認証](docs/github-agent-identity.md)を参照してください。

## ドキュメント

- 提供範囲、バージョン方針、導入、更新、リリース: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- GitHub Appによるエージェントごとの操作主体の分離: [docs/github-agent-identity.md](docs/github-agent-identity.md)
- 認証情報とセキュリティ境界: [SECURITY.md](SECURITY.md)
- このリポジトリの変更ルール: [AGENTS.md](AGENTS.md)
