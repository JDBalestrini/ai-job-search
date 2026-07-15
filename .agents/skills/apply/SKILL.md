---
name: apply
version: 1.0.0
description: >
  Run the full job application workflow: parse a posting, evaluate fit, draft a tailored CV and cover letter, use a reviewer subagent, compile PDFs, run ATS checks, and present final outputs.
context: fork
---

# apply workflow - Drafter-Reviewer Job Application Workflow

You are orchestrating a drafter plus independent-reviewer workflow. The job posting is provided in the user's request, either as a URL or pasted text.

Follow these steps **exactly in order**. Do not skip steps.

**Token-efficiency rules for this workflow:**
- Never re-read a file whose contents are already in your context from an earlier step. If you read it in Step 1, it is still available in Step 2.
- When dispatching the reviewer subagent, pass draft content **inline in the subagent prompt** rather than asking the subagent to read files you already have in memory.
- Run the full verification checklist exactly once, at the end (Step 6). The reviewer focuses on content critique, not verification.
- Step 5 (compile and inspect PDFs) is mandatory and non-skippable - LaTeX page-break decisions are unpredictable, and `.tex` files that look fine often produce broken PDFs (orphaned entry titles, cover letters spilling to page 2, bullet fonts mismatching).

---

## Step 0: Parse Input

- If the user request looks like a URL, fetch the job posting content.
- If it is pasted text, use it directly.
- Extract: **company name**, **role title**, **department** (if mentioned), **location**, and **language** of the posting (Danish or English).
- Store these for use throughout the workflow.

---

## Step 1: DRAFTER - Evaluate Fit

Read the evaluation framework:
- `private_profile/04-job-evaluation.md`
- `private_profile/01-candidate-profile.md`

If either private profile file is missing, stop and ask the user to run `the setup skill` before applying. Do not fall back to tracked placeholder examples for candidate facts.

Using the framework from `04-job-evaluation.md`, evaluate the job posting against the candidate's profile. Extract and retain a requirement map for later CV tailoring:

- **Required qualifications:** named tools, education, experience level, responsibilities, and must-have competencies.
- **Preferred qualifications:** nice-to-have tools, domain experience, soft skills, and company/team signals.
- **Role priorities:** infer the top 3-5 hiring priorities from repeated or prominent posting language.
- **Unsupported gaps:** requirements not supported by the private profile. These remain visible as gaps; do not hide them with keyword stuffing.

If the salary lookup tool is configured, run:

```bash
python salary_lookup.py "<Company Name>" --json
```

If the posting specifies a city, add `--city "<City>"` to narrow results. Parse the JSON output and include the salary benchmark in the evaluation. If the tool is not configured or returns an error, skip the salary benchmark.

Present the evaluation to the user with:

1. **Skills match** - which required/preferred skills match vs. gaps
2. **Experience match** - how work history maps to the role
3. **Behavioral/culture match** - how behavioral profile fits the role/company culture
4. **Salary benchmark** - salary index for the company (if available)
5. **Overall fit score** and recommendation (strong fit / moderate fit / weak fit)

After presenting the evaluation, ask the user:
> "Should I proceed with drafting the CV and cover letter for this role?"

**If the user says no, stop here.** If yes, continue to Step 2.

---

## Step 2: DRAFTER - Draft CV + Cover Letter

You already have `01-candidate-profile.md` and `04-job-evaluation.md` in context from Step 1. **Do not re-read them.**

Read only the reference files you do not yet have:
- `private_profile/03-writing-style.md`
- `private_profile/05-cv-templates.md`
- `private_profile/06-cover-letter-templates.md`

If `private_profile/05-cv-templates.md` contains an `ACTIVE-TEMPLATE` managed block, read the referenced manifest and template skeleton before drafting. Use the skeleton's commands, section order, margins, spacing, page limit, and class/style dependencies as authoritative where they conflict with stock moderncv guidance. If the referenced template is missing or fails to compile, tell the user and fall back to the stock `cv/main_example.tex` moderncv template only with explicit user approval.

If the active CV template manifest declares a matching cover-letter template, or `private_profile/06-cover-letter-templates.md` contains an `ACTIVE-COVER-TEMPLATE` block, read that cover-letter manifest and skeleton before drafting the letter. When `jd-resume` is the active CV template, use `templates/cover-letter/jd-resume/template.tex` automatically. Do not fall back to the unrelated stock `cover.cls` design unless the matching template is missing or fails and the user approves the fallback.

