---
title: filings
description: Fetch SEC filings, canonical sections, XBRL statements, and filing report tables.
---

# finance filings

The `filings.*` commands read public SEC EDGAR filings through Finance CLI's SEC and edgartools integration. Use this namespace when a workflow needs filing discovery, canonical 10-K sections, structured XBRL statement rows, or filing summary reports.

For SEC access, set `FINANCE_SEC_USER_AGENT` in environments where SEC requires explicit caller identification.

## finance filings.recent

Fetch recent SEC filings for a public company.

### What it does

`finance filings.recent` resolves a ticker to SEC company metadata and returns recent filings filtered by form type. Each filing includes form, accession number, filing date, report date, acceptance timestamp, filing items, and the SEC filing URL.

### When to use it

Use this command first when the user provides a ticker but not a specific filing URL or accession number.

### Usage

```bash
finance filings.recent SYMBOL [forms=8-K,10-Q limit=20 classify=false]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker symbol | Company ticker to resolve through SEC metadata. |
| `forms` | No | Provider default | Comma-separated SEC form types, such as `10-K,10-Q,8-K` | Filters returned filings by form. |
| `limit` | No | `20` | Integer | Maximum filings returned. |
| `classify` | No | `false` | `true`, `false` | Adds event classification when supported. |

### Basic usage

```bash
finance filings.recent AAPL forms=10-K,10-Q limit=2 --output json
finance filings.recent NVDA forms=8-K limit=10 classify=true --output json
```

### Example output

This output was generated with `finance filings.recent AAPL forms=10-K,10-Q limit=2 --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "cik": "0000320193",
    "filings": [
      {
        "form": "10-Q",
        "accession_no": "0000320193-26-000013",
        "filed_at": "2026-05-01",
        "report_date": "2026-03-28",
        "acceptance_datetime": "2026-05-01T10:01:00.000Z",
        "items": [],
        "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/aapl-20260328.htm"
      },
      {
        "form": "10-Q",
        "accession_no": "0000320193-26-000006",
        "filed_at": "2026-01-30",
        "report_date": "2025-12-27",
        "acceptance_datetime": "2026-01-30T11:01:32.000Z",
        "items": [],
        "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019326000006/aapl-20251227.htm"
      }
    ],
    "count": 2,
    "source": "sec_edgar"
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
| `data.symbol` | string | Ticker passed to the command. |
| `data.company_name` | string | Company name from SEC metadata. |
| `data.cik` | string | SEC CIK, zero-padded when returned by this command. |
| `data.filings` | array | Filing rows after form and limit filtering. |
| `data.filings[].form` | string | SEC form type. |
| `data.filings[].accession_no` | string | Filing accession number. |
| `data.filings[].filed_at` | string | Filing date. |
| `data.filings[].report_date` | string | Period of report. |
| `data.filings[].acceptance_datetime` | string | SEC acceptance timestamp. |
| `data.filings[].items` | array | Form items when available, mainly for event filings. |
| `data.filings[].url` | string | SEC filing document URL. |
| `data.count` | integer | Number of filings returned. |
| `data.source` | string | Provider identifier. |

## finance filings.sections

List canonical and provider-discovered sections for a filing.

### What it does

`finance filings.sections` resolves a filing by ticker, accession number, or URL and returns supported Finance CLI section keys plus the sections discovered by edgartools. Supported sections include canonical keys such as `business`, `risk_factors`, `mda`, `financial_statements`, and `segments`.

### When to use it

Use this command before `finance filings.read` when you need to confirm which sections are available in the target filing.

### Usage

