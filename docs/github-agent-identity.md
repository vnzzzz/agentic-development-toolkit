# GitHub Agent identity

`agent-dev`は、Claude Code / CodexからGitHubへwriteする際にHuman credentialを流用せず、AgentごとのGitHub App bot identityを利用するための認証補助を提供します。

## Identity model

推奨するprincipal分離は次のとおりです。

```text
Human      -> GitHub user
Claude     -> dedicated GitHub App
Codex      -> dedicated GitHub App
ChatGPT    -> ChatGPT Codex Connector (supervised exception)
```

GitHub API上のactorとGit commitのAuthor / Committerは別のidentity layerです。`agent-github-auth`はGitHub App Installation Tokenとbot用Git identityを同時に設定し、`gh` / `git push` / `git commit`を同じApp botへ揃えます。

ChatGPT Codex Connectorのdirect writeは、このrepositoryでの実測ではHuman GitHub userとして記録されるため、専用App botとは分離できません。Human-supervisedな例外として扱います。

## GitHub Appの前提

Agentごとに専用GitHub Appを作成し、利用者自身でinstallation repository scopeとrepository permissionsを制御してください。

基本permissions:

```text
Metadata       read
Contents       read/write
Issues         read/write
Pull requests  read/write
```

必要な場合のみ:

```text
Actions          read
Checks           read
Commit statuses  read
```

既定では付与しません。

```text
Administration
Workflows
Secrets
Environments
Actions write
```

repository accessは`Only select repositories`を安全側の推奨とします。permission、installation scope、credentialのtrust boundaryは[SECURITY.md](../SECURITY.md)を正本とします。

GitHub Appの登録、permission、installation手順はGitHub公式資料を正本とします。

- [Registering a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app)
- [Choosing permissions for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)
- [Installing your own GitHub App](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app)

## Private key配置

Feature install時に次のcontainer-local directoryだけを作成します。

```text
~/.config/agent-dev/github-apps/
├── claude/
└── codex/
```

private keyは利用者がbuild / rebuild後に配置します。

```text
~/.config/agent-dev/github-apps/claude/private-key.pem
~/.config/agent-dev/github-apps/codex/private-key.pem
```

private keyはmode `0600`、current user ownershipを必須とし、symlinkは拒否します。このpathのcredential lifecycleと永続化要件は[SECURITY.md](../SECURITY.md)を参照してください。

GitHub App private keyの管理はGitHub公式資料を参照してください。

- [Managing private keys for GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps)

## Profile設定

profileにはApp IDだけを設定します。App slugは利用者入力を信用せず、private keyとApp IDで署名したApp JWTを使って`GET /app`から取得します。

```bash
agent-github-auth configure claude <APP_ID>
agent-github-auth configure codex <APP_ID>
```

App IDはsecretではありません。設定は各profileの`config.json`へ保存されます。

状態確認:

```bash
agent-github-auth status claude
```

`status`はprivate key、App JWTで取得したbot identity、current repositoryへのinstallation、repo-scoped Installation Tokenのmint / revokeを確認します。token値は表示しません。revokeに失敗した場合は成功扱いせず異常終了します。

## Agent session

Claude用session:

```bash
agent-github-auth claude
```

Codex用session:

```bash
agent-github-auth codex
```

特定commandだけを実行する場合:

```bash
agent-github-auth claude -- claude
agent-github-auth codex -- codex
```

session activationはApp credentialの排他利用をpreflightします。`GH_TOKEN` / `GITHUB_TOKEN` / `GH_ENTERPRISE_TOKEN` / `GITHUB_ENTERPRISE_TOKEN`が既に設定されている場合、または永続`gh auth`設定に既知のaccountが存在する場合はsessionを開始しません。credentialの出所を推測してshadowするのではなくfail closedします。Humanとして`gh`を使う環境とAgent App sessionを同時に成立させないことが前提です。

