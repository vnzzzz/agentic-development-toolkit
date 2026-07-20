# ローカルSkillリポジトリ

`skills/`は、個別に管理するSkillリポジトリをローカルへ配置するためのワークスペースです。このREADMEと任意の`.gitkeep`を除き、配下は親Gitリポジトリからignoreされます。

親テンプレートから新しいSkillを作成する場合:

```bash
cp -R templates/skill-repository skills/<skill-name>
# skills/<skill-name>/skill/SKILL.mdを編集する
# 子を個別管理する準備ができた段階で、子ディレクトリ内のGitを初期化する
```

既存Skillは、実在するリポジトリURLを使って`skills/<skill-name>`へcloneします。親ワークスペースは子リポジトリのURLや存在を仮定しません。

作成またはclone後、同じ`skill/`をClaude CodeとCodexへ公開します。

```bash
make validate
make link-skills
```

現段階ではGit submoduleを使用せず、親から`skills/`配下をcommitしません。親がreview済みの子commitを再現可能に固定する必要が生じた場合だけ、submoduleを検討します。

親をcommitする前に、indexを変更しないdry-runで境界を確認します。

```bash
git check-ignore -v skills/<skill-name>/skill/SKILL.md
git add -n .
```

出力に`skills/<skill-name>/`、`.claude/skills/`、`.agents/skills/`の生成物が含まれてはいけません。