```bash
finance filings.sections [SYMBOL] [accession=ACCESSION|url=URL] [form=10-K]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Required unless `accession` or `url` is set | None | Public ticker symbol | Resolves the latest filing matching `form`. |
| `symbol` | Required unless positional `SYMBOL`, `accession`, or `url` is set | None | Public ticker symbol | Keyword ticker form. |
| `accession` | Required unless `SYMBOL`, `symbol`, or `url` is set | None | SEC accession number | Reads a specific filing. |
| `accession_no` | Required unless another filing source is set | None | SEC accession number | Alias for `accession`. |
| `url` | Required unless a symbol or accession is set | None | SEC filing URL | Reads a specific SEC filing URL. |
| `form` | No | `10-K` | SEC form type | Form used when resolving the latest filing by ticker. |

### Basic usage

```bash
finance filings.sections AAPL form=10-K --output json
finance filings.sections accession=0000320193-25-000079 --output json
```

### Example output

This output was generated with `finance filings.sections AAPL form=10-K --output json`.

```json
{
  "ok": true,
  "data": {
    "filing": {
      "company": "Apple Inc.",
      "cik": "320193",
      "form": "10-K",
      "filing_date": "2025-10-31",
      "period_of_report": "2025-09-27",
      "accession_no": "0000320193-25-000079",
      "filing_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm",
      "homepage_url": "https://www.sec.gov/Archives/edgar/data/320193/0000320193-25-000079-index.html",
      "text_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/0000320193-25-000079.txt"
    },
    "supported_sections": [
      {
        "key": "business",
        "title": "Business",
        "edgar_section": "part_i_item_1",
        "available": true,
        "char_count": 16051
      },
      {
        "key": "risk_factors",
        "title": "Risk Factors",
        "edgar_section": "part_i_item_1a",
        "available": true,
        "char_count": 68160
      },
      {
        "key": "mda",
        "title": "Management's Discussion and Analysis",
        "edgar_section": "part_ii_item_7",
        "available": true,
        "char_count": 18015
      },
      {
        "key": "financial_statements",
        "title": "Financial Statements and Supplementary Data",
        "edgar_section": "part_ii_item_8",
        "available": true,
        "char_count": 60863
      },
      {
        "key": "segments",
        "title": "Segments",
        "edgar_section": null,
        "available": true,
        "char_count": 720
      }
    ],
    "edgartools_sections": [
      "part_i_item_1",
      "part_ii_item_7a",
      "part_ii_item_8",
      "part_iv_item_8",
      "part_ii_item_9",
      "part_ii_item_9a",
      "part_ii_item_9b",
      "part_ii_item_9c",
      "part_iii_item_10",
      "part_iii_item_11",
      "part_iii_item_12",
      "part_iii_item_13",
      "part_iii_item_14",
      "part_iv_item_15",
      "part_iv_item_16",
      "part_iv_power_of_attorney_(included_on_the_signatures_page_of_this_annual_report_on_form_10-k).",
      "part_i_item_1a",
      "part_i_item_1b",
      "part_i_item_1c",
      "part_i_item_2",
      "part_i_item_3",
      "part_i_item_4",
      "part_ii_item_5",
      "part_ii_item_6",
      "part_ii_item_7"
    ],
    "source": "edgartools"
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
| `data.filing` | object | Filing metadata used for the section lookup. |
| `data.filing.company` | string | Company name. |
| `data.filing.cik` | string | SEC CIK. |
| `data.filing.form` | string | Filing form. |
| `data.filing.filing_date` | string | Filing date. |
| `data.filing.period_of_report` | string | Period of report. |
| `data.filing.accession_no` | string | SEC accession number. |
| `data.filing.filing_url` | string | Primary filing document URL. |
| `data.supported_sections` | array | Finance CLI canonical section keys and availability. |
| `data.supported_sections[].key` | string | Section key accepted by `filings.read section=...`. |
| `data.supported_sections[].available` | boolean | Whether edgartools found text for the section. |
| `data.supported_sections[].char_count` | integer | Extracted section character count. |
| `data.edgartools_sections` | array | Raw edgartools section identifiers discovered in the filing. |
| `data.source` | string | Provider identifier. |

## finance filings.read

Read a canonical filing section as bounded text.

### What it does

`finance filings.read` resolves a filing and extracts a section such as `business`, `risk_factors`, `mda`, or `segments`. It returns filing metadata, section metadata, bounded text, character counts, and truncation state.

### When to use it

Use this command when you need narrative 10-K text for quote extraction, document scanning, or downstream analysis. Use `filings.statement` or `filings.report` instead for structured financial statement rows.

### Usage

```bash
finance filings.read [SYMBOL] [accession=ACCESSION|url=URL] [form=10-K section=business|risk_factors|mda|segments max_chars=8000]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` / `symbol` | Required unless `accession` or `url` is set | None | Public ticker symbol | Resolves the latest filing matching `form`. |
| `accession` / `accession_no` | Required unless symbol or URL is set | None | SEC accession number | Reads a specific filing. |
| `url` | Required unless symbol or accession is set | None | SEC filing URL | Reads a specific filing URL. |
| `form` | No | `10-K` | SEC form type | Form used when resolving by ticker. |
| `section` | No | `business` | `business`, `risk_factors`, `mda`, `financial_statements`, `segments` | Canonical section key. |
| `max_chars` | No | `8000` | Integer | Maximum section text characters returned. |

### Basic usage

```bash
finance filings.read AAPL form=10-K section=business max_chars=300 --output json
finance filings.read accession=0000320193-25-000079 section=risk_factors max_chars=3000 --output json
```

### Example output

This output was generated with `finance filings.read AAPL form=10-K section=business max_chars=300 --output json`.

```json
{
  "ok": true,
  "data": {
    "filing": {
      "company": "Apple Inc.",
      "cik": "320193",
      "form": "10-K",
      "filing_date": "2025-10-31",
      "period_of_report": "2025-09-27",
      "accession_no": "0000320193-25-000079",
      "filing_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm",
      "homepage_url": "https://www.sec.gov/Archives/edgar/data/320193/0000320193-25-000079-index.html",
      "text_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/0000320193-25-000079.txt"
    },
    "section": {
      "key": "business",
      "title": "Business",
      "edgar_section": "part_i_item_1"
    },
    "text": "Item 1. Business\n\nCompany Background\n\nThe Company designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services. The Company’s fiscal year is the 52- or 53-week period that ends on the last Saturday of September.\n\nProdu",
    "char_count": 16051,
    "returned_chars": 300,
    "truncated": true,
    "source": "edgartools"
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
| `data.filing` | object | Filing metadata. |
| `data.section.key` | string | Section key that was read. |
| `data.section.title` | string | Human-readable section title. |
| `data.section.edgar_section` | string or null | Underlying edgartools/SEC section identifier. |
| `data.text` | string | Section text after `max_chars` truncation. |
| `data.char_count` | integer | Full section character count. |
| `data.returned_chars` | integer | Characters returned in `data.text`. |
| `data.truncated` | boolean | Whether section text was truncated. |
| `data.source` | string | Provider identifier. |

## finance filings.statement

Read structured XBRL statement rows from a filing.

### What it does

`finance filings.statement` returns rows from an XBRL statement family: income statement, balance sheet, or cash flow statement. Rows include concept names, labels, hierarchy metadata, balance type, parent links, and period-indexed values.

### When to use it

Use this command when the question asks for structured financial statement line items. Use `query` to narrow large statements before sending results to another tool or model.

### Usage

```bash
finance filings.statement [SYMBOL] [accession=ACCESSION|url=URL] [form=10-K statement=income|balance|cashflow query=TEXT include_abstract=false max_rows=0]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` / `symbol` | Required unless `accession` or `url` is set | None | Public ticker symbol | Resolves the latest filing matching `form`. |
| `accession` / `accession_no` | Required unless symbol or URL is set | None | SEC accession number | Reads a specific filing. |
| `url` | Required unless symbol or accession is set | None | SEC filing URL | Reads a specific filing URL. |
| `form` | No | `10-K` | SEC form type | Form used when resolving by ticker. |
| `statement` | No | `income` | `income`, `balance`, `cashflow` | Statement family. |
| `query` | No | None | Text | Filters rows by concept or label. |
| `include_abstract` | No | `false` | `true`, `false` | Includes abstract/header rows when true. |
| `max_rows` | No | `0` | Integer; `0` means unlimited | Maximum rows returned after filtering. |

### Basic usage

```bash
finance filings.statement COST statement=balance query="Common Stock" max_rows=3 --output json
finance filings.statement AAPL statement=income max_rows=20 --output json
```

### Example output

This output was generated with `finance filings.statement COST statement=balance query="Common Stock" max_rows=3 --output json`.

```json
{
  "ok": true,
  "data": {
    "filing": {
      "company": "COSTCO WHOLESALE CORP /NEW",
      "cik": "909832",
      "form": "10-K",
      "filing_date": "2025-10-08",
      "period_of_report": "2025-08-31",
      "accession_no": "0000909832-25-000101",
      "filing_url": "https://www.sec.gov/Archives/edgar/data/909832/000090983225000101/cost-20250831.htm",
      "homepage_url": "https://www.sec.gov/Archives/edgar/data/909832/0000909832-25-000101-index.html",
      "text_url": "https://www.sec.gov/Archives/edgar/data/909832/000090983225000101/0000909832-25-000101.txt"
    },
    "statement": "balance",
    "periods": [
      "2025-08-31",
      "2024-09-01",
      "2023-09-03"
    ],
    "rows": [
      {
        "concept": "us-gaap_CommonStockValue",
        "label": "Common Stock $.005 par value; 900,000,000 shares authorized; 443,237,000 and 442,126,000 shares issued and outstanding",
        "level": 4,
        "abstract": false,
        "balance": "credit",
        "parent": "us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterestAbstract",
        "calculation_parent": "us-gaap_StockholdersEquity",
        "values": {
          "2025-08-31": {
            "raw": 2000000,
            "reported": 2,
            "unit": "usd",
            "decimals": -6,
            "period_type": "instant",
            "preferred_sign": 1
          },
          "2024-09-01": {
            "raw": 2000000,
            "reported": 2,
            "unit": "usd",
            "decimals": -6,
            "period_type": "instant",
            "preferred_sign": 1
          }
        }
      }
    ],
    "count": 1,
    "truncated": false,
    "source": "edgartools"
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
| `data.filing` | object | Filing metadata. |
| `data.statement` | string | Statement family used for the query. |
| `data.periods` | array | Period labels available in the statement. |
| `data.rows` | array | Statement rows after filtering. |
| `data.rows[].concept` | string | XBRL concept name. |
| `data.rows[].label` | string | Reported row label. |
| `data.rows[].level` | integer | Presentation hierarchy level. |
| `data.rows[].abstract` | boolean | Whether the row is an abstract/header row. |
| `data.rows[].balance` | string or null | XBRL balance type when available. |
| `data.rows[].parent` | string or null | Presentation parent concept. |
| `data.rows[].calculation_parent` | string or null | Calculation parent concept. |
| `data.rows[].values` | object | Values keyed by period. |
| `data.rows[].values.*.raw` | number or null | Raw XBRL value. |
| `data.rows[].values.*.reported` | number or null | Value scaled by XBRL decimals. |
| `data.rows[].values.*.unit` | string or null | Unit such as `usd`. |
| `data.rows[].values.*.decimals` | integer or null | XBRL decimals metadata. |
| `data.count` | integer | Rows returned. |
| `data.truncated` | boolean | Whether rows were truncated by `max_rows`. |
| `data.source` | string | Provider identifier. |

## finance filings.reports

List filing summary reports available through edgartools.

### What it does

`finance filings.reports` returns the named reports attached to a filing, optionally filtered by query. Reports include note disclosures, detail tables, statement schedules, and other report fragments exposed by edgartools.

### When to use it

Use this command before `finance filings.report` when you need to discover the exact report short name to read.

### Usage

```bash
finance filings.reports [SYMBOL] [accession=ACCESSION|url=URL] [form=10-K query=TEXT]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` / `symbol` | Required unless `accession` or `url` is set | None | Public ticker symbol | Resolves the latest filing matching `form`. |
| `accession` / `accession_no` | Required unless symbol or URL is set | None | SEC accession number | Reads a specific filing. |
| `url` | Required unless symbol or accession is set | None | SEC filing URL | Reads a specific filing URL. |
| `form` | No | `10-K` | SEC form type | Form used when resolving by ticker. |
| `query` | No | None | Text | Filters report short names, long names, and categories. |

### Basic usage

```bash
finance filings.reports COST form=10-K query=lease --output json
finance filings.reports COST form=10-K --output json
```

### Example output

This output was generated with `finance filings.reports COST form=10-K query=lease --output json`.

```json
{
  "ok": true,
  "data": {
    "filing": {
      "company": "COSTCO WHOLESALE CORP /NEW",
      "cik": "909832",
      "form": "10-K",
      "filing_date": "2025-10-08",
      "period_of_report": "2025-08-31",
      "accession_no": "0000909832-25-000101",
      "filing_url": "https://www.sec.gov/Archives/edgar/data/909832/000090983225000101/cost-20250831.htm",
      "homepage_url": "https://www.sec.gov/Archives/edgar/data/909832/0000909832-25-000101-index.html",
      "text_url": "https://www.sec.gov/Archives/edgar/data/909832/000090983225000101/0000909832-25-000101.txt"
    },
    "reports": [
      {
        "short_name": "Leases",
        "long_name": "9952161 - Disclosure - Leases",
        "category": "Notes",
        "file_name": "R13.htm"
      },
      {
        "short_name": "Leases (Tables)",
        "long_name": "9955516 - Disclosure - Leases (Tables)",
        "category": "Tables",
        "file_name": "R28.htm"
      },
      {
        "short_name": "Accounting Policies - Leases (Details)",
        "long_name": "9955528 - Disclosure - Accounting Policies - Leases (Details)",
        "category": "Details",
        "file_name": "R38.htm"
      },
      {
        "short_name": "Leases, Supplemental Balance Sheet Information (Details)",
        "long_name": "9955543 - Disclosure - Leases, Supplemental Balance Sheet Information (Details)",
        "category": "Details",
        "file_name": "R52.htm"
      },
      {
        "short_name": "Leases, Components of Lease Expense (Details)",
        "long_name": "9955544 - Disclosure - Leases, Components of Lease Expense (Details)",
        "category": "Details",
        "file_name": "R53.htm"
      },
      {
        "short_name": "Leases, Supplemental Cash Flow Information (Details)",
        "long_name": "9955545 - Disclosure - Leases, Supplemental Cash Flow Information (Details)",
        "category": "Details",
        "file_name": "R54.htm"
      },
      {
        "short_name": "Leases, Future Minimum Payments (Details)",
        "long_name": "9955546 - Disclosure - Leases, Future Minimum Payments (Details)",
        "category": "Details",
        "file_name": "R55.htm"
      }
    ],
    "count": 7,
    "query": "lease",
    "source": "edgartools"
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
| `data.filing` | object | Filing metadata. |
| `data.reports` | array | Matching report descriptors. |
| `data.reports[].short_name` | string | Report name accepted by `filings.report name=...`. |
| `data.reports[].long_name` | string | Full provider report name. |
| `data.reports[].category` | string | Report category, such as `Notes`, `Tables`, or `Details`. |
| `data.reports[].file_name` | string | Filing report file name. |
| `data.count` | integer | Number of matching reports. |
| `data.query` | string or null | Query filter used. |
| `data.source` | string | Provider identifier. |

## finance filings.report

Read a named filing summary report and optional filtered rows.

### What it does

`finance filings.report` reads one report discovered by `filings.reports`. It returns report metadata, rendered text, structured rows when parseable, character counts, row counts, and truncation metadata.

### When to use it

Use this command when you need a specific filing note table or disclosure report, such as leases, debt, revenue recognition, or balance sheet details.

### Usage

```bash
finance filings.report [SYMBOL] [accession=ACCESSION|url=URL] name='Report Short Name' [form=10-K query=TEXT max_rows=25 max_chars=8000]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` / `symbol` | Required unless `accession` or `url` is set | None | Public ticker symbol | Resolves the latest filing matching `form`. |
| `accession` / `accession_no` | Required unless symbol or URL is set | None | SEC accession number | Reads a specific filing. |
| `url` | Required unless symbol or accession is set | None | SEC filing URL | Reads a specific filing URL. |
| `name` | Yes | None | Report short name | Report to read. Use `filings.reports` to discover this value. |
| `report` | Yes, unless `name` is set | None | Report short name | Alias for `name`. |
| `form` | No | `10-K` | SEC form type | Form used when resolving by ticker. |
| `query` | No | None | Text | Filters structured report rows. |
| `max_rows` | No | `25` | Integer; `0` means unlimited | Maximum structured rows returned. |
| `max_chars` | No | `8000` | Integer | Maximum report text characters returned. |

### Basic usage

```bash
finance filings.report COST name='Leases, Supplemental Balance Sheet Information (Details)' query='operating lease liabilities' max_rows=3 --output json
finance filings.report COST name='Consolidated Balance Sheets (Parenthetical)' --output json
```

### Example output

This output was generated with `finance filings.report COST name='Leases, Supplemental Balance Sheet Information (Details)' query='operating lease liabilities' max_rows=3 --output json`.

```json
{
  "ok": true,
  "data": {
    "filing": {
      "company": "COSTCO WHOLESALE CORP /NEW",
      "cik": "909832",
      "form": "10-K",
      "filing_date": "2025-10-08",
      "period_of_report": "2025-08-31",
      "accession_no": "0000909832-25-000101",
      "filing_url": "https://www.sec.gov/Archives/edgar/data/909832/000090983225000101/cost-20250831.htm",
      "homepage_url": "https://www.sec.gov/Archives/edgar/data/909832/0000909832-25-000101-index.html",
      "text_url": "https://www.sec.gov/Archives/edgar/data/909832/000090983225000101/0000909832-25-000101.txt"
    },
    "report": {
      "short_name": "Leases, Supplemental Balance Sheet Information (Details)",
      "long_name": "9955543 - Disclosure - Leases, Supplemental Balance Sheet Information (Details)",
      "category": "Details",
      "file_name": "R52.htm"
    },
    "text": "Leases, Supplemental Balance \n Sheet Information (Details) - \n USD ($) \n $ in Millions Aug. 31, 2025 Sep. 01, 2024 \n ────────────────────────────────────────────────────────────────────────────── \n Operating Lease and Finance \n Lease Right-of-Use-Assets \n [Abstract] \n Operating lease right-of-use $ 2,725 $ 2,617 \n assets \n Finance lease assets $ 1,488 $ 1,433 \n Finance lease assets Other long-term Other long-term \n assets assets \n OperatingLeaseandFinanceLeaseri $ 4,213 $ 4,050 \n ghtofuseassets \n Current Operating and Finance \n Lease Liabilities [Abstract] \n Current operating lease 208 179 \n liabilities \n Current finance lease $ 78 $ 147 \n liabilities \n Operating lease liabilities Other current Other current \n liabilities liabilities \n Finance lease liabilities Other current Other current \n liabilities liabilities \n Long-Term Operating and Finance \n Lease Liabilities [Abstract] \n Long-term operating lease $ 2,460 $ 2,375 \n liabilities \n Long-term finance lease $ 1,401 $ 1,351 \n liabilities \n Long-term finance lease Other long-term Other long-term \n liabilities liabilities liabilities \n OperatingLeaseandFinanceLeaseLi $ 4,147 $ 4,052 \n abilities \n Other Supplemental Balance \n Sheet Information [Abstract] \n Operating Lease, Weighted 20 years 19 years \n Average Remaining Lease Term \n Finance Lease, Weighted Average 25 years 23 years \n Remaining Lease Term \n Operating Lease, Weighted 3% 3% \n Average Discount Rate, Percent \n Finance Lease, Weighted Average 5% 5% \n Discount Rate, Percent",
    "rows": [
      {
        "table": "Leases, Supplemental Balance Sheet Information (Details) - USD ($) $ in Millions",
        "context": [
          "Current Operating and Finance Lease Liabilities [Abstract]"
        ],
        "label": "Current operating lease liabilities",
        "concept": "us-gaap_OperatingLeaseLiabilityCurrent",
        "abstract": false,
        "values": [
          {
            "column": "Aug. 31, 2025",
            "text": "208",
            "number": 208
          },
          {
            "column": "Sep. 01, 2024",
            "text": "179",
            "number": 179
          }
        ]
      },
      {
        "table": "Leases, Supplemental Balance Sheet Information (Details) - USD ($) $ in Millions",
        "context": [
          "Current Operating and Finance Lease Liabilities [Abstract]"
        ],
        "label": "Current finance lease liabilities",
        "concept": "us-gaap_FinanceLeaseLiabilityCurrent",
        "abstract": false,
        "values": [
          {
            "column": "Aug. 31, 2025",
            "text": "$ 78",
            "number": 78
          },
          {
            "column": "Sep. 01, 2024",
            "text": "$ 147",
            "number": 147
          }
        ]
      },
      {
        "table": "Leases, Supplemental Balance Sheet Information (Details) - USD ($) $ in Millions",
        "context": [
          "Current Operating and Finance Lease Liabilities [Abstract]"
        ],
        "label": "Operating lease liabilities",
        "concept": "us-gaap_OperatingLeaseLiabilityCurrentStatementOfFinancialPositionExtensibleList",
        "abstract": false,
        "values": [
          {
            "column": "Aug. 31, 2025",
            "text": "Other current liabilities",
            "number": null
          },
          {
            "column": "Sep. 01, 2024",
            "text": "Other current liabilities",
            "number": null
          }
        ]
      }
    ],
    "row_count": 3,
    "row_query": "operating lease liabilities",
    "rows_truncated": true,
    "char_count": 1506,
    "returned_chars": 1506,
    "truncated": false,
    "source": "edgartools"
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
| `data.filing` | object | Filing metadata. |
| `data.report` | object | Report descriptor selected by `name` or `report`. |
| `data.report.short_name` | string | Report short name. |
| `data.report.long_name` | string | Full provider report name. |
| `data.report.category` | string | Report category. |
| `data.report.file_name` | string | Filing report file name. |
| `data.text` | string | Rendered report text after `max_chars` truncation. |
| `data.rows` | array | Structured report rows when parseable. |
| `data.rows[].table` | string | Source table title. |
| `data.rows[].context` | array | Hierarchical row context. |
| `data.rows[].label` | string | Row label. |
| `data.rows[].concept` | string or null | XBRL concept when available. |
| `data.rows[].abstract` | boolean | Whether the row is abstract/header-like. |
| `data.rows[].values` | array | Column values for the row. |
| `data.rows[].values[].column` | string | Column header. |
| `data.rows[].values[].text` | string | Raw cell text. |
| `data.rows[].values[].number` | number or null | Parsed numeric value when available. |
| `data.row_count` | integer | Number of structured rows returned. |
| `data.row_query` | string or null | Row filter used. |
| `data.rows_truncated` | boolean | Whether rows were truncated by `max_rows`. |
| `data.char_count` | integer | Full report text character count. |
| `data.returned_chars` | integer | Characters returned in `data.text`. |
| `data.truncated` | boolean | Whether report text was truncated by `max_chars`. |
| `data.source` | string | Provider identifier. |
