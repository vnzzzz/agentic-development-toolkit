# セキュリティポリシー

## 信頼モデル

Agent Skillは、instructionsだけでなくscript、dependency、symlink、binary assetを含み得る実行可能なsupply-chain inputとして扱います。

Skillを利用する前に、そのsource repositoryが配布する`SKILL.md`とruntime resourceを確認し、必要な権限と外部アクセスを把握してください。

## 共通Dev Container Featureのセキュリティ制御

`src/agent-dev/`のFeatureは、複数projectで再利用するAgent開発環境を配布します。

- Feature sourceとGHCR artifactへcredential、token、認証済みconfigを含めない。
- Claude Code、Codex、GitHub CLIの認証状態は相互に分離したnamed volumeへ保存する。
- volume名には`${devcontainerId}`を含め、別Dev Containerとの認証状態共有を避ける。
- hostのcredential directory、SSH directory、Docker socketをbind mountしない。
- Claude CodeとCodex CLIの既定versionはFeature metadataで固定する。
- GitHub CLIとNode.jsは公式Dev Container Featureへの依存として導入する。
- GitHub ActionsからGHCRへpublishするときはworkflow固有の`GITHUB_TOKEN`を利用し、個人PATをCI secretへ保存しない。
- 外部GitHub Actionsはfull commit SHAで固定する。

volume名やcontainer内のmount先は秘密情報として扱いません。公開Featureからこれらの構成が分かっても、named volumeに保存されたcredentialそのものは公開されません。

一方、認証済みDev Container内で同じuser権限により実行されるcodeは、そのcontainerの認証状態へアクセスできます。認証volumeを利用するDev Containerはtrusted repository向けの環境とし、未確認のrepository、script、dependencyをcredential access可能な状態で実行しないでください。

## 親ワークスペースのセキュリティ制御

Featureへの移行が完了するまで、既存の親ワークスペースは次を管理します。

- Dev Containerはnon-rootの`vscode` userで実行する。
- Claude Code、Codex、GitHub CLIの認証情報は相互に分離したnamed volumeへ保存する。
- repository設定からhost credential directoryやDocker socketをmountしない。
- Agent CLIのversionは`package.json`で固定する。
- GitHub CLIは公式Dev Container Feature `ghcr.io/devcontainers/features/github-cli:1`から導入する。
- Dev Container起動時にGit初期化、submodule更新、source repository固有dependencyの導入、source repository固有testの実行を行わない。
- post-create時のローカルSkill link生成はbest-effortとし、不正なローカルsourceが親環境そのものの利用を妨げないようにする。
- 親CIは親のcode、shell script、configuration、template、security設定を検証し、`repos/*`のSkill固有runtimeを中央実行しない。
- 外部GitHub Actionsはfull commit SHAで固定する。

## Skillソースリポジトリとの境界

`repos/*`は親Gitからignoreされます。各source repositoryは、自身のSkill本体、runtime dependency、test、fixture、manifest、CI、security update、releaseを所有します。

standalone Skillでは`skill/`全体を配布バンドルとし、配布後にrepository-only fileへ依存しないことをsource repository側で検証します。Plugin repositoryでは、provider自身がPlugin metadataとnative Plugin loadingを検証します。

第三者のSkillをリンクまたは実行する前に、少なくとも次を確認してください。

1. `SKILL.md`、bundled script、dependency、binary asset、symlinkを確認する。
2. network access、subprocess、credential access、filesystem write、destructive operationが必要か確認する。
3. source repositoryが提供するtestとsecurity checkを実行する。
4. credential、Skill root外へescapeするsymlink、obfuscated code、mutable remote URLから直接実行されるcodeを許可しない。

## セキュリティ問題の報告

Issueへcredentialや機密sourceを貼り付けないでください。再現に必要な最小情報、関連version、機密情報を除去したcommand outputを共有してください。
