# Skill repository template

Rename this repository and the `name` field in `skill/SKILL.md` to the same lowercase hyphenated Skill name.

`skill/` is the distributable bundle. Keep repository-only tests, fixtures, CI, dependency metadata, and release tooling outside it. Do not add a repository-root `SKILL.md`.

Run:

```bash
make test
```

`make test` validates the Skill metadata, copies `skill/` into an isolated temporary directory, checks bundled local links and symlink boundaries, syntax-checks bundled Python / shell scripts, and then runs repository tests.

For Skills with executable scripts, add integration tests that execute the copied distributable bundle against representative fixtures. Repository tests may use fixtures outside `skill/`, but the runtime Skill must not depend on repository-only files after distribution.
