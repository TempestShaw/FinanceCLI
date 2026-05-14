---
title: market
description: Quotes, OHLCV, market regime, and sector heat.
---

Use `market.*` for market data and broad market context. Live values are time-sensitive; treat examples as output shape, not fixed numbers.

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
