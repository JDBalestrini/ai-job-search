# CivicJobs.ca URL Reference

- Portal: https://www.civicjobs.ca/
- Robots: `User-agent: *`, `Crawl-delay: 5`, disallows `/mobile/`; several named SEO crawlers are disallowed.
- Live check: root, `/jobs`, `/careers`, and `/rss` returned HTTP 403 to low-volume non-authenticated requests.
- Status: manual-search fallback. No automated parser is registered because access controls should not be bypassed.
- Manual URL generated: `/jobs?search=<query>&location=<location>`.
