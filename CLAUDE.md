# Claude Code向け補足

Repository全体の作業ルールは`AGENTS.md`を正本とします。Claude Code固有の例外はありません。

## Workflow

- Feature sourceは`src/agent-dev/`、実container testは`test/agent-dev/`を変更する。
- consumer repositoryやAgent Skill sourceをこのrepository配下へcloneして管理しない。
- release対象の変更ではFeature versionを更新する。
- 完了前のcheckは`AGENTS.md`に従う。

## Supporting documents

- [AGENTS.md](AGENTS.md)
- [docs/dev-container-feature.md](docs/dev-container-feature.md)
- [SECURITY.md](SECURITY.md)
