#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SUSPICIOUS_NAMES = {
    ".env",
    ".env.local",
    "auth.json",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
    "service-account.json",
}
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "OpenAI key": re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    "Anthropic key": re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
EXTERNAL_ACTION = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s@]+)@([^\s#]+)", re.MULTILINE)
FULL_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def workflow_files() -> list[Path]:
    workflow_dirs = (
        ROOT / ".github" / "workflows",
        ROOT / "templates" / "skill-repository" / ".github" / "workflows",
    )
    return sorted(
        path
        for directory in workflow_dirs
        if directory.is_dir()
        for path in directory.glob("*.y*ml")
    )


def mount_source(mount: str) -> str:
    for item in mount.split(","):
        if item.startswith("source="):
            return item.removeprefix("source=")
    return ""


def audit_devcontainer(findings: list[str]) -> None:
    dockerfile = (ROOT / ".devcontainer" / "Dockerfile").read_text(encoding="utf-8")
    path = ROOT / ".devcontainer" / "devcontainer.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    relative = path.relative_to(ROOT)

    if config.get("remoteUser") in {None, "root"}:
        findings.append(f"{relative}: must explicitly run as a non-root user")

    serialized = json.dumps(config)
    for forbidden in (
        "/var/run/docker.sock",
        "/.ssh",
        "--dangerously-skip-permissions",
        "--dangerously-bypass-approvals-and-sandbox",
        "CODEX_UNSAFE_ALLOW_NO_SANDBOX",
        "--privileged",
        "seccomp=unconfined",
        "apparmor=unconfined",
    ):
        if forbidden in serialized:
            findings.append(f"{relative}: contains forbidden capability, flag, or mount: {forbidden}")

    if "initializeCommand" in config:
        findings.append(
            f"{relative}: host-side initializeCommand is not allowed; startup must not depend on Git state"
        )

    mounts = config.get("mounts", [])
    claude_mounts = [mount for mount in mounts if "target=/home/vscode/.claude" in mount]
    codex_mounts = [mount for mount in mounts if "target=/home/vscode/.codex" in mount]
    if len(claude_mounts) != 1:
        findings.append(f"{relative}: must define one isolated Claude authentication volume")
    if len(codex_mounts) != 1:
        findings.append(f"{relative}: must define one isolated Codex authentication volume")
    if claude_mounts and codex_mounts and mount_source(claude_mounts[0]) == mount_source(codex_mounts[0]):
        findings.append(f"{relative}: Claude and Codex authentication must use different volumes")

    if "COPY skills" in dockerfile or "pip install" in dockerfile:
        findings.append(
            ".devcontainer/Dockerfile: repository-controlled dependencies must not execute during the root image build"
        )


def audit_workflows(findings: list[str]) -> None:
    for path in sorted(workflow_files()):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        if "pull_request_target:" in text:
            findings.append(f"{relative}: pull_request_target is not allowed")
        if re.search(r"permissions:\s*(?:write-all|read-all)", text):
            findings.append(f"{relative}: broad workflow permissions are not allowed")
        if "permissions:" not in text:
            findings.append(f"{relative}: explicit permissions block is required")
        if re.search(r"(?:curl|wget)[^\n|]*\|\s*(?:ba)?sh", text):
            findings.append(f"{relative}: remote script piping to a shell is not allowed")
        for action, revision in EXTERNAL_ACTION.findall(text):
            if action.startswith("./"):
                continue
            if not FULL_COMMIT_SHA.fullmatch(revision):
                findings.append(
                    f"{relative}: external action {action}@{revision} must be pinned to a full commit SHA"
                )


def parent_managed_paths() -> list[Path]:
    excluded_top_level = {".agents", ".claude", ".codex", ".git", ".venv", "build", "skills"}
    paths: list[Path] = []
    for path in ROOT.iterdir():
        if path.name in excluded_top_level:
            continue
        if path.is_dir():
            paths.extend(path.rglob("*"))
        else:
            paths.append(path)
    for path in (ROOT / "skills" / "README.md", ROOT / "skills" / ".gitkeep"):
        if path.exists():
            paths.append(path)
    return sorted(paths)


def audit_repository_files(findings: list[str]) -> None:
    excluded_parts = {".git", "build", ".venv", "__pycache__"}
    text_suffixes = {".md", ".py", ".sh", ".json", ".toml", ".yml", ".yaml", ".txt"}
    for path in parent_managed_paths():
        if any(part in excluded_parts for part in path.parts):
            continue
        relative = path.relative_to(ROOT)
        if path.name in SUSPICIOUS_NAMES:
            findings.append(f"{relative}: credential-like filename is present in a parent-managed path")
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in text_suffixes:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{relative}: possible {label}")


def audit_agent_cli_versions(findings: list[str]) -> None:
    package_file = ROOT / "package.json"
    package = json.loads(package_file.read_text(encoding="utf-8"))
    dependencies = package.get("dependencies", {})
    semantic_version = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
    for name in ("@anthropic-ai/claude-code", "@openai/codex"):
        version = dependencies.get(name, "")
        if not semantic_version.fullmatch(version):
            findings.append(f"package.json: {name} must use an exact semantic version")


def main() -> int:
    findings: list[str] = []
    audit_devcontainer(findings)
    audit_workflows(findings)
    audit_repository_files(findings)
    audit_agent_cli_versions(findings)
    if findings:
        print("Security audit failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print("Security audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
