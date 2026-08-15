# `repos/` の使い方

`repos/`は、開発対象のSkillソースリポジトリをローカルへ配置するdirectoryです。`repos/README.md`と任意の`.gitkeep`を除き、配下は親Gitからignoreされます。

## 対応する配置

```text
standalone
repos/<repository>/skill/SKILL.md

collection
repos/<repository>/skills/<skill-name>/SKILL.md

Plugin marketplace
repos/<repository>/plugins/<plugin-name>/skills/<skill-name>/SKILL.md
```

repository直下の`SKILL.md`や、`skill/`・`skills/`・`plugins/`を同一repositoryへ混在させるlayoutは使用しません。

## 追加後の操作

standalone repositoryをtemplateから作成する場合:

```bash
cp -R templates/skill-repository repos/<skill-name>
# repos/<skill-name>/skill/SKILL.mdを編集する
```

既存repositoryは`repos/<repository>`へcloneします。

その後、親ワークスペースrootで実行します。

```bash
make validate
make link-skills
```

standalone / collection Skillは`.claude/skills/`と`.agents/skills/`からworking treeへ直接linkされます。Plugin repositoryは探索・validation対象ですが、個別Skillはdirect linkされません。

各source repositoryは独立したGit repositoryとしてbranch、PR、CI、version、releaseを管理し、親へsubmoduleとして登録しません。

詳細なlayout、配布検証、Plugin providerのlocal検証、Git / CI責務は [Skillソースリポジトリの運用](../docs/skill-repository-management.md) を参照してください。
