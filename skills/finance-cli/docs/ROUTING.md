# Routing

Use `finance --list` and `tools.json` as the source of truth for the installed command set. Prefer `tools.json` over prose when parameter names, defaults, enums, side effects, or output schemas matter.

Use `--output json` for canonical command capture. Use compact record outputs only after selecting the fields the agent needs.

Most company workflows are symbol-based. Extract the ticker before running symbol commands; do not pass a full natural-language task as the `SYMBOL` argument. Use `research.plan SYMBOL` as a checklist after the ticker is known.

| User asks for | Prefer | Details |
| --- | --- | --- |
| Research workflow planning for a company | `research.plan SYMBOL` | Pass only the ticker as `SYMBOL`; keep the user question as your own task context. |
| Latest SEC filing, accession, filing URL | `filings.recent` | Use before section/table reads when the user only gives a ticker. |
| XBRL income, balance, or cashflow rows | `filings.statement` | Best for structured SEC statement rows. |
| A named SEC report table | `filings.reports`, then `filings.report` | Discover report names before reading rows. |
| Narrative 10-K/10-Q sections | `filings.sections`, then `filings.read` | Use canonical section keys when available. |
| Phrase or table discovery in PDF/HTML | `document.scan` | Returns match IDs and character offsets. |
| Context around a scan result | `document.window` | Use `match_id` or character offsets from `document.scan`. |
| Extract PDF tables | `document.tables` | Use when text windows are not enough for table structure. |
| Scanned/image-heavy PDFs | `document.ocr` | OCR fallback after native text extraction is insufficient. |
| Explicit finance math | `formula.*` | Use only when numeric inputs are explicit or cited. |
| DCF, NPV, IRR, WACC, scenario math | `valuation.*` | Deterministic math, not investment advice. |
| Quotes, bars, market status, broad market context | `market.*` | Preserve provider and timestamp/date fields. |
| Company calendar or earnings-date rows | `calendar.*` | Provider coverage can vary by symbol. |
| Sector, industry, or screen discovery | `sector.*`, `industry.*`, `screen.*` | Use for Yahoo-defined keys, groups, and screens. |
| News or dated event context | `price.context`, `filings.recent` | Do not infer causality from proximity alone. |
| Transcript evidence | `transcripts.*` | Preserve URLs, quarters, prepared remarks, and Q&A turns. |
| Investor presentation discovery | `ir.*` | Preserve company IR and SEC exhibit URLs. |
| Official company releases or investor events | `ir.releases`, `ir.events` | Pass `url=` for a known official feed or page when automatic discovery is incomplete. Feed publication time can differ from event time. |
| Macro data or historically known observations | `macro.search`, `macro.series` | Requires FRED_API_KEY. Use `as_of` for historical vintages; retain units and frequency. |
| Taiwan company monthly revenue or material announcements | `fundamentals.revenue`, `disclosures.recent` | TWSE-listed companies only, current snapshots. Revenue is thousands of TWD; do not infer full history. |
| Actual exchange issue breadth | `market.breadth NASDAQ` | Nasdaq-only A/D counts; preserve source dates, age and missing dates. |
| Short positions or daily short-sale activity | `short.interest`, `short.volume` | Settlement snapshots and off-exchange daily volume are different measures; observe FINRA usage terms. |
| Futures positions by trader category | `positioning.cot` | Preserve contract code, futures-only report family and position date; it is not a publication timestamp. |
| Energy inventories or state electricity retail sales/prices | `energy.inventory`, `energy.electricity` | Requires EIA_API_KEY. Preserve geography, frequency, periods and units. |
| Reproducible strategy checks | `backtest.*` | Use explicit symbols, dates, strategy names, and parameters. |
| Provider setup/debugging | `sources.*` | Use `sources.status` for local setup and `sources.test SOURCE symbol=SYMBOL` before relying on a live provider. |
