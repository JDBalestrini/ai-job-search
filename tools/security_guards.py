#!/usr/bin/env python3
"""Supply-chain guards for the template's riskiest surfaces.

Run from anywhere: python tools/security_guards.py

This repo ships CLI code that every fork user may execute, plus a retained
legacy Claude Code settings file for migration reference. These guards make
dangerous changes LOUD, not impossible: a PR that intentionally needs one of
them must update the allowlists in this file in the same diff, so the change
is explicit and reviewable rather than buried.

Checks:
1. .claude/settings.json - if retained, every legacy permissions.allow entry
   must be in the exact allowlist below. Catches permission widening in the
   legacy reference file.
2. .gitignore - the personal-data ignore rules must all still be present.
   Catches weakening that would make future users silently commit their
   tracker, profile exports, or application archives.
3. private_profile/ - no files under this directory may be tracked.
   Catches accidental commits of candidate data.
4. Tracked template/example files - required placeholder tokens must remain.
   Catches accidental personalization of public-safe examples.
5. .agents/**/package.json - no npm/bun lifecycle scripts (preinstall,
   install, postinstall, prepare, prepack) and no trustedDependencies.
   Catches code execution smuggled into `bun install`.
6. Active application workflow guidance must not instruct Codex to copy a
   populated private/master resume as the generated CV.
   Catches regressions that turn tailoring into a near-verbatim copy.

Stdlib only. Exit 0 on success, 1 with a failure list otherwise.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []

# The exact legacy Claude permission entries retained for migration reference.
# Codex permissions are documented in AGENTS.md, SETUP.md, and
# CODEX_MIGRATION.md rather than auto-approved through this JSON file.
ALLOWED_PERMISSIONS = {
    "Skill(job-application-assistant)",
    "Bash(bun run:*)",
    "Bash(python salary_lookup.py:*)",
    "Bash(python3 salary_lookup.py:*)",
    "Bash(pdftotext:*)",
}

# Personal-data ignore rules that must never disappear from .gitignore.
REQUIRED_IGNORE_RULES = [
    "private_profile/",
    "salary_data.json",
    "salary_data*.json",
    "job_scraper/seen_jobs.json",
    "job_scraper/*.json",
    "cv/main_*.tex",
    "!cv/main_example.tex",
    "cv/main_*.pdf",
    "cover_letters/cover_*.tex",
    "documents/cv/**",
    "documents/linkedin/**",
    "documents/diplomas/**",
    "documents/references/**",
    "documents/applications/**",
    "documents/**",
    "!documents/README.md",
    "job_search_tracker.csv",
    "job_search_tracker*.csv",
]

FORBIDDEN_SCRIPTS = {"preinstall", "install", "postinstall", "prepare", "prepack"}

TRACKED_PLACEHOLDER_RULES = {
    Path("cv/main_example.tex"): [
        "[First]",
        "[Last]",
        "[your.email@example.com]",
        "[Job Title]",
    ],
    Path("cover_letters/cover_example.tex"): [
        "[YOUR NAME]",
        "your.email@example.com",
        "[Hiring Manager / Team]",
    ],
    Path(".agents/skills/job-application-assistant/01-candidate-profile.md"): [
        "[YOUR_NAME]",
        "[YOUR_EMAIL]",
        "[JOB_TITLE]",
    ],
    Path(".agents/skills/job-scraper/search-queries.md"): [
        "[YOUR_PRIMARY_ROLE_TYPE]",
        "[YOUR_PRIMARY_JOB_TITLE]",
        "[YOUR_CITY]",
    ],
    Path("templates/cv/jd-resume/template.tex"): [
        "[Full Name]",
        "[Email Address]",
        "[Company Name]",
        "[Skill Group]",
    ],
}

FORBIDDEN_WORKFLOW_PHRASES = {
    Path(".agents/skills/apply/SKILL.md"): [
        "Prefer `private_profile/cv/main.tex` as the private master CV source",
        "read the most recent existing CV",
    ],
    Path(".agents/skills/job-application-assistant/SKILL.md"): [
        "Read the most relevant existing CV variant from `cv/` as a starting point",
    ],
    Path(".agents/skills/job-application-assistant/05-cv-templates.md"): [
        "**Master reference:** `cv/main_example.tex`",
    ],
}


def check_permissions() -> None:
    path = ROOT / ".claude" / "settings.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f".claude/settings.json: unreadable or invalid JSON: {exc}")
        return
    if not isinstance(data, dict):
        errors.append(".claude/settings.json: top-level JSON value must be an object")
        return
    permissions = data.get("permissions", {})
    if not isinstance(permissions, dict):
        errors.append(".claude/settings.json: permissions must be an object")
        return
    allow = permissions.get("allow", [])
    if not isinstance(allow, list) or not all(isinstance(entry, str) for entry in allow):
        errors.append(".claude/settings.json: permissions.allow must be a list of strings")
        return
    for entry in allow:
        if entry not in ALLOWED_PERMISSIONS:
            errors.append(
                f".claude/settings.json: permission not in the reviewed allowlist: {entry!r}. "
                "Pre-approved permissions run without prompting on every fork. If this entry is "
                "intentional, add it to ALLOWED_PERMISSIONS in tools/security_guards.py in the "
                "same PR so the widening is explicit and reviewable."
            )
    for entry in ALLOWED_PERMISSIONS - set(allow):
        # Not an error: settings may legitimately drop an entry. But an
        # allowlist entry that no longer exists should be pruned.
        print(f"note: allowlisted permission not present in settings.json: {entry!r}")


def check_gitignore() -> None:
    path = ROOT / ".gitignore"
    try:
        rules = {line.strip() for line in path.read_text(encoding="utf-8").splitlines()}
    except OSError as exc:
        errors.append(f".gitignore: unreadable: {exc}")
        return
    for rule in REQUIRED_IGNORE_RULES:
        if rule not in rules:
            errors.append(
                f".gitignore: required personal-data rule missing: {rule!r}. "
                "These rules keep fork users from committing personal data. If the rule moved "
                "or was renamed intentionally, update REQUIRED_IGNORE_RULES in "
                "tools/security_guards.py in the same PR."
            )


def check_private_profile_not_tracked() -> None:
    if not (ROOT / ".git").exists():
        return
    result = subprocess.run(
        ["git", "ls-files", "--", "private_profile"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        errors.append(f"git ls-files private_profile failed: {result.stderr.strip()}")
        return
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    if tracked:
        errors.append(
            "private_profile: candidate-data files must not be tracked: "
            + ", ".join(tracked)
        )


def check_tracked_template_placeholders() -> None:
    for relpath, placeholders in TRACKED_PLACEHOLDER_RULES.items():
        path = ROOT / relpath
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{relpath}: unreadable tracked template/example file: {exc}")
            continue
        missing = [token for token in placeholders if token not in text]
        if missing:
            errors.append(
                f"{relpath}: required placeholder token(s) missing: {missing}. "
                "Tracked templates/examples must stay sanitized; write real candidate data "
                "under private_profile/ instead."
            )


def check_package_manifests() -> None:
    manifests = [
        p for p in ROOT.glob(".agents/**/package.json") if "node_modules" not in p.parts
    ]
    if not manifests:
        errors.append(".agents: no package.json files found - glob roots are wrong or the tree moved")
    for manifest in manifests:
        relpath = manifest.relative_to(ROOT)
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relpath}: unreadable or invalid JSON: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{relpath}: top-level JSON value must be an object")
            continue
        scripts = data.get("scripts", {})
        if not isinstance(scripts, dict):
            errors.append(f"{relpath}: scripts must be an object")
            continue
        bad = FORBIDDEN_SCRIPTS & set(scripts)
        if bad:
            errors.append(
                f"{relpath}: lifecycle script(s) {sorted(bad)} are forbidden - they execute "
                "arbitrary code during `bun install` on every fork user's machine."
            )
        if "trustedDependencies" in data:
            errors.append(
                f"{relpath}: trustedDependencies is forbidden - it re-enables dependency "
                "lifecycle scripts that bun blocks by default."
            )


def check_cv_tailoring_workflow_guidance() -> None:
    for relpath, phrases in FORBIDDEN_WORKFLOW_PHRASES.items():
        path = ROOT / relpath
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{relpath}: unreadable workflow guidance: {exc}")
            continue
        for phrase in phrases:
            if phrase in text:
                errors.append(
                    f"{relpath}: forbidden CV workflow phrase found: {phrase!r}. "
                    "Application CVs must be generated from structured profile facts plus "
                    "the sanitized LaTeX skeleton after relevance scoring; populated private "
                    "or previous CVs are supporting evidence only, not starting documents to copy."
                )


def main() -> int:
    check_permissions()
    check_gitignore()
    check_private_profile_not_tracked()
    check_tracked_template_placeholders()
    check_package_manifests()
    check_cv_tailoring_workflow_guidance()
    if errors:
        print(f"security_guards: {len(errors)} failure(s)")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("security_guards: OK (permissions allowlist, gitignore rules, private profile, placeholders, package manifests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
