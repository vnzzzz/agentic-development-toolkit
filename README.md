# Agent Skill Development Workspace

Claude CodeとCodexの両方でAgent Skillを開発するための親workspaceです。親repositoryは共通環境と横断ツールだけを管理し、Skillの正本は`repos/`配下へcloneまたは作成したsource repository側に置きます。

source repositoryは、1 Skillを持つstandalone repositoryと、複数Skillを持つcollection repositoryの両方を扱えます。

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
├── .claude/skills/             # mutable local Skill用の生成リンク
└── .agents/skills/             # mutable local Skill用の生成リンク
```

## 対応するrepository形式

```text
standalone repository
repos/<repository>/skill/SKILL.md

collection repository
repos/<repository>/skills/<skill-name>/SKILL.md
```

`.claude/skills/<name>`と`.agents/skills/<name>`は、repository形式に関係なく実際のlocal Skill rootへ直接linkします。

repository直下の`SKILL.md`、`skill/`と`skills/`を同時に持つ曖昧なlayout、必要な`SKILL.md`を欠くdirectoryは検証エラーです。複数repositoryで同じSkill名が見つかった場合も失敗します。

## shared agent-skills Plugin

workspace自身が通常利用する汎用Skillは、public repository `vnzzzz/agent-skills`のCodex / Claude Code Pluginから導入します。

- Skill本文を親workspaceへ複製しません。
- git submoduleや固定revisionを使いません。
- 個別Skill名や`agent-skills/skills/<name>`を親workspaceへ列挙しません。
- Dev Container作成時にmarketplaceを登録または更新し、最新Pluginを導入します。
- public GitHub repositoryのHTTPS取得なのでGitHub認証情報は不要です。GitHubへの外向きHTTPS通信は必要です。

Plugin bootstrapは次で単独実行できます。Codex / Claude Code CLIが先に必要です。

```bash
bash scripts/install-agent-skills-plugin.sh
```

`AGENT_SKILLS_MARKETPLACE_SOURCE`を指定すると、開発中のlocal marketplaceを検証できます。

```bash
AGENT_SKILLS_MARKETPLACE_SOURCE="$PWD/repos/agent-skills" \
  bash scripts/install-agent-skills-plugin.sh
```

## Dev Container

展開直後や`git init`前でもDev Containerを起動できます。

1. VS Codeで **Dev Containers: Reopen in Container** を実行する。
2. post-createがClaude Code / Codex CLIを導入する。
3. post-createが`agent-skills` Pluginを両Agentへ導入する。
4. Claude Codeは`claude`、Codexは`codex`で必要なAgent認証を行う。
5. `make doctor`で環境を確認する。
6. `make test`で親workspaceを検証する。

Pluginの取得元はpublic GitHubであり、GitHub認証とAgent自身の認証は別物です。
post-createはAgent CLI、shared Plugin、ローカルSkillへのlinkを用意します。Skill固有依存やSkill固有testは自動実行せず、各source repositoryの手順に従います。

Dev Containerを使わない場合は`make bootstrap`で親用のローカルPython環境と探索linkを用意できます。Agent CLI、shared Plugin、source repository固有依存は導入しません。

## source repositoryを追加する

standalone repositoryを雛形から作成する場合:

```bash
cp -R templates/skill-repository repos/<skill-name>
# repos/<skill-name>/skill/SKILL.mdを編集
make validate
make link-skills
```

既存repositoryは、実在するURLを使って`repos/<repository>`へcloneします。collection repositoryでは`skills/<skill-name>/SKILL.md`を追加・編集します。詳しくは`repos/README.md`を参照してください。

mutableな開発用repositoryはsubmoduleにしません。
`repos/agent-skills`でshared collection自体を開発する場合も、他のcollection repositoryと同じlocal sourceとして扱います。

## 親workspaceのコマンド

```bash
make validate       # ローカルSkillのfrontmatter、配置、配布境界を検証。0件でも成功
make link-skills    # Claude Code/Codex双方のlocal探索linkを同期。0件なら古いlinkを削除
make test           # 親のunit testと親セキュリティ監査だけを実行
make audit          # 親workflow、Dev Container、親管理ファイルを監査
make doctor         # ツールとローカルSkill一覧を表示。0件は成功、不正配置は診断して失敗
```

Skill固有の依存導入、test、demo、manifest、release、配布物生成は各source repository内で実行します。

## Git境界を確認する

親をcommitする前に、indexを変更しないdry-runで確認します。

```bash
git check-ignore -v repos/<repository>/skill/SKILL.md
git add -n .
```

`git add -n .`の出力に`repos/<repository>/`、`.claude/skills/<name>`、`.agents/skills/<name>`が含まれてはいけません。

## CI責務

- 親CI: 親のPython・shell・設定、探索/検証/linkロジック、Plugin bootstrap script、0件動作、一時fixture、standalone template、親セキュリティ設定。
- `agent-skills` Plugin横断検証: Codex / Claude Codeの実CLIを使い、`repos/agent-skills`等のlocal marketplaceから導入して確認する。
- source repository側CI: Skill本体、固有script、依存、tests、fixtures、demo、manifest、release、配布物。

設計判断は`docs/adr/0001-polyrepo-workspace.md`と`docs/adr/0002-skill-collection-repositories.md`、repository運用は`docs/skill-repository-management.md`を参照してください。
