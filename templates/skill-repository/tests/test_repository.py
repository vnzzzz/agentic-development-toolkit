from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def test_skill_file_exists(self) -> None:
        self.assertTrue((ROOT / "skill" / "SKILL.md").is_file())

    def test_skill_has_no_credential_files(self) -> None:
        forbidden = {".env", ".env.local", "auth.json", "credentials.json", "id_rsa", "id_ed25519"}
        actual = {path.name for path in (ROOT / "skill").rglob("*") if path.is_file()}
        self.assertFalse(actual & forbidden)


if __name__ == "__main__":
    unittest.main()
