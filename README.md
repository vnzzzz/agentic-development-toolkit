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

Dev Containerをbuildすると`.devcontainer-lock.json`が生成されます。このlockfileもGitで管理することで、`agent-dev:1`が更新されても、明示的に更新するまでは同じversionとdigestを利用できます。

更新を確認・適用する場合はDev Containers CLIを使います。

```bash
devcontainer outdated
devcontainer upgrade
```

更新後はlockfileの差分を確認し、Dev Containerをrebuildして動作確認します。導入方法、versioning、更新方法の詳細は[共通Dev Container Feature](docs/dev-container-feature.md)を参照してください。

## GitHubへの書き込みをエージェントごとに分ける

Claude CodeやCodexからGitHubへ書き込む際、個人のGitHubアカウントとは別に、エージェント専用のGitHub Appを使うことができます。`agent-github-auth`を利用すると、GitHub上の操作主体とGit commitのAuthor / CommitterをGitHub App botへ揃えられます。

設定方法や必要な権限、認証情報の扱い、Rulesetとの組み合わせは[GitHub Agent identity](docs/github-agent-identity.md)を参照してください。

## このリポジトリを開発する

このリポジトリ自身のDev Containerは、公開済みの`agent-dev:1`を利用します。編集中の`src/agent-dev/`を自身の開発環境へ直接読み込む構成にはしていません。

```bash
make validate
make test
```

Featureのsourceは`src/agent-dev/`、実際のcontainerを使うtestは`test/agent-dev/`にあります。releaseは`main`からGitHub Actionsで手動実行します。

## ドキュメント

- 導入方法、versioning、更新、release: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- GitHub Appによるエージェントのidentity分離: [docs/github-agent-identity.md](docs/github-agent-identity.md)
- credentialやtrust boundary: [SECURITY.md](SECURITY.md)
- このリポジトリの変更ルール: [AGENTS.md](AGENTS.md)
