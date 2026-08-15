# Agent Skill Development Workspace

Claude CodeとCodexの両方でAgent Skillを開発するための親workspaceです。親repositoryは共通環境と横断ツールだけを管理し、Skillの正本は`repos/`配下へcloneまたは作成したsource repository側に置きます。

source repositoryは、1 Skillを持つstandalone repository、複数Skillを持つcollection repository、Plugin marketplace repositoryを扱えます。

## 構成

```text
.
├── .devcontainer/              # Claude Code / Codex CLI入り開発環境
├── .github/workflows/          # 親workspaceだけのCI・セキュリティ
├── scripts/                    # Skill探索・検証・Plugin bootstrap・親監査
├── templates/skill-repository/ # standalone Skill repositoryの雛形
├── tests/                      # 親workspaceのテスト
├── repos/
│   ├── README.md               # 親Gitで管理する利用案内
│   └── <repository>/           # 親Gitでは管理しないsource repository
├── .claude/skills/             # standalone / collection authoring用の生成リンク
└── .agents/skills/             # standalone / collection authoring用の生成リンク
```

## 開発モードと配布検証

このworkspaceでは、編集時のfeedback loopと配布状態の検証を分けます。

### Normal Plugin consumption

workspace自身が通常利用する汎用Skillは、public `vnzzzz/agent-skills` PluginとしてCodex / Claude Codeへ導入します。Dev Container作成時にpublic marketplaceからfresh installします。

### Authoring mode

standalone / collection repositoryは、`.claude/skills/<name>`と`.agents/skills/<name>`から`repos/`配下の実Skill rootへ直接linkします。

working treeをそのまま読むため、`SKILL.md`だけでなくSkill root内の`scripts/`、`references/`、assets等も編集直後の内容を利用できます。これは開発用のdirect exposureであり、配布済みbundleの検証ではありません。

### Distribution validation

各source repository自身が、実際に配布する範囲だけで成立することをCIで検証します。

standalone Skill templateでは`skill/`全体を配布bundleの正本とし、`make test`で一時directoryへ隔離copyしてlocal link、symlink境界、bundled Python / shell scriptのsyntaxを確認します。実行可能scriptを持つSkillでは、各repository側で代表fixtureを使ったruntime integration testも追加します。

Plugin repositoryはSkill directoryをproject-local Skillとして直接linkしません。Plugin namespace、packaging、cache、resource resolutionを含め、provider repository自身のnative Plugin toolingで確認します。

## 対応するrepository形式

```text
standalone repository
repos/<repository>/skill/SKILL.md

collection repository
repos/<repository>/skills/<skill-name>/SKILL.md

Plugin marketplace repository
repos/<repository>/plugins/<plugin-name>/skills/<skill-name>/SKILL.md
```

standalone / collection Skillはrepository形式に関係なく実際のlocal Skill rootへ直接linkします。

Plugin marketplace repositoryは探索・metadata validation・name collision検査の対象ですが、`.claude/skills` / `.agents/skills`へはlinkしません。Pluginとしてのnative loadingで検証してください。

一つのsource repositoryで`skill/`、`skills/`、`plugins/`を混在させるlayoutは検証エラーです。Plugin repositoryではSkillを持たないPluginを許容しますが、少なくとも一つの`plugins/<plugin-name>/skills/`が必要です。複数repositoryやPluginで同じSkill名が見つかった場合も失敗します。

## shared agent-skills Plugin

workspace自身が通常利用する汎用Skillは、public repository `vnzzzz/agent-skills`のCodex / Claude Code Pluginから導入します。

- Skill本文を親workspaceへ複製しません。
- git submoduleや固定revisionを使いません。
- 個別Skill名やprovider repository内部pathをPlugin bootstrapへ列挙しません。
- Dev Container作成時にmarketplaceを登録または更新し、最新Pluginを導入します。
- public GitHub repositoryのHTTPS取得なのでGitHub認証情報は不要です。GitHubへの外向きHTTPS通信は必要です。

Plugin bootstrapは次で単独実行できます。Codex / Claude Code CLIが先に必要です。

```bash
bash scripts/install-agent-skills-plugin.sh
```

`agent-skills` providerのlocal marketplaceをCodex側で検証する場合は、sourceを明示してfresh installします。

```bash
AGENT_SKILLS_MARKETPLACE_SOURCE="$PWD/repos/agent-skills" \
  bash scripts/install-agent-skills-plugin.sh
```

