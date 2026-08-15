# Skillソースリポジトリの運用

この文書は、`repos/`配下で開発するSkillソースリポジトリの配置、ローカル開発、配布検証、Git / CI責務の正本です。

設計判断の背景は`docs/adr/`、security boundaryは`SECURITY.md`を参照してください。

## 対応するrepository形式

### standalone repository

1 repositoryが1 Skillを持つ形式です。

```text
repos/<repository>/
└── skill/
    ├── SKILL.md
    ├── scripts/
    └── references/
```

repository directory名とSkillの`name`を一致させます。`skill/` directory全体が配布バンドルの正本です。

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

各`skills/<skill-name>` directory名とSkillの`name`を一致させます。repository名自体はSkill名と一致する必要はありません。

### Plugin marketplace repository

1 repositoryが1つ以上のPlugin packageを持ち、そのPlugin配下にSkill collectionを持つ形式です。

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

Skillを持たないPlugin directoryは探索対象外です。`plugins/`配下には少なくとも1つの`plugins/<plugin-name>/skills/`が必要です。各Skill directory名とSkillの`name`を一致させます。

### 不正なlayout

次はconfiguration errorとして扱います。

- repository直下の`SKILL.md`
- 同一repositoryで`skill/`、`skills/`、`plugins/`を混在させるlayout
- Skill directoryに`SKILL.md`が存在しない不完全layout
- 複数のlocal source repository / Pluginで同じSkill名を定義する構成

## 利用モード

### 通常のPlugin利用

親ワークスペース自身が利用する共通Skillは、public `vnzzzz/agent-skills` Pluginから導入します。

この通常利用copyと、`repos/`配下のmutableな開発working copyは別のものとして扱います。親ワークスペースへSkill本文を複製したり、`repos/agent-skills`を通常利用copyとして流用したりしません。

### ローカル開発

standalone / collection repositoryでは、次を実行してworking treeのSkill rootをClaude Code / Codexの双方へ直接公開します。

```bash
make validate
make link-skills
```

生成されるlinkは次のとおりです。

```text
standalone
.claude/skills/<name> -> repos/<repository>/skill
.agents/skills/<name> -> repos/<repository>/skill

collection
.claude/skills/<name> -> repos/<repository>/skills/<name>
.agents/skills/<name> -> repos/<repository>/skills/<name>
```

Skill root内の`scripts/`、`references/`、assetもworking treeから直接利用されます。この経路は編集内容をすぐAgentへ反映するためのものであり、配布packageの検証ではありません。

Plugin repositoryのSkillは`.claude/skills/` / `.agents/skills/`へ直接linkしません。Plugin namespace、packaging、cache、bundled resource resolutionを含めて確認するため、native Plugin toolingを使用します。

### 配布検証

各source repositoryは、自身が実際に配布するfile setだけで成立することを自身のCIで検証します。親ワークスペースはchild repository固有のruntime testを中央実行しません。

standalone Skill templateでは次を実行します。

```bash
cd repos/<skill-name>
make test
```

`make test`には少なくとも次が含まれます。

- `skill/SKILL.md`のmetadata validation
- `skill/`をtemporary directoryへ隔離copyしたdistribution-boundary validation
- bundle内の全Markdown documentについて、local linkがSkill root内に留まりtargetが存在することの確認
- symlinkがSkill root外へescapeせず、targetが存在することの確認
- bundled Python / shell scriptのsyntax check
- repository固有のunit / integration test

Generic validatorはSkill固有のruntime behaviorまで保証しません。実行可能scriptを持つSkill repositoryでは、隔離した配布バンドルを代表fixtureに対して実行するintegration testを追加します。

Testやfixture自体はrepository側に置けますが、配布後のruntimeがrepository-only fileへ依存してはなりません。

collection / Plugin repositoryは、それぞれのproviderがlayoutとrelease方式に合わせた同等のdistribution-boundary testを所有します。

## source repositoryを追加する

### standalone repositoryをtemplateから作成する

親ワークスペースrootで実行します。

```bash
cp -R templates/skill-repository repos/<skill-name>
# repos/<skill-name>/skill/SKILL.mdを編集する
make validate
make link-skills
cd repos/<skill-name>
make test
```

Skill repositoryを個別管理する準備ができたら、そのdirectory内でGitを初期化してpublishします。親ワークスペースはremote URLを仮定しません。

### 既存repositoryをcloneする

実在するrepository URLを`repos/<repository>`へcloneし、親ワークスペースrootで実行します。

```bash
make validate
make link-skills
```

standalone / collection repositoryはdirect authoring linkが生成されます。Plugin repositoryは探索・validation対象ですが、個別Skill linkは生成されません。

## Plugin providerのlocal検証

`agent-skills` providerをlocal working copyから検証する場合の例を示します。

### Codex

local marketplace sourceへ明示的に切り替えます。

```bash
AGENT_SKILLS_MARKETPLACE_SOURCE="$PWD/repos/agent-skills" \
  bash scripts/install-agent-skills-plugin.sh
```

bootstrapは同じmarketplace名の既存sourceを置き換えて再導入します。検証後は環境変数を付けずに再実行し、public default sourceへ戻します。

```bash
bash scripts/install-agent-skills-plugin.sh
```

### Claude Code

Plugin rootをworking copyから直接読み込みます。

```bash
claude --plugin-dir "$PWD/repos/agent-skills/plugins/agent-skills"
```

この経路ではindividual Skillをproject-local linkへ展開せず、Plugin namespaceを保ったままsession単位で確認できます。

## 親Gitとの境界

`repos/*`は親Gitからignoreします。各source repositoryは独立したGit repositoryとして管理し、親へsubmoduleとして登録しません。

親をcommitする前に、indexを変更しないdry-runで境界を確認できます。

```bash
git check-ignore -v repos/<repository>/skill/SKILL.md
git add -n .
```

collection / Plugin repositoryでも`repos/<repository>/`全体がignore対象です。`git add -n .`へsource repositoryや`.claude/skills/`、`.agents/skills/`の生成linkが含まれてはいけません。

## Git / CIの責務

| 対象 | 所有するもの |
|---|---|
| 親ワークスペース | Dev Container、Agent CLI bootstrap、generic discovery / validation / link tooling、standalone template、親test、親security設定、shared Plugin integration |
| Skill source repository | Skill本体、runtime resource、dependency、test、fixture、distribution-boundary test、security update、CI、version、release |
| Plugin provider repository | 上記に加えてPlugin metadata、Plugin packaging、native Plugin loading / distribution validation |

各`repos/<repository>`は、自身のbranch、commit、PR、CI、version、releaseを独立して管理します。親リポジトリはlocal child commit SHAを記録しません。

親CIが成功しても、ローカルにcloneされているすべてのSkillのruntime test成功を意味しません。各source repositoryのPRが自身のruntimeと配布境界を検証します。

## 関連文書

- `docs/adr/0001-polyrepo-workspace.md`: polyrepo workspaceを採用した理由
- `docs/adr/0002-skill-collection-repositories.md`: standalone / collection対応
- `docs/adr/0003-authoring-and-distribution-validation.md`: direct authoringとdistribution validationの分離
- `SECURITY.md`: trust modelとsecurity boundary
- `docs/github-repository-settings.md`: GitHub repository-level settings
