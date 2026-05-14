---
title: symbol
description: Company identity and public-company snapshot commands.
---

Use `symbol.*` when a workflow needs company identity before pulling filings, transcripts, fundamentals, or market data.

## Parameters

### `symbol.profile`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Company ticker to resolve through market metadata and SEC ticker metadata. |

### `symbol.snapshot`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Same implementation as `symbol.profile`; returns quote, company metadata, CIK, and source attribution. |

## Profile

```bash
finance symbol.profile NVDA
```

A live run returned NVIDIA's company profile with CIK `0001045810` and source attribution from both Yahoo Finance and SEC EDGAR.

```json
{
  "symbol": "NVDA",
  "cik": "0001045810",
  "sources": ["yfinance", "sec_edgar"]
}
```

## Snapshot

```bash
finance symbol.snapshot NVDA
```

Tested `symbol.snapshot` result:

```json
{
  "symbol": "NVDA",
  "company_name": "NVIDIA Corporation",
  "sector": "Technology",
  "industry": "Semiconductors",
  "last_price": 225.83,
  "market_cap": 5469721067520,
  "currency": "USD",
  "cik": "0001045810",
  "sources": ["yfinance", "sec_edgar"],
  "website": "https://www.nvidia.com"
}
```

`symbol.snapshot` is the broader one-command overview. Use it when an application needs a starter bundle before deciding which deeper namespace to call next. Price and market-cap fields are live values.
