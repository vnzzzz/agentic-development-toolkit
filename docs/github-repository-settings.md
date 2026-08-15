# GitHub repository設定

GitHub Actionsのworkflow fileだけでは、branch protectionやrepository-level security featureを強制できません。親リポジトリと各Skill source repositoryはownershipが異なるため、それぞれが実際に持つCIとsecurity featureに合わせて設定します。

## 親リポジトリ

推奨設定は次のとおりです。

- `main`を保護し、親リポジトリで実際に存在する必須CI checkをrequired status checkに設定する。
- force pushと保護branchの削除を禁止する。
- 親が管理するdependencyについてDependabot alertsとsecurity updatesを有効にする。
- 利用可能なrepository plan / security productの範囲でsecret scanningとpush protectionを有効にする。
- GitHub Actionsで利用できるactionをGitHub-owned actionまたは明示したallowlistへ制限する。
- 初回のexternal contributorが実行するworkflowにはapprovalを要求する。
- `GITHUB_TOKEN`のdefault permissionはread-onlyを基本とし、write permissionが必要なworkflowだけ`permissions`で明示的に追加する。

親のDependabot設定は親リポジトリが管理するmanifestだけを対象とします。親Gitからignoreされる`repos/*`配下のsource repositoryは更新しません。

## Skillソースリポジトリ

各source repositoryは、自身の実装とrelease lifecycleに合わせて次を設定します。

- required status check
- dependency update
- code scanning
- secret scanning / push protection
- release protection
- branch protection
- collaborator access

Dependabot設定も各source repository内に置き、そのrepositoryが所有するmanifestを対象にします。

## GitHub Code Security関連check

このリポジトリのsecurity workflowでは、利用可能なGitHub security featureに応じて一部jobを実行します。

public repositoryではCode Securityの一部機能を追加契約なしで利用できます。private / internal repositoryでは、organizationのplanとGitHub Code Security / Secret Protection等の有効化状況に依存します。

private repositoryでこのリポジトリのGitHub Advanced Security系checkを有効にする場合は、必要なsecurity productがrepositoryで利用可能であることを確認した上で、repository variableを設定します。

```text
ENABLE_GHAS_CHECKS=true
```

この条件を満たさないprivate repositoryでは対象jobをskipし、portableな親checkだけを継続して実行します。

## 将来child revisionを固定する場合

現在、親リポジトリはGit submoduleを使用せず、`repos/*`のchild commitを記録しません。

将来、review済みchild commitを親から再現可能に固定する要件が生じた場合は、その時点でcheckout / update方式を設計し、ADRとして記録します。現時点では将来要件のためだけにpinning mechanismを追加しません。
