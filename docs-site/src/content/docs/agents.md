---
title: Agent Guide
description: Routing rules and safety boundaries for LLM agents using Finance CLI.
---

Use this page when an agent needs to decide which command to call. Use [`tools.json`](/FinanceCLI/tools.json) for exact parameter schemas, output schemas, side-effect labels, and command-specific routing notes.

## Read Order

1. [`llms.txt`](/FinanceCLI/llms.txt) for the compact entry point.
2. [`tools.json`](/FinanceCLI/tools.json) for command schemas and side effects.
3. The relevant namespace page for examples and result shape.
4. [`trust`](/FinanceCLI/trust/) before summarizing evidence.

## Routing Rules

| User asks for | Prefer | Why |
| --- | --- | --- |
| Latest filings or a filing URL/accession | `filings.recent` | Finds SEC filing candidates and preserves accession/source metadata. |
| XBRL financial statement rows | `filings.statement` | Returns structured income, balance, or cashflow rows. |
| A known SEC report table | `filings.reports`, then `filings.report` | Discovers report names before reading rows. |
| Narrative 10-K sections | `filings.sections`, then `filings.read` | Uses canonical section keys such as business, risk factors, MD&A, and segments. |
| Phrase or table discovery inside a filing/document | `document.scan` | Returns match IDs and character offsets for follow-up reads. |
| More context around a scan hit | `document.window` | Reads a bounded window by offset or match ID. |
| Scanned/image-heavy PDFs | `document.ocr` | OCR fallback after native text extraction is not enough. |
| Explicit finance math | `formula.*` | Deterministic calculators with inputs and method. |
| DCF, NPV, IRR, WACC, scenario math | `valuation.*` | Deterministic valuation helpers from explicit assumptions. |
| Current quote, bars, market status, broad context | `market.*` | Provider-attributed market data and summaries. |
| Sector, industry, or Yahoo screen discovery | `sector.*`, `industry.*`, `screen.*` | Discovers supported keys and runs predefined market views. |
| Earnings calendar fields | `calendar.*` | Company calendar and earnings-date rows. |
| News/event context | `news.*`, `price.context` | Source-attributed event windows and dated context. |
| Transcripts and KPI evidence | `transcripts.*`, `kpi.*` | Preserves transcript URLs, quarters, snippets, and metric labels. |
| Reproducible strategy check | `backtest.*` | Uses explicit symbols, dates, strategy names, and parameters. |
| Provider setup/debugging | `sources.*` | Lists capabilities and probes configured providers. |

## Calculator Boundaries

- Use `formula.*` only when all numeric inputs are explicit in the user prompt or extracted from cited command output.
- Use `valuation.*` only for deterministic math. Do not describe valuation output as investment advice.
- If an input is missing, ask for it or run the appropriate extraction command first.

## Evidence Rules

- Cite `accession`, `url`, `report_name`, `section`, `page`, `start_char`, `end_char`, `match_id`, `source`, `provider`, and `timestamp` when available.
- Treat Yahoo, FMP, SEC, GDELT, transcripts, and company IR as source-specific records, not ground truth.
- Never claim live market data without source/provider and date/timestamp fields when available.
- Preserve `warnings`; they are part of the result.

## Failure Handling

- If `ok=false`, surface `error` directly and do not fabricate replacement data.
- If `ok=true` with empty arrays, report that no matching records were returned by that source.
- If `ok=true` with warnings, summarize the usable data and keep the warnings attached.
- If a command needs a provider key or dependency, let the command fail clearly and show the error.
