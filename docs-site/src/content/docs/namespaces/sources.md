---
title: sources
description: Inspect provider inventory, configuration, and connectivity.
---

Use `sources.*` before a workflow when you want to know which providers are installed, which API keys are configured, and whether a live source can answer a minimal request.

## Parameters

### `sources.list`

No parameters. Lists known providers, packages, capabilities, and static notes without network calls.

### `sources.status`

No parameters. Checks installed packages and configured environment variables without network calls.

### `sources.test`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` / `source` | No | All sources when omitted | `yfinance`, `sec`, `gdelt`, `motley_fool`, `company_ir`, `fmp`, `pymupdf`, `camelot`, `paddleocr`, `alphavantage`, `alpaca`, `all` | Provider to probe. Positional `SOURCE` and `source=SOURCE` are equivalent. |
| `symbol` | No | `AAPL` | Public ticker | Symbol used by probes that need a ticker. |
| `timeout` | No | `30` | Seconds | Timeout for connectivity checks. |

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

A local status run reports installed document, table, OCR, SEC, transcript, and market-data packages, plus the configured state for keyed services.

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

## Configuration Model

`sources.status` is the setup view; `sources.test` is the connectivity view. Together they make it easy to confirm which namespaces are ready before running a larger workflow.
