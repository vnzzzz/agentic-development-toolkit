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
- Agent identityにはHuman PAT / Human `gh auth` credentialを流用しない。
- Agentごとに専用GitHub Appを使用し、least privilegeとrepository installation scopeを利用者側で設定する。
- GitHub App private keyをworkspace、repository、GHCR artifact、named volumeへ保存しない。
- GitHub App Installation Tokenをdiskやcredential storeへ永続保存しない。

## Credential boundary

Featureは次のnamed volumeを利用します。

- Claude Code: `agentic-dev-claude-${devcontainerId}`
- Codex: `agentic-dev-codex-${devcontainerId}`
- GitHub CLI: `agentic-dev-gh-${devcontainerId}`

volume名、container内mount先、環境変数は秘密情報ではありません。これらが公開されてもcredentialそのものはFeature sourceやGHCR artifactへ含まれません。

一方、認証済みcontainer内のcodeは同じuser権限で認証状態へアクセスできます。未確認のrepository、script、dependencyをcredential access可能な状態で実行しないでください。

認証状態を破棄する場合は対象Dev Containerを削除し、対応するnamed volumeを削除します。必要に応じてprovider側でもtoken / sessionをrevokeします。

## GitHub Agent identity

Claude / CodexからGitHubへwriteする場合は、Agentごとの専用GitHub Appを利用します。GitHub Appの作成、repository installation scope、repository permissions、private key rotationは利用者責任です。

`agent-github-auth`用private keyは次のcontainer-local pathへ利用者が配置します。

```text
~/.config/agent-dev/github-apps/<profile>/private-key.pem
```

このpathはnamed volumeではありません。private keyはDev Container rebuildで消えることを仕様とし、workspaceやGit管理対象へ退避しません。mode `0600`かつcurrent user ownershipを必須とし、symlinkは拒否します。

認証sessionではactivation時のrepositoryだけにscopeした短命Installation Tokenを必要時に発行し、`gh` / Git HTTPS credentialへ供給します。tokenはdisk、named volume、`gh auth` credential storeへ保存しません。

App sessionはcredential sourceを排他的にします。`GH_TOKEN` / `GITHUB_TOKEN` / Enterprise token環境変数が既に設定されている場合、または永続`gh auth`設定に既知のaccountが存在する場合はsessionを開始しません。Human credentialをshadowして継続するのではなくfail closedします。

App-authenticated `gh`は永続化されたHuman用`GH_CONFIG_DIR`を参照せず、commandごとの一時config directoryを使用します。hostは`github.com`、default repositoryはactivation時のrepositoryに固定し、Enterprise用token環境変数とinteractive promptを無効化します。

Gitはsession内でlower-precedence credential helperをresetし、`credential.useHttpPath`でactivation時repositoryのpath一致を要求します。lower-precedenceの`http.extraHeader`も空値でresetし、GitHub接続でSSH credentialへfallbackしないよう`GIT_SSH_COMMAND`とaskpassを無効化します。

これらはHuman credentialを誤利用しないためのworkflow guardです。認証済みcontainer内のAgent processはprivate keyを読めるため、同一user processを敵対的にsandboxする機構ではありません。private key compromise時の最終的なrepository blast radiusはGitHub App installation scopeです。runtime tokenのrepository scopeはdefense-in-depthであり、installation scopeの代替ではありません。

`agent-github-auth`はGitHub.comのみを対象とし、App JWT / Installation Token発行先APIを利用者環境変数から変更しません。

GitHub Agent identityのpermissions、利用方法、Ruleset前提は[GitHub Agent identity](docs/github-agent-identity.md)を参照してください。

Docker daemonを操作できる主体はcontainerやnamed volumeの境界を越えられます。Docker socketをAgent Containerへmountしない現行方針を維持します。

## Release supply chain

published exact Feature versionは、supply-chain上の識別子としてimmutableに扱います。release workflowは最小権限の`GITHUB_TOKEN`を使用し、外部Actionをfull commit SHAへ固定します。

version判定、失敗条件、publish手順などのrelease behaviorは[共通Dev Container Feature](docs/dev-container-feature.md#release-workflow)を正本とします。

## Authoring boundary

このrepository自身の`.devcontainer/`はFeature authoring用の最小環境です。配布対象の`agent-dev`を自己参照せず、consumer repositoryを配下へcloneする親workspaceも持ちません。

実container testはDockerが利用できる環境またはGitHub Actionsで行います。distributed FeatureへDocker socket mountやprivileged設定を追加してtest環境を成立させません。

## Reporting

Issueへcredentialや機密sourceを貼り付けないでください。再現に必要な最小情報、関連version、機密情報を除去したcommand outputだけを共有してください。

## Supporting documents

- Featureのconsumer / release contract: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- GitHub Agent identity: [docs/github-agent-identity.md](docs/github-agent-identity.md)
- repository変更時の制約: [AGENTS.md](AGENTS.md)