session開始時に`origin`からrepositoryを解決し、その`owner/repository`をsessionの認証対象として固定します。session中に別directoryへ`cd`してもtoken scopeは変更しません。`git -C`や`gh -R`などで別repositoryを指定しても、そのrepository用tokenを追加発行せず、認証対象外の操作はfail closedします。

session内では次を自動設定します。

- session開始時に選択したrepositoryだけを対象にGitHub App Installation Tokenを必要時に発行
- `gh`実行ごとに一時`GH_CONFIG_DIR`を作り、永続化されたHuman用GitHub CLI credential / alias / extension configを参照しない
- `gh`のhostを`github.com`、default repositoryをsession repositoryへ固定し、Enterprise token環境変数とinteractive promptを無効化
- `gh` command終了時にtokenをbest-effortでrevokeし、一時config directoryを削除
- `git fetch` / `git pull` / `git push` / `git ls-remote`は専用wrapperでGit process全体に1つの短命tokenを供給し、process終了時にbest-effortでrevoke
- Git credential helperはwrapperが供給したprocess-local tokenだけを返し、`github.com`かつsession repositoryのHTTPS pathが一致する場合だけcredentialを供給
- lower-precedenceのGit credential helperと`http.extraHeader`をresetし、既存Human Authorization headerへのfallbackを禁止
- GitHub SSH remoteをsession内だけHTTPSへrewriteし、Git SSH / askpassを無効化してSSH identityへのfallbackを禁止
- App JWTで認証されたApp metadataからslugを取得
- Git Author / Committerを`{app-slug}[bot]`へ設定
- bot user IDをGitHub APIから解決し、GitHub公式形式のnoreply emailを使用

local-onlyなGit commandはInstallation Tokenを発行せず、実際にremote認証が必要な上記commandだけをwrapper対象とします。credentialの保存可否、token lifecycle、private key compromise時の境界は[SECURITY.md](../SECURITY.md)を正本とします。

`agent-github-auth`はGitHub.comだけを対象とします。GitHub Enterprise Server向けの保存済みcredentialや`GH_HOST`をApp sessionへ持ち込みません。

GitHub Appの認証とInstallation Tokenの仕様はGitHub公式資料を参照してください。

- [Authenticating as a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app)
- [Generating an installation access token for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)
- [REST API endpoints for GitHub Apps](https://docs.github.com/en/rest/apps/apps)
- [GitHub CLI environment variables](https://cli.github.com/manual/gh_help_environment)
- [GitHub CLI authentication status](https://cli.github.com/manual/gh_auth_status)

## Repository scope

runtimeではsession activation時のGit remote `origin`からrepositoryを解決し、そのrepository名をsessionの認証対象として固定してInstallation Tokenを発行します。

```text
Git remote origin at activation
  -> owner/repository
  -> freeze as session repository
  -> repository-scoped Installation Token
```

repository選択を各wrapperのcurrent working directoryから再計算しないため、session中の`cd`や`git -C`で意図せずtoken scopeが変わることはありません。別repositoryを操作する場合は、そのrepositoryで新しい`agent-github-auth` sessionを開始します。

このruntime behaviorとGitHub App installation scopeの関係、保証範囲は[SECURITY.md](../SECURITY.md)を参照してください。

## Repository rules

Agent Appへdefault / protected branchのbypassを与えないでください。repository側では少なくとも次をGitHub Rulesetで強制します。

- default branchへのPull Request必須
- required status checks
- force push禁止
- branch deletion禁止
- Agent Appによるdefault branch直接更新禁止

RulesetはFeatureが自動作成しません。GitHub側のrepository security controlとして管理してください。

- [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Creating rulesets for a repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)

## Security

credential persistence、Human credentialの扱い、GitHub App permission / installation scope、private key、Docker daemon、trusted repositoryを含むtrust boundaryは[SECURITY.md](../SECURITY.md)を唯一の正本とします。このdocumentでは操作方法とidentityの挙動だけを定義し、別のsecurity contractを持ちません。
