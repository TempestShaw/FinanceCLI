# Routing

Use `finance --list` and `tools.json` as the source of truth for the installed command set. Prefer `tools.json` over prose when parameter names, defaults, enums, side effects, or output schemas matter.

| User asks for | Prefer | Notes |
| --- | --- | --- |
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
| News or dated event context | `news.*`, `price.context` | Do not infer causality from proximity alone. |
| Transcripts and KPI evidence | `transcripts.*`, `kpi.*` | Preserve URLs, quarters, snippets, and metric labels. |
| Investor presentation discovery | `ir.*` | Preserve company IR and SEC exhibit URLs. |
| Reproducible strategy checks | `backtest.*` | Use explicit symbols, dates, strategy names, and parameters. |
| Provider setup/debugging | `sources.*` | Use `sources.status` before assuming a provider is configured. |
