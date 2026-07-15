# Search Queries for Job Scraper

<!-- SETUP: Customize these queries based on your skills, target roles, and location -->

## Search Sites

Primary (your market's job boards - scaffold one with `the add-portal skill`):
- **[YOUR_JOB_BOARD]** - your market's largest general job board
- **linkedin.com/jobs** - LinkedIn job listings (filter: [YOUR_COUNTRY] / [YOUR_CITY])
- **[YOUR_INDUSTRY_JOB_BOARD]** - a niche/industry board for your field (optional)
- **[YOUR_ADDITIONAL_JOB_BOARD]** - another major board for your market (optional)

Canadian portal examples (enable or adapt in `private_profile/search-queries.md`; do not store personal search history here):
- **canada-job-bank-search** - Government of Canada Job Bank, fully automated, public HTML search/detail with 5-second robots crawl delay
- **engineering-careers-search** - EngineeringCareers.ca, fully automated public HTML search/detail
- **eluta-search** - Eluta, partially automated public SEO result/detail pages only; no `/search/` or `/cache` scraping
- **workable-search** - Jobs by Workable, partially automated public embedded structured data; keep volume low and do not bypass Cloudflare challenges
- **civicjobs-search** - CivicJobs.ca, manual-search fallback only because live automated checks returned HTTP 403
- **indeed-canada-search** - Indeed Canada, manual-search fallback only because robots/access controls disallow or block relevant job retrieval

Secondary (company career pages via Google):
- Direct Google searches with `site:` filters for known target companies

## Query Categories

Queries are grouped by priority. Each query should be combined with your location terms (e.g. your city, region, or metro area) where the site supports it.

### Priority 1: [YOUR_PRIMARY_ROLE_TYPE]

These match your strongest and most desired career direction.

```
site:[YOUR_JOB_BOARD] "[YOUR_PRIMARY_JOB_TITLE]" [YOUR_CITY]
site:[YOUR_JOB_BOARD] "[YOUR_KEY_SKILL]" [YOUR_CITY]
site:linkedin.com/jobs "[YOUR_PRIMARY_JOB_TITLE]" [YOUR_COUNTRY]
canada-job-bank-search --query "[YOUR_PRIMARY_JOB_TITLE]" --location "[YOUR_CITY], [PROVINCE]"
engineering-careers-search --query "[YOUR_PRIMARY_JOB_TITLE]" --location "[YOUR_PROVINCE]"
workable-search --query "[YOUR_PRIMARY_JOB_TITLE]" --location "Canada"
```

### Priority 2: [YOUR_DOMAIN_EXPERTISE]

These match your domain expertise.

```
site:[YOUR_JOB_BOARD] [YOUR_DOMAIN_KEYWORD_1] [YOUR_CITY] OR [YOUR_REGION]
site:[YOUR_JOB_BOARD] [YOUR_DOMAIN_KEYWORD_2] [YOUR_COUNTRY]
site:linkedin.com/jobs [YOUR_DOMAIN_KEYWORD_1] [YOUR_CITY] [YOUR_COUNTRY]
eluta-search --query "[YOUR_DOMAIN_KEYWORD_1]" --location "[YOUR_CITY] [PROVINCE]"
canada-job-bank-search --query "[YOUR_DOMAIN_KEYWORD_2]" --location "[YOUR_PROVINCE]"
```

### Priority 3: [YOUR_ADJACENT_ROLE_TYPE]

Adjacent roles you could pivot into.

```
site:[YOUR_JOB_BOARD] "[YOUR_ADJACENT_TITLE_1]" [YOUR_KEY_SKILL] [YOUR_CITY]
site:[YOUR_JOB_BOARD] "[YOUR_ADJACENT_TITLE_2]" [YOUR_KEY_SKILL] [YOUR_CITY]
civicjobs-search --query "[YOUR_ADJACENT_TITLE_1]" --location "[YOUR_CITY], [PROVINCE]"
indeed-canada-search --query "[YOUR_ADJACENT_TITLE_2]" --location "[YOUR_CITY], [PROVINCE]"
```

### Priority 4: Broader Technical / Consulting

Wider net for general technical roles.

```
site:[YOUR_JOB_BOARD] [YOUR_KEY_SKILL] developer [YOUR_CITY]
site:linkedin.com/jobs "[YOUR_KEY_SKILL] developer" [YOUR_CITY]
site:[YOUR_JOB_BOARD] "technical consultant" [YOUR_DOMAIN] [YOUR_CITY]
```

## Location Filter

When evaluating results, verify the job location is within reasonable commute distance from your home. Define acceptable areas:
- [YOUR_CITY] and surrounding areas
- [ACCEPTABLE_AREA_1]
- [ACCEPTABLE_AREA_2]
- [BORDERLINE_AREA] (borderline - ~X min by transit)
- [TOO_FAR_AREA] (too far)

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- "the job-scraper skill [focus_area]" -> relevant category queries + custom focus-specific queries
