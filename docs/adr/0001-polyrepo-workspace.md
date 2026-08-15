# ADR 0001: 独立したローカルSkill repositoryを持つ親ワークスペース

- 状態: 採用。ADR 0002により一部変更
- 日付: 2026-07-20

## 背景

開発環境はClaude CodeとCodexの両方をサポートしつつ、どちらか一方のSkill探索directoryを正本にしてはならない。また、各Skillが独自のGit履歴、CI、dependency、fixture、release processを持てる必要がある。

親リポジトリは、child Skill repositoryが1件も存在しないclone直後の状態でも利用可能である必要がある。開発途中のchild contentsを親Gitで管理するとownershipが曖昧になり、後から独立repositoryへ切り出す作業も複雑になる。

一方、親がchild commitを固定する要件はまだないため、この時点でGit submoduleを必須にするとcloneや更新の運用だけが増える。

## 決定

以下は本ADR採用時点の決定である。配置directoryと対応repository形式は後続のADR 0002で変更された。

1. 独立したchild repositoryを配置するローカルworkspaceとして`skills/`を使用する。
2. `skills/README.md`と任意の`.gitkeep`を除き、`skills/*`を親Gitからignoreする。
3. 各child repositoryの配布対象Skillを`skills/<repository>/skill/SKILL.md`へ置く。repository直下の`SKILL.md`と不完全なchild layoutは拒否する。
4. `.claude/skills/`と`.agents/skills/`から同一のchild `skill/` directoryへrelative symlinkを生成する。
5. ローカルSkillが0件の状態を正常とする。validation、link生成、diagnosis、test、CIは0件でも成功しなければならない。
6. 親のautomationはDev Container、discovery tooling、template、親test、documentation、親security設定に限定する。
7. child固有のdependency、test、fixture、demo、manifest、release、distribution artifact、CI、Dependabotは各child repositoryで管理する。
8. Git submoduleは採用しない。親がreview済みchild commitを再現可能な形で固定する要件が生じた場合に再検討する。

ADR 0002は、独立したsource ownershipとsubmoduleを採用しない方針を維持したまま、ローカル配置directoryを`repos/`へ変更し、standalone repositoryに加えてcollection repositoryへ対応した。

## 影響

- 親リポジトリはSkill implementationを含まないclone直後でもcheckを通せる。
- ローカルchild repositoryを作成またはcloneしても親Git indexは変化しない。
- Claude CodeとCodexは、複製された別々のSkillではなく同じAgent-neutralな正本を参照できる。
- 親CIはtemporary fixtureでdiscovery behaviorを検証し、ローカルchildのautomationを実行しない。
- child repositoryはGit初期化、commit、publish、test、releaseを独立して行う必要がある。
- 親リポジトリはローカルでcheckoutされているchild commitを記録しない。

## 検討した代替案

### Git submoduleを最初から使う

現時点ではchild commitを固定する要件がなく、child remoteの存在も前提にできないため採用しなかった。親からchild versionを再現可能に選択する要件が生じた場合の選択肢として残す。

### Git subtreeを使う

双方向のhistory synchronizationに運用負荷があり、child contentsも親historyへ残るため採用しなかった。

### 全Skillを親monorepoで管理する

ownership boundaryが不明確になり、後から独立したhistoryやreleaseへ分けにくくなるため採用しなかった。

### AgentごとのSkill探索directoryへSkillを複製する

copy間でdriftが発生し、一方のAgentにだけ修正が入る可能性があるため採用しなかった。
