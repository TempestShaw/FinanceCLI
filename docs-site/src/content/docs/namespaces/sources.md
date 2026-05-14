---
title: sources
description: Inspect provider inventory, configuration, and live connectivity.
---

Use `sources.*` before a workflow when you want to know which providers are installed, which API keys are configured, and whether a live source can answer a minimal request.

## Commands

```bash
finance sources.list
finance sources.status
finance sources.test yfinance symbol=AAPL
finance sources.test sec symbol=AAPL
```

Tested `sources.list` result shape:

```json
{
  "sources": [
    {
      "name": "yfinance",
      "capabilities": ["quote", "ohlcv", "fundamentals"],
      "package": "yfinance",
      "package_installed": true,
      "notes": "Public market data via yfinance."
    }
  ],
  "count": 11
}
```

`sources.list` is a static inventory. It does not make network calls.

`sources.status` checks installed Python packages and environment variables. It does not call the remote provider, so it is safe to run during setup.

## Example Result

A local status run reported installed document, table, OCR, SEC, transcript, and market-data packages, while `FMP_API_KEY` was not configured. Commands that need FMP, such as `estimates.consensus`, fail clearly until the key is set.

```json
{
  "ok": true,
  "data": {
    "count": 11,
    "summary": {
      "configured": 8,
      "missing_config": 3
    }
  }
}
```

Tested `sources.test yfinance` and `sources.test sec` result shape:

```json
{
  "symbol": "AAPL",
  "results": [
    {
      "name": "yfinance",
      "configured": true,
      "ok": true,
      "status": "ok",
      "latency_ms": 1225.17,
      "capabilities": ["quote", "ohlcv", "fundamentals"]
    }
  ],
  "summary": {
    "configured": 1,
    "ok": 1,
    "failed": 0,
    "missing_config": 0
  }
}
```

## Failure Model

Missing packages, keys, or provider configuration are reported as source status, not silently replaced with synthetic data. Provider test commands may still fail later because remote services can rate limit, change HTML, or be temporarily unavailable.
