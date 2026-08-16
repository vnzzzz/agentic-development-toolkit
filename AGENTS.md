# Repository作業ルール

このrepositoryはDev Container Featureのsource、test、CI、release設定だけを管理します。consumer projectのsourceやSkill collectionを管理しません。

## Security constraints

- credential、token、認証済みconfigをFeature source、test fixture、artifactへ含めない。
- hostのcredential directory、SSH directory、Docker socketをFeatureからmountしない。
- 外部GitHub Actionsはfull commit SHAで固定し、workflow permissionは必要最小限にする。
- release workflowでは個人PATを使わず、workflow固有の`GITHUB_TOKEN`を使う。
- 既にpublish済みのexact Feature versionを上書きしない。GHCRのversion照会を判定できない場合もreleaseを止める。
- testを通すためにsecurity boundaryやvalidationを弱めない。

## Scope

- Featureの配布境界は`src/<feature-id>/`とする。配布後にrepository外のfileへ依存させない。
- `test/<feature-id>/`は対応するFeatureを実containerで検証する。
- project固有runtime、service、port、dependencyはconsumer repositoryへ置く。
- consumer repositoryをこのrepository配下へcloneするworkspace機構、Skill探索link、submodule管理を追加しない。
- Claude Code / Codexの既定versionはFeature metadataだけで管理し、別のdependency manifestへ複製しない。
- repository自身の`.devcontainer`は公開済み`agent-dev`だけを参照し、編集中の`src/agent-dev`をlocal Featureとして参照しない。

## Workflow

1. Featureの挙動を変更する場合は`src/agent-dev/`と対応するtestを更新する。
2. release対象の変更では`src/agent-dev/devcontainer-feature.json`のSemVerを更新する。
3. Claude Code / Codexの既定versionを変える場合はFeature metadataを更新し、実container testで導入結果を確認する。
4. `make validate`を実行する。
5. Dockerが利用できる場合は`make test`も実行する。
6. PRでは`feature-ci`と`security`が成功していることを確認する。
7. self-hosting用`.devcontainer-lock.json`は未公開versionへ先行更新しない。新versionのrelease後、必要に応じて別changeで`devcontainer upgrade`する。

## Documentation

- READMEはrepositoryの目的、基本workflow、入口だけを記載する。
- Featureのconsumer contract、version、releaseは`docs/dev-container-feature.md`を正本とする。
- trust boundaryとcredentialの扱いは`SECURITY.md`を正本とする。
- 同じ仕様を複数documentへ複製しない。

## Supporting documents

- [README.md](README.md)
- [docs/dev-container-feature.md](docs/dev-container-feature.md)
- [SECURITY.md](SECURITY.md)
