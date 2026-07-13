# AI Job Search - Codex Repository Instructions

This repository is a personal job application workspace for OpenAI Codex. Treat it as a private, source-grounded career assistant workspace for the candidate described in this file and in `.agents/skills/job-application-assistant/`.

## Role

Codex helps with:

1. Job fit evaluation against the candidate profile, skills, experience, constraints, and behavioral profile.
2. CV tailoring using the existing LaTeX templates and candidate data.
3. Cover-letter drafting using the existing LaTeX template and writing rules.
4. Independent application review through a Codex subagent workflow.
5. Interview preparation using the tracked application archive and STAR examples.
6. Search, ranking, tracking, setup, template registration, portal generation, outcome logging, reset, and upskilling workflows through skills in `.agents/skills/`.

## Candidate Profile

The setup skill populates these placeholders. Until then, do not infer missing facts.

### Identity
- **Name:** [YOUR_NAME]
- **Location:** [YOUR_CITY], [YOUR_COUNTRY] ([YOUR_COMMUTE_CONSTRAINTS])
- **Languages:** [YOUR_LANGUAGES]
- **Status:** [YOUR_EMPLOYMENT_STATUS]
- **LinkedIn headline:** "[YOUR_LINKEDIN_HEADLINE]"

### Education
- **[DEGREE_LEVEL] in [FIELD]** ([YEAR_START]-[YEAR_END]) - [INSTITUTION]
  - Thesis: "[THESIS_TITLE]"
  - Topics: [KEY_TOPICS]

### Professional Experience
- **[JOB_TITLE]** ([START_DATE] - [END_DATE]) - **[COMPANY]** ([LOCATION])
  - [KEY_RESPONSIBILITY_1]
  - [KEY_RESPONSIBILITY_2]
  - [KEY_ACHIEVEMENT]

### Technical Skills
- **Primary:** [YOUR_PRIMARY_SKILLS]
- **Secondary:** [YOUR_SECONDARY_SKILLS]
- **Domain:** [YOUR_DOMAIN_EXPERTISE]
- **Software:** [YOUR_TOOLS_AND_SOFTWARE]

### Behavioral Profile
- **[TRAIT_1]** - [DESCRIPTION]
- **[TRAIT_2]** - [DESCRIPTION]
- **Strengths:** [YOUR_STRENGTHS]
- **Growth areas:** [YOUR_GROWTH_AREAS]
- **Thrives in:** [YOUR_IDEAL_ENVIRONMENT]

### Career Direction
- **What excites the candidate:** [PASSION_1], [PASSION_2]
- **Target sectors:** [SECTOR_1], [SECTOR_2]
- **Deal-breakers:** [DEALBREAKER_1], [DEALBREAKER_2]

## Active Repo Structure

- `AGENTS.md` - active Codex repository instructions and high-level candidate profile.
- `.agents/skills/` - Codex skills for workflows and job portal CLIs.
- `.agents/skills/job-application-assistant/` - candidate profile, behavioral profile, writing style, job evaluation, CV, cover letter, and interview reference files.
- `cv/` - LaTeX CV variants.
- `cover_letters/` - LaTeX cover letters and `cover.cls`.
- `templates/` - custom templates registered by the add-template skill.
- `documents/` - private source materials and application archives.
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
- A named AI tool may appear in a CV, cover letter, or interview answer only when the candidate profile explicitly says the candidate used that named tool in the underlying work. Using Codex to prepare an application is not evidence that the candidate used Codex during the job or project.
- Do not automatically replace old Claude Code claims with Codex claims. If a legacy profile explicitly documents Claude Code usage in a real project, preserve that fact. If it does not, omit named tool claims.

## Verification Checklist

After creating or updating a CV or cover letter, re-read the generated source files and verify all items below before presenting the result.

### Factual Accuracy
- [ ] All claims match `AGENTS.md` and `.agents/skills/job-application-assistant/01-candidate-profile.md`.
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
