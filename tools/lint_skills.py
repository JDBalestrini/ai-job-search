#!/usr/bin/env python3
"""Lint the repo's active Codex skill files and legacy Claude reference files.

Run from anywhere: python tools/lint_skills.py

Checks:
- Every active SKILL.md (.agents/skills/*) has YAML frontmatter that
  parses, with non-empty `name` and `description` keys
- Legacy .claude markdown files are explicitly marked as legacy
- .claude/settings.json remains valid JSON when retained for migration reference

Exit code 0 on success, 1 with a failure list otherwise.
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("lint_skills.py requires PyYAML: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def check_skill(path: Path) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if not (text.startswith("---\n") or text.startswith("---\r\n")):
        errors.append(f"{rel(path)}: missing YAML frontmatter (file must start with ---)")
        return
    end = text.find("\n---", 4)
    if end == -1:
        errors.append(f"{rel(path)}: unterminated YAML frontmatter")
        return
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        errors.append(f"{rel(path)}: frontmatter is not valid YAML: {exc}")
        return
    if not isinstance(data, dict):
        errors.append(f"{rel(path)}: frontmatter did not parse to a mapping")
        return
    for key in ("name", "description"):
        if not data.get(key):
            errors.append(f"{rel(path)}: frontmatter missing required key '{key}'")

def check_legacy_marker(path: Path) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("<!-- LEGACY CLAUDE CODE REFERENCE:"):
        errors.append(f"{rel(path)}: retained Claude file must start with the legacy marker")


def check_settings() -> None:
    path = ROOT / ".claude" / "settings.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f".claude/settings.json: {exc}")
        return
    if not isinstance(data, dict):
        errors.append(".claude/settings.json: expected top-level JSON value to be an object")
        return
    permissions = data.get("permissions", {})
    if not isinstance(permissions, dict):
        errors.append(".claude/settings.json: expected permissions to be an object")
        return
    if not isinstance(permissions.get("allow"), list):
        errors.append(".claude/settings.json: expected permissions.allow to be a list")


def main() -> int:
    skills = sorted(ROOT.glob(".agents/skills/*/SKILL.md"))
    legacy_markdown = sorted((ROOT / ".claude").glob("**/*.md"))
    if not skills:
        errors.append("no active SKILL.md files found under .agents/skills/")

    for skill in skills:
        check_skill(skill)
    for path in legacy_markdown:
        check_legacy_marker(path)
    check_settings()

    if errors:
        print(f"lint_skills: {len(errors)} failure(s)")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"lint_skills: OK ({len(skills)} active skills, {len(legacy_markdown)} legacy Claude markdown files, legacy settings.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
