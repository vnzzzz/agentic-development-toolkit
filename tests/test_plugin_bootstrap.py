from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PluginBootstrapTests(unittest.TestCase):
    def test_bootstrap_uses_plugin_package_without_enumerating_skills(self) -> None:
        script = (ROOT / "scripts" / "install-agent-skills-plugin.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("vnzzzz/agent-skills", script)
        self.assertIn("codex plugin marketplace add", script)
        self.assertIn("codex plugin add", script)
        self.assertIn("claude plugin uninstall", script)
        self.assertIn("claude plugin marketplace", script)
        self.assertIn("claude plugin install", script)
        self.assertLess(
            script.index("claude plugin uninstall"),
            script.index("claude plugin marketplace remove"),
        )
        self.assertNotIn("readable-code", script)
        self.assertNotIn("japanese-technical-writing", script)
        self.assertNotIn("skills/", script)
        self.assertNotIn("git submodule", script)

    def test_devcontainer_installs_clis_before_plugin(self) -> None:
        script = (ROOT / ".devcontainer" / "post-create.sh").read_text(encoding="utf-8")
        self.assertLess(
            script.index("install-agent-clis.sh"),
            script.index("install-agent-skills-plugin.sh"),
        )


if __name__ == "__main__":
    unittest.main()
