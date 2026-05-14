---
title: Data Sources And Keys
description: Environment variables and data-source areas used by Finance CLI.
---

Many commands work without a paid key. Some live data sources need environment variables:

| Variable | Enables |
| --- | --- |
| `FMP_API_KEY` | Financial Modeling Prep consensus estimates. |
| `ALPHAVANTAGE_API_KEY` or `ALPHA_VANTAGE_API_KEY` | Alpha Vantage market data fallback. |
| `ALPACA_API_KEY` and `ALPACA_API_SECRET` | Alpaca market-data fallback. |

SEC filing, document, formula, table, OCR, Yahoo market data, and local backtest commands are available from the default install.

## Common Source Areas

| Area | Commands |
| --- | --- |
| SEC filings | `filings.*`, `document.*`, `ir.*` |
| Market data | `market.*`, `price.*`, `valuation.*` |
| News context | `news.*`, `price.context` |
| Transcripts and KPIs | `transcripts.*`, `kpi.*` |
| Formulas and valuation | `formula.*`, `valuation.*`, `estimates.*` |
| Backtesting | `backtest.*` |
