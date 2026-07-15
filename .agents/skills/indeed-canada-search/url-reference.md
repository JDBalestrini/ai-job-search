# Indeed Canada URL Reference

- Portal: https://ca.indeed.com/
- Robots: disallows many relevant job/search/detail paths including `/jobs`, `/jobs/CA`, `/viewjob?`, `/m/viewjob?`, `/rss`, `/rpc/`, `/graphql`, and related tracking/apply paths for broad user agents; also blocks several scraper bots entirely.
- Live check: `/jobs?q=mechanical+engineer&l=Vancouver%2C+BC` returned HTTP 403.
- Status: manual-search fallback only. No automated retrieval is implemented.
- Manual URL generated: `/jobs?q=<query>&l=<location>`.
