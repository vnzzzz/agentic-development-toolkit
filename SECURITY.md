# Security policy

## Trust model

Agent Skills are executable supply-chain inputs. Review `SKILL.md`, bundled scripts, dependencies, and binary assets in each source repository before use.

## Parent workspace controls

- The Dev Container runs as the non-root `vscode` user.
- Claude Code and Codex authentication use separate named volumes.
- Host credential directories and the Docker socket are not mounted by repository configuration.
- Agent CLI versions are pinned in `package.json`.
- Dev Container startup does not initialize Git, submodules, source-repository dependencies, or source-repository tests.
- Local Skill link generation is best-effort during post-create so an invalid local source does not prevent access to the parent environment.
- Parent CI checks only parent code, shell scripts, configuration, templates, and security settings.
- External GitHub Actions are pinned to full commit SHAs.

## Source repository boundary

Directories under `repos/*` are ignored by the parent Git repository. A source repository may be standalone (`skill/SKILL.md`) or a collection (`skills/<skill-name>/SKILL.md`). Each source repository owns review and automation for its Skill files, runtime dependencies, tests, fixtures, manifests, releases, and Dependabot configuration.

Before linking or running a third-party Skill:

1. Review its instructions, scripts, dependencies, binary assets, and symlinks.
2. Confirm the need for network, subprocesses, credential access, and destructive writes.
3. Run the source repository's own tests and security checks.
4. Do not allow credentials, escaping symlinks, obfuscated code, or execution from mutable remote URLs.

## Reporting

Do not include credentials or sensitive source files in issues. Report a minimal reproduction, relevant versions, and sanitized command output.
