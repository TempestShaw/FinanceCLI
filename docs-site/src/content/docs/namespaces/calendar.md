---
title: calendar
description: Company earnings and dividend calendar data from Yahoo Finance.
---

Use `calendar.*` when a workflow needs company event dates next to filings, market data, and valuation work.

## Commands

```bash
finance calendar.company AAPL
finance calendar.earnings AAPL limit=8
```

## Parameters

### `calendar.company`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Company ticker. |

### `calendar.earnings`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Company ticker. |
| `limit` | No | `12` | Integer | Maximum earnings-date rows. |

## Result Shape

```json
{
  "symbol": "AAPL",
  "rows": [
    {
      "earnings_date": "2026-07-30",
      "eps_estimate": 1.91,
      "reported_eps": null,
      "surprise": null
    }
  ],
  "count": 1,
  "source": "yfinance"
}
```
