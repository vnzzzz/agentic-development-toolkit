# 共通Dev Container Feature

`agent-dev`は、Claude CodeとCodexを利用するprojectへ共通toolと認証基盤を追加するDev Container Featureです。consumer repositoryは自身をVS Code workspace / Git rootとして直接開き、project固有runtimeはconsumer側で管理します。

## Scope

Featureが提供するもの:

- Node.js 22、GitHub CLI、共通CLI
- version固定のClaude Code / Codex CLI
- Claude Code / Codex / Human用GitHub CLIの認証volume
- GitHub App bot identity用`agent-github-auth`
- Claude Code / CodexのVS Code extension
- public `vnzzzz/agent-skills` Plugin bootstrap

consumer側で管理するもの:

- Python、Go等のproject runtime
- project固有dependency、service、port、VS Code設定
- GitHub Appの作成、permissions、installation scope、private key

install scriptはDebian / Ubuntu系Dev Container imageを対象とします。

## Consumer workflow

`.devcontainer/devcontainer.json`からmajor versionを参照します。

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

build後に生成される`.devcontainer-lock.json`をcommitしてください。major tagが更新されても、lockfileを更新するまで既存projectは同じexact versionとdigestを利用します。

Claude Code / Codexは必要に応じてloginします。Humanの`gh auth login`とAgent App sessionは分離してください。

### GitHub Agent identity

profile設定:

```bash
agent-github-auth configure claude <APP_ID>
agent-github-auth configure codex <APP_ID>
```

private key配置:

```text
~/.config/agent-dev/github-apps/claude/private-key.pem
~/.config/agent-dev/github-apps/codex/private-key.pem
```

確認・起動:

```bash
agent-github-auth status claude
agent-github-auth claude
agent-github-auth codex -- codex
```

permissions、credential lifecycle、repository scope、Rulesetは[GitHub Agent identity](github-agent-identity.md)を参照してください。trust boundaryは[SECURITY.md](../SECURITY.md)を正本とします。

## Versioning

Feature versionとAgent CLIの既定versionは`src/agent-dev/devcontainer-feature.json`を正本とします。

- patch: 後方互換なbug fix / CLI patch更新
- minor: 後方互換な機能追加
- major: consumer側の変更が必要なbreaking change

published exact versionはimmutableです。同じversionを異なる内容で再publishしません。

## Consumer update

```bash
devcontainer outdated
devcontainer upgrade
```

更新後はlockfile差分とDev Container buildを通常のcode changeとしてreviewします。`agent-dev:1`を参照するconsumerは`2.x`へ自動移行しません。

## Release workflow

Feature sourceは`src/agent-dev/`です。release対象変更ではSemVerを更新し、PRで`feature-ci` / `security`が成功してからmergeします。

releaseは`main`から`.github/workflows/release-feature.yml`を手動実行します。workflowは次をfail closedで確認します。

- exact versionが未publishである
- version照会結果を判定できる
- publishにはworkflow固有`GITHUB_TOKEN`と`packages: write`だけを使用する

publish先:

```text
ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev
```

認証なしで利用する場合は、Feature collection metadata packageと`agent-dev` packageの両方をPublicにします。

## Authoring workflow

repository自身の`.devcontainer/`は公開済み`agent-dev:1`を利用し、編集中の`src/agent-dev/`を自己参照しません。

```bash
make validate
make test
```

- `make validate`: metadata、shell syntax / ShellCheck、release version guard
- `make test`: `devcontainer features test`による実container検証

未publish versionは別containerで検証します。release後にself-hosting環境へ採用する場合は、別changeで`devcontainer upgrade`して`.devcontainer-lock.json`をreviewします。

## Supporting documents

- repository入口: [README.md](../README.md)
- GitHub Agent identity: [github-agent-identity.md](github-agent-identity.md)
- trust boundary: [SECURITY.md](../SECURITY.md)
- repository変更規則: [AGENTS.md](../AGENTS.md)
