# Recommended GitHub repository settings

Workflow files cannot enforce repository-level controls. Apply settings according to repository ownership rather than assuming the parent and every child have identical checks.

## Parent repository

- Protect `main` and require the parent `ci` checks that actually exist.
- Block force pushes and branch deletion.
- Enable Dependabot alerts and security updates for parent-managed dependencies.
- Enable secret scanning and push protection where the repository plan supports them.
- Restrict Actions to GitHub-owned actions or an explicit allowlist.
- Require approval for first-time external contributors.
- Set the default `GITHUB_TOKEN` permission to read-only.

The parent Dependabot configuration covers only parent manifests. It does not update ignored repositories under `skills/`.

## Child Skill repositories

Each child configures its own required checks, dependency updates, code scanning, release protection, and access controls. Child Dependabot must live in the child repository and cover that child's manifests.

## GitHub Code Security checks

Dependency Review and CodeQL run automatically for public repositories. For a private repository with the required GitHub security product enabled, create this repository variable:

```text
ENABLE_GHAS_CHECKS=true
```

Without that product, those jobs are intentionally skipped for private repositories; portable parent checks continue to run.

## Future pinned-child integration

The parent currently uses no submodules. If a future requirement introduces pinned child commits, document and review the checkout/update workflow at that time rather than preconfiguring it now.
