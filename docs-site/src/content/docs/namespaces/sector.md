---
title: sector
description: Discover Yahoo Finance sectors, industries, and sector table data.
---

# finance sector

The `sector.*` commands discover Yahoo Finance sector keys, sector industries, and sector table data. Use this namespace when the user asks for sector-level context or needs a valid sector key before industry work.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance sector.industries

List industries in a sector.

### What it does

`finance sector.industries` lists industries in a sector. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `key`, `name`, `industries`, `count`, `source`.

### When to use it

Use this command after `finance sector.keys` when you need valid industry keys inside a sector before calling `finance industry.overview` or `finance industry.table`.

### Usage

```bash
finance sector.industries KEY [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `key` | Yes | None | String | Sector or industry key returned by the corresponding keys command. |

### Basic usage

```bash
finance sector.industries technology --output json
```

### Example output

This output was generated with `finance sector.industries technology --output json`.

```json
{
  "ok": true,
  "data": {
    "key": "technology",
    "name": "Technology",
    "industries": [
      {
        "key": "semiconductors",
        "name": "Semiconductors",
        "symbol": "^YH31130020",
        "market_weight": 0.4168796
      },
      {
        "key": "software-infrastructure",
        "name": "Software - Infrastructure",
        "symbol": "^YH31110030",
        "market_weight": 0.18857579
      },
      {
        "key": "consumer-electronics",
        "name": "Consumer Electronics",
        "symbol": "^YH31120030",
        "market_weight": 0.1598143
      },
      {
        "key": "software-application",
        "name": "Software - Application",
        "symbol": "^YH31110020",
        "market_weight": 0.060947914
      },
      {
        "key": "semiconductor-equipment-materials",
        "name": "Semiconductor Equipment & Materials",
        "symbol": "^YH31130010",
        "market_weight": 0.04376187
      },
      {
        "key": "computer-hardware",
        "name": "Computer Hardware",
        "symbol": "^YH31120020",
        "market_weight": 0.037487555
      },
      {
        "key": "communication-equipment",
        "name": "Communication Equipment",
        "symbol": "^YH31120010",
        "market_weight": 0.03203036
      },
      {
        "key": "electronic-components",
        "name": "Electronic Components",
        "symbol": "^YH31120040",
        "market_weight": 0.02396074
      },
      {
        "key": "information-technology-services",
        "name": "Information Technology Services",
        "symbol": "^YH31110010",
        "market_weight": 0.021127515
      },
      {
        "key": "scientific-technical-instruments",
        "name": "Scientific & Technical Instruments",
        "symbol": "^YH31120060",
        "market_weight": 0.011458799
      },
      {
        "key": "solar",
        "name": "Solar",
        "symbol": "^YH31130030",
        "market_weight": 0.0024080568
      },
      {
        "key": "electronics-computer-distribution",
        "name": "Electronics & Computer Distribution",
        "symbol": "^YH31120050",
        "market_weight": 0.0015475056
      }
    ],
    "count": 12,
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
| `data.industries` | array | Industries returned for a sector. |
| `data.industries[]` | object | Industries returned for a sector. |
| `data.key` | string | Stable key that can be passed back to this namespace as an argument. |
| `data.name` | string | Human-readable sector name. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.industries[].key` | string | Stable key that can be passed back to this namespace as an argument. |
| `data.industries[].market_weight` | number | Sector or industry market-weight value. |
| `data.industries[].name` | string | Human-readable industry name. |
| `data.industries[].symbol` | string | Yahoo Finance industry index symbol. |

## finance sector.keys

List Yahoo sector keys.

### What it does

`finance sector.keys` lists Yahoo sector keys. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `sectors`, `source`.

### When to use it

Use this command before other `sector.*` commands when you need the exact sector key accepted by Finance CLI.

### Usage

```bash
finance sector.keys [--output json]
```

### Arguments

No arguments.

### Basic usage

```bash
finance sector.keys --output json
```

### Example output

This output was generated with `finance sector.keys --output json`.

```json
{
  "ok": true,
  "data": {
    "sectors": [
      {
        "key": "basic-materials",
        "name": "Basic Materials"
      },
      {
        "key": "communication-services",
        "name": "Communication Services"
      },
      {
        "key": "consumer-cyclical",
        "name": "Consumer Cyclical"
      },
      {
        "key": "consumer-defensive",
        "name": "Consumer Defensive"
      },
      {
        "key": "energy",
        "name": "Energy"
      },
      {
        "key": "financial-services",
        "name": "Financial Services"
      },
      {
        "key": "healthcare",
        "name": "Healthcare"
      },
      {
        "key": "industrials",
        "name": "Industrials"
      },
      {
        "key": "real-estate",
        "name": "Real Estate"
      },
      {
        "key": "technology",
        "name": "Technology"
      },
      {
        "key": "utilities",
        "name": "Utilities"
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
| `data.sectors` | array | Sector key records. |
| `data.sectors[]` | object | Sector key records. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.sectors[].key` | string | Stable key that can be passed back to this namespace as an argument. |
| `data.sectors[].name` | string | Human-readable sector name. |

## finance sector.overview

Fetch sector overview metadata.

### What it does

`finance sector.overview` fetches sector overview metadata. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `key`, `name`, `symbol`, `overview`, `source`.

### When to use it

Use this command when you need high-level sector metadata such as company count, market cap, description, industry count, and market weight.

### Usage

```bash
finance sector.overview KEY [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `key` | Yes | None | String | Sector or industry key returned by the corresponding keys command. |

### Basic usage

```bash
finance sector.overview technology --output json
```

### Example output

This output was generated with `finance sector.overview technology --output json`.

```json
{
  "ok": true,
  "data": {
    "key": "technology",
    "name": "Technology",
    "symbol": "^YH311",
    "overview": {
      "companies_count": 943,
      "market_cap": 27420029616128,
      "message_board_id": "INDEXYH311",
      "description": "Companies engaged in the design, development, and support of computer operating systems and applications. This sector also includes companies that make computer equipment, data storage products, networking products, semiconductors, and components. Companies in this sector include Apple, Microsoft, and IBM.",
      "industries_count": 12,
      "market_weight": 0.32443243,
      "employee_count": 7965742
    },
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
| `data.key` | string | Stable key that can be passed back to this namespace as an argument. |
| `data.name` | string | Human-readable sector name. |
| `data.overview` | object | Overview metadata for a sector or industry. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Yahoo Finance sector index symbol. |
| `data.overview.companies_count` | integer | Number of companies represented by the provider object. |
| `data.overview.description` | string | Provider description for this item. |
| `data.overview.employee_count` | integer | Employee count returned in the provider overview. |
| `data.overview.industries_count` | integer | Number of industries in the sector. |
| `data.overview.market_cap` | integer | Market capitalization. |
| `data.overview.market_weight` | number | Sector or industry market-weight value. |
| `data.overview.message_board_id` | string | Yahoo Finance message-board identifier. |

## finance sector.table

Fetch sector top companies, funds, or reports.

### What it does

`finance sector.table` fetches sector top companies, funds, or reports. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `key`, `name`, `table`, `rows`, `count`, `source`.

### When to use it

Use this command when you need sector constituents, sector ETFs, sector mutual funds, or provider research report rows for a known sector key.

### Usage

```bash
finance sector.table KEY [table=top_companies|top_etfs|top_mutual_funds|research_reports limit=25] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `key` | Yes | None | String | Sector or industry key returned by the corresponding keys command. |
| `limit` | No | `25` | Integer | Maximum number of records returned. |
| `table` | No | None | `top_companies`, `top_etfs`, `top_mutual_funds`, `research_reports` | Table key to return for the sector or industry. |

### Basic usage

```bash
finance sector.table technology table=top_companies limit=5 --output json
```

### Example output

This output was generated with `finance sector.table technology table=top_companies limit=5 --output json`.

```json
{
  "ok": true,
  "data": {
    "key": "technology",
    "name": "Technology",
    "table": "top_companies",
    "rows": [
      {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "rating": "Strong Buy",
        "market_weight": 0.20974006
      },
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "rating": "Buy",
        "market_weight": 0.16090755
      },
      {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "rating": "Strong Buy",
        "market_weight": 0.11173458
      },
      {
        "symbol": "AVGO",
        "name": "Broadcom Inc.",
        "rating": "Strong Buy",
        "market_weight": 0.0764972
      },
      {
        "symbol": "MU",
        "name": "Micron Technology, Inc.",
        "rating": "Strong Buy",
        "market_weight": 0.032150272
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
| `data.key` | string | Stable key that can be passed back to this namespace as an argument. |
| `data.name` | string | Human-readable sector name. |
| `data.rows` | array | Structured rows returned by the command. |
| `data.rows[]` | object | Structured rows returned by the command. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.table` | string | Sector or industry table key returned by the command. |
| `data.rows[].market_weight` | number | Sector or industry market-weight value. |
| `data.rows[].name` | string | Company, fund, ETF, or report name for the row. |
| `data.rows[].rating` | string | Provider rating label for the row. |
| `data.rows[].symbol` | string | Ticker or provider symbol for the row. |
