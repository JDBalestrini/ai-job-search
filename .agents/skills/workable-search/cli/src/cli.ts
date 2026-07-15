interface Flags {
  _: string[]
  [k: string]: string | boolean | string[]
}

interface JobResult {
  id: string
  title: string
  company: string | null
  location: string | null
  city: string | null
  province: string | null
  country: string | null
  remote: string | null
  date: string | null
  closingDate: string | null
  employmentType: string | null
  salary: string | null
  url: string
  applyUrl: string | null
  portal: string
  sourceId: string
}

interface DetailResult extends JobResult {
  description: string | null
}

const UA = "Mozilla/5.0 (compatible; CodexJobSearch/1.0; personal low-volume use)"

function parseFlags(argv: string[]): Flags {
  const flags: Flags = { _: [] }
  const alias: Record<string, string> = { q: "query", l: "location", n: "limit" }
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a.startsWith("--") || a.startsWith("-")) {
      const key = alias[a.replace(/^-+/, "")] ?? a.replace(/^-+/, "")
      const next = argv[i + 1]
      if (next === undefined || next.startsWith("-")) flags[key] = true
      else {
        flags[key] = next
        i++
      }
    } else flags._.push(a)
  }
  return flags
}

function writeError(error: string, code: string): number {
  process.stderr.write(JSON.stringify({ error, code }) + "\n")
  return 1
}

function decodeHtml(text: string): string {
  return text
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&nbsp;/g, " ")
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(parseInt(d, 10)))
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
}

function stripTags(html: string): string {
  return decodeHtml(html.replace(/<\s*br\s*\/?>/gi, "\n").replace(/<\/(p|li|div|h\d)>/gi, "\n").replace(/<[^>]+>/g, " "))
    .replace(/[ \t]+/g, " ")
    .replace(/\n\s+/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim()
}

function clean(html: string | undefined | null): string | null {
  if (!html) return null
  const value = stripTags(html).replace(/\s+/g, " ").trim()
  return value || null
}

async function fetchText(url: string): Promise<string> {
  const response = await fetch(url, {
    headers: {
      "User-Agent": UA,
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-CA,en;q=0.9",
    },
    redirect: "follow",
  })
  if (response.status === 404) return ""
  if (!response.ok) throw new Error(`Request failed: ${response.status} ${response.statusText}`)
  return response.text()
}

function splitLocation(location: string | null): { city: string | null; province: string | null; country: string | null } {
  if (!location) return { city: null, province: null, country: "Canada" }
  const normalized = location.replace(/^Location\s+/i, "").replace(/\(City\)/gi, "").replace(/\(([^)]+)\)/g, ", $1").replace(/\s+/g, " ").trim()
  const parts = normalized.split(",").map((p) => p.trim()).filter(Boolean)
  return {
    city: parts[0] ?? null,
    province: parts[1] ?? null,
    country: /canada/i.test(location) ? "Canada" : "Canada",
  }
}

function output(results: JobResult[], page: number, format: string): number {
  if (format === "table") {
    process.stdout.write(["Title | Company | Location | Date | URL", "--- | --- | --- | --- | ---", ...results.map((r) => `${r.title} | ${r.company ?? ""} | ${r.location ?? ""} | ${r.date ?? ""} | ${r.url}`)].join("\n") + "\n")
  } else if (format === "plain") {
    process.stdout.write(results.map((r) => `${r.title} — ${r.company ?? "unknown"} — ${r.location ?? "unknown"}\n${r.url}`).join("\n\n") + "\n")
  } else {
    process.stdout.write(JSON.stringify({ meta: { count: results.length, page }, results }, null, 2) + "\n")
  }
  return 0
}

function outputDetail(result: DetailResult, format: string): number {
  if (format === "plain") {
    process.stdout.write(`${result.title}\n${result.company ?? ""}\n${result.location ?? ""}\n${result.url}\n\n${result.description ?? ""}\n`)
  } else {
    process.stdout.write(JSON.stringify(result, null, 2) + "\n")
  }
  return 0
}

const PORTAL = "Jobs by Workable"
const BASE = "https://jobs.workable.com"

function searchUrl(query: string, location: string | undefined, page: number): string {
  const u = new URL(`${BASE}/search`)
  u.searchParams.set("query", query)
  if (location) u.searchParams.set("location", location)
  if (page > 1) u.searchParams.set("page", String(page))
  return u.toString()
}

