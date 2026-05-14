---
title: fundamentals
description: Pull company financial statements.
---

Use `fundamentals.statement` for financial statement rows from the market-data provider.

## Parameters

### `fundamentals.statement`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Company ticker. |
| `statement` | No | `income` | `income`, `balance`, `cashflow` | Statement family. |
| `period` | No | `annual` | `annual`, `quarterly` | Reporting period frequency. |

## Income Statement

```bash
finance fundamentals.statement NVDA statement=income period=annual
```

A live run returned annual income-statement rows with dates as columns and line items as records. Example rows included normalized EBITDA and EBIT for NVIDIA's fiscal years.

```json
{
  "symbol": "NVDA",
  "statement": "income",
  "period": "annual",
  "rows": [
    {
      "label": "Normalized EBITDA",
      "values": {
        "2026-01-31": 144552000000
      }
    }
  ],
  "source": "yfinance"
}
```

Use `filings.statement` instead when you specifically need SEC/XBRL concepts, accessions, units, or filing-level provenance.
