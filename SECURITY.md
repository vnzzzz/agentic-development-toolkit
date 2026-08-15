# セキュリティポリシー

## 信頼モデル

`agent-dev`はClaude Code、Codex、GitHub CLIを導入し、認証状態を永続化する開発環境です。Featureを利用するDev Container内で同じuser権限により実行されるcodeは、そのcontainerの認証状態へアクセスできるため、trusted repositoryでの利用を前提とします。

## Featureのセキュリティ制御

- Feature sourceとGHCR artifactへcredential、token、認証済みconfigを含めない。
- Claude Code、Codex、GitHub CLIの認証状態は相互に分離したnamed volumeへ保存する。
- volume名には`${devcontainerId}`を含め、Dev Container単位で分離する。
- hostのcredential directory、SSH directory、Docker socketをbind mountしない。
- Claude CodeとCodex CLIの既定versionを固定する。
- Node.jsとGitHub CLIは公式Dev Container Featureへの依存として導入する。
- GitHub ActionsからGHCRへpublishするときはworkflow固有の`GITHUB_TOKEN`を利用し、個人PATをCI secretへ保存しない。
- 外部GitHub Actionsはfull commit SHAで固定する。

volume名、container内mount先、環境変数は秘密情報ではありません。これらが公開されても、named volumeに保存されたcredentialそのものはFeature sourceやartifactへ含まれません。

認証状態を破棄する場合は対象Dev Containerを削除したうえで対応するnamed volumeを削除し、必要に応じてprovider側でもtoken/sessionをrevokeします。

## Feature authoring repositoryの境界

このrepository自身の`.devcontainer/`はFeature authoring用の最小環境です。配布対象の`agent-dev`を自己参照せず、consumer repositoryを配下へcloneする親workspace機構も持ちません。

実container testはDockerが利用できる環境またはGitHub Actionsで実行します。distributed Featureへhost Docker socketやprivileged設定を追加してtest環境を成立させることはしません。

## セキュリティ問題の報告

Issueへcredentialや機密sourceを貼り付けないでください。再現に必要な最小情報、関連version、機密情報を除去したcommand outputを共有してください。
