# ADR 0002: standalone / collection Skill repositoryをサポートする

- 状態: 採用。ADR 0003により一部変更
- 日付: 2026-08-14

## 背景

ADR 0001では、Agent Skillのsourceを親Git historyの外へ置き、Claude CodeとCodexの双方から一つの正本を参照する親ワークスペースを採用した。

当初のimplementationは、`skills/<repository>/skill/SKILL.md`に1 repositoryあたり1 Skillを置く前提だった。一方、新しい共有repositoryである`agent-skills`は、`skills/<skill-name>/SKILL.md`配下に複数の再利用可能なSkillを持つcollectionとして構成されている。

standalone形式をcollection形式へ置き換えると、独立したrepository、history、dependency、test、release processを必要とするSkillの開発性を失う。また、`agent-skills`だけをspecial caseにすると、親ワークスペースが特定repositoryへ依存する。

## 決定

以下は本ADR採用時点の決定である。Plugin repositoryの追加とPlugin Skillのdirect link停止は後続のADR 0003で変更された。

1. 親ワークスペースで配置する単位をSkillではなくsource repositoryとし、ローカル配置directoryを`skills/`から`repos/`へ変更する。
2. 次の2つのrepository layoutをサポートする。
   - standalone: `repos/<repository>/skill/SKILL.md`
   - collection: `repos/<repository>/skills/<skill-name>/SKILL.md`
3. 既存のstandalone repository templateを維持する。
4. 両layoutの全Skillを探索し、`.claude/skills/<name>`と`.agents/skills/<name>`から実際のSkill rootへ直接リンクする。
5. standalone repositoryではrepository directory名、collection repositoryではSkill directory名を、該当するSkillの`name`と一致させる。
6. repository直下の`SKILL.md`、`skill/`と`skills/`を併置するrepository、不完全なSkill directory、ローカルrepository間で重複するSkill名を拒否する。
7. ローカルsource repositoryが0件の状態を正常とする。明示的に作成された空のcollection `skills/` directoryも正常とする。
8. mutableな開発用source repositoryは引き続き親Gitからignoreし、Git submoduleにはしない。
9. 親automationの責務をdiscovery、repository横断validation、link生成、Dev Container、親test、documentation、親security controlに限定する。
10. `agent-skills`というrepository名をhard-codeしない。collection対応はgenericなrepository capabilityとして実装する。

ADR 0003は、Plugin marketplace repositoryを追加し、direct Skill authoringとnative Plugin distribution validationを分離した。そのため、本ADRのdirect linkに関する決定はstandalone / collection repositoryにのみ適用される。

## 影響

- 同じworkspaceでstandalone Skill repositoryと複数Skillを持つcollection repositoryを開発できる。
- collection repositoryではrepository identityとSkill identityを分離できる。
- direct authoring対象では、Claude CodeとCodexがcopyではなく同じSkill sourceを参照し続ける。
- 親validationはlink生成前にstandalone / collection source間のname collisionを検出できる。
- 旧`skills/`配下のlocal working copyは`repos/`配下へ移動または再cloneする必要がある。
- 対応layoutを持たないsource repositoryはsilent ignoreせずconfiguration errorとする。
- 親ワークスペース自身が通常利用するshared Skillのversion選択は、mutableな開発working copyとは別の問題として扱う。

## 検討した代替案

### collection repositoryだけをサポートする

独立したlifecycle、dependency、test、distributionを必要とするSkillではstandalone repositoryが引き続き有用なため採用しなかった。

### 親配置directoryを`skills/`のままにする

repository自体を配置するdirectoryの中に、さらにcollection用の`skills/`が現れ、`skills/agent-skills/skills/...`のようにownership unitが分かりにくくなるため採用しなかった。`repos/`は配置単位がrepositoryであることを明確にする。

### `agent-skills`だけをspecial caseにする

特定repository名やURLではなくrepository shapeをサポートすべきであるため採用しなかった。

### mutableな開発repositoryをsubmoduleへ変換する

ADR 0001と同じ理由で採用しなかった。親はmutableな開発working copyのrevisionを固定する必要がない。