Record the active CV page limit from `private_profile/05-cv-templates.md` or the active template manifest. If no custom template is active, use the stock page limit from `.agents/skills/job-application-assistant/05-cv-templates.md`. All later CV page-count checks use this active limit; do not assume every template is two pages.

Also read one existing cover letter file as a concrete structural reference:
- Read any existing `cover_letters/cover_*.tex` or `cover_letters/Cover_*.tex` file as a template reference.

For the CV, separate facts from wording and layout:
- `private_profile/01-candidate-profile.md` is the authoritative fact store for candidate facts.
- `private_profile/main.tex` or `private_profile/cv/main.tex` may be read only as supporting evidence and visual reference for the candidate's existing resume style. It is **not** the output template, not the primary source of truth, and not a file to copy with minor edits.
- The active template skeleton (`templates/cv/.../template.tex`) or stock `cv/main_example.tex` defines the LaTeX structure and commands. Generate a fresh `cv/main_<company>.tex` from that skeleton.
- Preserve exact dates, titles, employers, education, contact facts, and metrics from the private profile. Rewrite only wording/emphasis; never alter factual meaning.

### Step 2a: CV Tailoring Ledger (mandatory before writing LaTeX)

Before drafting the CV source, build a concise tailoring ledger in memory using the requirement map from Step 1. Do not write this ledger to tracked files; include a summary in Step 6.

For every candidate role, project, skill group, education item, award group, and source bullet in `01-candidate-profile.md`:

1. Score relevance to the posting:
   - 3 = directly matches a required qualification or core responsibility.
   - 2 = supports a preferred qualification or strong company/team signal.
   - 1 = transferable but secondary.
   - 0 = unrelated for this application.
2. Score uniqueness:
   - 2 = the only concrete evidence for an important requirement.
   - 1 = useful but duplicated elsewhere.
   - 0 = redundant.
3. Score recency/credibility:
   - 2 = recent professional, research, or high-signal project evidence.
   - 1 = older or secondary evidence.
   - 0 = weak support.
4. Mark the decision:
   - **selected** - include in the CV.
   - **shortened** - include role/project but fewer bullets.
   - **omitted** - leave out because page budget and relevance do not justify it.
   - **reordered** - move section, role, bullet, or skill group because the posting makes it higher signal.
5. Record the reason in one sentence.

Selection rules:
- Select the strongest relevant content under the page limit. Do not carry every role, project, award, or skill forward by default.
- Keep mandatory identity, contact, highest/current education, exact dates, titles, employers, and locations.
- Omit or condense low-relevance older roles, low-signal awards, generic skills, and duplicated bullets even if they appear in the master resume.
- Reorder skills and bullets so the posting's strongest supported requirements appear first.
- Section ordering may change when justified by the posting, unless an active template manifest explicitly forbids it. If the manifest says to preserve section order, preserve the top-level order but still tailor the content within each section.
- Rewrite selected bullets for emphasis and clarity using job language only where the underlying profile supports it.
- Do not require artificial paraphrasing when an existing bullet is already optimal and relevant; exact reuse is acceptable for individual high-signal bullets.

### Step 2b: Anti-Copy Safeguard (mandatory after drafting CV)

After drafting `cv/main_<company>.tex` but before writing the final cover letter or dispatching the reviewer, compare the generated CV body with `private_profile/main.tex` or `private_profile/cv/main.tex` if available.

Fail the draft and revise before continuing when either condition is true:
- The generated CV retains substantially all master resume roles/projects/skills/bullets without selection or omission.
- The generated CV is effectively a full copy with only contact, company, summary, or small wording changes.

When comparing, ignore unavoidable identical tokens: candidate name, contact details, degree titles, employer names, role titles, locations, dates, metrics, LaTeX commands, section headings, and technical terms. Do not penalize exact reuse of a few relevant bullets when the tailoring ledger justifies them.

If the safeguard fails:
1. Return to the tailoring ledger.
2. Cut or shorten the lowest-relevance retained items first.
3. Reorder skills/bullets toward the posting.
4. Rerun the comparison before continuing.

### CV (`cv/main_<company>.tex`)
- Always in **English**
- Follow the active template override in `private_profile/05-cv-templates.md` when present; otherwise follow the moderncv/banking format from the stock fallback guidance
- If the active template requires class/style files, copy them beside the generated CV or reference them by a stable relative path exactly as the manifest instructs
- Build the document from the sanitized template skeleton, not from the populated private master resume
- Select, shorten, omit, and reorder content according to the tailoring ledger
- Reframe skills and achievements to match job requirements without changing factual meaning
- Keep to the active template's exact page limit. For the active `jd-resume` template, this means exactly 1 page.

