# Template: jd-resume cover letter

- **Type:** Cover letter
- **Engine:** lualatex
- **Page target:** concise, usually 1 page, but longer is allowed when the application content warrants it
- **Fonts:** Latin Modern via the TeX distribution; no bundled font files required
- **Class/packages:** reuses `templates/cv/jd-resume/resume.cls`, `article`, `geometry`, `parskip`, `enumitem`, `ifthen`, `hyperref`

## Compile command

    cd cover_letters && lualatex -interaction=nonstopmode cover_<company>_<role>.tex

## Visual match to `jd-resume`

- Reuse the `resume.cls` header commands from the CV: `\name` and `\address`.
- Preserve the same margins as the CV: `left=0.4 in, top=0.5in, right=0.4 in, bottom=0.4in`.
- Preserve the same primary font family and weights: Latin Modern, uppercase bold name, normal-weight contact lines, bold section-like labels only where needed in the letter body.
- Preserve the same contact formatting: centered lines, diamond separators from `resume.cls`, literal email/phone text, LinkedIn, GitHub, and portfolio links.
- Preserve the same hyperlink styling: blue links from `resume.cls`/`hyperref`.
- Do not use `cover.cls`, Lato, Raleway, icon fonts, or `fontspec` for this matching template.

## Letter conventions

- Include date, recipient/company block when available, greeting, concise body paragraphs, closing, and printed name.
- Use `\recipientrow{company}{street}{city, province/state}{postal/ZIP}{country}{date}` for the recipient/date area.
- The recipient row keeps the company/address block on the left and the date on the right. The top line of the date aligns with the company-name line.
- The macro includes a small top offset so the date moves down to the recipient block rather than pulling the recipient block upward.
- The left and right blocks are separate minipages, so long company names or multi-line addresses wrap without overlapping the date.
- Do not import resume sections, resume headings, or resume-style bullet density into the letter.
- Bullets are optional. Prefer 0-3 bullets only when they clarify direct requirement matches.
- Keep the letter concise. Do not force it to one page by changing margins, font sizes, or header styling; a second page is acceptable when the content is useful and grounded.

## Required assets

- `templates/cv/jd-resume/resume.cls`
- No bundled fonts or absolute paths.

## Generated output

Generated letters live under ignored `cover_letters/cover_<company>_<role>.tex`. When generated there, the document class path should be:

    \documentclass{../templates/cv/jd-resume/resume}

This path is relative to the ignored `cover_letters/` output directory and is Windows/MiKTeX compatible.
