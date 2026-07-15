# Jobs by Workable URL Reference

- Portal: https://jobs.workable.com/
- Robots: `Allow: /search/*`; `Disallow: /search*?*`, `/search`, `/profile*`, `/company-login-unauthorized`.
- Search URL inspected: `/search?query=<query>&location=<location>` returns embedded `window.jobBoard.initialState["api/v1/jobs"]`.
- Detail URL: `/view/<slug>/...` includes schema.org `JobPosting` JSON and `window.jobBoard.initialState`.
- Result fields: `id`, `title`, `company.title`, `locations`, `location`, `created`, `employmentType`, `workplace`, `url`, `linkoutUrl`.
- Pagination: initial state exposes `nextPageToken`, but no stable documented token endpoint was adopted for this low-volume parser.
- Limitations: Cloudflare script is present; do not bypass challenges or CAPTCHAs.
