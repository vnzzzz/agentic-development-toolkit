# Agent Skill 開発ワークスペース

Claude CodeとCodexの両方でAgent Skillを開発するためのワークスペースです。

この親リポジトリは、Dev Container、Skillの探索・検証ツール、standalone Skill用テンプレート、親CIを管理します。実際に開発するSkillの正本は、`repos/`配下へ配置する独立したSkillソースリポジトリが持ちます。

## はじめに

推奨する利用方法はDev Containerです。

1. VS Codeで **Dev Containers: Reopen in Container** を実行する。
2. 必要に応じてClaude CodeとCodexでAgent認証を行う。
3. `make doctor` で環境とローカルSkillの状態を確認する。
4. `make test` で親ワークスペースを検証する。

Dev Containerを使わない場合は、`make bootstrap` で親ワークスペース用のローカル環境とSkill探索リンクを準備できます。Agent CLI、共有Plugin、各Skill固有の依存関係は導入しません。

## 3つの利用モード

| モード | 用途 | 読み込み方 |
|---|---|---|
| 通常利用 | このワークスペース自身が共通Skillを利用する | public `vnzzzz/agent-skills` Pluginを利用 |
| ローカル開発 | standalone / collection Skillのworking treeを編集する | `.claude/skills/` / `.agents/skills/` からSkill rootへ直接リンク |
| 配布検証 | 実際の配布範囲でSkillまたはPluginが成立することを確認する | 各source repositoryのCIまたはnative Plugin toolingで検証 |

ローカル開発用の直接リンクは、編集内容をすぐにAgentへ反映するための仕組みです。Pluginのnamespaceやpackagingを含む配布状態の検証とは区別します。

詳細は [Skillソースリポジトリの運用](docs/skill-repository-management.md) を参照してください。

## 対応するSkillソースリポジトリ

```text
standalone repository
repos/<repository>/skill/SKILL.md

collection repository
repos/<repository>/skills/<skill-name>/SKILL.md

Plugin marketplace repository
repos/<repository>/plugins/<plugin-name>/skills/<skill-name>/SKILL.md
```

`repos/*` は親Gitの管理対象外です。各source repositoryが自身のGit履歴、PR、CI、依存関係、version、releaseを管理します。親リポジトリからsubmoduleとして固定しません。

## 主なコマンド

| コマンド | 役割 |
|---|---|
| `make validate` | ローカルSkillの配置、frontmatter、Skill root境界を検証する |
| `make link-skills` | standalone / collection Skillの開発用リンクを同期する |
| `make doctor` | Agent CLIとローカルSkillの状態を表示する |
| `make test` | 親ワークスペースのtestとsecurity auditを実行する |
| `make audit` | 親ワークスペースのsecurity設定を監査する |
| `make bootstrap` | Dev Containerを使わない場合の親ローカル環境を準備する |

Skill固有のtestや依存関係の導入は、各source repository側で実行します。

## 文書

- [Skillソースリポジトリの運用](docs/skill-repository-management.md): repository layout、ローカル開発、配布検証、Git / CI責務
- [GitHub repository設定](docs/github-repository-settings.md): branch protectionやGitHub security設定
- [Security policy](SECURITY.md): trust modelとsecurity boundary
- [ADR 0001](docs/adr/0001-polyrepo-workspace.md): 独立したSkill repositoryを扱うpolyrepo workspaceの採用
- [ADR 0002](docs/adr/0002-skill-collection-repositories.md): standalone / collection repository対応
- [ADR 0003](docs/adr/0003-authoring-and-distribution-validation.md): ローカル開発と配布検証の分離

`repos/`直下での最小操作は [repos/README.md](repos/README.md) を参照してください。
