# Repository作業ルール

このリポジトリを変更するAgentは、以下のrepository-local ruleに従ってください。一般的な利用方法は`README.md`、Skillソースリポジトリの運用は`docs/skill-repository-management.md`、security boundaryは`SECURITY.md`を正本とします。

## 責務境界

- `repos/*` は独立したローカルsource repositoryとして扱い、親Gitへ追加しない。親が管理するのは`repos/README.md`と任意の`repos/.gitkeep`だけとする。
- standalone、collection、Plugin marketplaceの各layoutは`docs/skill-repository-management.md`で定義された形を維持する。
- `.claude/skills/`と`.agents/skills/`はstandalone / collection Skillのローカル開発用に生成される。生成リンクを直接編集しない。
- Plugin repositoryのSkillをproject-local Skillとして直接リンクしない。Pluginとしての検証はnative Plugin toolingを使用する。
- `skill_workspace.py`の探索処理へ特定repository名やSkill名をhard-codeしない。
- 親ワークスペースが通常利用する共通Skillは`vnzzzz/agent-skills` Pluginから取得し、Skill本文を親リポジトリへ複製しない。
- `repos/*`をGit submodule化しない。各source repositoryのGit履歴、PR、CI、依存関係、version、releaseはそのrepository自身が所有する。
- 親CIから`repos/*`をcloneしてSkill固有testを中央実行しない。
- standalone Skillでは`skill/`全体を配布バンドルとし、配布後に必要なscript、reference、assetをその外側へ依存させない。
- credential、hostのSSH directory、Docker socket、cloud credentialをrepository設定からmountしない。Agentのpermission bypass設定を追加しない。
- public GitHubからのPlugin導入にGitHub credentialを要求しない。
- testやsecurity checkを通すためにvalidationを弱めない。
- Agent Skillの共通本文はopen formatを優先し、Agent固有metadataは薄いdistribution adapterに留める。

## 文書変更

- READMEへ詳細仕様を複製せず、詳細の正本へリンクする。
- 設計判断はADR、日常のrepository運用は`docs/skill-repository-management.md`、security ruleは`SECURITY.md`へ置く。
- code上のidentifier、path、command、設定値は文書の日本語化を理由に変更しない。
- ADRの過去のdecisionは後続ADRで変更されていても書き換えず、amend関係を明示する。

## 必須check

変更完了前に実行する。

```bash
make test
make audit
```

Skill探索またはリンク生成を変更した場合は、追加で実行する。

```bash
make validate
make link-skills
```

standalone Skill templateを変更した場合は、templateから作成したrepositoryでも`make test`が成功することを確認する。