### Cover Letter (`cover_letters/cover_<company>_<role>.tex`)
- **Match the language of the job posting** (Danish posting -> Danish cover letter, English posting -> English cover letter)
- Follow the active cover-letter template from `private_profile/06-cover-letter-templates.md` when present
- If the active CV template is `jd-resume`, build from `templates/cover-letter/jd-resume/template.tex` so the CV and cover letter share header typography, contact formatting, margins, font family, hyperlink styling, and visual identity
- Use the stock `cover.cls` template only when no active matching cover-letter template is configured or the user approves fallback after a matching-template failure
- For the `jd-resume` cover-letter template, use the structured `\recipientrow{company}{street}{city, province/state}{postal/ZIP}{country}{date}` macro. Verify company address fields from the posting, official company pages, or authoritative listings; do not guess street addresses.
- Tailor the opening paragraph to the specific role and company
- Address to a named person if available in the posting, otherwise "Dear Hiring Manager" (or equivalent in posting language)
- Keep concise, but cover letters may exceed one page when the extra content is useful, specific, and grounded
- Mention a named AI tool only when the candidate profile explicitly documents that the candidate used that tool in the underlying work being described. Using Codex to prepare this application is not evidence that the candidate used Codex in a job, project, or achievement.

Write both files to disk. Keep the exact text of both drafts in working memory - you will pass them inline to the reviewer in Step 3 and revise them in Step 4 without re-reading.

---

## Step 3: REVIEWER - Research & Critique

Use a **Codex subagent workflow** to run a fresh-context `general-purpose` reviewer subagent. Pass the drafts **inline in the prompt** below. Scope the reviewer's file reads to content-critique essentials only. The reviewer does not need the LaTeX template files (`05`, `06`) to critique content, since those govern structural/LaTeX concerns the drafter already applied.

Replace `<COMPANY>`, `<ROLE>`, `<INSERT_JOB_POSTING_TEXT_HERE>`, `<INSERT_CV_DRAFT_HERE>`, and `<INSERT_COVER_LETTER_DRAFT_HERE>` with actual values before dispatching.

```
You are a hiring manager proxy reviewing a job application. Your job is to make the application as targeted and compelling as possible.

## Your Tasks

### 1. Research the Company
Use web search and page fetching to research:
- The company's website, mission, and recent news
- The specific department or team (if mentioned in the posting)
- Any recent projects, press releases, or strategic initiatives relevant to the role
- Company culture and values

### 2. Read Reference Materials (content-critique only)
Read these four files - and only these - to ground your critique:
- `private_profile/01-candidate-profile.md`
- `private_profile/02-behavioral-profile.md` - use this specifically to check whether the cover letter's voice matches the candidate's natural register. A "Collaborator" PI profile, for example, should not be given a combative, solo-hero tone; a "Persuader" profile should not be given over-hedged, apologetic phrasing.
- `private_profile/03-writing-style.md`
- `private_profile/04-job-evaluation.md`

Do NOT read `05-cv-templates.md` or `06-cover-letter-templates.md` - those govern LaTeX structure the drafter already applied and are not needed for content critique.

### 3. Drafts to Review
Both drafts are provided inline below. Do NOT read the draft files from disk. Use these exact texts.

<CV_DRAFT file="cv/main_<COMPANY>.tex">
<INSERT_CV_DRAFT_HERE>
</CV_DRAFT>

<COVER_LETTER_DRAFT file="cover_letters/cover_<COMPANY>_<ROLE>.tex">
<INSERT_COVER_LETTER_DRAFT_HERE>
</COVER_LETTER_DRAFT>

### 4. Job Posting
<JOB_POSTING>
<INSERT_JOB_POSTING_TEXT_HERE>
</JOB_POSTING>

### 5. Produce Feedback

Return your feedback in **two parts**:

**Part A - Structured edits (preferred format whenever possible):**
A JSON array of concrete edits the drafter can apply directly without re-reading the files. Each edit is an object:
```json
{
  "file": "cv/main_<COMPANY>.tex" | "cover_letters/cover_<COMPANY>_<ROLE>.tex",
  "old_string": "<exact text currently in the draft>",
  "new_string": "<replacement text>",
  "reason": "<one-line rationale: keyword match / company angle / reframing / style>"
}
```
Only use this format when you can quote the exact `old_string` from the drafts above. Make `old_string` unique - include enough surrounding context so it matches exactly once per file.

**Part B - Narrative suggestions (for judgment calls that are not mechanical edits):**
Prose suggestions grouped by category. Produce each category even if your finding is "no issues" - silence on a category can be mistaken for skipping it.
- **Tailoring quality** - explicitly judge whether the CV appears genuinely selected, ordered, and rewritten for this posting rather than copied from a master resume. Identify irrelevant retained bullets, missing high-value evidence, weak ordering, generic wording, and unsupported claims.
- **Missed keywords/requirements** - what to add and roughly where, if it cannot be expressed as a clean string replacement
- **Company/department-specific angles** - connections between experience and the company's strategic priorities, based on your research
- **Action-oriented reframing** - identify passive, generic, or low-energy statements and suggest action-oriented rewrites. Use this category especially for structural weakness that doesn't fit a single-sentence swap (e.g., "the whole opening paragraph reads as passive - restructure around your single strongest match to the posting").
- **Tone and style issues** - check against `03-writing-style.md` AND `02-behavioral-profile.md`. Flag any issues with tone, formality, or voice (cliches, hedging, over-humility, inconsistent register), and specifically flag any mismatch between the letter's voice and the candidate's natural register as described in the behavioral profile.

**CRITICAL RULE:** All suggestions must be grounded in actual profile data. Do NOT suggest fabricating skills, experience, or achievements. If a requirement is a gap, say so honestly and suggest how to frame adjacent experience instead.

**AI TOOL CLAIM RULE:** Do not add Codex, Claude Code, ChatGPT, Gemini, or any other named AI tool to the application unless the candidate profile explicitly says that named tool was used in the underlying experience. Preparing the application with an AI assistant is not a candidate credential.

Do **not** run a verification checklist - the drafter will do that in the final step. Focus on content critique.

Return Part A and Part B together as a single structured message.
```

