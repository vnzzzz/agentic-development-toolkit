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

### Plugin marketplace repository

1 repositoryが一つ以上のPlugin packageを持ち、Plugin配下にSkill collectionを持つ形式です。

```text
repos/<repository>/
└── plugins/
    └── <plugin-name>/
        └── skills/
            ├── <skill-a>/
            │   └── SKILL.md
            └── <skill-b>/
                └── SKILL.md
```

Skillを持たないPlugin directoryは探索対象外です。少なくとも一つの`plugins/<plugin-name>/skills/`が必要です。
各Skill directory名とSkillの`name`は一致させます。

repository直下の`SKILL.md`はサポートしません。`skill/`、`skills/`、`plugins/`を同一repositoryで混在させるlayoutや、Skill directoryに`SKILL.md`がない不完全layoutはconfiguration errorです。

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

standalone / collection / Plugin marketplaceのいずれでも、`.claude/skills/<name>`と`.agents/skills/<name>`は実際のSkill rootへ直接linkされます。同名Skillが複数source repositoryやPluginから見つかった場合は失敗します。

Plugin marketplaceそのものを実Agentへinstallして検証する場合は、そのrepositoryをsourceとしてPlugin bootstrapを実行します。`agent-skills`では次の形です。

```bash
AGENT_SKILLS_MARKETPLACE_SOURCE="$PWD/repos/agent-skills" \
  bash scripts/install-agent-skills-plugin.sh
```

## Parent Git boundary

親をcommitする前に、indexを変更しないdry-runで確認します。

```bash
git check-ignore -v repos/<repository>/skill/SKILL.md
git add -n .
```

collection / Plugin marketplace repositoryの場合も`repos/<repository>/`全体がignore対象です。dry-runにsource repositoryやgenerated discovery linkが含まれてはいけません。

## Source repository responsibilities

各source repositoryは次を所有します。

- Skillの`SKILL.md`とbundled runtime resources
- Skill固有scriptsとdependencies
- tests、fixtures、demos
- security reviewとdependency updates
- Plugin metadataを含むmanifest、versioning、releases、distribution
- GitHub ActionsとDependabot設定

親workspaceはSkill metadataの探索・横断validation・mutable local source用discovery link生成と、必要なPlugin integration testを行います。source repository固有dependencyのinstallやSkill固有testは自動実行しません。

## shared Pluginとの関係

`repos/`はmutableな開発用working copyの置き場です。
親workspace自身が通常利用するshared Skillは`vnzzzz/agent-skills` Pluginとして別に導入し、`repos/`のcloneを通常利用copyとして流用しません。

shared Pluginは特定revisionへpinせず、Dev Container作成時にpublic marketplaceから最新を導入します。
