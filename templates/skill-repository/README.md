# Agent Skill repository template

1つのstandalone Agent Skillを独立repositoryとして開発するためのtemplateです。

repository名と`skill/SKILL.md`の`name`は、同じlowercase hyphenated形式のSkill名にしてください。

## 配布境界

`skill/` directory全体が配布バンドルです。

Skillの実行時に必要なscript、reference、assetは`skill/`内へ置きます。test、fixture、CI、dependency metadata、release toolingなどrepositoryでのみ必要なfileは`skill/`外へ置けます。

repository直下へ`SKILL.md`を追加しないでください。

## 検証

変更完了前に実行します。

```bash
make test
```

`make test`は次を確認します。

- `skill/SKILL.md`のmetadata
- 隔離copyした`skill/`内のMarkdown local linkとsymlink boundary
- bundled Python / shell scriptのsyntax
- repository固有test

実行可能scriptを持つSkillでは、隔離した配布バンドルを代表fixtureに対して実行するintegration testも追加してください。repository側のtestは`skill/`外のfixtureを利用できますが、配布後のSkill runtimeがrepository-only fileへ依存してはいけません。

Agent向けのrepository-local ruleは`AGENTS.md`、security requirementは`SECURITY.md`を参照してください。
