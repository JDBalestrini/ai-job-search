# Government of Canada Job Bank URL Reference

- Portal: https://www.jobbank.gc.ca/jobsearch/jobsearch
- Robots: `User-agent: *` with `Crawl-delay: 5`; no search/detail disallow observed.
- Search endpoint: `/jobsearch/jobsearch?searchstring=<query>&locationstring=<location>&page=<n>&sort=M`
- Detail endpoint: `/jobsearch/jobposting/<numeric-id>`
- Result anchors: `<article id="article-<id>">`, `a.resultJobItem`, `.noctitle`, `li.business`, `li.location`, `li.date`, `li.salary`.
- Pagination: `page=<n>`.
- Recency: no stable `jobage` parameter confirmed; `--jobage` is accepted for CLI compatibility but not applied.
