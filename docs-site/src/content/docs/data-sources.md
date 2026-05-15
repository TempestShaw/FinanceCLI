---
title: Data Sources And Keys
description: Environment variables and data-source areas used by Finance CLI.
---

Finance CLI combines public providers, local parsers, and optional credentialed data sources. Use this page to understand which commands are available after a default install and which environment variables unlock provider-specific features.

## Check Local Readiness

Run these commands after installation:

```bash
finance sources.list --output json
finance sources.status --output json
```

`sources.list` shows known providers and capabilities. `sources.status` checks package imports and configured environment variables without running connectivity probes.

## Default Install

These areas work from the default package install, subject to normal provider availability:

| Area | Enables |
| --- | --- |
| SEC filings | Filing discovery, filing sections, XBRL statement rows, and filing reports through `filings.*`. |
| Documents | Native PDF/HTML text extraction, document scanning, windows, table extraction, and OCR through `document.*`. |
| Yahoo Finance | Quotes, OHLCV, fundamentals, calendars, sectors, industries, and screens through `market.*`, `fundamentals.*`, `calendar.*`, `sector.*`, `industry.*`, and `screen.*`. |
| News and transcripts | Public GDELT news search/analysis and public transcript pages through `news.*`, `transcripts.*`, and `kpi.*`. |
| Calculators | Deterministic finance formulas and valuation math through `formula.*` and `valuation.*`. |
| Backtests | Built-in VectorBT strategy runs, tuning, and factor payload helpers through `backtest.*`. |

## Optional Environment Variables

Some provider-backed commands use environment variables:

| Variable | Enables |
| --- | --- |
| `FMP_API_KEY` | Financial Modeling Prep consensus estimates. |
| `ALPHAVANTAGE_API_KEY` or `ALPHA_VANTAGE_API_KEY` | Alpha Vantage market data fallback. |
| `ALPACA_API_KEY` and `ALPACA_API_SECRET` | Alpaca market-data fallback. |
| `FINANCE_SEC_USER_AGENT` | Optional SEC request identity string for EDGAR access. |

Finance CLI reads these variables at runtime. It does not write API keys into project files or persistent config.

## Common Source Areas

| Area | Commands |
| --- | --- |
| SEC filings | `filings.*`, `document.*`, `ir.*` |
| Market data | `market.*`, `price.*`, `valuation.*` |
| News context | `news.*`, `price.context` |
| Transcripts and KPIs | `transcripts.*`, `kpi.*` |
| Formulas and valuation | `formula.*`, `valuation.*`, `estimates.*` |
| Backtesting | `backtest.*` |

## Provider Tests

Use `sources.test` when you want a lightweight validation query:

```bash
finance sources.test yfinance symbol=AAPL --output json
finance sources.test sec symbol=AAPL --output json
finance sources.test all symbol=MSFT timeout=60 --output json
```

The result includes provider-level `ok`, `configured`, `status`, latency, capabilities, and summary fields. For command-specific examples, use the namespace pages under Command Reference.
