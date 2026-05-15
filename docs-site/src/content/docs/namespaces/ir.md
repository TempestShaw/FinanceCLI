---
title: ir
description: Find and read investor-relations presentations and filing-hosted documents.
---

# finance ir

The `ir.*` commands find investor-relations presentation links and read presentation or filing document text. Use this namespace when company materials outside structured filings are useful for research.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance ir.presentations

Discover IR and investor day presentations from SEC 8-K Exhibit 99 filings.

### What it does

`finance ir.presentations` discovers IR and investor day presentations from SEC 8-K Exhibit 99 filings. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `presentations`, `count`, `source`, `sources_used`, `notes`, `warnings`.

### When to use it

Use this command when you need to find investor presentations, investor-day decks, or earnings slide decks before extracting text from one candidate.

Behavior details: Scans recent 8-K filings for Exhibit 99 files with presentation or slides keywords. source=auto uses SEC first, then company IR fallback when SEC finds no candidates. source=all combines SEC and company IR candidates. Press releases and earnings releases are filtered unless a distinct deck/slides signal is present. confidence: high = strong presentation signal, medium = weaker or conflicting signal. kind: investor_day | earnings_presentation | ir_presentation | exhibit_99. Use ir.read url=URL to extract text from a candidate.

### Usage

```bash
finance ir.presentations SYMBOL [limit=20 source=auto|sec|company_ir|all] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `source` | No | None | `auto`, `sec`, `company_ir`, `all` | Provider/source key accepted by this command. |
| `limit` | No | `20` | Integer | Maximum number of records returned. |

### Basic usage

```bash
finance ir.presentations IOT --output json
```

### Example output

This output was generated with `finance ir.presentations IOT --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "presentations": [
      {
        "title": "Investor Presentation of Q4 2026, PDF file, (opens in new window)",
        "date": "2026",
        "kind": "earnings_presentation",
        "source": "company_ir",
        "url": "https://s29.q4cdn.com/853855404/files/doc_financials/2026/q4/Q4-FY26-Investor-Presentation-3.pdf",
        "page_url": "https://investors.samsara.com/",
        "page_title": "Samsara Inc. - Investor Relations",
        "company_name": "Samsara Inc.",
        "symbol": "IOT",
        "confidence": "high",
        "why_matched": "IR page link fuzzy-matches 'investor presentation'",
        "warnings": [
          "document is hosted on an external CDN linked from the IR page"
        ]
      }
    ],
    "count": 1,
    "source": "auto",
    "sources_used": [
      "sec_edgar",
      "company_ir"
    ],
    "notes": [
      "SEC candidates are scored from Exhibit 99 description and filename keywords.",
      "Company IR fallback is conservative and only crawls company/IR domains.",
      "Press releases and earnings releases are filtered unless a distinct deck/slides signal is present.",
      "Confidence 'high' = strong presentation signal; 'medium' = weaker or conflicting signal.",
      "kind: investor_day | earnings_presentation | ir_presentation | exhibit_99"
    ],
    "warnings": []
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.notes` | array | Additional notes that affect interpretation. |
| `data.notes[]` | string | Additional notes that affect interpretation. |
| `data.presentations` | array | Investor-relations presentation records. |
| `data.presentations[]` | object | Investor-relations presentation records. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.sources_used` | array | Source families used to build the result. |
| `data.sources_used[]` | string | Source families used to build the result. |
| `data.symbol` | string | Ticker symbol used by the command. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |
| `data.presentations[].company_name` | string | Company name returned by the provider. |
| `data.presentations[].confidence` | string | Match confidence for the presentation candidate. |
| `data.presentations[].date` | string | Presentation or filing date when available. |
| `data.presentations[].kind` | string | Presentation or document kind. |
| `data.presentations[].page_title` | string | Title of the linked page. |
| `data.presentations[].page_url` | string | Source page URL. |
| `data.presentations[].source` | string | Provider or source identifier for the returned data. |
| `data.presentations[].symbol` | string | Company ticker associated with the presentation. |
| `data.presentations[].title` | string | Presentation title or link text. |
| `data.presentations[].url` | string | Source URL. |
| `data.presentations[].warnings` | array | Non-fatal warnings returned by the command. |
| `data.presentations[].warnings[]` | string | Non-fatal warnings returned by the command. |
| `data.presentations[].why_matched` | string | Reason a record matched the requested query. |

## finance ir.read

Extract text from an IR presentation exhibit URL.

### What it does

