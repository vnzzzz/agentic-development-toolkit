# セキュリティポリシー

`agent-dev`は認証情報を扱うため、trusted repositoryでの利用を前提とします。認証済みcontainer内で同じuser権限により実行されるcodeは、そのuserが読めるcredentialへアクセスできます。

## Invariants

- credential、token、認証済みconfigをFeature source、test fixture、GHCR artifactへ含めない。
- hostのcredential directory、SSH directory、Docker socketをbind mountしない。
- Claude Code、Codex、GitHub CLIの認証状態を分離する。
- Agent identityへHuman PAT / Human `gh auth` credentialを流用しない。
- GitHub writeにはAgentごとの専用GitHub Appを使用する。
- GitHub App private keyをworkspace、repository、GHCR artifact、named volumeへ保存しない。
- Installation Tokenをdiskやcredential storeへ永続保存しない。
- GitHub Appのpermissionsとinstallation repository scopeは利用者がleast privilegeで設定する。

## Credential storage

Claude Code、Codex、Human用GitHub CLIの認証状態はDev Containerごとのnamed volumeへ分離します。

```text
agentic-dev-claude-${devcontainerId}
agentic-dev-codex-${devcontainerId}
agentic-dev-gh-${devcontainerId}
```

named volumeはsecret vaultではありません。同じDocker daemonを操作できる主体はvolumeへアクセスできるため、Docker daemonをtrust boundaryとし、Agent ContainerへDocker socketをmountしません。

認証状態を破棄する場合はcontainerと対応volumeを削除し、必要に応じてprovider側でもsession / tokenをrevokeします。

## GitHub Agent identity

GitHub App private keyはcontainer-localな次のpathへ配置します。

```text
~/.config/agent-dev/github-apps/<profile>/private-key.pem
```

private keyはDev Container rebuildで消えることを仕様とします。credential directoryはmode `0700`、config / private keyはmode `0600`、current user ownershipを要求し、path途中を含むsymlinkを拒否します。

`agent-github-auth` sessionは次をfail-closedで保証します。

- activation時のrepositoryだけにscopeしたInstallation Tokenを発行する。
- ambient GitHub tokenや保存済みHuman `gh auth` accountと共存しない。
- `gh`は一時configを使い、`github.com`以外の明示targetをtoken発行前に拒否する。
- authenticated Git operationは別のAuthorization header / credential helperを検出したらtoken発行前に拒否する。
- GitHub SSH、interactive credential promptへfallbackしない。
- GitHub App API通信はuser curl configを読み込まずHTTPSだけを使用する。

これらはcredentialの誤利用を防ぐworkflow guardであり、同一user processをsandboxする機構ではありません。Agent processはprivate keyを読めるため、private key compromise時の最終的なrepository boundaryはGitHub App installation scopeです。runtime tokenのrepository scopeはdefense-in-depthです。

利用方法とGitHub App permissionsは[GitHub Agent identity](docs/github-agent-identity.md)を参照してください。

## Release supply chain

- Claude Code / Codex CLIの既定versionを固定する。
- Node.js / GitHub CLIは公式Dev Container Featureから導入する。
- 外部GitHub Actionsはfull commit SHAへ固定する。
- release workflowは`contents: read`と`packages: write`だけを使用し、個人PATを使わない。
- published exact Feature versionはimmutableとして扱う。

release behaviorは[共通Dev Container Feature](docs/dev-container-feature.md#release-workflow)を正本とします。

## Authoring boundary

repository自身の`.devcontainer/`は公開済みFeatureだけを利用し、編集中のFeature sourceを自己参照しません。実container testのためにdistributed FeatureへDocker socket mountやprivileged設定を追加しません。

## Reporting

Issueへcredentialや機密sourceを貼り付けません。再現に必要な最小情報と、機密情報を除去したoutputだけを共有してください。

## Supporting documents

- Feature contract: [docs/dev-container-feature.md](docs/dev-container-feature.md)
- GitHub Agent identity: [docs/github-agent-identity.md](docs/github-agent-identity.md)
- repository変更規則: [AGENTS.md](AGENTS.md)
