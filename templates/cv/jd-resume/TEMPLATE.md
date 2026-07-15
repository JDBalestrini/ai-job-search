# Template: jd-resume

- **Type:** CV
- **Engine:** lualatex
- **Page limit:** 1 page(s)
- **Fonts:** Latin Modern via the TeX distribution; no bundled font files required
- **Class/packages:** `resume.cls` custom class, `article`, `geometry`, `parskip`, `ifthen`, `hyperref`

## Compile command

    cd cv && lualatex -interaction=nonstopmode main_<company>.tex

## Matching cover-letter template

- **Template:** `templates/cover-letter/jd-resume/template.tex`
- **Manifest:** `templates/cover-letter/jd-resume/TEMPLATE.md`
- **Engine:** `lualatex`
- **Class dependency:** reuses `templates/cv/jd-resume/resume.cls`

When this CV template is active, generate cover letters with the matching `jd-resume` cover-letter template so the resume and letter share typography, margins, header layout, contact formatting, link styling, and overall visual identity.

## Style rules

- Preserve the custom `resume` document class and its commands: `\name`, `\address`, `\tab`, `\itab`, and `rSection`.
- Preserve the existing margins exactly: `left=0.4 in, top=0.5in, right=0.4 in, bottom=0.4in`.
- Preserve section order: Education, WORK EXPERIENCE, PROJECT EXPERIENCE, SKILLS.
- Preserve section heading capitalization and divider style from `rSection`.
- Preserve compact list spacing with `\vspace{-3pt}` before lists and `\itemsep -4pt {}` inside lists.
- Do not add class-level list-spacing overrides, stretchable glue, `\vfill`, `\flushbottom`, or manual spacing mechanisms to occupy extra page height.
- Preserve role layout: organization on the left, location italicized on the right, title on the left, dates on the right.
- Preserve skill rows using `\makebox[3.2cm]{$\textbf{...}$\hfill}` labels.
- Use profile-supported facts only. Replace placeholders from `private_profile/` data; never put real personal information in this tracked skeleton.

## Known pitfalls

- The registered `resume.cls` keeps the original styling and accepts the one-argument `\begin{rSection}{...}` usage from the private source.
- The template is very compact and intended for exactly one page. Prefer relevance-weighted content cuts over changing margins, font sizes, `\vspace`, or `\itemsep`.
- Generated CV files must be able to find `resume.cls`; copy `templates/cv/jd-resume/resume.cls` beside the generated `cv/main_<company>.tex`, or reference it by a stable relative path.

## One-page fit loop

For this template, any CV that compiles to more than one page has failed the draft. Do not solve overflow primarily by shrinking fonts, margins, line spacing, or other visual compression. Return to content selection and reduce in this order:

1. Remove low-relevance bullets.
2. Combine overlapping bullets.
3. Shorten verbose bullets.
4. Remove low-value awards or secondary details.
5. Shorten lower-priority projects.
6. Omit the least relevant experience or project if necessary.
7. Reduce skills to only role-relevant items.

Keep 2-4 strong bullets for the most relevant role and 1-3 bullets for secondary roles. Every retained bullet must support a specific posting requirement. If one page cannot be achieved without unacceptable formatting or removal of essential evidence, fail clearly and explain the tradeoff.

After a draft reaches one page, inspect page utilization using the template's normal spacing. If the bottom of the page has a conspicuous unused block, do not stretch the design with fake spacing. Re-score omitted and shortened content for the current posting, restore the next-highest-relevance non-duplicative bullet, project detail, award, or skill row that supports a requirement, then recompile and recheck the one-page limit. Stop when the page is naturally well utilized without crowding.
