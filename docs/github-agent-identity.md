# GitHub Appによるエージェント認証

`agent-github-auth`は、Claude Code / CodexのGitHub操作を個人アカウントから分離し、エージェント専用のGitHub App botとして実行するためのコマンドです。

GitHub API上の操作主体とGit commitのAuthor / Committerは別ですが、このコマンドは両方を同じApp botへ揃えます。

## 構成

| 操作主体 | GitHub上のidentity |
|---|---|
| 個人の操作 | GitHub user |
| Claude Code | Claude専用GitHub App |
| Codex | Codex専用GitHub App |

エージェントごとに専用GitHub Appを作成し、repository accessとpermissionsをGitHub側で制御します。Appの作成、権限設定、インストール方法はGitHub公式資料を参照してください。[^1][^2][^3]

基本permissionsは次のとおりです。

```text
Metadata       read
Contents       read/write
Issues         read/write
Pull requests  read/write
```

`Actions` / `Checks` / `Commit statuses` は必要な場合のみreadを追加します。`Administration` / `Workflows` / `Secrets` / `Environments` / `Actions write` は既定では付与しません。

repository accessは`Only select repositories`を推奨します。認証情報と権限境界の詳細は[SECURITY.md](../SECURITY.md)を正本とします。

## 設定

profileにはApp IDだけを保存します。

```bash
agent-github-auth configure claude <APP_ID>
agent-github-auth configure codex <APP_ID>
```

private keyは次へ配置します。

```text
~/.config/agent-dev/github-apps/claude/private-key.pem
~/.config/agent-dev/github-apps/codex/private-key.pem
```

private keyはmode `0600`、current user ownershipが必要です。Dev Containerをrebuildすると消えるため、rebuild後は再配置します。

設定確認:

```bash
agent-github-auth status claude
```

`status`はApp、current repositoryへのinstallation、repository限定Installation Tokenの発行とrevokeを確認します。token値は表示しません。GitHub App認証とInstallation Tokenの仕様は公式資料を参照してください。[^4][^5]

## セッション

interactive session:

```bash
agent-github-auth claude
```

特定commandだけを実行する場合:

```bash
agent-github-auth claude -- claude
agent-github-auth codex -- codex
```

セッション開始時の`origin`を認証対象repositoryとして固定します。別repositoryを操作する場合は、そのrepositoryで新しいセッションを開始します。

セッションでは次を強制します。

- `gh` / 認証が必要なGit操作ごとに短命Installation Tokenを発行し、diskへ保存しない
- `gh` / Git / commit Author / Committerを同じApp botへ揃える
- 個人の`gh auth`、ambient token、既存Git credentialへfallbackしない
- `github.com`以外を対象とする`gh`操作を拒否する
- 別のAuthorization header、credential helper、credential埋め込みURLが有効な場合はfail closedとする
- GitHub SSHやinteractive credential promptへfallbackしない

App tokenを利用するGit commandは`fetch` / `pull` / `push` / `ls-remote`に限定します。Git alias経由のnetwork operationはサポートしません。

private key compromise時を含むセキュリティ境界は[SECURITY.md](../SECURITY.md)を参照してください。

## Ruleset

GitHub Appにはdefault branchのbypassを与えません。repository側では少なくとも次をRulesetで強制します。

- Pull Request必須
- required status checks
- force push禁止
- branch deletion禁止
- GitHub Appによるdefault branch直接更新禁止

Rulesetは`agent-dev`から自動作成しません。設定方法はGitHub公式資料を参照してください。[^6][^7]

## 参考資料

[^1]: [GitHub Docs, Registering a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app)
[^2]: [GitHub Docs, Choosing permissions for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)
[^3]: [GitHub Docs, Installing your own GitHub App](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app)
[^4]: [GitHub Docs, Authenticating as a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app)
[^5]: [GitHub Docs, Generating an installation access token for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)
[^6]: [GitHub Docs, About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
[^7]: [GitHub Docs, Creating rulesets for a repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)
