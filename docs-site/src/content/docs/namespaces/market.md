---
title: market
description: Quotes, OHLCV, market regime, and sector heat.
---

Use `market.*` for market data and broad market context. Live values are time-sensitive; treat examples as output shape, not fixed numbers.

## Parameters

### `market.quote`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Symbol to quote. |

### `market.ohlcv`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL[,SYMBOL...]` | Yes | None | One ticker or comma-separated tickers | Single-symbol calls return one OHLCV result; multi-symbol calls return batch output. |
| `timeframe` | No | `1d` | Provider-supported timeframe | Bar interval. |
| `start_date` | No | None | `YYYY-MM-DD` | Start date for historical bars. |
| `end_date` | No | None | `YYYY-MM-DD` | End date for historical bars. |
| `limit` | No | `200` | Integer | Maximum rows when date bounds are not enough. |
| `provider` | No | `auto` | `auto`, provider name | Provider selection. |
| `include_attempts` | No | `false` | Boolean | Includes provider-attempt diagnostics when `true`. |

### `market.status`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `MARKET` | No | `US` | Market code | Market universe for open/close status and index summary. |

### `market.regime`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `MARKET` | No | `US` | Market code | Market universe for regime signals. |
| `TIMEFRAME` | No | `swing` | Timeframe label | Regime horizon. |

### `market.sector_heat`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `MARKET` | No | `US` | Market code | Market universe. |
| `LOOKBACK_DAYS` | No | `20` | Integer | Ranking lookback window. |
| `GROUP_BY` | No | `sector` | Grouping label | Grouping used for heat rankings. |

## Quote And OHLCV

```bash
finance market.quote NVDA
finance market.ohlcv NVDA timeframe=1d limit=3
```

A live quote run returned Yahoo Finance data for NVIDIA with company name, sector, last price, market cap, source attribution, and a fallback reason explaining why Alpha Vantage was not used without an API key.

`market.ohlcv` returns dated rows:

```json
{
  "symbol": "NVDA",
  "timeframe": "1d",
  "rows": [
    { "date": "2026-05-13", "open": 220.0, "high": 226.0, "low": 219.0, "close": 225.83, "volume": 123456789 }
  ],
  "source": "yfinance"
}
```

## Regime And Sector Heat

```bash
finance market.regime US swing
finance market.sector_heat US 20 sector
```

`market.regime` summarizes risk signals such as broad equity and volatility behavior. A tested run returned `risk_on` with confidence and a list of supporting signals.

`market.sector_heat` ranks sector ETFs over a lookback window and returns leaders, laggards, and source attribution. Use it for market context, not as a standalone investment signal.

## Market Status

```bash
finance market.status US
```

`market.status` returns Yahoo's market state summary for the requested market. The result includes `market_state`, `status`, and `summary` fields, with source attribution.
