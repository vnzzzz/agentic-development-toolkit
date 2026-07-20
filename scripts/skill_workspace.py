#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
DISCOVERY_DIRS = (ROOT / ".claude" / "skills", ROOT / ".agents" / "skills")
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SECRET_FILENAMES = {
    ".env",
    ".env.local",
    "auth.json",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
    "service-account.json",
}


@dataclass(frozen=True)
class Skill:
    name: str
    repository_root: Path
    skill_root: Path
    description: str


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing opening YAML frontmatter delimiter")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError(f"{path}: missing closing YAML frontmatter delimiter") from exc

    result: dict[str, str] = {}
    for number, raw_line in enumerate(lines[1:end], start=2):
        line = raw_line.strip()
        if not line or line.startswith("#") or raw_line.startswith((" ", "\t")):
            continue
        if ":" not in raw_line:
            raise ValueError(f"{path}:{number}: invalid top-level frontmatter entry")
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in {"name", "description"}:
            result[key] = value
    return result


def discover_skills() -> list[Skill]:
    skills: list[Skill] = []
    if not SKILLS_DIR.exists():
        return skills

    for repository_root in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        candidates = [
            repository_root / "skill" / "SKILL.md",
            repository_root / "SKILL.md",
        ]
        matches = [path for path in candidates if path.is_file()]
        if not matches:
            continue
        if len(matches) != 1:
            raise ValueError(
                f"{repository_root}: both repository-root and skill/SKILL.md exist; choose one distribution root"
            )
        skill_root = matches[0].parent
        metadata = parse_frontmatter(matches[0])
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        skills.append(Skill(name, repository_root, skill_root, description))
    return skills


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def validate_skill(skill: Skill) -> list[str]:
    errors: list[str] = []
    skill_file = skill.skill_root / "SKILL.md"
    if not skill.name:
        errors.append(f"{skill_file}: required frontmatter field 'name' is empty")
    elif len(skill.name) > 64 or not NAME_PATTERN.fullmatch(skill.name):
        errors.append(
            f"{skill_file}: name must be <=64 chars and contain lowercase letters, digits, and interior hyphens"
        )
    if skill.name and skill.repository_root.name != skill.name:
        errors.append(
            f"{skill.repository_root}: repository directory must match Skill name '{skill.name}'"
        )
    if not skill.description:
        errors.append(f"{skill_file}: required frontmatter field 'description' is empty")
    elif len(skill.description) > 1024:
        errors.append(f"{skill_file}: description exceeds 1024 characters")

    resolved_root = skill.skill_root.resolve()
    for path in skill.skill_root.rglob("*"):
        if path.name in SECRET_FILENAMES:
            errors.append(f"{path}: credential-like file must not be bundled in a Skill")
        if path.is_symlink():
            resolved = path.resolve(strict=False)
            if not is_relative_to(resolved, resolved_root):
                errors.append(f"{path}: symlink escapes Skill root ({resolved})")

    if len(skill_file.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append(f"{skill_file}: keep SKILL.md at or below 500 lines; move detail into references/")

    return errors


def command_validate() -> int:
    try:
        skills = discover_skills()
    except (OSError, ValueError) as exc:
        print(f"Validation failed:\n- {exc}", file=sys.stderr)
        return 1
    errors: list[str] = []
    names: set[str] = set()
    for skill in skills:
        if skill.name in names:
            errors.append(f"duplicate Skill name: {skill.name}")
        names.add(skill.name)
        errors.extend(validate_skill(skill))

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if not skills:
        print("Validated 0 Skill(s).")
        return 0

    print(f"Validated {len(skills)} Skill(s):")
    for skill in skills:
        print(f"- {skill.name}: {skill.skill_root.relative_to(ROOT)}")
    return 0


def relative_symlink_target(link_parent: Path, target: Path) -> Path:
    return Path(os.path.relpath(target, start=link_parent))


def command_link() -> int:
    if command_validate() != 0:
        return 1
    skills = discover_skills()
    expected_names = {skill.name for skill in skills}

    for discovery_dir in DISCOVERY_DIRS:
        discovery_dir.mkdir(parents=True, exist_ok=True)
        for path in discovery_dir.iterdir():
            if path.name == ".gitkeep":
                continue
            if path.is_symlink() and path.name not in expected_names:
                path.unlink()
            elif not path.is_symlink():
                print(
                    f"Refusing to replace unmanaged path: {path.relative_to(ROOT)}",
                    file=sys.stderr,
                )
                return 1

        for skill in skills:
            link = discovery_dir / skill.name
            target = relative_symlink_target(discovery_dir, skill.skill_root)
            if link.is_symlink():
                if link.resolve(strict=False) == skill.skill_root.resolve():
                    continue
                link.unlink()
            link.symlink_to(target, target_is_directory=True)

    print(f"Linked {len(skills)} Skill(s) for Claude Code and Codex.")
    return 0


def command_doctor() -> int:
    print(f"workspace: {ROOT}")
    print(f"python: {sys.version.split()[0]}")
    for executable in ("git", "make", "claude", "codex"):
        path = shutil.which(executable)
        if not path:
            print(f"{executable}: not found")
            continue
        completed = subprocess.run(
            [executable, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        first_line = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else path
        print(f"{executable}: {first_line}")

    print("skills:")
    for skill in discover_skills():
        git_marker = "independent-git" if (skill.repository_root / ".git").exists() else "local-directory"
        print(f"- {skill.name}: {skill.skill_root.relative_to(ROOT)} [{git_marker}]")

    print(f"checked_at: {datetime.now(timezone.utc).isoformat()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the Agent Skill development workspace")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    subparsers.add_parser("link")
    subparsers.add_parser("doctor")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "validate":
        return command_validate()
    if args.command == "link":
        return command_link()
    if args.command == "doctor":
        return command_doctor()
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
