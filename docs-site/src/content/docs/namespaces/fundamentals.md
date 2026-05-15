---
title: fundamentals
description: Fetch structured financial statement rows from provider fundamentals data.
---

# finance fundamentals

The `fundamentals.*` commands return structured statement rows from provider fundamentals data. Use this namespace when a workflow needs income statement, balance sheet, or cash flow rows outside SEC filing table extraction.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance fundamentals.statement

Fetch income/balance/cashflow statement data.

### What it does

`finance fundamentals.statement` fetches income/balance/cashflow statement data. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `statement`, `period`, `rows`, `source`.

### When to use it

Use this command when you need provider financial statement rows quickly and do not need SEC accession-level citation. For filing-tied XBRL rows, use `finance filings.statement` instead.

### Usage

```bash
finance fundamentals.statement SYMBOL [statement=income|balance|cashflow period=annual|quarterly] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `period` | No | None | `annual`, `quarterly` | Reporting cadence requested from the provider. |
| `statement` | No | None | `income`, `balance`, `cashflow` | Financial statement family to return. |

### Basic usage

```bash
finance fundamentals.statement NVDA statement=income period=quarterly --output json
```

### Example output

This output was generated with `finance fundamentals.statement NVDA statement=income period=quarterly --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "NVDA",
    "statement": "income",
    "period": "quarterly",
    "rows": [
      {
        "field": "Tax Effect Of Unusual Items",
        "2026-01-31": 0,
        "2025-10-31": 0,
        "2025-07-31": 0,
        "2025-04-30": 0,
        "2025-01-31": 0
      },
      {
        "field": "Tax Rate For Calcs",
        "2026-01-31": 0.147585,
        "2025-10-31": 0.158846,
        "2025-07-31": 0.153304,
        "2025-04-30": 0.143,
        "2025-01-31": 0.123964
      },
      {
        "field": "Normalized EBITDA",
        "2026-01-31": 51283000000,
        "2025-10-31": 38748000000,
        "2025-07-31": 31937000000,
        "2025-04-30": 22584000000,
        "2025-01-31": 25821000000
      },
      {
        "field": "Net Income From Continuing Operation Net Minority Interest",
        "2026-01-31": 42960000000,
        "2025-10-31": 31910000000,
        "2025-07-31": 26422000000,
        "2025-04-30": 18775000000,
        "2025-01-31": 22091000000
      },
      {
        "field": "Reconciled Depreciation",
        "2026-01-31": 812000000,
        "2025-10-31": 751000000,
        "2025-07-31": 669000000,
        "2025-04-30": 611000000,
        "2025-01-31": 543000000
      },
      {
        "field": "Reconciled Cost Of Revenue",
        "2026-01-31": 17034000000,
        "2025-10-31": 15157000000,
        "2025-07-31": 12890000000,
        "2025-04-30": 17394000000,
        "2025-01-31": 10608000000
      },
      {
        "field": "EBITDA",
        "2026-01-31": 51283000000,
        "2025-10-31": 38748000000,
        "2025-07-31": 31937000000,
        "2025-04-30": 22584000000,
        "2025-01-31": 25821000000
      },
      {
        "field": "EBIT",
        "2026-01-31": 50471000000,
        "2025-10-31": 37997000000,
        "2025-07-31": 31268000000,
        "2025-04-30": 21973000000,
        "2025-01-31": 25278000000
      },
      {
        "field": "Net Interest Income",
        "2026-01-31": 495000000,
        "2025-10-31": 563000000,
        "2025-07-31": 530000000,
        "2025-04-30": 452000000,
        "2025-01-31": 450000000
      },
      {
        "field": "Interest Expense",
        "2026-01-31": 73000000,
        "2025-10-31": 61000000,
        "2025-07-31": 62000000,
        "2025-04-30": 63000000,
        "2025-01-31": 61000000
      },
      {
        "field": "Interest Income",
        "2026-01-31": 568000000,
        "2025-10-31": 624000000,
        "2025-07-31": 592000000,
        "2025-04-30": 515000000,
        "2025-01-31": 511000000
      },
      {
        "field": "Normalized Income",
        "2026-01-31": 42960000000,
        "2025-10-31": 31910000000,
        "2025-07-31": 26422000000,
        "2025-04-30": 18775000000,
        "2025-01-31": 22091000000
      },
      {
        "field": "Net Income From Continuing And Discontinued Operation",
        "2026-01-31": 42960000000,
        "2025-10-31": 31910000000,
        "2025-07-31": 26422000000,
        "2025-04-30": 18775000000,
        "2025-01-31": 22091000000
      },
      {
        "field": "Total Expenses",
        "2026-01-31": 23828000000,
        "2025-10-31": 20996000000,
        "2025-07-31": 18303000000,
        "2025-04-30": 22424000000,
        "2025-01-31": 15297000000
      },
      {
        "field": "Total Operating Income As Reported",
        "2026-01-31": 44299000000,
        "2025-10-31": 36010000000,
        "2025-07-31": 28440000000,
        "2025-04-30": 21638000000,
        "2025-01-31": 24034000000
      },
      {
        "field": "Diluted Average Shares",
        "2026-01-31": 24432000000,
        "2025-10-31": 24483000000,
        "2025-07-31": 24532000000,
        "2025-04-30": 24611000000,
        "2025-01-31": 24706000000
      },
      {
        "field": "Basic Average Shares",
        "2026-01-31": 24304000000,
        "2025-10-31": 24327000000,
        "2025-07-31": 24366000000,
        "2025-04-30": 24441000000,
        "2025-01-31": 24489000000
      },
      {
        "field": "Diluted EPS",
        "2026-01-31": 1.76,
        "2025-10-31": 1.3,
        "2025-07-31": 1.08,
        "2025-04-30": 0.76,
        "2025-01-31": 0.89
      },
      {
        "field": "Basic EPS",
        "2026-01-31": 1.77,
        "2025-10-31": 1.31,
        "2025-07-31": 1.08,
        "2025-04-30": 0.77,
        "2025-01-31": 0.9
      },
      {
        "field": "Diluted NI Availto Com Stockholders",
        "2026-01-31": 42960000000,
        "2025-10-31": 31910000000,
        "2025-07-31": 26422000000,
        "2025-04-30": 18775000000,
        "2025-01-31": 22091000000
      },
      {
        "field": "Net Income Common Stockholders",
        "2026-01-31": 42960000000,
        "2025-10-31": 31910000000,
        "2025-07-31": 26422000000,
        "2025-04-30": 18775000000,
        "2025-01-31": 22091000000
      },
      {
        "field": "Net Income",
        "2026-01-31": 42960000000,
        "2025-10-31": 31910000000,
        "2025-07-31": 26422000000,
        "2025-04-30": 18775000000,
        "2025-01-31": 22091000000
      },
      {
        "field": "Net Income Including Noncontrolling Interests",
        "2026-01-31": 42960000000,
        "2025-10-31": 31910000000,
        "2025-07-31": 26422000000,
        "2025-04-30": 18775000000,
        "2025-01-31": 22091000000
      },
      {
        "field": "Net Income Continuous Operations",
        "2026-01-31": 42960000000,
        "2025-10-31": 31910000000,
        "2025-07-31": 26422000000,
        "2025-04-30": 18775000000,
        "2025-01-31": 22091000000
      },
      {
        "field": "Tax Provision",
        "2026-01-31": 7438000000,
        "2025-10-31": 6026000000,
        "2025-07-31": 4784000000,
        "2025-04-30": 3135000000,
        "2025-01-31": 3126000000
      },
      {
        "field": "Pretax Income",
        "2026-01-31": 50398000000,
        "2025-10-31": 37936000000,
        "2025-07-31": 31206000000,
        "2025-04-30": 21910000000,
        "2025-01-31": 25217000000
      },
      {
        "field": "Other Income Expense",
        "2026-01-31": 5604000000,
        "2025-10-31": 1363000000,
        "2025-07-31": 2236000000,
        "2025-04-30": -180000000,
        "2025-01-31": 733000000
      },
      {
        "field": "Other Non Operating Income Expenses",
        "2026-01-31": 5604000000,
        "2025-10-31": 1363000000,
        "2025-07-31": 2236000000,
        "2025-04-30": -180000000,
        "2025-01-31": 733000000
      },
      {
        "field": "Net Non Operating Interest Income Expense",
        "2026-01-31": 495000000,
        "2025-10-31": 563000000,
        "2025-07-31": 530000000,
        "2025-04-30": 452000000,
        "2025-01-31": 450000000
      },
      {
        "field": "Interest Expense Non Operating",
        "2026-01-31": 73000000,
        "2025-10-31": 61000000,
        "2025-07-31": 62000000,
        "2025-04-30": 63000000,
        "2025-01-31": 61000000
      },
      {
        "field": "Interest Income Non Operating",
        "2026-01-31": 568000000,
        "2025-10-31": 624000000,
        "2025-07-31": 592000000,
        "2025-04-30": 515000000,
        "2025-01-31": 511000000
      },
      {
        "field": "Operating Income",
        "2026-01-31": 44299000000,
        "2025-10-31": 36010000000,
        "2025-07-31": 28440000000,
        "2025-04-30": 21638000000,
        "2025-01-31": 24034000000
      },
      {
        "field": "Operating Expense",
        "2026-01-31": 6794000000,
        "2025-10-31": 5839000000,
        "2025-07-31": 5413000000,
        "2025-04-30": 5030000000,
        "2025-01-31": 4689000000
      },
      {
        "field": "Research And Development",
        "2026-01-31": 5512000000,
        "2025-10-31": 4705000000,
        "2025-07-31": 4291000000,
        "2025-04-30": 3989000000,
        "2025-01-31": 3714000000
      },
      {
        "field": "Selling General And Administration",
        "2026-01-31": 1282000000,
        "2025-10-31": 1134000000,
        "2025-07-31": 1122000000,
        "2025-04-30": 1041000000,
        "2025-01-31": 975000000
      },
      {
        "field": "Gross Profit",
        "2026-01-31": 51093000000,
        "2025-10-31": 41849000000,
        "2025-07-31": 33853000000,
        "2025-04-30": 26668000000,
        "2025-01-31": 28723000000
      },
      {
        "field": "Cost Of Revenue",
        "2026-01-31": 17034000000,
        "2025-10-31": 15157000000,
        "2025-07-31": 12890000000,
        "2025-04-30": 17394000000,
        "2025-01-31": 10608000000
      },
      {
        "field": "Total Revenue",
        "2026-01-31": 68127000000,
        "2025-10-31": 57006000000,
        "2025-07-31": 46743000000,
        "2025-04-30": 44062000000,
        "2025-01-31": 39331000000
      },
      {
        "field": "Operating Revenue",
        "2026-01-31": 68127000000,
        "2025-10-31": 57006000000,
        "2025-07-31": 46743000000,
        "2025-04-30": 44062000000,
        "2025-01-31": 39331000000
      }
    ],
    "source": "yfinance"
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
| `data.period` | string | Reporting cadence returned by the provider. |
| `data.rows` | array | Structured rows returned by the command. |
| `data.rows[]` | object | Structured rows returned by the command. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.statement` | string | Statement family returned by the provider. |
| `data.symbol` | string | Ticker symbol used for the statement request. |
| `data.rows[].2025-01-31` | number | Value for the `2025-01-31` reporting period column. |
| `data.rows[].2025-04-30` | number | Value for the `2025-04-30` reporting period column. |
| `data.rows[].2025-07-31` | number | Value for the `2025-07-31` reporting period column. |
| `data.rows[].2025-10-31` | number | Value for the `2025-10-31` reporting period column. |
| `data.rows[].2026-01-31` | number | Value for the `2026-01-31` reporting period column. |
| `data.rows[].field` | string | Statement or provider field name. |
