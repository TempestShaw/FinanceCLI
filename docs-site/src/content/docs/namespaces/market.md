---
title: market
description: Fetch quotes, bars, market status, regime summaries, and sector heat snapshots.
---

# finance market

The `market.*` commands return market data snapshots, historical OHLCV rows, market status, regime signals, and sector heat summaries. Use this namespace before price-sensitive analysis that needs provider timestamp and source attribution.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance market.ohlcv

Fetch normalized OHLCV records for one or more symbols.

### What it does

`finance market.ohlcv` fetches normalized OHLCV records for one or more symbols. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `timeframe`, `rows`, `count`, `source`.

### When to use it

Use this command when you need historical bars for a chart, backtest, event window, or price-reaction calculation.

Behavior details: Arguments use key=value syntax for script-friendly CLI calls.

### Usage

```bash
finance market.ohlcv SYMBOL[,SYMBOL...] [timeframe=1d start_date=YYYY-MM-DD end_date=YYYY-MM-DD limit=200 provider=auto include_attempts=false] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbols` | Yes | None | String | Ticker symbol or comma-separated ticker list, such as `AAPL,MSFT,NVDA`. |
| `end_date` | No | None | `YYYY-MM-DD` | Last bar date to request. |
| `include_attempts` | No | `false` | `true`, `false` | Include provider-attempt diagnostics. |
| `limit` | No | `200` | Integer | Maximum number of records returned. |
| `provider` | No | `auto` | String | Provider selection. Use `auto` unless you need to force a supported provider. |
| `start_date` | No | None | `YYYY-MM-DD` | First bar date to request. |
| `timeframe` | No | `1d` | String | Bar interval such as `1d`, where supported by the provider. |

### Basic usage

```bash
finance market.ohlcv NVDA timeframe=1d limit=5 --output json
```

### Example output

This output was generated with `finance market.ohlcv NVDA timeframe=1d limit=5 --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "NVDA",
    "timeframe": "1d",
    "rows": [
      {
        "symbol": "NVDA",
        "date": "2026-05-08 00:00:00-04:00",
        "open": 213.02999877929688,
        "high": 217.8000030517578,
        "low": 212.88999938964844,
        "close": 215.1999969482422,
        "volume": 136421400,
        "adjusted_close": 215.1999969482422,
        "source": "yfinance"
      },
      {
        "symbol": "NVDA",
        "date": "2026-05-11 00:00:00-04:00",
        "open": 214.0399932861328,
        "high": 222.3000030517578,
        "low": 213.88999938964844,
        "close": 219.44000244140625,
        "volume": 160685800,
        "adjusted_close": 219.44000244140625,
        "source": "yfinance"
      },
      {
        "symbol": "NVDA",
        "date": "2026-05-12 00:00:00-04:00",
        "open": 218.5500030517578,
        "high": 223.75,
        "low": 214.9199981689453,
        "close": 220.77999877929688,
        "volume": 159176600,
        "adjusted_close": 220.77999877929688,
        "source": "yfinance"
      },
      {
        "symbol": "NVDA",
        "date": "2026-05-13 00:00:00-04:00",
        "open": 224.92999267578125,
        "high": 227.83999633789062,
        "low": 221.57000732421875,
        "close": 225.8300018310547,
        "volume": 150405400,
        "adjusted_close": 225.8300018310547,
        "source": "yfinance"
      },
      {
        "symbol": "NVDA",
        "date": "2026-05-14 00:00:00-04:00",
        "open": 229.72999572753906,
        "high": 236.5399932861328,
        "low": 229.30999755859375,
        "close": 235.74000549316406,
        "volume": 175521705,
        "adjusted_close": 235.74000549316406,
        "source": "yfinance"
      }
    ],
    "count": 5,
    "source": "yfinance"
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.rows` | array | Structured rows returned by the command. |
| `data.rows[]` | object | Structured rows returned by the command. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Ticker symbol returned for the bar set. |
| `data.timeframe` | string | Bar interval used for the request. |
| `data.rows[].adjusted_close` | number | Split/dividend-adjusted close price. |
| `data.rows[].close` | number | OHLCV close price. |
| `data.rows[].date` | string | Bar timestamp returned by the provider. |
| `data.rows[].high` | number | OHLCV high price. |
| `data.rows[].low` | number | OHLCV low price. |
| `data.rows[].open` | number | OHLCV open price. |
| `data.rows[].source` | string | Provider or source identifier for the returned data. |
| `data.rows[].symbol` | string | Ticker symbol for the bar row. |
| `data.rows[].volume` | integer | Trading volume. |

## finance market.quote

Fetch quote via the best available provider.

### What it does

`finance market.quote` fetches quote via the best available provider. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `company_name`, `sector`, `industry`, `website`, `ir_website`, `last_price`, `market_cap`.

