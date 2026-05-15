---
title: calendar
description: Read company and market calendar events from configured public providers.
---

# finance calendar

The `calendar.*` commands return company-level calendar data and earnings-event lists. Use this namespace when a workflow needs upcoming or historical event dates before doing filings, estimates, or price-context work.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance calendar.company

Fetch company earnings/dividend calendar fields.

### What it does

`finance calendar.company` fetches company earnings/dividend calendar fields. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `calendar`, `source`.

### When to use it

Use this command when you need a compact company calendar object with upcoming earnings, dividend dates, and provider consensus ranges.

### Usage

```bash
finance calendar.company SYMBOL [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |

### Basic usage

```bash
finance calendar.company AAPL --output json
```

### Example output

This output was generated with `finance calendar.company AAPL --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "AAPL",
    "calendar": {
      "Dividend Date": "2026-05-13",
      "Ex-Dividend Date": "2026-05-10",
      "Earnings Date": [
        "2026-07-30"
      ],
      "Earnings High": 1.99,
      "Earnings Low": 1.83,
      "Earnings Average": 1.89077,
      "Revenue High": 112000000000,
      "Revenue Low": 107501000000,
      "Revenue Average": 108790845560
    },
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
| `data.calendar` | object | Company calendar object returned by the provider. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Ticker symbol used for the calendar request. |
| `data.calendar.Dividend Date` | string | Yahoo calendar dividend date field. |
| `data.calendar.Earnings Average` | number | Yahoo consensus earnings average field. |
| `data.calendar.Earnings Date` | array | Yahoo calendar earnings date field. |
| `data.calendar.Earnings Date[]` | string | Yahoo calendar earnings date field. |
| `data.calendar.Earnings High` | number | Yahoo consensus earnings high field. |
| `data.calendar.Earnings Low` | number | Yahoo consensus earnings low field. |
| `data.calendar.Ex-Dividend Date` | string | Yahoo calendar ex-dividend date field. |
| `data.calendar.Revenue Average` | integer | Yahoo consensus revenue average field. |
| `data.calendar.Revenue High` | integer | Yahoo consensus revenue high field. |
| `data.calendar.Revenue Low` | integer | Yahoo consensus revenue low field. |

## finance calendar.earnings

Fetch earnings-date rows for a company.

### What it does

`finance calendar.earnings` fetches earnings-date rows for a company. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `rows`, `count`, `source`.

### When to use it

Use this command when you need an earnings-date list with estimate, reported EPS, and surprise fields for recent or upcoming events.

### Usage

```bash
finance calendar.earnings SYMBOL [limit=12] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `limit` | No | `12` | Integer | Maximum number of records returned. |

### Basic usage

```bash
finance calendar.earnings AAPL limit=4 --output json
```

### Example output

This output was generated with `finance calendar.earnings AAPL limit=4 --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "AAPL",
    "rows": [
      {
        "earnings_date": "2026-07-30T16:00:00-04:00",
        "eps_estimate": 1.89,
        "reported_eps": null,
        "surprise": null
      },
      {
        "earnings_date": "2026-04-30T16:00:00-04:00",
        "eps_estimate": 1.94,
        "reported_eps": 2.01,
        "surprise": 3.46
      },
      {
        "earnings_date": "2026-01-29T16:00:00-05:00",
        "eps_estimate": 2.67,
        "reported_eps": 2.84,
        "surprise": 6.25
      },
      {
        "earnings_date": "2025-10-30T16:00:00-04:00",
        "eps_estimate": 1.77,
        "reported_eps": 1.85,
        "surprise": 4.52
      }
    ],
    "count": 4,
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
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.rows` | array | Structured rows returned by the command. |
| `data.rows[]` | object | Structured rows returned by the command. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Ticker symbol used for the earnings calendar request. |
| `data.rows[].earnings_date` | string | Earnings date returned by the provider. |
| `data.rows[].eps_estimate` | number | Consensus EPS estimate when available. |
| `data.rows[].reported_eps` | number or null | Reported EPS for the event when available. |
| `data.rows[].surprise` | number or null | EPS surprise value when available. |
