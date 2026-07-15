# EngineeringCareers.ca URL Reference

- Portal: https://www.engineeringcareers.ca/
- Robots: disallows `/invalid-request/`, `/analytics/`, `/apply-profile/`, `*/emailjob/*`, `*/previewjob/*`; public `/jobs/` and `/job/<id>/...` not disallowed.
- Search endpoint: `/jobs/?keywords=<query>&location=<location>`
- Detail endpoint: `/job/<id>/<slug>/`
- Result anchors: `li.lister__item`, `id="item-<id>"`, `.lister__header`, `.lister__meta-item--location`, `.lister__meta-item--salary`, `.lister__meta-item--recruiter`.
- Pagination: likely page query supported by site; CLI sends `Page=<n>` for page > 1.
- Recency: no stable public job-age parameter confirmed.