---

## Step 4: DRAFTER - Revise Based on Feedback

Once the reviewer subagent returns its feedback:

1. **Apply Part A (structured edits) directly with the targeted file-editing capability.** Do NOT re-read the draft files - you already have them in context from Step 2, and the reviewer's `old_string` values were quoted from that same text. For each edit in the JSON array, make a targeted edit with the given `file`, `old_string`, and `new_string`. Skip any whose rationale would require fabricating content.
2. **Apply Part B (narrative suggestions)** using judgment. These need interpretation, not mechanical replacement. Walk through every Part B category the reviewer returned and address it:
   - **Tailoring quality:** remove irrelevant retained bullets, add stronger omitted evidence when supported, improve ordering, and replace generic wording. If the reviewer says the CV still looks copied from the master resume, return to Step 2a/2b before compiling.
   - **Missed keywords/requirements:** add the keyword or capability where it fits naturally in the CV or cover letter. Prefer the experience bullets (concrete evidence) over the profile statement (abstract claim).
   - **Company/department-specific angles:** weave the reviewer's research into the cover letter opening or motivation paragraph. Verify every company claim independently before including it. Do not trust reviewer research at face value.
   - **Action-oriented reframing:** rewrite passive or generic phrasing (CV profile statement, cover letter opening, bullet leads). Structural weakness that the reviewer flagged without a clean JSON edit lives here.
   - **Tone and style issues:** apply the writing-style-guide fixes (no em-dashes, no cliches, no apologetic hedging, consistent first-person active voice).
   Use targeted edits for targeted changes; only re-read a file if an edit fails because the surrounding text has shifted.
3. Do NOT incorporate any suggestion that would fabricate skills or experience. If a posting requirement is a genuine gap, acknowledge it honestly and frame adjacent experience instead.

After all edits are applied, the two files on disk are the final drafts.

---

## Step 5: DRAFTER - Compile & Inspect PDFs (MANDATORY)

**Never skip this step.** The `.tex` files looking fine is not sufficient - LaTeX page-break decisions are unpredictable and commonly produce broken layouts (orphaned job titles separated from their bullets, cover letters spilling to 2 pages, bullet fonts not matching body text). Compile both documents and visually verify the PDFs before presenting.

### 5a. Compile

```bash
cd cv && lualatex -interaction=nonstopmode main_<company>.tex
cd ../cover_letters && lualatex -interaction=nonstopmode cover_<company>_<role>.tex
```

- CV uses **lualatex** - pdflatex fails on modern MiKTeX with fontawesome5 font-expansion errors. lualatex handles the same sources cleanly.
- Cover letter uses the active cover-letter template's engine. For the matching `jd-resume` cover-letter template, use **lualatex**. The stock `cover.cls` fallback uses **xelatex** because it requires fontspec.

