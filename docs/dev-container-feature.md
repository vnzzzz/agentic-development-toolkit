# 共通Dev Container Feature

`agent-dev`は、Claude CodeとCodexを利用するプロジェクトで共通する開発環境をDev Container Featureとして提供します。

各プロジェクトは自身をVS Code workspaceおよびGit repository rootとして開き、プロジェクト固有のruntimeやserviceだけをローカルの`.devcontainer/devcontainer.json`で定義します。

## 責務

`agent-dev`は次を管理します。

- Node.js 22とGitHub CLIを公式Dev Container Featureへの依存として導入する。
- Claude CodeとCodex CLIを既定のexact versionで導入する。
- `git`、`jq`、`make`、`shellcheck`、`unzip`、`zip`などの共通CLIを導入する。
- Claude Code、Codex、GitHub CLIの認証状態を相互に分離したnamed volumeへ保存する。
- Claude CodeとCodexのVS Code extensionを追加する。
- container作成後にpublic `vnzzzz/agent-skills` PluginをClaude CodeとCodexへ導入する。

Python、Go、project固有のNode.js設定、database、port、project固有extensionなどは各projectの責務です。

現時点のFeature install scriptはDebian / Ubuntu系のDev Container imageを対象とします。

## 利用方法

repositoryを`vnzzzz/agentic-development-toolkit`へrenameし、FeatureをGHCRへ公開した後は、各projectから次のように参照します。

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

`${devcontainerId}`はDev Containerごとに一意で、rebuild間では安定するため、認証状態をrebuild後も保持しながら別Dev Containerとは分離できます。

Feature sourceやGHCR artifactにcredential、token、認証済みconfigを含めません。公開されるのはvolume名のpattern、container内のmount先、環境変数などの構成情報だけです。hostの`~/.ssh`や各CLIのcredential directoryをbind mountしません。

一方、認証済みDev Container内で同じuser権限により実行されるcodeは、そのcontainerの認証状態へアクセスできます。このため、認証volumeを利用するDev Containerでは信頼できるrepositoryだけを開き、未確認のscriptやdependencyをcredential access可能な状態で実行しないことを前提とします。

認証状態を破棄する場合は対象Dev Containerを削除したうえで対応するnamed volumeを削除し、必要に応じて各provider側でもtoken/sessionをrevokeします。

## version管理

Feature自身は`src/agent-dev/devcontainer-feature.json`のSemVerで管理します。Claude CodeとCodex CLIの既定versionも同じmetadataに明示し、再現性のない`latest` installを避けます。

既定versionを更新する場合はFeature versionも更新し、Feature CIで実containerへのinstallを確認してからreleaseします。

## release

Featureの正本は`src/agent-dev/`です。releaseは`.github/workflows/release-feature.yml`をGitHub Actionsから手動実行します。

release workflowは次の条件を満たす場合だけpublishします。

- default branchの`main`から実行している。
- repository名が`vnzzzz/agentic-development-toolkit`である。

publishにはworkflow固有の`GITHUB_TOKEN`と`packages: write`を利用し、個人PATをCI secretとして保存しません。Dev Containers公式Actionが`src/`配下のFeatureをOCI artifactとしてGHCRへpublishします。

publish先は次です。

```text
ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev
```

GHCRでは初回publishしたpackageはprivateです。匿名pull可能にする場合は、初回publish後にGitHubのpackage settingsでvisibilityをpublicへ変更します。visibility変更はrelease workflowの責務には含めません。