function extractJsonAfter(html: string, marker: string): unknown | null {
  const idx = html.indexOf(marker)
  if (idx < 0) return null
  const start = html.indexOf("{", idx + marker.length)
  if (start < 0) return null
  let depth = 0
  let inStr = false
  let esc = false
  for (let i = start; i < html.length; i++) {
    const ch = html[i]
    if (inStr) {
      if (esc) esc = false
      else if (ch === "\\") esc = true
      else if (ch === '"') inStr = false
    } else {
      if (ch === '"') inStr = true
      else if (ch === "{") depth++
      else if (ch === "}") {
        depth--
        if (depth === 0) return JSON.parse(html.slice(start, i + 1))
      }
    }
  }
  return null
}

function fromJob(job: any): JobResult {
  const location = Array.isArray(job.locations) ? job.locations.join("; ") : [job.location?.city, job.location?.subregion, job.location?.countryName].filter(Boolean).join(", ")
  const loc = splitLocation(location || null)
  return {
    id: job.id ?? job.url,
    title: job.title ?? "(untitled)",
    company: job.company?.title ?? null,
    location: location || null,
    city: job.location?.city || loc.city,
    province: job.location?.subregion || loc.province,
    country: job.location?.countryName || loc.country,
    remote: job.workplace ?? null,
    date: job.created ?? null,
    closingDate: null,
    employmentType: job.employmentType || null,
    salary: clean(job.benefitsSection?.match(/Salary[^<]*/i)?.[0] ?? null),
    url: job.url,
    applyUrl: job.linkoutUrl ?? job.url,
    portal: PORTAL,
    sourceId: job.id ?? job.url,
  }
}

async function runSearch(flags: Flags): Promise<number> {
  const query = typeof flags.query === "string" ? flags.query : ""
  if (!query) return writeError("search requires --query/-q", "NO_QUERY")
  const page = flags.page ? Math.max(1, parseInt(flags.page as string, 10)) : 1
  const html = await fetchText(searchUrl(query, typeof flags.location === "string" ? flags.location : undefined, page))
  const data = extractJsonAfter(html, '"api/v1/jobs":{"status":200,"data":') as { jobs?: unknown[] } | null
  const results = (data?.jobs ?? []).map((j) => fromJob(j)).slice(0, flags.limit ? parseInt(flags.limit as string, 10) : undefined)
  return output(results, page, String(flags.format || "json"))
}

async function runDetail(idOrUrl: string, flags: Flags): Promise<number> {
  const url = idOrUrl.startsWith("http") ? idOrUrl : `${BASE}/view/${idOrUrl}`
  const html = await fetchText(url)
  const job = extractJsonAfter(html, '"data":') as any
  const ld = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/i)?.[1]
  const parsed = job?.title ? job : ld ? JSON.parse(ld) : null
  if (!parsed) return writeError("Could not parse Workable job detail", "PARSE")
  const base = fromJob({ ...parsed, company: parsed.company ?? { title: parsed.hiringOrganization?.name }, url: parsed.url ?? url, created: parsed.datePosted, locations: parsed.jobLocation?.address ? [[parsed.jobLocation.address.addressLocality, parsed.jobLocation.address.addressRegion, parsed.jobLocation.address.addressCountry].filter(Boolean).join(", ")] : undefined })
  return outputDetail({ ...base, description: stripTags([parsed.description, parsed.requirementsSection, parsed.benefitsSection].filter(Boolean).join("\n\n")) }, String(flags.format || "json"))
}

const HELP = `workable-search — search Canadian jobs

USAGE
  bun run src/cli.ts search -q "mechanical engineer" -l "Vancouver, BC" [--limit 5] [--format json|table|plain]
  bun run src/cli.ts detail <id|url> [--format json|plain]

FLAGS
  --query, -q <text>       Keywords or title. Required for search.
  --location, -l <text>    Canadian location such as Vancouver, Toronto, Ontario, Canada, or Remote Canada.
  --jobage <days>          Accepted for contract compatibility; used only where the portal supports it.
  --page <n>               1-indexed page where supported.
  --limit, -n <n>          Client-side result cap.
  --format <fmt>           json (default), table, or plain.
`

async function main(): Promise<number> {
  const flags = parseFlags(process.argv.slice(2))
  const cmd = flags._[0]
  if (!cmd || flags.help || flags.h) {
    process.stdout.write(HELP)
    return cmd ? 0 : 1
  }
  try {
    if (cmd === "search") return await runSearch(flags)
    if (cmd === "detail") {
      const id = flags._[1]
      if (!id) return writeError("detail requires an <id|url>", "NO_ID")
      return await runDetail(id, flags)
    }
    return writeError(`Unknown command "${cmd}"`, "BAD_CMD")
  } catch (err) {
    return writeError(err instanceof Error ? err.message : String(err), "FETCH")
  }
}

main().then((code) => process.exit(code))
