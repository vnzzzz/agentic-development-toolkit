# Repository作業ルール

このrepositoryは、複数projectで利用するDev Container Featureのsource、test、CI、release設定を管理します。

## 責務境界

- `src/<feature-id>/`をFeatureの配布境界とする。配布後にrepository外のfileへ依存させない。
- `test/<feature-id>/`は`src/<feature-id>/`と対応させ、実containerでFeatureの契約を検証する。
- consumer repositoryをこのrepository配下へcloneするworkspace機構、Skill探索link、submodule管理を追加しない。
- project固有runtime、service、port、dependencyはconsumer repository側へ置く。
- Claude Code / Codexの既定versionを変更する場合は`package.json`とFeature metadataを同期し、Feature versionも更新する。
- credential、token、認証済みconfigをFeature sourceやartifactへ含めない。
- hostのcredential directory、SSH directory、Docker socketをFeatureからmountしない。
- 外部GitHub Actionsはfull commit SHAで固定し、workflow permissionは最小化する。
- testを通すためにsecurity boundaryやvalidationを弱めない。

## 文書

- READMEはrepositoryの役割と基本操作に限定する。
- Featureの利用契約、認証境界、release手順は`docs/dev-container-feature.md`を正本とする。
- security ruleは`SECURITY.md`を正本とする。

## 必須check

変更完了前に次を実行する。

```bash
make validate
```

Dockerが利用できる環境では追加で次を実行する。

```bash
make test
```

PRではGitHub Actionsの`feature-ci`と`security`が成功していることを確認する。
