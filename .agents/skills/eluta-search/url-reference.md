# Eluta URL Reference

- Portal: https://www.eluta.ca/jobs
- Robots: disallows `/search/`, `/cache`, `/cache?`, `/rss?`, notification and system paths.
- Search endpoint used: SEO pages like `/<query-slug>-jobs-in-<location-slug>`.
- Detail endpoint used: public `/spl/<slug>?imo=...` links from result cards.
- Result anchors: `div.organic-job`, `data-url`, `a.lk-job-title`, `a.employer`, `.location`, `.lk.lastseen`.
- Pagination: `?pg=<n>` appears to be supported on SEO result pages.
- Limitations: no cache scraping; external employer apply pages are not fetched automatically.
