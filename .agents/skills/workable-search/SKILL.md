---
name: workable-search
version: 1.0.0
description: >
  Search Jobs by Workable for Canadian job postings. Trigger on Jobs by Workable, Canada jobs, Canadian job search,
  engineering jobs Canada, robotics engineer Canada, mechanical designer Canada, automation engineer Canada,
  controls engineer Canada, Vancouver jobs, Toronto jobs, Ontario jobs, British Columbia jobs.
context: fork
---

# Jobs by Workable Search

Status: **partially automated**



## Access method

Parses public Jobs by Workable pages and embedded initial state / schema.org JSON. Robots allows `/search/*` but disallows query-string `/search?...`; use low-volume personal searches and prefer detail URLs when known.

## Commands

```bash
cd .agents/skills/workable-search/cli
bun run src/cli.ts search -q "mechanical engineer" -l "Vancouver, BC" --limit 5 --format table
bun run src/cli.ts detail <id-or-url> --format plain
```

Flags: `--query/-q`, `--location/-l`, `--jobage`, `--page`, `--limit/-n`, `--format json|table|plain`.

## Examples

```bash
bun run src/cli.ts search -q "robotics engineer" -l "Vancouver, BC" --limit 5 --format table
bun run src/cli.ts search -q "mechatronics engineer" -l "Ontario" --limit 5 --format json
bun run src/cli.ts search -q "automation engineer" -l "Toronto, ON" --jobage 14 --format table
bun run src/cli.ts search -q "mechanical designer" -l "Waterloo, ON" --limit 5 --format table
bun run src/cli.ts search -q "entry-level engineer" -l "Remote Canada" --limit 5 --format table
```

## Output

Search emits `{ "meta": { "count": n, "page": n }, "results": [...] }`. Results include title, employer, location, city, province, country, remote/workplace signal, posting date, closing date, employment type, salary, source URL, apply URL, portal name, and stable source id when available.

## Limitations

See `url-reference.md` for robots.txt, terms/access notes, URL parameters, pagination notes, and parser anchors.
