# ADR 0003: mutableなSkill開発と配布検証を分離する

- 状態: 採用
- 日付: 2026-08-15

## 背景

このワークスペースでは、disk上では似て見えるが正しさの条件が異なる3つの用途を扱う。

1. 親ワークスペース自身が、public `vnzzzz/agent-skills` Pluginから共有Skillを通常利用する。
2. `repos/`配下のstandalone / collection Skill repositoryを編集するとき、working treeを短いfeedback loopでAgentへ反映する。
3. Plugin repositoryやscriptを含むSkillについて、repository-only fileやproject-localな探索挙動へ依存せず、実際の配布packageとして成立することを確認する。

`.claude/skills/`と`.agents/skills/`からmutableなSkill rootへ直接リンクする方法は、copyやpackagingなしで変更を反映できるため開発に適している。一方、この方法ではPlugin namespace、Plugin cache、配布file set、bundled resource resolutionが配布後と同じになることを証明できない。

script、reference、assetを含むSkillではこの差が重要になる。repository checkout上では動作していても、配布物に含まれないtest、fixture、generated file、sibling directoryへ誤って依存する可能性がある。

Plugin repositoryではさらに、同等のinstalled Pluginが存在する状態で個別Skillもproject-local linkとして公開すると、どのsourceが有効か分かりにくくなる。また、project-local Skillとして読む経路ではPlugin namespaceが失われる。

## 決定

1. 次の3 modeを明確に分離する。
   - 通常のPlugin利用
   - mutableなdirect authoring
   - distribution validation
2. 親ワークスペースの通常利用では、Dev Container作成時にpublic `vnzzzz/agent-skills` Pluginを導入する。
3. direct authoring linkはstandalone / collection repositoryにだけ生成する。
   - `repos/<repository>/skill/<...>`
   - `repos/<repository>/skills/<skill-name>/<...>`
4. Plugin repositoryのSkillはmetadata、layout、duplicate name、Skill root security boundaryの探索・validation対象には含めるが、`.claude/skills/`や`.agents/skills/`へlinkしない。
5. Plugin repositoryの配布検証はprovider repositoryが所有するnative Plugin mechanismで行う。共有`agent-skills` providerでは次を利用できる。
   - Claude Code: Plugin working treeを`--plugin-dir`で読み込む。
   - Codex: workspace bootstrapを使って既存marketplace installationをlocal marketplace sourceへ切り替え、検証後にpublic sourceへ戻す。
6. standalone repository templateでは`skill/` directory全体を配布バンドルの正本とする。
7. templateの`make test`はrepository unit testより前に、隔離copyした`skill/`を検証する。
   - local Markdown linkがbundle内に留まり、targetが存在すること。
   - symlinkがSkill root外へescapeしないこと。
   - bundled Python / shell scriptのsyntaxが正しいこと。
8. genericなdistribution validationだけでSkill固有runtime behaviorを保証したことにはしない。実行可能scriptを持つSkill repositoryは、配布bundleを代表fixtureに対して実行するintegration testを追加する。
9. 親CIはworkspace infrastructure、genericなdiscovery / link behavior、standalone template、shared Plugin integrationだけを検証する。すべてのchild repositoryをcloneして実行してはならない。
10. 各child repositoryは独立したGit repositoryとして、branch、commit、PR、dependency、test、CI、security update、version、release、distribution artifactを所有する。
11. `repos/*`は引き続き親Gitからignoreし、Git submoduleへ変換しない。

## 影響

- standalone / collection SkillはClaude CodeとCodexに対する即時のworking-tree feedbackを維持できる。
- Plugin working copyがinstalled Pluginと重複するunnamespacedなproject-local Skill entryを作らなくなる。
- native Plugin testingによって、direct Skill linkでは再現できないPlugin runtimeの性質を検証できる。
- scriptを含むstandalone Skillは、testやdependencyを親workspaceへ移さずに共通のdistribution-boundary checkを利用できる。
- 親CIが成功しても、ローカルに存在するすべてのchild Skillのruntime test成功を意味しない。これは各source repositoryへ意図的に委譲する。
- child CIのfailureと親workspace infrastructureのfailureを分離できる。
- 親はlocal child revisionを記録しないため、child releaseの再現性は親checkoutではなくchild repository自身が担保する。

## 検討した代替案

### 編集中のすべてのSkillをPluginとしてinstallする

standalone SkillにはPlugin packagingが必須ではなく、編集のたびにreinstallするとdirect working-tree authoringよりfeedback loopが遅くなるため採用しなかった。

### Plugin Skillをdirect linkし、別途Plugin validationも行う

installed Pluginとunnamespacedなproject-local copyが同時に見える状態を残し、source selectionを判断しにくくするためdefaultには採用しなかった。

### すべてのchild CIを親workspaceから実行する

親はchild固有のdependency、fixture、runtime version、release lifecycleを所有しない。中央実行すると無関係なrepositoryを結合し、親CIがlocal source availabilityへ依存するため採用しなかった。

### `repos/*`をGit submoduleへ変換する

mutableな開発working copyに親所有のrevision pinは不要であり、各child repository自身がrelease再現に必要なGit historyを持つため採用しなかった。

### testとfixtureを配布Skill bundle内へ置く

testやfixtureは、Skill runtimeで実際に必要な場合を除きdevelopment assetである。genericな要件としてbundle内へ含めるのではなく、runtime fileがbundle内で完結することをdistribution validationで確認する方針とした。
