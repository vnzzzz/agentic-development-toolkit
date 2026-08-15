# 共通Dev Container Feature

`agent-dev`は、Claude CodeとCodexを利用するprojectで共通する開発環境をDev Container Featureとして提供します。

各projectは自身をVS Code workspace / Git repository rootとして直接開き、project固有runtimeやserviceだけをローカルの`.devcontainer/devcontainer.json`で定義します。

## 責務

`agent-dev`は次を管理します。

- Node.js 22とGitHub CLIを公式Dev Container Featureへの依存として導入する。
- Claude CodeとCodex CLIを既定のexact versionで導入する。
- `git`、`jq`、`make`、`shellcheck`、`unzip`、`zip`などの共通CLIを導入する。
- Claude Code、Codex、GitHub CLIの認証状態を相互に分離したnamed volumeへ保存する。
- Claude CodeとCodexのVS Code extensionを追加する。
- container作成後にpublic `vnzzzz/agent-skills` PluginをClaude CodeとCodexへ導入する。

Python、Go、project固有のNode.js設定、database、port、project固有extensionなどはconsumer repositoryの責務です。

現時点のFeature install scriptはDebian / Ubuntu系のDev Container imageを対象とします。

## 利用方法

初回GHCR release後は、各projectから次のように参照します。

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

project固有runtimeが必要な場合は、そのprojectの`features`へ追加します。`agent-dev`のためにproject sourceを別workspace配下へcloneする必要はありません。

consumer repositoryでは`.devcontainer-lock.json`をcommitし、実際に解決したFeature versionとdigestを固定します。

## 認証状態の永続化とsecurity boundary

Featureは次のnamed volumeをmountします。

- Claude Code: `agentic-dev-claude-${devcontainerId}`
- Codex: `agentic-dev-codex-${devcontainerId}`
- GitHub CLI: `agentic-dev-gh-${devcontainerId}`

`${devcontainerId}`はDev Containerごとに一意でrebuild間では安定するため、認証状態をrebuild後も保持しながら別Dev Containerとは分離できます。

Feature sourceやGHCR artifactにcredential、token、認証済みconfigを含めません。公開されるのはvolume名のpattern、container内のmount先、環境変数などの構成情報だけです。hostの`~/.ssh`や各CLIのcredential directoryをbind mountしません。

一方、認証済みDev Container内で同じuser権限により実行されるcodeは、そのcontainerの認証状態へアクセスできます。このため、信頼できるrepositoryだけで利用し、未確認のscriptやdependencyをcredential access可能な状態で実行しないことを前提とします。

認証状態を破棄する場合は対象Dev Containerを削除したうえで対応するnamed volumeを削除し、必要に応じてprovider側でもtoken/sessionをrevokeします。

## version管理

Feature自身は`src/agent-dev/devcontainer-feature.json`のSemVerで管理します。Claude CodeとCodex CLIの既定versionは同じmetadataに明示し、`package.json`のversion pinとCIで同期を検証します。

既定versionやFeatureの挙動を変更する場合はFeature versionも更新し、Feature CIで実containerへのinstallを確認してからreleaseします。

## Feature authoring

このrepository自身の`.devcontainer/`はbootstrap用の最小authoring環境であり、配布対象の`agent-dev`を自己参照しません。Node.js、GitHub CLI、Dev Container CLIを提供し、Feature本体の検証は`src/`と`test/`を直接対象にします。

静的検証は`make validate`、Dockerが利用できる環境での実container testは`make test`で実行します。GitHub Actionsでは同じFeatureを`devcontainer features test`で検証します。

## release

Featureの正本は`src/agent-dev/`です。releaseは`.github/workflows/release-feature.yml`をGitHub Actionsから`main`で手動実行します。

publishにはworkflow固有の`GITHUB_TOKEN`と`packages: write`を利用し、個人PATをCI secretとして保存しません。Dev Containers公式Actionが`src/`配下のFeatureをOCI artifactとしてGHCRへpublishします。

publish先は次です。

```text
ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev
```

初回publish後、匿名pullさせる場合はGitHub package settingsでvisibilityをpublicへ変更します。visibility変更はrelease workflowの責務には含めません。
