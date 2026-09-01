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

function extractDeadline(html: string): string | null {
  const schema = html.match(/"validThrough"\s*:\s*"(\d{4}-\d{2}-\d{2})/i)
  if (schema) return schema[1]
  const label = html.match(/(?:application deadline|closing date|valid through)[\s\S]{0,100}?(\d{4}-\d{2}-\d{2})/i)
  return label?.[1] ?? null
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

const PORTAL = "EngineeringCareers.ca"
const BASE = "https://www.engineeringcareers.ca"

function searchUrl(query: string, location: string | undefined, page: number): string {
  const u = new URL(`${BASE}/jobs/`)
  u.searchParams.set("keywords", query)
  if (location) u.searchParams.set("location", location)
  if (page > 1) u.searchParams.set("Page", String(page))
  return u.toString()
}

function parseCards(html: string): JobResult[] {
  const chunks = html.split(/<li class="lister__item/).slice(1)
  return chunks.flatMap((chunk): JobResult[] => {
    const id = chunk.match(/id="item-(\d+)"/)?.[1]
    const href = decodeHtml(chunk.match(/href="\s*([^"]*\/job\/\d+\/[^"]+)"/i)?.[1] ?? "").replace(/\s+/g, "")
    const title = clean(chunk.match(/<h3 class="lister__header"[\s\S]*?<span>([\s\S]*?)<\/span>/i)?.[1])
    if (!id || !href || !title) return []
    const location = clean(chunk.match(/lister__meta-item--location"[^>]*>([\s\S]*?)<\/li>/i)?.[1])
    const salary = clean(chunk.match(/lister__meta-item--salary"[^>]*>([\s\S]*?)<\/li>/i)?.[1])
    const company = clean(chunk.match(/lister__meta-item--recruiter"[^>]*>([\s\S]*?)<\/li>/i)?.[1])
    const loc = splitLocation(location)
    const url = href.startsWith("http") ? href : `${BASE}${href}`
    return [{ id, title, company, location, city: loc.city, province: loc.province, country: loc.country, remote: /remote/i.test(location ?? "") ? "remote" : null, date: null, closingDate: null, employmentType: null, salary, url, applyUrl: url, portal: PORTAL, sourceId: id }]
  })
}

async function runSearch(flags: Flags): Promise<number> {
  const query = typeof flags.query === "string" ? flags.query : ""
  if (!query) return writeError("search requires --query/-q", "NO_QUERY")
  const page = flags.page ? Math.max(1, parseInt(flags.page as string, 10)) : 1
  const html = await fetchText(searchUrl(query, typeof flags.location === "string" ? flags.location : undefined, page))
  return output(parseCards(html).slice(0, flags.limit ? parseInt(flags.limit as string, 10) : undefined), page, String(flags.format || "json"))
}

async function runDetail(idOrUrl: string, flags: Flags): Promise<number> {
  const url = idOrUrl.startsWith("http") ? idOrUrl : `${BASE}/job/${idOrUrl}/`
  const html = await fetchText(url)
  const id = url.match(/\/job\/(\d+)/)?.[1] ?? idOrUrl
  const title = clean(html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1])?.replace(/\s+job with.*$/i, "") || "(untitled)"
  const company = clean(html.match(/job with ([^|<]+)\s*\|/i)?.[1])
  const location = clean(html.match(/jobLocation[\s\S]*?addressLocality"[^>]*content="([^"]+)"/i)?.[1])
  const loc = splitLocation(location)
  const description = clean(html.match(/class="job-description[\s\S]*?(?=<section|<aside|<\/main>)/i)?.[0] ?? html)
  return outputDetail({ id, title, company, location, city: loc.city, province: loc.province, country: loc.country, remote: null, date: null, closingDate: extractDeadline(html), employmentType: null, salary: null, url, applyUrl: url, portal: PORTAL, sourceId: id, description }, String(flags.format || "json"))
}

const HELP = `engineering-careers-search — search Canadian jobs

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
