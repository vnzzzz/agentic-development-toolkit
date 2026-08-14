from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import skill_workspace


def write_skill(skill_root: Path, name: str) -> None:
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Plugin repository fixture.\n---\n",
        encoding="utf-8",
    )


class PluginRepositoryLayoutTests(unittest.TestCase):
    def patch_workspace(self, temp_root: Path):
        discovery = (temp_root / ".claude" / "skills", temp_root / ".agents" / "skills")
        return patch.multiple(
            skill_workspace,
            ROOT=temp_root,
            REPOS_DIR=temp_root / "repos",
            DISCOVERY_DIRS=discovery,
        )

    def test_discovers_skills_inside_plugin_marketplace_repository(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repository = temp_root / "repos" / "shared-marketplace"
            write_skill(repository / "plugins" / "shared" / "skills" / "readable-code", "readable-code")
            write_skill(
                repository / "plugins" / "shared" / "skills" / "japanese-technical-writing",
                "japanese-technical-writing",
            )

            with self.patch_workspace(temp_root):
                skills = skill_workspace.discover_skills()

            self.assertEqual(
                ["japanese-technical-writing", "readable-code"],
                [skill.name for skill in skills],
            )
            self.assertTrue(all(skill.layout == "plugin-collection" for skill in skills))

    def test_links_plugin_repository_skills_for_both_agents(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_root = (
                temp_root
                / "repos"
                / "shared-marketplace"
                / "plugins"
                / "shared"
                / "skills"
                / "readable-code"
            )
            write_skill(skill_root, "readable-code")
            discovery = (temp_root / ".claude" / "skills", temp_root / ".agents" / "skills")

            with self.patch_workspace(temp_root):
                self.assertEqual(0, skill_workspace.command_link())

            for directory in discovery:
                self.assertEqual(skill_root.resolve(), (directory / "readable-code").resolve())

    def test_rejects_ambiguous_root_collection_and_plugin_layout(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir) / "repository"
            write_skill(repository / "skills" / "one", "one")
            write_skill(repository / "plugins" / "shared" / "skills" / "two", "two")

            with self.assertRaisesRegex(ValueError, "ambiguous Skill repository layout"):
                skill_workspace.discover_repository_skills(repository)


if __name__ == "__main__":
    unittest.main()
