# Skill repository management

`repos/`は、Agent Skillのsource repositoryをローカルへ配置するdirectoryです。配下のsource repositoryは親Gitからignoreされ、submoduleとしては管理しません。

## 対応するsource repository

### standalone repository

1 repositoryが1 Skillを持つ形式です。

```text
repos/<repository>/
└── skill/
    └── SKILL.md
```

standalone repository名とSkillの`name`は一致させます。

### collection repository

1 repositoryが複数Skillを持つ形式です。

```text
repos/<repository>/
└── skills/
    ├── <skill-a>/
    │   └── SKILL.md
    └── <skill-b>/
        └── SKILL.md
```

各`skills/<skill-name>` directory名とそのSkillの`name`は一致させます。collection repository名自体はSkill名と一致する必要はありません。

repository直下の`SKILL.md`はサポートしません。`skill/`と`skills/`の両方を持つrepositoryや、Skill directoryに`SKILL.md`がない不完全layoutはconfiguration errorです。

## standalone repositoryを作成する

```bash
cp -R templates/skill-repository repos/<skill-name>
# repos/<skill-name>/skill/SKILL.mdを編集
make validate
make link-skills
```

repositoryを個別管理する準備ができた段階で、そのdirectory内でGitを初期化・publishします。親workspaceはremote URLを仮定しません。

## 既存repositoryをcloneする

実在するrepository URLを`repos/<repository>`へcloneし、次を実行します。

```bash
make validate
make link-skills
```

standalone / collectionのどちらでも、`.claude/skills/<name>`と`.agents/skills/<name>`は実際のSkill rootへ直接linkされます。同名Skillが複数source repositoryから見つかった場合は失敗します。

## Parent Git boundary

親をcommitする前に、indexを変更しないdry-runで確認します。

```bash
git check-ignore -v repos/<repository>/skill/SKILL.md
git add -n .
```

collection repositoryの場合も`repos/<repository>/`全体がignore対象です。dry-runにsource repositoryやgenerated discovery linkが含まれてはいけません。

## Source repository responsibilities

各source repositoryは次を所有します。

- Skillの`SKILL.md`とbundled runtime resources
- Skill固有scriptsとdependencies
- tests、fixtures、demos
- security reviewとdependency updates
- manifest、versioning、releases、distribution archives
- GitHub ActionsとDependabot設定

親workspaceはSkill metadataの探索・横断validation・discovery link生成だけを行い、source repository固有dependencyのinstallやtestを自動実行しません。

## Submoduleとの関係

`repos/`はmutableな開発用working copyの置き場なのでsubmoduleにしません。

review済みの特定revisionを親workspace自身の通常利用Skillとして再現可能に固定する必要がある場合は、開発用working copyとは別責務としてpin方式を検討します。mutableな開発sourceと固定consumer copyを同一path・同一責務として扱いません。
