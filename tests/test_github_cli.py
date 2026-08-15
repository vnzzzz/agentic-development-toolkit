from __future__ import annotations

import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import security_audit
import skill_workspace


class GitHubCliWorkspaceTests(unittest.TestCase):
    def test_devcontainer_provides_github_cli_with_isolated_persistent_config(self) -> None:
        config = json.loads((ROOT / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8"))

        self.assertIn("ghcr.io/devcontainers/features/github-cli:1", config["features"])
        mounts = [security_audit.parse_mount(mount) for mount in config["mounts"]]
        auth_targets = {
            "/home/vscode/.claude",
            "/home/vscode/.codex",
            "/home/vscode/.config/gh",
        }
        auth_mounts = [mount for mount in mounts if mount.get("target") in auth_targets]

        self.assertEqual(3, len(auth_mounts))
        self.assertTrue(all(mount.get("type") == "volume" for mount in auth_mounts))
        self.assertTrue(all(mount.get("source") for mount in auth_mounts))
        self.assertEqual(3, len({mount["source"] for mount in auth_mounts}))

    def test_security_audit_rejects_host_bind_for_github_cli_auth(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            devcontainer_dir = temp_root / ".devcontainer"
            devcontainer_dir.mkdir()
            (devcontainer_dir / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
            config = {
                "remoteUser": "vscode",
                "features": {"ghcr.io/devcontainers/features/github-cli:1": {}},
                "mounts": [
                    "source=claude,target=/home/vscode/.claude,type=volume",
                    "source=codex,target=/home/vscode/.codex,type=volume",
                    "source=/home/me/.config/gh,target=/home/vscode/.config/gh,type=bind",
                ],
            }
            (devcontainer_dir / "devcontainer.json").write_text(
                json.dumps(config),
                encoding="utf-8",
            )

            findings: list[str] = []
            with patch.object(security_audit, "ROOT", temp_root):
                security_audit.audit_devcontainer(findings)

        self.assertIn(
            ".devcontainer/devcontainer.json: GitHub CLI authentication must use a named volume",
            findings,
        )

    def test_doctor_reports_github_cli_version(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repos_dir = Path(temp_dir) / "repos"
            repos_dir.mkdir()

            def fake_run(args, **kwargs):
                return subprocess.CompletedProcess(args, 0, stdout=f"{args[0]} version-test\n")

            with (
                patch.object(skill_workspace, "REPOS_DIR", repos_dir),
                patch.object(skill_workspace.shutil, "which", side_effect=lambda name: f"/usr/bin/{name}"),
                patch.object(skill_workspace.subprocess, "run", side_effect=fake_run),
                redirect_stdout(StringIO()) as output,
            ):
                self.assertEqual(0, skill_workspace.command_doctor())

        self.assertIn("gh: gh version-test", output.getvalue())


if __name__ == "__main__":
    unittest.main()
