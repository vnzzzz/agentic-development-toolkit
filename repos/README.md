# ローカルSkill source repository

`repos/`は、Agent Skillのsource repositoryをローカルへ配置するためのworkspaceです。このREADMEと任意の`.gitkeep`を除き、配下は親Git repositoryからignoreされます。

このworkspaceでは次の3形式を扱います。

```text
standalone repository
repos/<repository>/skill/SKILL.md

collection repository
repos/<repository>/skills/<skill-name>/SKILL.md

Plugin marketplace repository
repos/<repository>/plugins/<plugin-name>/skills/<skill-name>/SKILL.md
```

standalone repositoryをテンプレートから作成する場合:

```bash
cp -R templates/skill-repository repos/<skill-name>
# repos/<skill-name>/skill/SKILL.mdを編集する
```

既存repositoryは実在するURLを使って`repos/<repository>`へcloneします。
collection repositoryでは`skills/<skill-name>/SKILL.md`、Plugin marketplace repositoryでは`plugins/<plugin-name>/skills/<skill-name>/SKILL.md`を各Skillの正本として扱います。
Plugin marketplace内でSkillを持たないPlugin directoryは探索対象外ですが、`plugins/`配下には少なくとも一つのSkill collectionが必要です。

repository直下の`SKILL.md`は使用しません。
`skill/`、`skills/`、`plugins/`を同じrepositoryに併置した曖昧なlayoutや、必要な`SKILL.md`を欠くSkill directoryは検証エラーになります。

作成またはclone後、次を実行します。

```bash
make validate
make link-skills
```

`.claude/skills/<name>`と`.agents/skills/<name>`は、repository形式に関係なく実際のSkill rootへ直接linkされます。
同じSkill名が複数repositoryまたはPluginに存在する場合はconfiguration errorです。

Plugin marketplace自体を実Agentへinstallして検証する場合は、そのrepositoryをmarketplace sourceとしてPlugin bootstrapへ渡します。
`agent-skills`のlocal working copyでは次の形です。

```bash
AGENT_SKILLS_MARKETPLACE_SOURCE="$PWD/repos/agent-skills" \
  bash scripts/install-agent-skills-plugin.sh
```

bootstrapは同じmarketplace名が別sourceから登録済みでも、既存marketplaceを置き換えて指定sourceから再導入します。

mutableな開発用repositoryを親Gitへsubmoduleとして登録しません。親をcommitする前に境界を確認します。

```bash
git check-ignore -v repos/<repository>/skill/SKILL.md
git add -n .
```

`git add -n .`の出力に`repos/<repository>/`や`.claude/skills/`、`.agents/skills/`の生成物が含まれてはいけません。
