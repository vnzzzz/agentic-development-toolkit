from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import skill_workspace  # noqa: E402


def create_skill(workspace: Path, name: str = "sample") -> Path:
    skill_root = workspace / "skills" / name / "skill"
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Temporary Skill fixture for workspace tests.\n---\n\n# Sample\n",
        encoding="utf-8",
    )
    return skill_root


class WorkspaceTests(unittest.TestCase):
    def test_empty_workspace_is_valid(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skills_dir = temp_root / "skills"
            skills_dir.mkdir()
            with (
                patch.object(skill_workspace, "ROOT", temp_root),
                patch.object(skill_workspace, "SKILLS_DIR", skills_dir),
                redirect_stdout(StringIO()) as output,
            ):
                self.assertEqual(0, skill_workspace.command_validate())
                self.assertEqual([], skill_workspace.discover_skills())
            self.assertIn("Validated 0 Skill(s).", output.getvalue())

    def test_temporary_skill_fixture_is_valid(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_root = create_skill(temp_root)
            with (
                patch.object(skill_workspace, "ROOT", temp_root),
                patch.object(skill_workspace, "SKILLS_DIR", temp_root / "skills"),
            ):
                skills = skill_workspace.discover_skills()
                self.assertEqual(["sample"], [skill.name for skill in skills])
                self.assertEqual([], skill_workspace.validate_skill(skills[0]))
                self.assertEqual(skill_root, skills[0].skill_root)

    def test_frontmatter_requires_delimiters(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "SKILL.md"
            path.write_text("name: invalid\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "opening YAML"):
                skill_workspace.parse_frontmatter(path)

    def test_link_creates_both_agent_discovery_entries(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_root = create_skill(temp_root)
            discovery = (temp_root / ".claude" / "skills", temp_root / ".agents" / "skills")
            with (
                patch.object(skill_workspace, "ROOT", temp_root),
                patch.object(skill_workspace, "SKILLS_DIR", temp_root / "skills"),
                patch.object(skill_workspace, "DISCOVERY_DIRS", discovery),
            ):
                self.assertEqual(0, skill_workspace.command_link())
                for directory in discovery:
                    link = directory / "sample"
                    self.assertTrue(link.is_symlink())
                    self.assertEqual(skill_root.resolve(), link.resolve())

    def test_link_with_no_skills_removes_stale_generated_links(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skills_dir = temp_root / "skills"
            skills_dir.mkdir()
            discovery = (temp_root / ".claude" / "skills", temp_root / ".agents" / "skills")
            for directory in discovery:
                directory.mkdir(parents=True)
                (directory / "stale").symlink_to("../../skills/stale/skill", target_is_directory=True)
            with (
                patch.object(skill_workspace, "ROOT", temp_root),
                patch.object(skill_workspace, "SKILLS_DIR", skills_dir),
                patch.object(skill_workspace, "DISCOVERY_DIRS", discovery),
            ):
                self.assertEqual(0, skill_workspace.command_link())
            self.assertTrue(all(not (directory / "stale").exists() for directory in discovery))
            self.assertTrue(all(not (directory / "stale").is_symlink() for directory in discovery))

    def test_doctor_succeeds_with_no_skills(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skills_dir = temp_root / "skills"
            skills_dir.mkdir()
            with (
                patch.object(skill_workspace, "ROOT", temp_root),
                patch.object(skill_workspace, "SKILLS_DIR", skills_dir),
                patch.object(skill_workspace.shutil, "which", return_value=None),
                redirect_stdout(StringIO()) as output,
            ):
                self.assertEqual(0, skill_workspace.command_doctor())
            self.assertIn("skills:\n", output.getvalue())

    def test_devcontainer_is_simple_and_supports_both_agents(self) -> None:
        dockerfile = (ROOT / ".devcontainer" / "Dockerfile").read_text(encoding="utf-8")
        self.assertLess(dockerfile.index("/etc/apt/sources.list.d/yarn.list"), dockerfile.index("    apt-get update;"))
        self.assertNotIn("bubblewrap", dockerfile)
        self.assertNotIn("iptables", dockerfile)
        self.assertNotIn("COPY skills", dockerfile)
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

    def test_parent_git_boundary_ignores_local_skills_and_generated_links(self) -> None:
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        for expected in (
            "/skills/*",
            "!/skills/README.md",
            "!/skills/.gitkeep",
            ".claude/skills/*",
            ".agents/skills/*",
        ):
            self.assertIn(expected, gitignore)
        self.assertFalse((ROOT / ".gitmodules").exists())

    def test_parent_automation_does_not_own_local_skills(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        security = (ROOT / ".github" / "workflows" / "security.yml").read_text(encoding="utf-8")
        for text in (makefile, ci, security):
            self.assertNotIn("skills/*", text)
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