`finance ir.read` extracts text from an IR presentation exhibit URL. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `url`, `text`, `char_count`, `returned_chars`, `truncated`, `format`, `pages`, `warnings`.

### When to use it

Use this command when you need to extract text from a presentation URL returned by `finance ir.presentations` or from a filing-hosted document URL.

Behavior details: HTML exhibits/pages are fetched and parsed to plain text. PDF extraction uses pypdf and returns page-level text when possible. ocr=auto or ocr=force uses the default PaddleOCR/PP-StructureV3 stack. Pass the url from ir.presentations output.

### Usage

```bash
finance ir.read url=URL [max_chars=12000 ocr=off|auto|force] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `url` | Yes | None | URL | Document URL to fetch and read. |
| `max_chars` | No | `12000` | Integer | Maximum text characters returned. |
| `ocr` | No | None | `off`, `auto`, `force` | OCR mode for PDFs or image-heavy documents. Use `off` for text-native documents, `auto` to fallback when text extraction is weak, and `force` to run OCR directly. |

### Basic usage

```bash
finance ir.read url=https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/aapl-20260328.htm ocr=off max_chars=800 --output json
```

### Example output

This output was generated with `finance ir.read url=https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/aapl-20260328.htm ocr=off max_chars=800 --output json`.

```json
{
  "ok": true,
  "data": {
    "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/aapl-20260328.htm",
    "text": "aapl-20260328\nfalse\n2026\nQ2\n0000320193\n--09-26\nP1Y\nP1Y\nP1Y\nP1Y\nhttp://fasb.org/us-gaap/2025#LongTermDebtCurrent http://fasb.org/us-gaap/2025#LongTermDebtNoncurrent\nhttp://fasb.org/us-gaap/2025#LongTermDebtCurrent http://fasb.org/us-gaap/2025#LongTermDebtNoncurrent\nP329D\nxbrli:shares\niso4217:USD\niso4217:USD\nxbrli:shares\nxbrli:pure\naapl:Customer\naapl:Vendor\n0000320193\n2025-09-28\n2026-03-28\n0000320193\nus-gaap:CommonStockMember\n2025-09-28\n2026-03-28\n0000320193\naapl:A1.625NotesDue2026Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A2.000NotesDue2027Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A1.375NotesDue2029Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A3.050NotesDue2029Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A0.500Notesdue2031Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A3.600NotesDue2042M",
    "char_count": 98063,
    "returned_chars": 800,
    "truncated": true,
    "format": "html",
    "pages": [
      {
        "page": 1,
        "text": "aapl-20260328\nfalse\n2026\nQ2\n0000320193\n--09-26\nP1Y\nP1Y\nP1Y\nP1Y\nhttp://fasb.org/us-gaap/2025#LongTermDebtCurrent http://fasb.org/us-gaap/2025#LongTermDebtNoncurrent\nhttp://fasb.org/us-gaap/2025#LongTermDebtCurrent http://fasb.org/us-gaap/2025#LongTermDebtNoncurrent\nP329D\nxbrli:shares\niso4217:USD\niso4217:USD\nxbrli:shares\nxbrli:pure\naapl:Customer\naapl:Vendor\n0000320193\n2025-09-28\n2026-03-28\n0000320193\nus-gaap:CommonStockMember\n2025-09-28\n2026-03-28\n0000320193\naapl:A1.625NotesDue2026Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A2.000NotesDue2027Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A1.375NotesDue2029Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A3.050NotesDue2029Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A0.500Notesdue2031Member\n2025-09-28\n2026-03-28\n0000320193\naapl:A3.600NotesDue2042M",
        "char_count": 98063,
        "returned_chars": 800,
        "truncated": true
      }
    ],
    "warnings": []
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.char_count` | integer | Total extracted character count before truncation. |
| `data.format` | string | Document format used by the reader. |
| `data.pages` | array | Page metadata or page count. |
| `data.pages[]` | object | Page metadata or page count. |
| `data.returned_chars` | integer | Characters included in this response. |
| `data.text` | string | Extracted document text after truncation. |
| `data.truncated` | boolean | Whether the command truncated the result. |
| `data.url` | string | Source URL. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |
| `data.pages[].char_count` | integer | Total extracted character count before truncation. |
| `data.pages[].page` | integer | Page number when available. |
| `data.pages[].returned_chars` | integer | Characters included in this response. |
| `data.pages[].text` | string | Extracted text for that page or page-like chunk. |
| `data.pages[].truncated` | boolean | Whether the command truncated the result. |
