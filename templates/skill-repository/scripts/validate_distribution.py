#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skill"
SKILL_FILE = SKILL_ROOT / "SKILL.md"
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def local_markdown_targets(markdown: str) -> list[str]:
    targets: list[str] = []
    for match in MARKDOWN_LINK_PATTERN.finditer(markdown):
        raw = match.group(1).strip()
        angle_wrapped = raw.startswith("<") and raw.endswith(">")
        if angle_wrapped:
            raw = raw[1:-1].strip()
        if not raw or raw.startswith("#"):
            continue

        # Outside angle brackets, unescaped whitespace starts the optional
        # Markdown link title rather than belonging to the path.
        if not angle_wrapped:
            raw = raw.split(maxsplit=1)[0]
        parsed = urlsplit(raw)
        if parsed.scheme or parsed.netloc:
            continue
        target = unquote(parsed.path)
        if target:
            targets.append(target)
    return targets


def validate_markdown_links(markdown_file: Path, skill_root: Path) -> list[str]:
    errors: list[str] = []
    resolved_root = skill_root.resolve()
    markdown = markdown_file.read_text(encoding="utf-8")
    for target in local_markdown_targets(markdown):
        resolved = (markdown_file.parent / target).resolve(strict=False)
        if not is_relative_to(resolved, resolved_root):
            errors.append(f"{markdown_file}: local link escapes distributable Skill root: {target}")
        elif not resolved.exists():
            errors.append(f"{markdown_file}: local link target does not exist in bundle: {target}")
    return errors


def validate_bundle_tree(skill_root: Path) -> list[str]:
    errors: list[str] = []
    resolved_root = skill_root.resolve()

    for path in skill_root.rglob("*"):
        if not path.is_symlink():
            continue
        resolved = path.resolve(strict=False)
        if not is_relative_to(resolved, resolved_root):
            errors.append(f"{path}: symlink escapes distributable Skill root ({resolved})")
        elif not resolved.exists():
            errors.append(f"{path}: symlink target does not exist in distributable Skill bundle ({resolved})")

    for markdown_file in sorted(skill_root.rglob("*.md")):
        if markdown_file.is_file():
            errors.extend(validate_markdown_links(markdown_file, skill_root))

    return errors


def validate_isolated_copy() -> list[str]:
    errors = validate_bundle_tree(SKILL_ROOT)
    if errors:
        return errors

    with TemporaryDirectory() as temp_dir:
        isolated_root = Path(temp_dir) / "skill"
        shutil.copytree(SKILL_ROOT, isolated_root, symlinks=True)
        errors.extend(validate_bundle_tree(isolated_root))
        if errors:
            return errors

        compiled = subprocess.run(
            [sys.executable, "-m", "compileall", "-q", str(isolated_root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if compiled.returncode != 0:
            detail = compiled.stdout.strip() or "Python compilation failed"
            errors.append(f"isolated Skill bundle Python syntax check failed: {detail}")

        shell_scripts = sorted(isolated_root.rglob("*.sh"))
        if shell_scripts:
            bash = shutil.which("bash")
            if bash is None:
                errors.append("bash is required to syntax-check bundled .sh scripts")
            else:
                for script in shell_scripts:
                    checked = subprocess.run(
                        [bash, "-n", str(script)],
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    if checked.returncode != 0:
                        detail = checked.stdout.strip() or "shell syntax check failed"
                        errors.append(f"{script.relative_to(isolated_root)}: {detail}")

    return errors


def main() -> int:
    if not SKILL_FILE.is_file():
        print("Distribution validation failed: skill/SKILL.md does not exist", file=sys.stderr)
        return 1

    errors = validate_isolated_copy()
    if errors:
        print("Distribution validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Validated isolated distributable Skill bundle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
