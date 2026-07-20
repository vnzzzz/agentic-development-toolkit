#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL_FILE = ROOT / "skill" / "SKILL.md"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def metadata() -> dict[str, str]:
    lines = SKILL_FILE.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("SKILL.md is missing the closing frontmatter delimiter") from exc
    values: dict[str, str] = {}
    for raw_line in lines[1:end]:
        if not raw_line or raw_line[0].isspace() or ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> int:
    try:
        values = metadata()
    except (OSError, ValueError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    name = values.get("name", "")
    description = values.get("description", "")
    errors: list[str] = []
    if not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        errors.append("name must be <=64 characters and use lowercase letters, digits, and hyphens")
    if ROOT.name != name:
        errors.append("repository directory name must match the Skill name")
    if not description or len(description) > 1024:
        errors.append("description is required and must be <=1024 characters")
    if len(SKILL_FILE.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append("SKILL.md must be <=500 lines; move detail into references/")
    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated {name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
