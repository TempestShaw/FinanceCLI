---
title: symbol
description: Company identity and public-company snapshot commands.
---

Use `symbol.*` when a workflow needs company identity before pulling filings, transcripts, fundamentals, or market data.

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

`symbol.snapshot` is the broader one-command overview. Use it when an application needs a starter bundle before deciding which deeper namespace to call next.
