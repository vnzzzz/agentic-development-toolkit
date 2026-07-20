# Skill repository management

`skills/` is a local placement directory for independent Skill repositories. Child directories are ignored by the parent Git repository and are not submodules.

## Create a local child from the template

```bash
cp -R templates/skill-repository skills/<skill-name>
# Edit skills/<skill-name>/skill/SKILL.md
make validate
make link-skills
```

Initialize and publish the child repository only after choosing its real remote and ownership. The parent does not create or assume a child remote.

## Clone an existing child

Clone the actual repository into `skills/<skill-name>`, then run:

```bash
make validate
make link-skills
```

Both generated links point to the child's same `skill/` directory.

## Parent Git boundary

Before committing the parent, verify without modifying the index:

```bash
git check-ignore -v skills/<skill-name>/skill/SKILL.md
git add -n .
```

The dry-run must not include child files or generated agent discovery links. Child Git status, commits, remotes, tests, and releases are managed from the child repository itself.

## Child repository responsibilities

Each child owns:

- `skill/SKILL.md` and bundled runtime resources
- Skill-specific scripts and dependencies
- tests, fixtures, and demos
- security review and dependency updates
- manifest, versioning, releases, and distribution archives
- GitHub Actions and Dependabot configuration

The parent only discovers metadata and generates links. It does not install child dependencies or run child tests automatically.

## When to reconsider submodules

Continue with ignored local repositories while Skills are being created independently. Consider a submodule only when all of the following are true:

- a child remote repository exists and has a stable release process;
- the parent must reproduce or review a specific child commit;
- contributors accept the additional clone and update workflow;
- parent CI has a concrete reason to test a pinned child version.

Until then, do not create `.gitmodules` or make submodule initialization a Dev Container requirement.
