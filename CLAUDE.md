# Claude Code向け補足

Repository全体の作業ルールは`AGENTS.md`を正本とし、Claude Codeでも同じルールに従います。

Claude Code固有の注意点は次のとおりです。

- `.claude/skills/`はstandalone / collection Skillのローカル開発用に生成されるため、リンク先ではなく生成リンク自体を編集しない。
- Plugin repositoryのworking copyをPluginとして確認する場合は、個別Skillを`.claude/skills/`へ展開せず、`claude --plugin-dir <plugin-root>`を使用する。
- 完了前の必須checkは`AGENTS.md`に従う。
