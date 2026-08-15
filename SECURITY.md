# セキュリティポリシー

`agent-dev`はClaude Code、Codex、GitHub CLIを導入し、認証状態をDev Container内へ永続化します。認証済みcontainerで同じuser権限により実行されるcodeは、その認証状態へアクセスできるため、trusted repositoryでの利用を前提とします。

## Security constraints

- Feature source、test fixture、GHCR artifactへcredential、token、認証済みconfigを含めない。
- hostのcredential directory、SSH directory、Docker socketをbind mountしない。
- Claude Code、Codex、GitHub CLIの認証状態を相互に分離する。
- volume名へ`${devcontainerId}`を含め、Dev Container単位で認証状態を分離する。
- Claude Code / Codex CLIの既定versionを固定する。
- Node.js / GitHub CLIは公式Dev Container Featureへの依存として導入する。
- 外部GitHub Actionsはfull commit SHAへ固定する。
- release workflowの権限は`contents: read`と`packages: write`に限定する。
- 個人PATをrelease用CI secretとして保存しない。

## Credential boundary

Featureは次のnamed volumeを利用します。

- Claude Code: `agentic-dev-claude-${devcontainerId}`
- Codex: `agentic-dev-codex-${devcontainerId}`
- GitHub CLI: `agentic-dev-gh-${devcontainerId}`

volume名、container内mount先、環境変数は秘密情報ではありません。これらが公開されてもcredentialそのものはFeature sourceやGHCR artifactへ含まれません。

一方、認証済みcontainer内のcodeは同じuser権限で認証状態へアクセスできます。未確認のrepository、script、dependencyをcredential access可能な状態で実行しないでください。

認証状態を破棄する場合は対象Dev Containerを削除し、対応するnamed volumeを削除します。必要に応じてprovider側でもtoken / sessionをrevokeします。

## Release supply chain

releaseはGitHub Actionsの`GITHUB_TOKEN`でGHCRへpublishします。workflowはpublish前にexact Feature versionをGHCRへ問い合わせます。

- versionが既に存在する場合はreleaseを失敗させる。
- versionが存在しない場合だけpublishへ進む。
- authentication、network、registry responseなどの理由で存在判定できない場合もreleaseを失敗させる。

これにより、既存versionをmutable artifactとして差し替えません。release対象の変更では`src/agent-dev/devcontainer-feature.json`のSemVerを更新してください。

## Authoring boundary

このrepository自身の`.devcontainer/`はFeature authoring用の最小環境です。配布対象の`agent-dev`を自己参照せず、consumer repositoryを配下へcloneする親workspaceも持ちません。

実container testはDockerが利用できる環境またはGitHub Actionsで行います。distributed FeatureへDocker socket mountやprivileged設定を追加してtest環境を成立させません。

## Reporting

Issueへcredentialや機密sourceを貼り付けないでください。再現に必要な最小情報、関連version、機密情報を除去したcommand outputだけを共有してください。

## Supporting documents

- Featureのconsumer / release contract: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- repository変更時の制約: [AGENTS.md](AGENTS.md)