### When to use it

Use this command when you need a current quote plus compact company fundamentals such as market cap, enterprise value, revenue, cash, debt, and source information.

Behavior details: Uses Alpha Vantage when configured, with Yahoo fallback.

### Usage

```bash
finance market.quote SYMBOL [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |

### Basic usage

```bash
finance market.quote NVDA --output json
```

### Example output

This output was generated with `finance market.quote NVDA --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "NVDA",
    "company_name": "NVIDIA Corporation",
    "sector": "Technology",
    "industry": "Semiconductors",
    "website": "https://www.nvidia.com",
    "ir_website": "http://phx.corporate-ir.net/phoenix.zhtml?c=116466&p=irol-IRHome",
    "last_price": 235.74,
    "market_cap": 5709746405376,
    "enterprise_value": 5677459701760,
    "shares_outstanding": 24220525225,
    "total_revenue": 215938007040,
    "cash": 62556000256,
    "debt": 11411999744,
    "net_debt": -51144000512,
    "currency": "USD",
    "source": "yfinance",
    "fallback_reason": "Alpha Vantage API key is required. Set ALPHAVANTAGE_API_KEY."
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.cash` | integer | Cash or cash equivalents. |
| `data.company_name` | string | Company name returned by the provider. |
| `data.currency` | string | Trading or reporting currency. |
| `data.debt` | integer | Debt returned by the provider. |
| `data.enterprise_value` | integer | Enterprise value. |
| `data.fallback_reason` | string | Reason the command used a fallback provider. |
| `data.industry` | string | Company industry classification. |
| `data.ir_website` | string | Investor-relations website URL. |
| `data.last_price` | number | Latest provider price. |
| `data.market_cap` | integer | Market capitalization. |
| `data.net_debt` | integer | Debt minus cash. |
| `data.sector` | string | Company or market sector. |
| `data.shares_outstanding` | integer | Shares outstanding. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Ticker symbol returned for the quote. |
| `data.total_revenue` | integer | Revenue returned by the provider. |
| `data.website` | string | Company website URL. |

## finance market.regime

Show market regime context.

### What it does

`finance market.regime` shows market regime context. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `market`, `timeframe`, `regime`, `confidence`, `signals`, `meta`.

### When to use it

Use this command when you need a broad market risk-on/risk-off summary built from deterministic benchmark signals.

### Usage

```bash
finance market.regime [MARKET=US] [TIMEFRAME=swing] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `market` | No | `US` | String | Market code for the benchmark set. |
| `timeframe` | No | `swing` | String | Regime horizon label used by the command. |

### Basic usage

```bash
finance market.regime US swing --output json
```

### Example output

This output was generated with `finance market.regime US swing --output json`.

```json
{
  "ok": true,
  "data": {
    "market": "US",
    "timeframe": "swing",
    "regime": "risk_on",
    "confidence": 0.9,
    "signals": [
      {
        "name": "index_trend",
        "symbol": "SPY",
        "value": "above_200dma",
        "direction": "bullish",
        "last_close": 748.17,
        "sma_50": 688.8826,
        "sma_200": 675.5481,
        "return_pct": 9.02
      },
      {
        "name": "breadth",
        "value": "constructive",
        "direction": "bullish",
        "positive_benchmark_count": 3,
        "above_50dma_count": 3,
        "total_benchmarks": 3
      },
      {
        "name": "volatility",
        "symbol": "^VIX",
        "value": "contained",
        "direction": "neutral",
        "last_close": 17.26
      }
    ],
    "meta": {
      "source": "historical_market_data",
      "as_of": "2026-05-15T01:38:47.788597+00:00",
      "notes": "Deterministic regime from configured benchmark ETFs/indexes; not an investment conclusion."
    }
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.confidence` | number | Regime confidence score. |
| `data.market` | string | Market code used by the regime model. |
| `data.meta` | object | Provider metadata for the result. |
| `data.regime` | string | Regime label produced by the command. |
| `data.signals` | array | Market-regime signal objects. |
| `data.signals[]` | object | Market-regime signal objects. |
| `data.timeframe` | string | Regime horizon label used by the command. |
| `data.meta.as_of` | string | Timestamp or date when the provider generated the summary. |
| `data.meta.notes` | string | Additional notes that affect interpretation. |
| `data.meta.source` | string | Provider or source identifier for the returned data. |
| `data.signals[].above_50dma_count` | integer | Number of benchmarks trading above their 50-day moving average. |
| `data.signals[].direction` | string | Bullish, bearish, or neutral interpretation for the signal. |
| `data.signals[].last_close` | number | Most recent close in the returned price window. |
| `data.signals[].name` | string | Signal name, such as trend, breadth, or volatility. |
| `data.signals[].positive_benchmark_count` | integer | Number of benchmarks with positive return in the lookback window. |
| `data.signals[].return_pct` | number | Return percentage for the period. |
| `data.signals[].sma_200` | number | 200-day simple moving average. |
| `data.signals[].sma_50` | number | 50-day simple moving average. |
| `data.signals[].symbol` | string | Benchmark symbol used by the signal when applicable. |
| `data.signals[].total_benchmarks` | integer | Number of benchmark instruments evaluated. |
| `data.signals[].value` | string | Discrete signal value used to classify the regime. |