検証後にpublic defaultへ戻すには、環境変数なしでもう一度実行します。

Claude CodeでPlugin working copyを直接検証する場合は、providerのPlugin rootを`--plugin-dir`で読み込みます。local Pluginはそのsessionだけ利用し、installed Pluginと同名の場合もlocal copyを優先できます。

```bash
claude --plugin-dir "$PWD/repos/agent-skills/plugins/agent-skills"
```

## Dev Container

展開直後や`git init`前でもDev Containerを起動できます。

1. VS Codeで **Dev Containers: Reopen in Container** を実行する。
2. post-createがClaude Code / Codex CLIを導入する。
3. post-createがpublic `agent-skills` Pluginを両Agentへ導入する。
4. post-createがstandalone / collectionのlocal authoring Skillへのlinkを同期する。Plugin Skillはlinkしない。
5. Claude Codeは`claude`、Codexは`codex`で必要なAgent認証を行う。
6. `make doctor`で環境を確認する。
7. `make test`で親workspaceを検証する。

Pluginの取得元はpublic GitHubであり、GitHub認証とAgent自身の認証は別物です。
post-createはAgent CLI、shared Plugin、ローカルauthoring Skillへのlinkを用意します。Skill固有依存やSkill固有testは自動実行せず、各source repositoryの手順に従います。

Dev Containerを使わない場合は`make bootstrap`で親用のローカルPython環境とauthoring linkを用意できます。Agent CLI、shared Plugin、source repository固有依存は導入しません。

## source repositoryを追加する

standalone repositoryを雛形から作成する場合:

```bash
cp -R templates/skill-repository repos/<skill-name>
# repos/<skill-name>/skill/SKILL.mdを編集
make validate
make link-skills
cd repos/<skill-name>
make test
```

既存repositoryは、実在するURLを使って`repos/<repository>`へcloneします。collection repositoryとPlugin marketplace repositoryも自動探索されます。詳しくは`repos/README.md`を参照してください。

mutableな開発用repositoryはsubmoduleにしません。
Plugin repositoryも他のlocal sourceと同じ探索・validation経路で扱いますが、Skill direct linkではなくnative Plugin validationを使います。

## 親workspaceのコマンド

```bash
make validate       # ローカルSkillのfrontmatter、配置、Skill root境界を横断検証。0件でも成功
make link-skills    # standalone / collectionのauthoring linkを同期。Plugin Skillや古いlinkは除去
make test           # 親のunit testと親セキュリティ監査だけを実行
make audit          # 親workflow、Dev Container、親管理ファイルを監査
make doctor         # ツールとローカルSkill一覧、direct/nativeの扱いを表示
```

Skill固有の依存導入、test、demo、manifest、release、配布物生成は各source repository内で実行します。

## Git境界を確認する

親をcommitする前に、indexを変更しないdry-runで確認します。

```bash
git check-ignore -v repos/<repository>/skill/SKILL.md
git add -n .
```

`git add -n .`の出力に`repos/<repository>/`、`.claude/skills/<name>`、`.agents/skills/<name>`が含まれてはいけません。

`repos/*`配下はそれぞれ独立Git repositoryとしてbranch、commit、PR、CI、releaseを管理します。親repositoryはlocal childのcommit SHAを記録せず、childをsubmoduleにも変換しません。

## CI責務

- 親CI: 親のPython・shell・設定、探索/検証/linkロジック、Plugin bootstrap script、0件動作、一時fixture、standalone template、親セキュリティ設定。
- shared `agent-skills` Plugin integration: Codex / Claude Codeの実CLIでpublic default sourceからの導入・再実行を確認し、local marketplaceへのsource切替とpublic sourceへの復帰も検証する。
- source repository側CI: Skill本体、固有script、依存、tests、fixtures、distribution-boundary test、demo、manifest、release、配布物。
- Plugin provider側CI: 上記に加え、Plugin metadataとnative Plugin loadingをprovider自身の責務で確認する。

parent CIから`repos/*`をcloneしてchild testを中央実行しません。workspace infrastructureとSkill implementationのfailure domainを分離し、各source repositoryのPRが自身のruntimeと配布境界を証明します。

設計判断は`docs/adr/0001-polyrepo-workspace.md`、`docs/adr/0002-skill-collection-repositories.md`、`docs/adr/0003-authoring-and-distribution-validation.md`、repository運用は`docs/skill-repository-management.md`を参照してください。
