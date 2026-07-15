# AI Job Search - Codex Repository Instructions

This repository is a job application workspace for OpenAI Codex. Treat tracked files as durable, non-personal framework instructions and sanitized examples. Candidate-specific data belongs only in the ignored `private_profile/` directory or ignored generated outputs.

## Role

Codex helps with:

1. Job fit evaluation against the candidate profile, skills, experience, constraints, and behavioral profile.
2. CV tailoring using the existing LaTeX templates and candidate data.
3. Cover-letter drafting using the existing LaTeX template and writing rules.
4. Independent application review through a Codex subagent workflow.
5. Interview preparation using the tracked application archive and STAR examples.
6. Search, ranking, tracking, setup, template registration, portal generation, outcome logging, reset, and upskilling workflows through skills in `.agents/skills/`.

## Private Profile Contract

The `setup` skill writes candidate facts to `private_profile/`. That directory is gitignored and must never be tracked. Until setup has populated private profile files, do not infer missing candidate facts.

Expected private files:

- `private_profile/01-candidate-profile.md`
- `private_profile/02-behavioral-profile.md`
- `private_profile/03-writing-style.md`
- `private_profile/04-job-evaluation.md`
- `private_profile/05-cv-templates.md`
- `private_profile/06-cover-letter-templates.md`
- `private_profile/07-interview-prep.md`
- `private_profile/search-queries.md`
- `private_profile/cv/main.tex` or another private master CV source

Tracked files under `.agents/skills/job-application-assistant/`, `.agents/skills/job-scraper/search-queries.md`, `cv/main_example.tex`, and `cover_letters/cover_example.tex` are sanitized examples and structural references only. Do not replace their placeholders with real candidate information.

## Active Repo Structure

- `AGENTS.md` - active Codex repository instructions. Keep non-personal.
- `private_profile/` - ignored candidate profile files, private CV source, and personalized search queries.
- `.agents/skills/` - Codex skills for workflows and job portal CLIs.
- `.agents/skills/job-application-assistant/` - sanitized profile, behavioral, writing style, job evaluation, CV, cover letter, and interview reference examples.
- `cv/` - sanitized stock CV template and ignored generated CV variants.
- `cover_letters/` - LaTeX cover letters and `cover.cls`.
- `templates/` - custom templates registered by the add-template skill.
- `documents/` - private source materials and application archives. Only `documents/README.md` and optional `.gitkeep` files are tracked.
- `job_scraper/` - scraper state.
- `upskill/` - learning-plan reports.
- `job_search_tracker.csv` - personal application tracker, gitignored.
- `.claude/` and `CLAUDE.md` - legacy Claude Code reference files retained during migration. Do not treat them as active instructions.

## Workflow Rules

When the user provides a job posting, always evaluate fit first. Present skills match, experience match, behavioral/culture match, salary benchmark when configured, gaps, and recommendation before drafting.

If the user proceeds, create a targeted CV and cover letter, run the independent reviewer subagent workflow, revise, compile, inspect PDFs, run ATS checks where possible, and report the verification checklist.

Use the converted skills in `.agents/skills/` for the major workflows:

- `setup` - onboard or update profile data.
- `job-scraper` - search installed job portals and deduplicate results.
- `rank` - batch-score scraped jobs.
- `apply` - full drafter-reviewer application workflow.
- `outcome` - record application results and archive materials.
- `interview` - build prep packs and run mock interviews.
- `expand` - add source-traced competencies from documents and public profiles.
- `upskill` - produce skill-gap heatmaps and learning plans.
- `add-template` - register custom LaTeX templates.
- `add-portal` - create new portal search skills.
- `reset` - reset profile data or personal documents after explicit confirmation.

## Evidence And Claim Rules

- Do not fabricate skills, tools, employers, dates, metrics, education, publications, awards, or outcomes.
- Reframe emphasis, not substance. A tailored bullet must pass the interview backtrack test: the candidate can defend it without saying "what I actually meant was..."
- Company-specific claims must be verified independently before inclusion.
- Never write candidate facts, contact details, salary data, tracker data, source documents, or application archives into tracked files. Use `private_profile/`, ignored generated outputs, and ignored tracker/archive files.
- A named AI tool may appear in a CV, cover letter, or interview answer only when the candidate profile explicitly says the candidate used that named tool in the underlying work. Using Codex to prepare an application is not evidence that the candidate used Codex during the job or project.
- Do not automatically replace old Claude Code claims with Codex claims. If a legacy profile explicitly documents Claude Code usage in a real project, preserve that fact. If it does not, omit named tool claims.

## Verification Checklist

After creating or updating a CV or cover letter, re-read the generated source files and verify all items below before presenting the result.

### Factual Accuracy
- [ ] All claims match `private_profile/01-candidate-profile.md` and other relevant `private_profile/` profile files.
- [ ] Job titles, dates, company names, locations, and contact details are correct.
- [ ] Company-specific claims have been independently verified.
- [ ] Named AI-tool claims are explicitly supported by the candidate profile.

### Targeting
- [ ] Profile statement and opening paragraph are tailored to the specific role.
- [ ] Skills and experience bullets map to the posting's required and preferred criteria.
- [ ] Key requirements are addressed, with genuine gaps acknowledged.
- [ ] Nice-to-have requirements are highlighted only when supported by the profile.

### Consistency
- [ ] CV follows the active CV template and page limit.
- [ ] Cover letter follows the active cover-letter template and page limit.
- [ ] Tone is consistent across CV and cover letter.
- [ ] No contradictions between CV, cover letter, profile, and application archive.

### LaTeX And PDF Quality
- [ ] CV compiles with `lualatex`.
- [ ] Cover letter compiles with `xelatex` unless a registered template says otherwise.
- [ ] CV is exactly 2 pages unless an active custom template sets a different limit.
- [ ] Cover letter is exactly 1 page unless an active custom template sets a different limit.
- [ ] No orphaned `\cventry` titles, isolated headings, clipped text, or awkward whitespace.
- [ ] Cover-letter bullet fonts match the body font.

### ATS And Keywords
- [ ] If `pdftotext` is available, the CV text layer extracts cleanly.
- [ ] Email and phone appear as literal text in extraction.
- [ ] Reading order matches the visual order.
- [ ] Posting keywords are covered honestly: add supported missing terms, leave genuine gaps visible, never stuff keywords.
