# 共通Dev Container Feature

`agent-dev`は、Claude CodeとCodexを利用するprojectへ共通開発環境を追加するDev Container Featureです。

consumer repositoryは自身をVS Code workspace / Git rootとして直接開きます。`agent-dev`はproject固有runtimeを置き換えず、Agent開発に共通するtoolと認証状態だけを追加します。

## Scope

`agent-dev`は次を提供します。

- Node.js 22
- GitHub CLI
- versionを固定したClaude Code / Codex CLI
- `git`、`jq`、`make`、`shellcheck`、`unzip`、`zip`などの共通CLI
- Claude Code / Codex / GitHub CLIの認証状態を保持するnamed volume
- GitHub App bot identityで`gh` / `git`を実行する`agent-github-auth`
- Claude Code / CodexのVS Code extension
- container作成後のpublic `vnzzzz/agent-skills` Plugin bootstrap

現時点のinstall scriptはDebian / Ubuntu系Dev Container imageを対象とします。

次はconsumer repositoryの責務です。

- Python、Goなどのproject runtime
- project固有のNode.js設定
- database、service、port
- project固有dependency
- project固有VS Code extension / setting
- GitHub Appの作成、repository installation scope、permissions、private key管理

## Consumer workflow

1. `.devcontainer/devcontainer.json`からmajor versionを参照します。

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

2. Dev Containerをbuildし、生成された`.devcontainer-lock.json`をcommitします。
3. 必要に応じてClaude Code、Codex、GitHub CLIへloginします。
4. Agent専用GitHub Appを使用する場合は[GitHub Agent identity](github-agent-identity.md)に従ってprofileとprivate keyを設定します。
5. project固有runtimeやserviceはconsumer側のDev Container設定へ追加します。

`agent-dev:1`のようにmajor versionを指定しても、lockfileが実際に解決したFeature versionとdigestを固定します。GHCR側の`1` tagが更新されても、lockfileを更新するまで既存projectのbuildは同じartifactを利用します。

## Security

credential、named volume、host mount、trusted repositoryに関する要件とtrust boundaryは[SECURITY.md](../SECURITY.md)を正本とします。`agent-dev`を利用する前に同文書を確認してください。

## GitHub Agent identity

FeatureはPATH上に`agent-github-auth`を提供します。profileにはApp IDだけを設定し、App slug / bot identityは認証済みApp metadataから自動取得します。

```bash
agent-github-auth configure claude <APP_ID>
agent-github-auth configure codex <APP_ID>
```

GitHub App private keyはbuild後に次へ配置し、mode `0600`にします。

```text
~/.config/agent-dev/github-apps/claude/private-key.pem
~/.config/agent-dev/github-apps/codex/private-key.pem
```

確認:

```bash
agent-github-auth status claude
```

Agent session:

```bash
agent-github-auth claude
agent-github-auth codex -- codex
```

session内では`gh`とGit HTTPS credentialがGitHub Appのrepo-scoped Installation Tokenを必要時に取得し、Git Author / Committerも同じApp botへ設定されます。Human GitHub credentialへのfallbackは行いません。

private keyはnamed volumeへ保存せず、Dev Container rebuildで消えます。詳細なpermissions、credential lifecycle、repository scope、Ruleset要件は[GitHub Agent identity](github-agent-identity.md)を参照し、trust boundaryは[SECURITY.md](../SECURITY.md)を正本とします。

## Versioning

Feature versionとClaude Code / Codexの既定versionは`src/agent-dev/devcontainer-feature.json`を唯一の正本として管理します。

- patch: bug fix、CLI patch更新など後方互換な修正
- minor: 後方互換な機能追加
- major: consumer側の変更が必要なbreaking change

Agent CLIの既定version更新はFeature contractの変更として手動で行います。npm dependency manifestやDependabot PRへversionを複製しません。install scriptはFeature optionで指定されたexact versionを導入し、導入後にversion一致を検証します。

published exact versionはimmutableとして扱います。同じ`1.0.0`を異なる内容で再publishしません。

## Consumer update

新しいFeature versionが公開されても、commit済みlockfileは自動では変わりません。

更新候補の確認:

```bash
devcontainer outdated
```

lockfileの更新:

```bash
devcontainer upgrade
```

更新後はconsumer repositoryのCIでDev Container buildを確認し、lockfile差分を通常のcode changeとしてreviewします。major versionを`1`で指定しているconsumerは`2.x`へ自動移行しません。

## Release workflow

Featureの正本は`src/agent-dev/`です。releaseは`.github/workflows/release-feature.yml`を`main`から手動実行します。

1. release対象の変更で`devcontainer-feature.json`のSemVerを更新する。
2. `make validate`を実行する。
3. Dockerが利用できる場合は`make test`を実行する。
4. PRをmergeする。
5. `main`から`release-feature` workflowを実行する。
6. workflowがGHCRに同じexact versionが存在しないことを検証する。
7. Dev Containers公式ActionでGHCRへpublishする。

publish先:

```text
ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev
```

release workflowは`GITHUB_TOKEN`と`packages: write`を利用します。個人PATは使用しません。

version確認はfail-closedです。

- exact versionが既に存在する: release失敗
- exact versionが存在しない: publishへ進む
- registryの照会結果を判定できない: release失敗

consumerやこのrepository自身が認証なしで利用するには、Feature collection metadata packageと`agent-dev` packageの両方がPublicであることをPackage settingsで確認します。

## Authoring workflow

このrepository自身の`.devcontainer/`も、GHCRへ公開済みの`agent-dev:1`を利用します。commit済み`.devcontainer-lock.json`が開発環境として使うexact versionとdigestを固定します。

これは循環依存ではありません。Featureの配布境界は`src/agent-dev/`だけであり、repositoryの`.devcontainer/`はartifactへ含まれません。self-hosting側は既にpublish済みartifactをconsumeし、編集中のFeature sourceを直接参照しません。

次versionを開発している間も、toolkit自身のDev Containerは直前に採用した公開済みversionを使います。候補versionは次のコマンドでsourceから別containerへ導入して検証します。

静的検証:

```bash
make validate
```

実container test:

```bash
make test
```

`make validate`は次を検証します。

- Feature metadata JSON
- shell syntax / ShellCheck
- release version guardの分岐

`make test`はさらに`devcontainer features test`で編集中のFeature sourceを別containerへ導入し、Agent CLI、`agent-skills` Plugin bootstrap、認証volume、GitHub App auth toolingの導入とfail-closed behaviorを確認します。

新しいFeature versionをreleaseした後、このrepository自身でも採用する場合は別changeとして`devcontainer upgrade`を実行し、`.devcontainer-lock.json`の差分をreviewします。未公開versionへself-hosting lockfileを先行更新しません。

## Supporting documents

- repositoryの入口: [README.md](../README.md)
- trust boundaryとcredential: [SECURITY.md](../SECURITY.md)
- GitHub Agent identity: [github-agent-identity.md](github-agent-identity.md)
- repository変更時の制約: [AGENTS.md](../AGENTS.md)
