---
title: filings
description: Fetch SEC filings, sections, statements, and reports.
---

Use `filings.*` for SEC EDGAR-backed workflows: finding filings, reading standard sections, and pulling XBRL statements or report tables.

## Recent Filings

```bash
finance filings.recent AAPL forms=10-K,10-Q limit=2
```

Example run shape:

```json
{
  "company": "Apple Inc.",
  "cik": "0000320193",
  "filings": [
    {
      "form": "10-Q",
      "filed_at": "2026-05-01",
      "url": "https://www.sec.gov/Archives/edgar/data/320193/..."
    }
  ]
}
```

## Filing Sections

```bash
finance filings.sections AAPL form=10-K
finance filings.read AAPL form=10-K section=business max_chars=1200
```

In a live Apple 10-K run, `filings.sections` found `business`, `risk_factors`, `mda`, `financial_statements`, and `segments`. `filings.read` returned section text with `char_count`, `returned_chars`, and `truncated` so callers can page or window the document deliberately.

## XBRL Statements And Reports

```bash
finance filings.statement COST statement=balance query="Common Stock" max_rows=5
finance filings.reports COST form=10-K query=lease
finance filings.report COST name="Leases, Supplemental Balance Sheet Information"
```

A Costco balance-sheet query returned the `us-gaap_CommonStockValue` row with 2025 and 2024 values. Use `query=` to narrow large statements before sending results to another step.

## When To Use document.*

Use `filings.statement` and `filings.report` when EDGAR exposes structured XBRL. Use `document.scan` or `document.window` when the target is narrative text, an exhibit, or a filing page that needs text search.
