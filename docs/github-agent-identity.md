# GitHub Agent identity

`agent-dev`は、Claude Code / CodexのGitHub writeをHuman credentialから分離し、AgentごとのGitHub App bot identityで実行します。

## Identity model

| Principal | GitHub identity |
|---|---|
| Human | GitHub user |
| Claude | dedicated GitHub App |
| Codex | dedicated GitHub App |
| ChatGPT | ChatGPT Codex Connector。現状はHuman-supervised exception |

GitHub API上のactorとGit commitのAuthor / Committerは別ですが、`agent-github-auth`は両方を同じApp botへ揃えます。

## GitHub Appの前提

Agentごとに専用GitHub Appを作成し、repository accessとpermissionsを利用者側で制御します。

基本permissions:

```text
Metadata       read
Contents       read/write
Issues         read/write
Pull requests  read/write
```

必要な場合のみ `Actions` / `Checks` / `Commit statuses` のreadを追加します。`Administration` / `Workflows` / `Secrets` / `Environments` / `Actions write` は既定で付与しません。

repository accessは`Only select repositories`を推奨します。詳細なtrust boundaryは[SECURITY.md](../SECURITY.md)を正本とします。

GitHub Appの作成・permission・installationはGitHub公式資料を参照してください。

- [Registering a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app)
- [Choosing permissions for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)
- [Installing your own GitHub App](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app)

## Setup

profileにはApp IDだけを保存します。App slugとbot identityは認証済みApp metadataから取得します。

```bash
agent-github-auth configure claude <APP_ID>
agent-github-auth configure codex <APP_ID>
```

build / rebuild後にprivate keyを配置します。

```text
~/.config/agent-dev/github-apps/claude/private-key.pem
~/.config/agent-dev/github-apps/codex/private-key.pem
```

private keyはmode `0600`、current user ownershipが必要です。保管条件とlifecycleは[SECURITY.md](../SECURITY.md)を参照してください。

確認:

```bash
agent-github-auth status claude
```

`status`はApp identity、current repositoryへのinstallation、repo-scoped Installation Tokenのmint / revokeを確認します。token値は表示しません。

## Agent session

interactive session:

```bash
agent-github-auth claude
```

特定commandだけを実行:

```bash
agent-github-auth claude -- claude
agent-github-auth codex -- codex
```

session開始時の`origin`を認証対象repositoryとして固定します。session中に`cd`してもtoken scopeは変わりません。別repositoryを操作する場合は、そのrepositoryで新しいsessionを開始します。

sessionでは次を保証します。

- `gh` / authenticated Git operationごとに短命Installation Tokenを発行し、diskへ保存しない
- `gh` / `git push` / Git Author / Committerを同じApp bot identityへ揃える
- Human `gh auth`、ambient GitHub token、既存Git credentialへfallbackしない
- `github.com`以外の`gh` targetを拒否する
- authenticated Git operationで別のAuthorization header / credential helperやcredential埋め込みURLが有効ならfail closedする
- GitHub SSH / interactive credential promptへfallbackしない

App tokenを利用するGit commandはcanonicalな`fetch` / `pull` / `push` / `ls-remote`に限定します。Git aliasからnetwork operationを実行する形はサポートせず、canonical commandを使用します。

実装上のcredential guardやprivate key compromise時の境界は[SECURITY.md](../SECURITY.md)を正本とします。

GitHub App認証の仕様:

- [Authenticating as a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app)
- [Generating an installation access token for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)

## Repository rules

Agent Appへdefault branchのbypassを与えません。repository側ではRulesetで少なくとも次を強制します。

- Pull Request必須
- required status checks
- force push禁止
- branch deletion禁止
- Agent Appによるdefault branch直接更新禁止

RulesetはFeatureから自動作成しません。

- [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Creating rulesets for a repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)

## Security

credential persistence、Human credential、private key、installation scope、Docker daemonを含むtrust boundaryは[SECURITY.md](../SECURITY.md)を唯一の正本とします。
