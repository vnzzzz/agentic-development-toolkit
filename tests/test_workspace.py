from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import skill_workspace


def write_skill(skill_root: Path, name: str) -> None:
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Temporary Skill fixture for workspace tests.\n---\n\n# Sample\n",
        encoding="utf-8",
    )


def create_standalone_skill(workspace: Path, name: str = "sample") -> Path:
    skill_root = workspace / "repos" / name / "skill"
    write_skill(skill_root, name)
    return skill_root


def create_collection_skill(
    workspace: Path, repository: str = "collection", name: str = "sample"
) -> Path:
    skill_root = workspace / "repos" / repository / "skills" / name
    write_skill(skill_root, name)
    return skill_root


class WorkspaceTests(unittest.TestCase):
    def patch_workspace(self, temp_root: Path):
        return patch.multiple(
            skill_workspace,
            ROOT=temp_root,
            REPOS_DIR=temp_root / "repos",
        )

    def test_empty_workspace_is_valid(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "repos").mkdir()
            with self.patch_workspace(temp_root), redirect_stdout(StringIO()) as output:
                self.assertEqual(0, skill_workspace.command_validate())
                self.assertEqual([], skill_workspace.discover_skills())
            self.assertIn("Validated 0 Skill(s).", output.getvalue())

    def test_standalone_skill_fixture_is_valid(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_root = create_standalone_skill(temp_root)
            with self.patch_workspace(temp_root):
                skills = skill_workspace.discover_skills()
                self.assertEqual(["sample"], [skill.name for skill in skills])
                self.assertEqual("standalone", skills[0].layout)
                self.assertEqual([], skill_workspace.validate_skill(skills[0]))
                self.assertEqual(skill_root, skills[0].skill_root)

    def test_collection_repository_discovers_multiple_skills(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            first = create_collection_skill(temp_root, name="first")
            second = create_collection_skill(temp_root, name="second")
            with self.patch_workspace(temp_root):
                skills = skill_workspace.discover_skills()
                self.assertEqual(["first", "second"], [skill.name for skill in skills])
                self.assertTrue(all(skill.layout == "collection" for skill in skills))
                self.assertEqual([first, second], [skill.skill_root for skill in skills])
                self.assertTrue(all(not skill_workspace.validate_skill(skill) for skill in skills))

    def test_standalone_and_collection_can_be_discovered_together(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            create_standalone_skill(temp_root, "standalone")
            create_collection_skill(temp_root, "collection", "shared")
            with self.patch_workspace(temp_root):
                skills = skill_workspace.discover_skills()
            self.assertEqual(["shared", "standalone"], [skill.name for skill in skills])

    def test_repository_root_skill_is_rejected(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repository = temp_root / "repos" / "sample"
            repository.mkdir(parents=True)
            (repository / "SKILL.md").write_text(
                "---\nname: sample\ndescription: Noncanonical fixture.\n---\n",
                encoding="utf-8",
            )
            with (
                self.patch_workspace(temp_root),
                self.assertRaisesRegex(ValueError, "repository-root SKILL.md is not supported"),
            ):
                skill_workspace.discover_skills()

    def test_repository_without_supported_layout_is_rejected(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "repos" / "sample").mkdir(parents=True)
            with (
                self.patch_workspace(temp_root),
                self.assertRaisesRegex(ValueError, "missing supported Skill layout"),
            ):
                skill_workspace.discover_skills()

    def test_incomplete_standalone_repository_is_rejected(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "repos" / "sample" / "skill").mkdir(parents=True)
            with (
                self.patch_workspace(temp_root),
                self.assertRaisesRegex(ValueError, "missing canonical Skill file skill/SKILL.md"),
            ):
                skill_workspace.discover_skills()

    def test_incomplete_collection_skill_is_rejected(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "repos" / "collection" / "skills" / "sample").mkdir(parents=True)
            with (
                self.patch_workspace(temp_root),
                self.assertRaisesRegex(ValueError, "missing canonical collection Skill file"),
            ):
                skill_workspace.discover_skills()

    def test_ambiguous_repository_layout_is_rejected(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            create_standalone_skill(temp_root, "sample")
            (temp_root / "repos" / "sample" / "skills").mkdir()
            with (
                self.patch_workspace(temp_root),
                self.assertRaisesRegex(ValueError, "ambiguous Skill repository layout"),
            ):
                skill_workspace.discover_skills()

    def test_collection_skill_directory_must_match_name(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_root = temp_root / "repos" / "collection" / "skills" / "wrong-dir"
            write_skill(skill_root, "expected-name")
            with self.patch_workspace(temp_root):
                skill = skill_workspace.discover_skills()[0]
                errors = skill_workspace.validate_skill(skill)
            self.assertTrue(any("collection Skill directory must match" in error for error in errors))

    def test_duplicate_skill_name_across_repositories_is_rejected(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            create_standalone_skill(temp_root, "duplicate")
            create_collection_skill(temp_root, "collection", "duplicate")
            with self.patch_workspace(temp_root), redirect_stderr(StringIO()) as error_output:
                self.assertEqual(1, skill_workspace.command_validate())
            self.assertIn("duplicate Skill name 'duplicate'", error_output.getvalue())

    def test_empty_collection_repository_is_valid(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "repos" / "collection" / "skills").mkdir(parents=True)
            with self.patch_workspace(temp_root), redirect_stdout(StringIO()):
                self.assertEqual([], skill_workspace.discover_skills())
                self.assertEqual(0, skill_workspace.command_validate())

    def test_frontmatter_requires_delimiters(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "SKILL.md"
            path.write_text("name: invalid\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "opening YAML"):
                skill_workspace.parse_frontmatter(path)

    def test_link_creates_entries_for_both_repository_layouts(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            standalone_root = create_standalone_skill(temp_root, "standalone")
            collection_root = create_collection_skill(temp_root, "collection", "shared")
            discovery = (temp_root / ".claude" / "skills", temp_root / ".agents" / "skills")
            with (
                self.patch_workspace(temp_root),
                patch.object(skill_workspace, "DISCOVERY_DIRS", discovery),
            ):
                self.assertEqual(0, skill_workspace.command_link())
                for directory in discovery:
                    self.assertEqual(standalone_root.resolve(), (directory / "standalone").resolve())
                    self.assertEqual(collection_root.resolve(), (directory / "shared").resolve())

    def test_link_with_no_skills_removes_stale_generated_links(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "repos").mkdir()
            discovery = (temp_root / ".claude" / "skills", temp_root / ".agents" / "skills")
            for directory in discovery:
                directory.mkdir(parents=True)
                (directory / "stale").symlink_to("../../repos/stale/skill", target_is_directory=True)
            with (
                self.patch_workspace(temp_root),
                patch.object(skill_workspace, "DISCOVERY_DIRS", discovery),
            ):
                self.assertEqual(0, skill_workspace.command_link())
            self.assertTrue(all(not (directory / "stale").exists() for directory in discovery))
            self.assertTrue(all(not (directory / "stale").is_symlink() for directory in discovery))

    def test_doctor_succeeds_with_no_skills(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "repos").mkdir()
            with (
                self.patch_workspace(temp_root),
                patch.object(skill_workspace.shutil, "which", return_value=None),
                redirect_stdout(StringIO()) as output,
            ):
                self.assertEqual(0, skill_workspace.command_doctor())
            self.assertIn("skills:\n- none", output.getvalue())

    def test_doctor_reports_invalid_skill_without_traceback(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_file = temp_root / "repos" / "sample" / "skill" / "SKILL.md"
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text("name: invalid\n", encoding="utf-8")
            with (
                self.patch_workspace(temp_root),
                patch.object(skill_workspace.shutil, "which", return_value=None),
                redirect_stdout(StringIO()) as output,
            ):
                self.assertEqual(1, skill_workspace.command_doctor())
            diagnostics = output.getvalue()
            self.assertIn("skills:\n- discovery failed:", diagnostics)
            self.assertIn("missing opening YAML frontmatter delimiter", diagnostics)
            self.assertNotIn("Traceback", diagnostics)

    def test_doctor_reports_frontmatter_validation_errors(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_root = temp_root / "repos" / "sample" / "skill"
            skill_root.mkdir(parents=True)
            (skill_root / "SKILL.md").write_text(
                "---\nname: sample\ndescription:\n---\n",
                encoding="utf-8",
            )
            with (
                self.patch_workspace(temp_root),
                patch.object(skill_workspace.shutil, "which", return_value=None),
                redirect_stdout(StringIO()) as output,
            ):
                self.assertEqual(1, skill_workspace.command_doctor())
            diagnostics = output.getvalue()
            self.assertIn("[local-directory, standalone, invalid]", diagnostics)
            self.assertIn("required frontmatter field 'description' is empty", diagnostics)

    def test_devcontainer_is_simple_and_supports_both_agents(self) -> None:
        dockerfile = (ROOT / ".devcontainer" / "Dockerfile").read_text(encoding="utf-8")
        self.assertLess(dockerfile.index("/etc/apt/sources.list.d/yarn.list"), dockerfile.index("    apt-get update;"))
        self.assertNotIn("bubblewrap", dockerfile)
        self.assertNotIn("iptables", dockerfile)
        self.assertNotIn("COPY repos", dockerfile)
        self.assertNotIn("pip install", dockerfile)

        devcontainer = json.loads((ROOT / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8"))
        node_options = devcontainer["features"]["ghcr.io/devcontainers/features/node:1"]
        self.assertIs(node_options["installYarnUsingApt"], False)
        self.assertEqual("vscode", devcontainer["remoteUser"])
        self.assertNotIn("initializeCommand", devcontainer)
        self.assertNotIn("runArgs", devcontainer)
        mounts = devcontainer["mounts"]
        self.assertTrue(any("target=/home/vscode/.claude" in mount for mount in mounts))
        self.assertTrue(any("target=/home/vscode/.codex" in mount for mount in mounts))
        extensions = devcontainer["customizations"]["vscode"]["extensions"]
        self.assertIn("anthropic.claude-code", extensions)
        self.assertIn("openai.chatgpt", extensions)

        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertRegex(package["dependencies"]["@anthropic-ai/claude-code"], r"^\d+\.\d+\.\d+$")
        self.assertRegex(package["dependencies"]["@openai/codex"], r"^\d+\.\d+\.\d+$")
        installer = (ROOT / "scripts" / "install-agent-clis.sh").read_text(encoding="utf-8")
        self.assertIn("package.json", installer)
        self.assertIn("@anthropic-ai/claude-code", installer)
        self.assertIn("@openai/codex", installer)

        post_create = (ROOT / ".devcontainer" / "post-create.sh").read_text(encoding="utf-8")
        executable_commands = post_create.split("cat <<", 1)[0]
        self.assertNotIn("make test", executable_commands)
        self.assertNotIn("install-skill-dependencies", post_create)
        self.assertIn("skill_workspace.py link", post_create)
        self.assertFalse((ROOT / ".devcontainer" / "install-skill-dependencies.sh").exists())

    def test_parent_git_boundary_ignores_local_repositories_and_generated_links(self) -> None:
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        for expected in (
            "/repos/*",
            "!/repos/README.md",
            "!/repos/.gitkeep",
            ".claude/skills/*",
            ".agents/skills/*",
        ):
            self.assertIn(expected, gitignore)
        self.assertNotIn("/skills/*", gitignore)
        self.assertFalse((ROOT / ".gitmodules").exists())

    @unittest.skipUnless(shutil.which("git"), "git is required for ignore-boundary validation")
    def test_parent_gitignore_semantics_exclude_sources_and_generated_links(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            shutil.copy2(ROOT / ".gitignore", repository / ".gitignore")
            (repository / "repos" / "sample" / "skill").mkdir(parents=True)
            (repository / "repos" / "sample" / "skill" / "SKILL.md").write_text(
                "fixture", encoding="utf-8"
            )
            (repository / "repos" / "README.md").write_text("tracked", encoding="utf-8")
            for discovery in (".claude", ".agents"):
                path = repository / discovery / "skills" / "sample"
                path.parent.mkdir(parents=True)
                path.write_text("generated", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)

            ignored = (
                "repos/sample/skill/SKILL.md",
                ".claude/skills/sample",
                ".agents/skills/sample",
            )
            for relative in ignored:
                completed = subprocess.run(
                    ["git", "check-ignore", "--no-index", "-q", relative],
                    cwd=repository,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, relative)

            readme = subprocess.run(
                ["git", "check-ignore", "--no-index", "-q", "repos/README.md"],
                cwd=repository,
                check=False,
            )
            self.assertEqual(1, readme.returncode)

    def test_parent_automation_does_not_own_local_repositories(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        security = (ROOT / ".github" / "workflows" / "security.yml").read_text(encoding="utf-8")
        for text in (makefile, ci, security):
            self.assertNotIn("repos/*", text)
            self.assertNotIn("requirements.lock", text)
            self.assertNotIn("skill_workspace.py test", text)
        self.assertNotIn("export-skill", makefile)

    def test_skill_repository_template_is_self_validating(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir) / "sample-skill"
            shutil.copytree(ROOT / "templates" / "skill-repository", repository)
            skill_file = repository / "skill" / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            text = text.replace("name: replace-with-skill-name", "name: sample-skill")
            text = text.replace(
                "description: Describe exactly what this Skill does, when it should trigger, and when it should not trigger.",
                "description: Validate the reusable Skill repository template.",
            )
            skill_file.write_text(text, encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, "scripts/validate_skill.py"],
                cwd=repository,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stdout)


if __name__ == "__main__":
    unittest.main()
