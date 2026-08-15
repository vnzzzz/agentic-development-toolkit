from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "skill-repository"


def prepare_repository(temp_dir: str) -> Path:
    repository = Path(temp_dir) / "sample-skill"
    shutil.copytree(TEMPLATE, repository)
    skill_file = repository / "skill" / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    text = text.replace("name: replace-with-skill-name", "name: sample-skill")
    text = text.replace(
        "description: Describe exactly what this Skill does, when it should trigger, and when it should not trigger.",
        "description: Validate the reusable Skill repository template.",
    )
    skill_file.write_text(text, encoding="utf-8")
    return repository


def run_distribution_validation(repository: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", "test-distribution"],
        cwd=repository,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


class TemplateDistributionTests(unittest.TestCase):
    def test_template_make_test_validates_isolated_distribution_bundle(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repository = prepare_repository(temp_dir)
            (repository / "skill" / "scripts").mkdir()
            (repository / "skill" / "scripts" / "helper.py").write_text(
                "def main() -> int:\n    return 0\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                ["make", "test"],
                cwd=repository,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stdout)
            self.assertIn("Validated isolated distributable Skill bundle.", completed.stdout)

    def test_distribution_validation_rejects_repository_escape(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repository = prepare_repository(temp_dir)
            skill_file = repository / "skill" / "SKILL.md"
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8")
                + "\n[repository-only fixture](../tests/test_repository.py)\n",
                encoding="utf-8",
            )

            completed = run_distribution_validation(repository)

            self.assertNotEqual(0, completed.returncode, completed.stdout)
            self.assertIn("local link escapes distributable Skill root", completed.stdout)

    def test_distribution_validation_checks_links_in_bundled_references(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repository = prepare_repository(temp_dir)
            references = repository / "skill" / "references"
            references.mkdir()
            (references / "details.md").write_text(
                "[repository-only fixture](../../tests/test_repository.py)\n",
                encoding="utf-8",
            )

            completed = run_distribution_validation(repository)

            self.assertNotEqual(0, completed.returncode, completed.stdout)
            self.assertIn("references/details.md", completed.stdout)
            self.assertIn("local link escapes distributable Skill root", completed.stdout)

    def test_distribution_validation_rejects_dangling_in_bundle_symlink(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repository = prepare_repository(temp_dir)
            scripts = repository / "skill" / "scripts"
            scripts.mkdir()
            (scripts / "helper.py").symlink_to("missing.py")

            completed = run_distribution_validation(repository)

            self.assertNotEqual(0, completed.returncode, completed.stdout)
            self.assertIn("symlink target does not exist in distributable Skill bundle", completed.stdout)


if __name__ == "__main__":
    unittest.main()
