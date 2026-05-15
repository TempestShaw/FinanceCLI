---
title: industry
description: Discover Yahoo Finance industry keys and inspect industry overview and table data.
---

# finance industry

The `industry.*` commands discover Yahoo Finance industry keys and return overview or table data for one industry. Use this namespace when the user asks for comparable companies, industry ETFs, mutual funds, or industry-level research context.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance industry.keys

List Yahoo industry keys, optionally filtered by sector.

### What it does

`finance industry.keys` lists Yahoo industry keys, optionally filtered by sector. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `industries`, `count`, `source`.

### When to use it

Use this command when you need a valid Yahoo industry key before calling `finance industry.overview` or `finance industry.table`.

### Usage

```bash
finance industry.keys [sector=SECTOR_KEY] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `sector` | No | `SECTOR_KEY` | String | Optional sector key used to filter the returned industry list. |

### Basic usage

```bash
finance industry.keys sector=technology --output json
```

### Example output

This output was generated with `finance industry.keys sector=technology --output json`.

```json
{
  "ok": true,
  "data": {
    "industries": [
      {
        "key": "solar",
        "name": "Solar",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "information-technology-services",
        "name": "Information Technology Services",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "computer-hardware",
        "name": "Computer Hardware",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "software-infrastructure",
        "name": "Software Infrastructure",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "scientific-technical-instruments",
        "name": "Scientific Technical Instruments",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "semiconductor-equipment-materials",
        "name": "Semiconductor Equipment Materials",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "electronic-components",
        "name": "Electronic Components",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "communication-equipment",
        "name": "Communication Equipment",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "consumer-electronics",
        "name": "Consumer Electronics",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "software-application",
        "name": "Software Application",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "electronics-computer-distribution",
        "name": "Electronics Computer Distribution",
        "sector_key": "technology",
        "sector_name": "Technology"
      },
      {
        "key": "semiconductors",
        "name": "Semiconductors",
        "sector_key": "technology",
        "sector_name": "Technology"
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
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.industries[].key` | string | Stable key that can be passed back to this namespace as an argument. |
| `data.industries[].name` | string | Human-readable industry name. |
| `data.industries[].sector_key` | string | Sector key that owns this industry. |
| `data.industries[].sector_name` | string | Human-readable sector name that owns this industry. |

## finance industry.overview

Fetch industry overview metadata.

### What it does

`finance industry.overview` fetches industry overview metadata. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `key`, `name`, `sector_key`, `sector_name`, `symbol`, `overview`, `source`.

### When to use it

Use this command when you need the industry description, company count, market cap, market weight, or parent sector for a known industry key.

### Usage

```bash
finance industry.overview KEY [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `key` | Yes | None | String | Sector or industry key returned by the corresponding keys command. |

### Basic usage

```bash
finance industry.overview software-infrastructure --output json
```

### Example output

This output was generated with `finance industry.overview software-infrastructure --output json`.

```json
{
  "ok": true,
  "data": {
    "key": "software-infrastructure",
    "name": "Software - Infrastructure",
    "sector_key": "technology",
    "sector_name": "Technology",
    "symbol": "^YH31110030",
    "overview": {
      "companies_count": 214,
      "market_cap": 5170753699840,
      "message_board_id": "INDEXYH31110030",
      "description": "Companies that develop, design, support, and provide system software and services, including operating systems, networking software and devices, web portal services, cloud storage, and related services.",
      "industries_count": null,
      "market_weight": 0.18857579,
      "employee_count": 827850
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
| `data.name` | string | Human-readable industry name. |
| `data.overview` | object | Overview metadata for a sector or industry. |
| `data.sector_key` | string | Sector key that owns this industry. |
| `data.sector_name` | string | Human-readable sector name that owns this industry. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Yahoo Finance industry index symbol. |
| `data.overview.companies_count` | integer | Number of companies represented by the provider object. |
| `data.overview.description` | string | Provider description for this item. |
| `data.overview.employee_count` | integer | Employee count returned in the provider overview. |
| `data.overview.industries_count` | null | Number of industries in the sector. |
| `data.overview.market_cap` | integer | Market capitalization. |
| `data.overview.market_weight` | number | Sector or industry market-weight value. |
| `data.overview.message_board_id` | string | Yahoo Finance message-board identifier. |

## finance industry.table

Fetch industry top companies or reports.

### What it does

`finance industry.table` fetches industry top companies or reports. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `key`, `name`, `sector_key`, `sector_name`, `table`, `rows`, `count`, `source`.

### When to use it

Use this command when you need comparable companies, growth leaders, top performers, or research report rows for a known industry key.

### Usage

```bash
finance industry.table KEY [table=top_companies|top_growth_companies|top_performing_companies|research_reports limit=25] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `key` | Yes | None | String | Sector or industry key returned by the corresponding keys command. |
| `limit` | No | `25` | Integer | Maximum number of records returned. |
| `table` | No | None | `top_companies`, `top_growth_companies`, `top_performing_companies`, `research_reports` | Table key to return for the sector or industry. |

### Basic usage

```bash
finance industry.table software-infrastructure table=top_companies limit=5 --output json
```

### Example output

This output was generated with `finance industry.table software-infrastructure table=top_companies limit=5 --output json`.

```json
{
  "ok": true,
  "data": {
    "key": "software-infrastructure",
    "name": "Software - Infrastructure",
    "sector_key": "technology",
    "sector_name": "Technology",
    "table": "top_companies",
    "rows": [
      {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "rating": "Strong Buy",
        "market_weight": 0.5923323
      },
      {
        "symbol": "ORCL",
        "name": "Oracle Corporation",
        "rating": "Buy",
        "market_weight": 0.109565884
      },
      {
        "symbol": "PLTR",
        "name": "Palantir Technologies Inc.",
        "rating": "Buy",
        "market_weight": 0.062436976
      },
      {
        "symbol": "PANW",
        "name": "Palo Alto Networks, Inc.",
        "rating": "Buy",
        "market_weight": 0.037624378
      },
      {
        "symbol": "CRWD",
        "name": "CrowdStrike Holdings, Inc.",
        "rating": "Buy",
        "market_weight": 0.028749423
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
| `data.name` | string | Human-readable industry name. |
| `data.rows` | array | Structured rows returned by the command. |
| `data.rows[]` | object | Structured rows returned by the command. |
| `data.sector_key` | string | Sector key that owns this industry. |
| `data.sector_name` | string | Human-readable sector name that owns this industry. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.table` | string | Sector or industry table key returned by the command. |
| `data.rows[].market_weight` | number | Sector or industry market-weight value. |
| `data.rows[].name` | string | Company or report name for the row. |
| `data.rows[].rating` | string | Provider rating label for the row. |
| `data.rows[].symbol` | string | Ticker or provider symbol for the row. |
