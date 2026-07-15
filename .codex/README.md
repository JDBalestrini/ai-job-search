# Codex Notes

This repository uses `AGENTS.md` and `.agents/skills/` for durable Codex instructions and reusable workflows.

There is no committed Codex equivalent of `.claude/settings.json` in this port. Codex permissions are handled by the active Codex runtime through per-command approvals, sandbox settings, and any user-specific Codex configuration outside this repository.

Recommended personal-use posture:

- Allow normal reads inside the repository.
- Allow writes only inside the repository unless you intentionally export artifacts elsewhere.
- Approve network access only for job posting fetches, company research, official documentation lookup, and job portal CLIs.
- Keep destructive commands, broad shell permissions, and credentialed external-account actions manual.
