---
name: job-application-assistant
description: >
  Assists with job applications: evaluating job postings, tailoring CVs, writing cover letters,
  and preparing for interviews. Triggers on keywords like: job posting, job application, CV,
  cover letter, resume, interview prep, job fit, career, application, apply, ansøgning, stilling
---

# Job Application Assistant

---

## Workflow

When the user provides a job posting (URL or text), follow this workflow:

### Step 1: Research & Evaluate Fit
- Fetch the job posting content (use web fetch for URLs)
- Analyze the posting for required competencies, keywords, and priorities
- Research the company (website, LinkedIn, mission, recent news)
- Load the evidence bank using `profile.yaml` -> `evidence/*.md` -> supporting private Markdown -> master CV, then score the posting against it. Search all evidence for the current posting; do not default to resume order or permanently prioritize employers/projects.
- Respect `NEEDS_CONFIRMATION.md`, provenance, team-versus-personal attribution, and completed/in-progress/planned status distinctions.
- Present the evaluation table and verdict
- Suggest whether the candidate should call the employer before applying (see `04-job-evaluation.md` for guidance)
- Ask the user if they want to proceed with an application

### Step 2: Tailor CV
- Read `private_profile/profile.yaml` as the authoritative structured source when present, and use `private_profile/evidence/*.md` for atomic job-specific evidence; legacy `01-candidate-profile.md` is supporting material only
- Use any existing CV only as supporting evidence or visual reference; do not copy a populated resume as the draft
- Follow the guidelines in `05-cv-templates.md`
- Extract the posting's requirements, score candidate roles/projects/skills/bullets for relevance, then select, shorten, omit, and reorder content before writing LaTeX
- Create `cv/main_<company>.tex` with tailored content
- Adjust: selected experiences/projects, skills section, bullet wording, bullet order, and section order when justified
- Compile and check against the active template page limit; if over the limit, return to content selection rather than compressing the visual design
- Compare the generated CV against the master resume and revise if it is effectively a full copy with only minor edits

### Step 3: Write Cover Letter
- Follow the writing style rules in `03-writing-style.md` (critical: no em-dashes, no cliches)
- Follow the template structure in `06-cover-letter-templates.md`
- When the active CV template is `jd-resume`, use the matching `templates/cover-letter/jd-resume/template.tex` cover-letter template and compile it with LuaLaTeX
- Create `cover_letters/cover_<company>_<role>.tex`
- Ensure the letter connects specific experience to the role requirements

### Step 4: Interview Preparation
- Follow the framework in `07-interview-prep.md`
- Prepare STAR-format answers for likely questions
- Identify role-specific talking points
- Draft questions the candidate should ask the interviewer

---

## Reference Files

| File | Purpose |
|------|---------|
| `profile.yaml` + `evidence/*.md` | Structured source of truth plus detailed atomic, provenance-aware evidence |
| `01-candidate-profile.md` (optional legacy) | Supporting candidate facts/configuration when present |
| `02-behavioral-profile.md` | Behavioral assessment, strengths, ideal environments |
| `03-writing-style.md` | Tone, structure, do's and don'ts |
| `04-job-evaluation.md` | Scoring framework for job fit |
| `05-cv-templates.md` | LaTeX CV structure and tailoring rules |
| `06-cover-letter-templates.md` | LaTeX cover letter structure and tailoring rules |
| `07-interview-prep.md` | STAR examples, tough questions, roleplay guidelines |

---

## Quick Commands

The user may also ask for individual steps without the full workflow:
- "Evaluate this job posting" - Step 1 only
- "Write a CV for [company]" - Step 2 only
- "Write a cover letter for [role] at [company]" - Step 3 only
- "Help me prepare for an interview at [company]" - Step 4 only
- "What jobs should I look for?" - Career strategy discussion using profile + evaluation framework