If either compile fails, fix the error and re-compile until clean.

### 5a.1 CV page-fit loop

After every CV compile, check the PDF page count against the active CV page limit.

If the CV exceeds the active limit:

1. Treat the draft as failed.
2. Return to the Step 2a tailoring ledger.
3. Shorten or omit lower-value content in this order:
   - remove low-relevance bullets;
   - combine overlapping bullets;
   - shorten verbose bullets;
   - remove low-value awards or secondary details;
   - shorten lower-priority projects;
   - omit the least relevant experience or project if necessary;
   - reduce skills to only role-relevant items.
4. Preserve readable visual design. Do not primarily fix overflow by shrinking fonts, margins, line spacing, or making the resume cramped.
5. Recompile and repeat until the CV is exactly the active page limit.

If the active limit cannot be met without unacceptable formatting or removal of essential role evidence, stop and explain the tradeoff clearly instead of presenting an over-limit CV as complete.

If the CV meets the active limit but leaves a conspicuous unused block at the bottom, treat the page-fit loop as incomplete. Do not stretch the page with fake content, larger type, larger margins, line-spacing changes, class-level list-spacing changes, `\vfill`, `\flushbottom`, or one-off bottom `\vspace`. Return to the tailoring ledger, re-score omitted and shortened content against this posting, restore the next-highest-relevance non-duplicative bullet, project detail, award, or skill row that supports a requirement, then recompile and recheck the page count. Stop when the page is naturally well utilized without crowding.

### 5b. Inspect layout

Inspect both PDFs via the file/PDF inspection capability and verify:

**CV (`cv/main_<company>.pdf`):**
- [ ] Exactly the active CV template page limit. For `jd-resume`, exactly 1 page.
- [ ] No orphaned `\cventry` titles - a job/education title line must never sit alone at the bottom of page 1 with its bullets on page 2. This is the most common failure.
- [ ] Section headings are not isolated at the top of page 2 with only 1-2 lines below
- [ ] No awkward whitespace gaps

**Cover letter (`cover_letters/cover_<company>_<role>.pdf`):**
- [ ] Page count is appropriate for the content; more than one page is allowed when justified
- [ ] Signature block visible, not cut off, and not isolated awkwardly
- [ ] Visual identity matches the active CV template: header typography, contact formatting, margins, font family, hyperlink styling, and spacing rhythm. For `jd-resume`, this means Latin Modern, uppercase bold centered name, diamond-separated centered contacts, blue hyperlinks, and 0.4/0.5 inch margins.
- [ ] Bullet list font matches surrounding body text. For `jd-resume`, bullets use the same Latin Modern body font; for stock `cover.cls`, body and bullets should use the configured cover fonts.

### 5c. Iterate until clean

If the layout has problems, edit the `.tex` files and recompile. Common fixes (see `05-cv-templates.md` and `06-cover-letter-templates.md` for full details):

- **Orphaned CV entry title:** `\usepackage{needspace}` in preamble, then `\needspace{5\baselineskip}` immediately before the problematic `\cventry`
- **CV spills to page 3 with only a trailing section:** `\enlargethispage{2-3\baselineskip}` before a late section
- **CV exceeds the active page limit:** cut content using **relevance-weighted cutting** (see `05-cv-templates.md` -> "Relevance-weighted cutting"). Score each candidate line by (a) relevance to THIS posting's keywords and responsibilities, (b) uniqueness (is it duplicated elsewhere?), (c) narrative load (does the cover letter depend on it?). Cut the lowest-total-score line first, regardless of section. Do NOT mechanically apply a static section-based priority order - an older-role bullet that hits posting keywords is worth more than a recent-role bullet that does not.
- **Stock cover.cls itemize breaks compile or uses wrong font:** close `\lettercontent{}` before the list, wrap the list in `{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont \begin{itemize}...\end{itemize}\par}`. This pitfall does not apply to the matching `jd-resume` cover-letter template, which uses ordinary LaTeX paragraphs and `itemize`.
- **Cover letter spills to 2 pages:** trim using the same relevance-weighted logic. First cut: sentences that restate what a bullet already said. Second cut: a bullet that does not hit posting keywords. Last resort: a bullet that does hit posting keywords. Never reduce geometry or line spacing.

Do not proceed to Step 6 until both PDFs pass inspection.

### 5d. ATS & keyword verification (CV)

