# Agent Skill Development Workspace

Claude CodeとCodexの両方でAgent Skillを開発するための親ワークスペースです。親リポジトリは共通環境と横断ツールだけを管理し、各Skillは独立したローカルディレクトリ、将来は個別Gitリポジトリとして管理します。

## 構成

```text
.
├── .devcontainer/              # Claude Code / Codex CLI入り開発環境
├── .github/workflows/          # 親ワークスペースだけのCI・セキュリティ
├── scripts/                    # Skill探索・検証・リンク生成、親監査
├── templates/skill-repository/ # 個別Skillリポジトリの雛形
├── tests/                      # 親ワークスペースのテスト
├── skills/
│   ├── README.md               # 親Gitで管理する利用案内
│   └── <skill-name>/           # 親Gitでは管理しないローカルSkillリポジトリ
├── .claude/skills/             # Claude Code用の生成リンク
└── .agents/skills/             # Codex用の生成リンク
```

`skills/*`、`.claude/skills/*`、`.agents/skills/*`は親Gitの管理対象外です。Skillの正本は各ローカルリポジトリの`skill/`に置き、両エージェントはその同じディレクトリを参照します。

## Dev Container

展開直後や`git init`前でもDev Containerを起動できます。

1. VS Codeで **Dev Containers: Reopen in Container** を実行する。
2. Claude Codeは`claude`、Codexは`codex`で必要な認証を行う。
3. `make doctor`で環境を確認する。
4. `make test`で親ワークスペースを検証する。

post-createはAgent CLIの導入とローカルSkillへのリンク生成だけを行います。Skill固有依存やSkill固有テストは自動実行せず、各子リポジトリの手順に従います。

Dev Containerを使わない場合は`make bootstrap`で親用のローカルPython環境と探索リンクを用意できます。Agent CLIと子Skill依存は導入しません。

## ローカルSkillを追加する

雛形から作成する場合:

```bash
cp -R templates/skill-repository skills/<skill-name>
# skills/<skill-name>/skill/SKILL.mdを編集
make validate
make link-skills
```

既存の個別リポジトリは、実在するURLを使って`skills/<skill-name>`へcloneします。親は子リポジトリのURLを仮定しません。詳しくは`skills/README.md`を参照してください。

現段階ではsubmoduleを使用しません。親がreview済みの子commitを再現可能に固定する必要が生じた場合だけ、将来の選択肢として検討します。

## 親ワークスペースのコマンド

```bash
make validate       # ローカルSkillのfrontmatterと配布境界を検証。0件でも成功
make link-skills    # Claude Code/Codex双方の探索リンクを同期。0件なら古いリンクを削除
make test           # 親のunit testと親セキュリティ監査だけを実行
make audit          # 親workflow、Dev Container、親管理ファイルを監査
make doctor         # ツールとローカルSkill一覧を表示。0件でも成功
```

Skill固有の依存導入、テスト、demo、manifest、release、配布物生成は、各`skills/<skill-name>`内で実行します。

## Git境界を確認する

親をcommitする前に、indexを変更しないdry-runで確認します。

```bash
git check-ignore -v skills/<skill-name>/skill/SKILL.md
git add -n .
```

`git add -n .`の出力に`skills/<skill-name>/`、`.claude/skills/<skill-name>`、`.agents/skills/<skill-name>`が含まれてはいけません。

## CI責務

- 親CI: 親のPython・shell・設定、探索/検証/リンクロジック、0件動作、一時fixture、テンプレート、親セキュリティ設定。
- 子CI: Skill本体、固有スクリプト、依存、tests、fixtures、demo、manifest、release、配布物。

設計判断は`docs/adr/0001-polyrepo-workspace.md`、子リポジトリ運用は`docs/skill-repository-management.md`を参照してください。