## finance market.sector_heat

Show sector heat rankings.

### What it does

`finance market.sector_heat` shows sector heat rankings. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `market`, `group_by`, `lookback_days`, `leaders`, `laggards`, `meta`.

### When to use it

Use this command when you need to rank sectors or market groups by recent lookback return.

### Usage

```bash
finance market.sector_heat [MARKET=US] [LOOKBACK_DAYS=20] [GROUP_BY=sector] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `group_by` | No | `sector` | String | Grouping dimension. The current command examples use `sector`. |
| `lookback_days` | No | `20` | Integer | Calendar lookback window used for heat ranking. |
| `market` | No | `US` | String | Market code for the configured sector ETF set. |

### Basic usage

```bash
finance market.sector_heat US 20 sector --output json
```

### Example output

This output was generated with `finance market.sector_heat US 20 sector --output json`.

```json
{
  "ok": true,
  "data": {
    "market": "US",
    "group_by": "sector",
    "lookback_days": 20,
    "leaders": [
      {
        "name": "Technology",
        "symbol": "XLK",
        "heat_score": 18.08,
        "return_pct": 18.08,
        "last_close": 179.5,
        "source": "historical_market_data"
      },
      {
        "name": "Consumer Staples",
        "symbol": "XLP",
        "heat_score": 4.36,
        "return_pct": 4.36,
        "last_close": 84.98,
        "source": "historical_market_data"
      },
      {
        "name": "Energy",
        "symbol": "XLE",
        "heat_score": 2.63,
        "return_pct": 2.63,
        "last_close": 58.07,
        "source": "historical_market_data"
      },
      {
        "name": "Industrials",
        "symbol": "XLI",
        "heat_score": 2.45,
        "return_pct": 2.45,
        "last_close": 174.51,
        "source": "historical_market_data"
      },
      {
        "name": "Consumer Discretionary",
        "symbol": "XLY",
        "heat_score": 0.88,
        "return_pct": 0.88,
        "last_close": 118.67,
        "source": "historical_market_data"
      }
    ],
    "laggards": [
      {
        "name": "Utilities",
        "symbol": "XLU",
        "heat_score": -3.13,
        "return_pct": -3.13,
        "last_close": 44.9,
        "source": "historical_market_data"
      },
      {
        "name": "Communication Services",
        "symbol": "XLC",
        "heat_score": -1.45,
        "return_pct": -1.45,
        "last_close": 117.11,
        "source": "historical_market_data"
      },
      {
        "name": "Financials",
        "symbol": "XLF",
        "heat_score": -1.42,
        "return_pct": -1.42,
        "last_close": 51.29,
        "source": "historical_market_data"
      },
      {
        "name": "Materials",
        "symbol": "XLB",
        "heat_score": -0.15,
        "return_pct": -0.15,
        "last_close": 51.67,
        "source": "historical_market_data"
      },
      {
        "name": "Health Care",
        "symbol": "XLV",
        "heat_score": 0.01,
        "return_pct": 0.01,
        "last_close": 146.63,
        "source": "historical_market_data"
      }
    ],
    "meta": {
      "source": "historical_market_data",
      "as_of": "2026-05-15T01:38:50.922109+00:00",
      "notes": "Heat score is lookback return percentage for configured public sector ETFs."
    }
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.group_by` | string | Grouping dimension used by the heat command. |
| `data.laggards` | array | Lowest-ranked sector, market, or heat records. |
| `data.laggards[]` | object | Lowest-ranked sector, market, or heat records. |
| `data.leaders` | array | Top-ranked sector, market, or heat records. |
| `data.leaders[]` | object | Top-ranked sector, market, or heat records. |
| `data.lookback_days` | integer | Lookback converted to calendar days. |
| `data.market` | string | Market code used by the heat calculation. |
| `data.meta` | object | Provider metadata for the result. |
| `data.laggards[].heat_score` | number | Composite sector heat score. |
| `data.laggards[].last_close` | number | Most recent close in the returned price window. |
| `data.laggards[].name` | string | Sector or group name for the laggard row. |
| `data.laggards[].return_pct` | number | Return percentage for the period. |
| `data.laggards[].source` | string | Provider or source identifier for the returned data. |
| `data.laggards[].symbol` | string | ETF or benchmark symbol for the laggard row. |
| `data.leaders[].heat_score` | number | Composite sector heat score. |
| `data.leaders[].last_close` | number | Most recent close in the returned price window. |
| `data.leaders[].name` | string | Sector or group name for the leader row. |
| `data.leaders[].return_pct` | number | Return percentage for the period. |
| `data.leaders[].source` | string | Provider or source identifier for the returned data. |
| `data.leaders[].symbol` | string | ETF or benchmark symbol for the leader row. |
| `data.meta.as_of` | string | Timestamp or date when the provider generated the summary. |
| `data.meta.notes` | string | Additional notes that affect interpretation. |
| `data.meta.source` | string | Provider or source identifier for the returned data. |

## finance market.status

Show Yahoo market open/close status and index summary.

### What it does

`finance market.status` shows Yahoo market open/close status and index summary. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `market`, `market_state`, `status`, `summary`, `source`.

### When to use it

Use to check current market open/close state and major-index summary.

### Usage

```bash
finance market.status [MARKET=US] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `market` | No | `US` | String | Market code. |

### Basic usage

```bash
finance market.status US --output json
```

### Example output

This output was generated with `finance market.status US --output json`.

```json
{
  "ok": true,
  "data": {
    "market": "US",
    "market_state": "REGULAR",
    "status": {
      "id": "us",
      "name": "U.S. markets",
      "status": "closed",
      "yfit_market_id": "us_market",
      "close": "2026-05-14T20:00:00+00:00",
      "message": "U.S. markets closed",
      "open": "2026-05-14T13:30:00+00:00",
      "yfit_market_status": "YFT_MARKET_CLOSED",
      "timezone": {
        "dst": "true",
        "gmtoffset": "-14400",
        "short": "EDT",
        "$text": "America/New_York"
      },
      "tz": "EDT"
    },
    "summary": [
      {
        "id": "CME",
        "symbol": "RTY=F",
        "name": "Russell 2000 Futures",
        "price": 2850.4,
        "change": -19,
        "change_pct": -0.6621594,
        "market_state": "REGULAR",
        "exchange": "CME"
      },
      {
        "id": "CBT",
        "symbol": "YM=F",
        "name": "Dow Futures",
        "price": 49991,
        "change": -163,
        "change_pct": -0.324999,
        "market_state": "REGULAR",
        "exchange": "CBOT"
      },
      {
        "id": "CXI",
        "symbol": "^VIX",
        "name": "VIX",
        "price": 17.26,
        "change": -0.6100006,
        "change_pct": -3.4135456,
        "market_state": "POSTPOST",
        "exchange": "Cboe Indices"
      },
      {
        "id": "CMX",
        "symbol": "GC=F",
        "name": "Gold",
        "price": 4617.5,
        "change": -67.799805,
        "change_pct": -1.447075,
        "market_state": "REGULAR",
        "exchange": "COMEX"
      }
    ],
    "source": "yfinance"
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.market` | string | Market code or broad market object. |
| `data.market_state` | string | Open/closed market state. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.status` | object | Provider, market, or run status. |
| `data.summary` | array | Short human-readable summary. |
| `data.summary[]` | object | Short human-readable summary. |
| `data.status.close` | string | Scheduled market close timestamp. |
| `data.status.id` | string | Source identifier for this nested provider record. |
| `data.status.message` | string | Provider message or status text. |
| `data.status.name` | string | Human-readable market name. |
| `data.status.open` | string | Scheduled market open timestamp. |
| `data.status.status` | string | Provider, market, or run status. |
| `data.status.timezone` | object | Market timezone metadata. |
| `data.status.tz` | string | Timezone abbreviation. |
| `data.status.yfit_market_id` | string | Yahoo Finance market identifier. |
| `data.status.yfit_market_status` | string | Yahoo Finance market status code. |
| `data.summary[].change` | number | Absolute price change. |
| `data.summary[].change_pct` | number | Price change as a decimal percentage value. |
| `data.summary[].exchange` | string | Exchange code or market venue. |
| `data.summary[].id` | string | Source identifier for this nested provider record. |
| `data.summary[].market_state` | string | Open/closed market state. |
| `data.summary[].name` | string | Display name for the index, future, commodity, or volatility instrument. |
| `data.summary[].price` | number | Latest provider price for the summary instrument. |
| `data.summary[].symbol` | string | Provider symbol for the summary instrument. |
| `data.status.timezone.$text` | string | Text value inside the provider timezone object. |
| `data.status.timezone.dst` | string | Daylight-saving flag from the provider timezone object. |
| `data.status.timezone.gmtoffset` | string | GMT offset from the provider timezone object. |
| `data.status.timezone.short` | string | Timezone abbreviation, such as `EDT`. |
