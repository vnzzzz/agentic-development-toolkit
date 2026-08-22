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

repository accessは`Only select repositories`を安全側の推奨とします。`All repositories`を選択した場合、private keyを取得したprocessはinstallationが許可するrepository全体を対象に新しいInstallation Tokenを発行できます。

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

private keyはmode `0600`、current user ownershipを必須とします。workspace、Git repository、Feature artifact、named volumeへは保存しません。Dev Container rebuildで消えることを仕様とします。

GitHub App private keyの管理はGitHub公式資料を参照してください。

- [Managing private keys for GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps)

## Profile設定

App IDとApp slugはsecretではありません。profileごとに次のcommandで設定します。

```bash
agent-github-auth configure claude <APP_ID> <APP_SLUG>
agent-github-auth configure codex <APP_ID> <APP_SLUG>
```

設定は各profileの`config.json`へ保存されます。rebuild後はprivate keyと合わせて再設定します。

状態確認:

```bash
agent-github-auth status claude
```

`status`はprivate key、bot identity、current repositoryへのinstallation、repo-scoped Installation Tokenのmint / revokeを確認します。token値は表示しません。

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

session内では次を自動設定します。

- current repositoryだけにscopeしたGitHub App Installation Tokenを必要時に発行
- `gh`実行時に短命tokenを注入し、終了後best-effortでrevoke
- Git HTTPS credential helperから`git fetch` / `git push`へ短命tokenを供給
- lower-precedenceのGit credential helperをリセットし、Human credentialへのfallbackを禁止
- GitHub SSH remoteをsession内だけHTTPSへrewriteし、SSH identityへのfallbackを禁止
- Git Author / Committerを`{app-slug}[bot]`へ設定
- bot user IDをGitHub APIから解決し、GitHub公式形式のnoreply emailを使用

Installation Tokenはdisk、named volume、`gh auth` credential storeへ保存しません。固定tokenを長時間保持せず、`gh` / Git credential取得ごとに新しいrepo-scoped tokenをmintします。

GitHub App Installation Tokenの仕様はGitHub公式資料を参照してください。

- [Generating an installation access token for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)
- [Authenticating as a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app)

## Repository scope

runtime tokenはcurrent repositoryのnameを指定して発行します。

```text
Git remote origin
  -> owner/repository
  -> repository-scoped Installation Token
```

これは通常操作のblast radiusをcurrent repositoryへ縮小します。ただしprivate key自体へAgent processがアクセスできるため、private key compromiseに対する最終境界はGitHub App installationのrepository accessです。

そのため、repository scopeの強制をtoolkitだけへ依存せず、GitHub App installation側でも必要最小限にしてください。

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

## Security boundary

`agent-dev`が保証する範囲:

- Human PAT / Human `gh auth` credentialをAgent identityとして利用しない
- private keyをworkspace / repository / Feature artifact / named volumeへ保存しない
- Installation Tokenを永続化しない
- runtime tokenをcurrent repositoryへ限定する
- Agent App permissionを超える権限を作らない

利用者責任:

- GitHub App自体のpermissions
- App installation repository scope
- private keyの配置・保管・revoke / rotation
- trusted repositoryでのみcredential-access可能なAgent sessionを利用すること
- repository Ruleset / branch protection

Docker daemonを操作できる主体はcontainerやnamed volumeの境界を越えられるため、Docker daemonはtrust boundary外です。Agent ContainerへDocker socketをmountしないでください。詳細は[SECURITY.md](../SECURITY.md)を参照してください。
