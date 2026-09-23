# GitHub App Authentication for Agents

[日本語](github-agent-identity.ja.md)

`agent-github-auth` runs GitHub operations from Claude Code / Codex as dedicated GitHub App bots, separate from a personal account.

The actor recorded by the GitHub API and the Author / Committer recorded in Git commits are separate identities. This command aligns both with the same App bot.

## Model

| Actor | GitHub account |
|---|---|
| Human operations | GitHub user |
| Claude Code | Dedicated GitHub App for Claude |
| Codex | Dedicated GitHub App for Codex |

Create a dedicated GitHub App for each Agent and control repository access and permissions on GitHub. See the official GitHub documentation for App registration, permission configuration, and installation.[^1][^2][^3]

The baseline permissions are:

```text
Metadata       read
Contents       read/write
Issues         read/write
Pull requests  read/write
```

Add read access for `Actions` / `Checks` / `Commit statuses` only when needed. Do not grant `Administration` / `Workflows` / `Secrets` / `Environments` / `Actions write` by default.

`Only select repositories` is recommended for repository access. [SECURITY.md](../SECURITY.md) is canonical for credential and permission boundaries.

## Configuration

An authentication profile stores only the App ID.

```bash
agent-github-auth configure claude <APP_ID>
agent-github-auth configure codex <APP_ID>
```

Place private keys at:

```text
~/.config/agent-dev/github-apps/claude/private-key.pem
~/.config/agent-dev/github-apps/codex/private-key.pem
```

A private key must be mode `0600` and owned by the executing user. It is lost when the Dev Container is rebuilt and must be restored after a rebuild.

Check configuration with:

```bash
agent-github-auth status claude
```

`status` verifies the App, its installation on the current repository, and issuance and revocation of a repository-scoped Installation Token. It never prints the token value. See the official documentation for GitHub App authentication and Installation Tokens.[^4][^5]

## Sessions

Interactive session:

```bash
agent-github-auth claude
```

Run a specific command:

```bash
agent-github-auth claude -- claude
agent-github-auth codex -- codex
```

The `origin` at session start is fixed as the authenticated repository. Start a new session from another repository before operating on that repository.

A session enforces the following:

- Issue a short-lived Installation Token for each authenticated `gh` or Git operation and never store it on disk.
- Align `gh`, Git, and commit Author / Committer with the same App bot.
- Do not use personal `gh auth`, ambient GitHub tokens, or existing Git credentials.
- Reject `gh` operations that explicitly target hosts other than `github.com`.
- Reject operations when another Authorization header, credential helper, or credential-bearing URL is active.
- Do not fall back to GitHub SSH or interactive credential input.

Git commands using an App token are limited to `fetch` / `pull` / `push` / `ls-remote`. Network operations through Git aliases are not supported.

See [SECURITY.md](../SECURITY.md) for the security boundary, including private-key compromise.

## Ruleset

Do not grant the GitHub App bypass access to the default branch. At minimum, enforce the following with repository Rulesets:

- Require Pull Requests
- Require status checks
- Block force pushes
- Block branch deletion
- Block direct default-branch updates by GitHub Apps

`agent-dev` does not create Rulesets automatically. See the official GitHub documentation for Ruleset configuration.[^6][^7]

## References

[^1]: [GitHub Docs, Registering a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app)
[^2]: [GitHub Docs, Choosing permissions for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)
[^3]: [GitHub Docs, Installing your own GitHub App](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app)
[^4]: [GitHub Docs, Authenticating as a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app)
[^5]: [GitHub Docs, Generating an installation access token for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)
[^6]: [GitHub Docs, About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
[^7]: [GitHub Docs, Creating rulesets for a repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)