An ATS parser reads the PDF's embedded **text layer**, not the rendered page - a CV that passed visual inspection can still extract as garbage (icon glyphs where the contact details should be, scrambled reading order in multi-column layouts). This step verifies what a parser actually sees. It applies to the **CV only**; cover letters rarely go through keyword screening.

**Availability check:** run `pdftotext -v`. `pdftotext` (poppler) is an optional dependency, not part of TeX distributions. If it is missing, print a one-line warning that the mechanical parse check is skipped, do the keyword-coverage check (item 3 below) against your visual PDF inspection instead, and note the degraded mode in the Step 6 report. Same graceful-skip pattern as the salary lookup.

**1. Extract the text layer:**

```bash
cd cv && pdftotext -layout main_<company>.pdf main_<company>.txt
```

Read the `.txt` file.

**2. Parseability checks** on the extracted text:

- [ ] **Text extracted at all**, with no garbage runs: no `(cid:NNN)` markers, no `ï¿½` replacement characters, no stretches of missing text that are visible in the PDF
- [ ] **Email and phone survive as literal text.** Icon fonts extract as glyph names (the stock template's contact line extracts as `MOBILE-ALT [+XX ...] - Envelope [your.email@...]`) - that noise is harmless, but the actual address and digits must be present. A contact detail carried only by an icon or a hyperlink target (like the `LinkedIn` link text) is invisible to an ATS; the email must be printed as text.
- [ ] **Reading order matches the visual order** - section headings appear in the same sequence as on the page, and lines from different sections are not interleaved. The stock banking template is single-column and safe; custom templates registered via `the add-template skill` with sidebars or multi-column layouts are where this breaks.
- [ ] **Dates recognizable** - each role and degree has its years present in the extraction.

Failures here are template-level problems: fix them in the `.tex` (e.g. print the email as text rather than icon-only), then re-run 5a-5c and re-extract. If a custom template's layout fundamentally scrambles extraction order, tell the user prominently - they may be trading ATS compatibility for looks.

**3. Keyword coverage.** Reuse the required/preferred keyword list you extracted in Step 1 - do not re-derive it. Match each keyword against the extracted text, **in the posting's language** (a Danish posting's keywords are matched in Danish even though the CV is in English - where the CV legitimately covers the concept in English, count it as synonym-only and note the language difference). Report a table:

| Keyword | Priority | Status | Note |
|---------|----------|--------|------|
| ... | required/preferred | covered / synonym-only / missing (have it) / missing (gap) | where it appears, or why absent |

- **covered** - the term appears (verbatim or trivial inflection).
- **synonym-only** - the concept is present under a different term. If the posting's exact term is truthfully applicable per the profile, prefer the posting's term (ATS keyword matches are often literal).
- **missing (have it)** - the profile shows the candidate genuinely has this skill but the CV never says it: add it where it fits naturally, preferring experience bullets (concrete evidence) over the profile statement, then re-run 5a-5c.
- **missing (gap)** - a genuine gap: leave it missing. **Never stuff keywords.** This is the same honesty rule the reviewer follows - a gap gets acknowledged in the cover letter's framing, not hidden in the CV.

**4. Clean up:** delete the extracted `.txt` file.

### 5e. Clean up build artifacts

After the final clean compile, delete the `.aux`, `.log`, `.out` files (keep the `.tex` and `.pdf`).

---

## Step 6: Present Final Output

Run the full verification checklist from `AGENTS.md` now - this is the **only** verification pass in the workflow. Re-read both files once here to verify final state on disk matches your mental model after the Step 4 and Step 5 edits.

### Verification Checklist
Report pass/fail for each item in the AGENTS.md verification checklist (factual accuracy, targeting, consistency, quality).

### Key Tailoring Decisions
Summarize 3-5 key decisions made to tailor the application and include the CV tailoring ledger summary:
- What was emphasized and why
- Which master resume items were selected, shortened, omitted, or reordered and why
- Which bullets were rewritten and why
- What company-specific angles were incorporated
- What the reviewer suggested that was most impactful
- Any gaps that were acknowledged or reframed

### Files Created
List the files written:
- `cv/main_<company>.tex`
- `cover_letters/cover_<company>_<role>.tex`

Tell the user: "Both files are ready for your review. Open them to check the final output before compiling."

### Next Steps
- **Submitted?** `the outcome skill <company>` logs it in the tracker and starts the per-application record that `the setup skill` later uses to calibrate the fit framework.
- **Interview scheduled?** `the interview skill` builds a stage-specific prep pack from this posting and the documents you just created.
