# Skill repository management

`repos/`は、Agent Skillのsource repositoryをローカルへ配置するdirectoryです。配下のsource repositoryは親Gitからignoreされ、submoduleとしては管理しません。

## 対応するsource repository

### standalone repository

1 repositoryが1 Skillを持つ形式です。

```text
repos/<repository>/
└── skill/
    ├── SKILL.md
    ├── scripts/
    └── references/
```

standalone repository名とSkillの`name`は一致させます。`skill/` directory全体が配布bundleの正本です。

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

## Authoring mode

standalone / collection repositoryは、次を実行するとworking treeのSkill rootがClaude Code / Codex双方へ直接linkされます。

```bash
make validate
make link-skills
```

- standalone: `.claude/skills/<name>` / `.agents/skills/<name>` → `repos/<repository>/skill`
- collection: `.claude/skills/<name>` / `.agents/skills/<name>` → `repos/<repository>/skills/<name>`

このlinkはmutable authoring用です。Skill root内の`scripts/`、`references/`、assets等もworking treeからそのまま利用できます。

Plugin repositoryのSkillはproject-local Skillへdirect linkしません。Pluginとしてのnamespace、packaging、cache、bundled resource resolutionを保った状態で検証するため、native Plugin toolingを使います。

## Distribution validation

各source repositoryは自身の配布境界をCIで検証します。parent workspaceはchild repositoryのruntime testを中央実行しません。

standalone templateでは次を実行します。

```bash
cd repos/<skill-name>
make test
```

`make test`は次を含みます。

- `skill/SKILL.md` metadata validation
- `skill/`を一時directoryへ隔離copy
- bundle内local Markdown linkが`skill/`外へ逃げないこと
- symlinkが配布Skill root外へescapeしないこと
- bundled Python / shell scriptのsyntax check
- repository固有unit / integration test

scriptの実挙動まではgeneric validatorだけでは保証できません。実行可能scriptを持つSkill repositoryでは、隔離された配布bundleを使って代表fixtureを処理するintegration testを追加します。testsやfixture自体はrepository側に置けますが、配布後のruntimeがrepository-only fileへ依存してはいけません。

collection / Plugin repositoryは各providerのlayoutとrelease方式に合わせて同等のdistribution-boundary testを所有します。

## standalone repositoryを作成する

```bash
cp -R templates/skill-repository repos/<skill-name>
# repos/<skill-name>/skill/SKILL.mdを編集
make validate
make link-skills
cd repos/<skill-name>
make test
```

repositoryを個別管理する準備ができた段階で、そのdirectory内でGitを初期化・publishします。親workspaceはremote URLを仮定しません。

## 既存repositoryをcloneする

実在するrepository URLを`repos/<repository>`へcloneし、次を実行します。

```bash
make validate
make link-skills
```

standalone / collection repositoryでは`.claude/skills/<name>`と`.agents/skills/<name>`が実際のSkill rootへ直接linkされます。同名Skillが複数source repositoryやPluginから見つかった場合はvalidationで失敗します。

Plugin repositoryは探索・validation対象ですが、個別Skill linkを作りません。provider repositoryのnative Plugin validationを利用します。

### `agent-skills` providerをlocal検証する

Codex側でlocal marketplaceを使う場合:

```bash
AGENT_SKILLS_MARKETPLACE_SOURCE="$PWD/repos/agent-skills" \
  bash scripts/install-agent-skills-plugin.sh
```

このbootstrapはinstalled Pluginとmarketplace sourceをfreshに置き換えるため、public Pluginとlocal Pluginを曖昧に併存させません。検証後は環境変数なしで再実行してpublic default sourceへ戻します。

Claude Code側ではPlugin rootを直接読み込めます。

```bash
claude --plugin-dir "$PWD/repos/agent-skills/plugins/agent-skills"
```

`--plugin-dir`はlocal Plugin working copyをsession単位で読み込むため、individual Skillをproject-local linkへ展開せずPlugin namespaceのまま確認できます。

## Parent Git boundary

親をcommitする前に、indexを変更しないdry-runで確認します。

```bash
git check-ignore -v repos/<repository>/skill/SKILL.md
git add -n .
```

collection / Plugin marketplace repositoryの場合も`repos/<repository>/`全体がignore対象です。dry-runにsource repositoryやgenerated discovery linkが含まれてはいけません。

各`repos/<repository>`は独立Git repositoryとしてbranch、commit、PR、CI、version、releaseを管理します。親workspaceはchild commitを記録せず、submoduleにも変換しません。

## Source repository responsibilities

各source repositoryは次を所有します。

- Skillの`SKILL.md`とbundled runtime resources
- Skill固有scriptsとdependencies
- tests、fixtures、demos
- distribution-boundary testとruntime integration test
- security reviewとdependency updates
- Plugin metadataを含むmanifest、versioning、releases、distribution
- GitHub ActionsとDependabot設定

親workspaceはSkill metadataの探索・横断validation・standalone / collection authoring link生成と、workspace自身が利用するshared Plugin integration testを行います。source repository固有dependencyのinstallやSkill固有testは自動実行しません。

## shared Pluginとの関係

`repos/`はmutableな開発用working copyの置き場です。
親workspace自身が通常利用するshared Skillは`vnzzzz/agent-skills` Pluginとして別に導入し、`repos/`のcloneを通常利用copyとして流用しません。

shared Pluginは特定revisionへpinせず、Dev Container作成時にpublic marketplaceから最新を導入します。Plugin providerのlocal working copyを検証するときだけnative local Plugin経路へ明示的に切り替えます。
