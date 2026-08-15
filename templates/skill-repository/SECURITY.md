# セキュリティポリシー

`SKILL.md`、bundled script、dependency、symlink、binary assetは、実行可能なsupply-chain inputとして扱います。

Skillがnetwork access、subprocess、filesystem write、credential access、destructive operationを必要とする場合は、その条件と目的を明示してください。

次を禁止します。

- credentialやsecretのcommit
- Skill root外へescapeするsymlink
- 内容をreviewできないobfuscated executableの同梱
- mutable remote URLから取得したcodeを検証せず直接実行する仕組み

配布後に必要なruntime resourceは`skill/`内へ含め、`make test`でdistribution boundaryを確認してください。
