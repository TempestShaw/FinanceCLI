---
title: screen
description: List and run predefined Yahoo Finance equity screens.
---

# finance screen

The `screen.*` commands list and run predefined Yahoo Finance equity screens. Use this namespace when the user asks for market lists such as gainers, undervalued stocks, or other predefined screen groups.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance screen.predefined

List predefined Yahoo equity screens.

### What it does

`finance screen.predefined` lists predefined Yahoo equity screens. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `queries`, `count`, `source`.

### When to use it

Use this command before `finance screen.run` when you do not know the exact predefined query key.

### Usage

```bash
finance screen.predefined [--output json]
```

### Arguments

No arguments.

### Basic usage

```bash
finance screen.predefined --output json
```

### Example output

This output was generated with `finance screen.predefined --output json`.

```json
{
  "ok": true,
  "data": {
    "queries": [
      {
        "key": "aggressive_small_caps",
        "name": "Aggressive Small Caps"
      },
      {
        "key": "conservative_foreign_funds",
        "name": "Conservative Foreign Funds"
      },
      {
        "key": "day_gainers",
        "name": "Day Gainers"
      },
      {
        "key": "day_losers",
        "name": "Day Losers"
      },
      {
        "key": "growth_technology_stocks",
        "name": "Growth Technology Stocks"
      },
      {
        "key": "high_yield_bond",
        "name": "High Yield Bond"
      },
      {
        "key": "most_actives",
        "name": "Most Actives"
      },
      {
        "key": "most_shorted_stocks",
        "name": "Most Shorted Stocks"
      },
      {
        "key": "portfolio_anchors",
        "name": "Portfolio Anchors"
      },
      {
        "key": "small_cap_gainers",
        "name": "Small Cap Gainers"
      },
      {
        "key": "solid_large_growth_funds",
        "name": "Solid Large Growth Funds"
      },
      {
        "key": "solid_midcap_growth_funds",
        "name": "Solid Midcap Growth Funds"
      },
      {
        "key": "top_mutual_funds",
        "name": "Top Mutual Funds"
      },
      {
        "key": "undervalued_growth_stocks",
        "name": "Undervalued Growth Stocks"
      },
      {
        "key": "undervalued_large_caps",
        "name": "Undervalued Large Caps"
      }
    ],
    "count": 15,
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
| `data.queries` | array | Predefined screen query records. |
| `data.queries[]` | object | Predefined screen query records. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.queries[].key` | string | Stable key that can be passed back to this namespace as an argument. |
| `data.queries[].name` | string | Human-readable screen name shown by Yahoo Finance. |

## finance screen.run

Run a predefined Yahoo equity screen.

### What it does

`finance screen.run` runs a predefined Yahoo equity screen. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `query`, `title`, `description`, `quotes`, `count`, `total`, `source`.

### When to use it

Use this command after `finance screen.predefined` when you have a valid screen key and want the current quote rows for that screen.

Behavior details: Use screen.predefined to list available query keys. count is the maximum number of quotes requested.

### Usage

```bash
finance screen.run QUERY [count=25 offset=0 sort_field=FIELD sort_asc=false] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `query` | Yes | None | String | Query string or predefined query key accepted by this command. |
| `count` | No | `25` | Integer | Maximum number of records requested. |
| `offset` | No | `0` | Integer | Result offset. |
| `sort_asc` | No | `false` | `true`, `false` | Sort ascending when set. |
| `sort_field` | No | None | String | Provider sort field. Leave unset to use the screen default. |

### Basic usage

```bash
finance screen.run day_gainers count=5 --output json
```

### Example output

This output was generated with `finance screen.run day_gainers count=5 --output json`.

```json
{
  "ok": true,
  "data": {
    "query": "day_gainers",
    "title": "Day Gainers",
    "description": "Discover the equities with the greatest gains in the trading day.",
    "quotes": [
      {
        "symbol": "POET",
        "name": "POET Technologies Inc.",
        "price": 20.57,
        "change_pct": 43.1454,
        "market_cap": 3141268992,
        "volume": 117146094,
        "sector": null,
        "industry": null,
        "exchange": "NCM"
      },
      {
        "symbol": "ONDS",
        "name": "Ondas Inc",
        "price": 11.21,
        "change_pct": 26.5237,
        "market_cap": 5556201472,
        "volume": 243177512,
        "sector": null,
        "industry": null,
        "exchange": "NCM"
      },
      {
        "symbol": "FRMI",
        "name": "Fermi Inc.",
        "price": 7.37,
        "change_pct": 22.8333,
        "market_cap": 4698921984,
        "volume": 56463131,
        "sector": null,
        "industry": null,
        "exchange": "NMS"
      },
      {
        "symbol": "RDW",
        "name": "Redwire Corporation",
        "price": 13.99,
        "change_pct": 22.0768,
        "market_cap": 2782872832,
        "volume": 63595271,
        "sector": null,
        "industry": null,
        "exchange": "NYQ"
      },
      {
        "symbol": "PCT",
        "name": "PureCycle Technologies, Inc.",
        "price": 12.39,
        "change_pct": 21.4706,
        "market_cap": 2240899584,
        "volume": 15393242,
        "sector": null,
        "industry": null,
        "exchange": "NCM"
      }
    ],
    "count": 5,
    "total": 217,
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
| `data.description` | string | Yahoo Finance description of what the screen selects. |
| `data.query` | string | Query key or search string used by the command. |
| `data.quotes` | array | Screen quote rows returned by the provider. |
| `data.quotes[]` | object | Screen quote rows returned by the provider. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.title` | string | Human-readable title for the selected screen. |
| `data.total` | integer | Provider-reported total result count when available. |
| `data.quotes[].change_pct` | number | Price change as a decimal percentage value. |
| `data.quotes[].exchange` | string | Exchange code or market venue. |
| `data.quotes[].industry` | string or null | Company industry classification when Yahoo returns it. |
| `data.quotes[].market_cap` | integer | Market capitalization. |
| `data.quotes[].name` | string | Company or security name for the quote row. |
| `data.quotes[].price` | number | Price associated with the event, quote, summary row, or order. |
| `data.quotes[].sector` | string or null | Company sector when Yahoo returns it. |
| `data.quotes[].symbol` | string | Ticker symbol for the quote row. |
| `data.quotes[].volume` | integer | Trading volume. |
