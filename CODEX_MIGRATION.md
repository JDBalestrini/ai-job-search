# Codex Migration

This repository has been ported from Claude Code workflows to OpenAI Codex workflows for personal use.

## Converted

- Added `AGENTS.md` as the active durable Codex instruction file.
- Copied the application assistant reference files from `.claude/skills/job-application-assistant/` to `.agents/skills/job-application-assistant/`.
- Converted the former `.claude/commands/` workflows into Codex skills:
  - `.agents/skills/setup/SKILL.md`
  - `.agents/skills/apply/SKILL.md`
  - `.agents/skills/rank/SKILL.md`
  - `.agents/skills/interview/SKILL.md`
  - `.agents/skills/outcome/SKILL.md`
  - `.agents/skills/expand/SKILL.md`
  - `.agents/skills/add-template/SKILL.md`
  - `.agents/skills/add-portal/SKILL.md`
  - `.agents/skills/reset/SKILL.md`
- Ported the Claude skills:
  - `.agents/skills/job-application-assistant/`
  - `.agents/skills/job-scraper/`
  - `.agents/skills/upskill/`
- Replaced Claude-specific workflow terminology in active skills:
  - `WebFetch` / `WebSearch` -> web fetching and web search.
  - `Read`, `Edit`, `Write`, `Bash` -> tool-independent read, edit, write, and shell instructions.
  - `Agent` -> Codex subagent workflow.
- Converted the independent application reviewer into the `apply` skill's Codex subagent workflow.
- Removed the old rule that automatically inserted a named AI tool into applications. Active instructions now allow a named AI tool only when the candidate profile explicitly documents that the candidate used that tool in the underlying work.
- Updated validation scripts so `.agents/skills/` is the active skill tree and `.claude/` is treated as legacy reference.

## Unchanged

- Existing job portal scraper CLIs under `.agents/skills/*/cli/`.
- LaTeX CV and cover-letter templates.
- `salary_lookup.py` and salary data shape.
- ATS checks using `pdftotext` when available.
- Application tracker schema in `job_search_tracker.csv`.
- Personal-data ignore rules in `.gitignore`.
- Document archive structure under `documents/`.

## Legacy Retained

`.claude/` and `CLAUDE.md` are retained temporarily for migration validation. They are marked with a legacy notice and should not be used as active instructions. Delete them only after validating that the Codex skills cover your workflow.

`.claude/settings.json` cannot be reproduced exactly in Codex because Codex uses a different permission and approval model. The retained file is documentation of the old Claude permission allowlist only. Codex permissions are handled by the Codex runtime approval flow and should remain scoped to the action being requested.

## How To Invoke Workflows

Start Codex from the repository root:

```bash
codex
```

Then ask for the skill by name:

- `Run the setup skill.`
- `Run the job-scraper skill for data science roles.`
- `Run the rank skill for new scraped jobs.`
- `Run the apply skill for <URL or pasted posting>.`
- `Run the outcome skill for <company>.`
- `Run the interview skill for <company>.`
- `Run the expand skill.`
- `Run the upskill skill.`
- `Run the add-template skill.`
- `Run the add-portal skill for <job board URL>.`
- `Run the reset skill for profile data.`

## Testing The Port

Recommended local validation:

```bash
py -m pytest
python tools/lint_skills.py
python tools/security_guards.py
```

On Windows PowerShell, prefer `py -m pytest` for the test suite. Before reporting
pytest as missing, check both `py -m pytest --version` and
`python -m pytest --version`, and report which launcher/interpreter is active.

Optional when LaTeX is installed:

```bash
cd cv && lualatex -interaction=nonstopmode -halt-on-error main_example.tex
cd ../cover_letters && xelatex -interaction=nonstopmode -halt-on-error cover_example.tex
```

Optional when Bun dependencies are installed:

```bash
cd .agents/skills/linkedin-search/cli && bun test
```

## Dry-Run Workflow

For a no-send dry run, use placeholder posting text and ask:

> Run the apply skill as a dry run using this placeholder posting. Do not send applications, do not contact external accounts, and write only local draft files if needed.

The workflow should evaluate fit first, draft only after approval, run the reviewer subagent prompt locally, compile if LaTeX is available, and report any skipped validation.

## Remaining Claude References

Intentional:

- `CLAUDE.md` and `.claude/**`: retained legacy reference, marked with a legacy notice.
- `CODEX_MIGRATION.md`: explains the migration from Claude Code.
- `AGENTS.md`: mentions legacy Claude Code claims only to forbid automatic replacement with Codex claims.
- `.agents/skills/apply/SKILL.md`: mentions Claude Code only inside the AI-tool claim rule, as an example of a named tool that must not be added unless supported by the candidate profile.
- Tests and validation scripts may mention `.claude/settings.json` as retained legacy reference.

Needs correction:

- Any Claude, Anthropic, `.claude`, `WebFetch`, `WebSearch`, `Read tool`, `Edit tool`, `Bash`, `Agent tool`, or obsolete slash-command reference outside the intentional legacy/migration contexts above should be corrected before validation is considered complete.
