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
- Claude Code / CodexのVS Code extension
- container作成後のpublic `vnzzzz/agent-skills` Plugin bootstrap

現時点のinstall scriptはDebian / Ubuntu系Dev Container imageを対象とします。

次はconsumer repositoryの責務です。

- Python、Goなどのproject runtime
- project固有のNode.js設定
- database、service、port
- project固有dependency
- project固有VS Code extension / setting

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
4. project固有runtimeやserviceはconsumer側のDev Container設定へ追加します。

`agent-dev:1`のようにmajor versionを指定しても、lockfileが実際に解決したFeature versionとdigestを固定します。GHCR側の`1` tagが更新されても、lockfileを更新するまで既存projectのbuildは同じartifactを利用します。

## Security

credential、named volume、host mount、trusted repositoryに関する要件とtrust boundaryは[SECURITY.md](../SECURITY.md)を正本とします。`agent-dev`を利用する前に同文書を確認してください。

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

初回publish時のpackageはprivateです。匿名pullさせる場合はGitHubのPackage settingsでpackage visibilityをpublicへ変更します。visibilityはpackage単位なので、同じpackageへ追加される後続versionごとにpublic化を繰り返す必要はありません。

## Authoring workflow

このrepository自身の`.devcontainer/`はFeature authoring用の最小環境です。未releaseの`agent-dev`を自己参照しません。

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

`make test`はさらに`devcontainer features test`でFeatureを実containerへ導入し、Agent CLI、`agent-skills` Plugin bootstrap、認証volumeの書き込み可能性を確認します。

## Supporting documents

- repositoryの入口: [README.md](../README.md)
- trust boundaryとcredential: [SECURITY.md](../SECURITY.md)
- repository変更時の制約: [AGENTS.md](../AGENTS.md)
