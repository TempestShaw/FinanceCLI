---
title: symbol
description: Resolve company profile and snapshot metadata for a ticker.
---

# finance symbol

The `symbol.*` commands return compact profile and snapshot data for a ticker. Use this namespace when a workflow needs company identity, sector, industry, market cap, website, or source handles before deeper analysis.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance symbol.profile

Show real quote and SEC company metadata for a symbol.

### What it does

`finance symbol.profile` shows real quote and SEC company metadata for a symbol. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `company_name`, `sector`, `industry`, `last_price`, `market_cap`, `currency`, `cik`.

### When to use it

Use this command when you need both market metadata and SEC identity fields for a ticker before fetching filings, transcripts, price context, or valuation inputs.

Behavior details: Uses yfinance for market metadata and SEC ticker metadata for CIK/company identity.

### Usage

```bash
finance symbol.profile SYMBOL [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |

### Basic usage

```bash
finance symbol.profile IOT --output json
```

### Example output

This output was generated with `finance symbol.profile IOT --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "company_name": "Samsara Inc.",
    "sector": "Technology",
    "industry": "Software - Infrastructure",
    "last_price": 27.99,
    "market_cap": 16310054912,
    "currency": "USD",
    "cik": "0001642896",
    "sources": [
      "yfinance",
      "sec_edgar"
    ],
    "website": "https://www.samsara.com",
    "ir_website": null
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
| `data.cik` | string | SEC Central Index Key when available. |
| `data.company_name` | string | Company name returned by the provider. |
| `data.currency` | string | Trading or reporting currency. |
| `data.industry` | string | Company industry classification. |
| `data.ir_website` | string or null | Investor-relations website URL when available. |
| `data.last_price` | number | Latest provider price. |
| `data.market_cap` | integer | Market capitalization. |
| `data.sector` | string | Company or market sector. |
| `data.sources` | array | Provider handles used to assemble the result. |
| `data.sources[]` | string | Individual provider handle used in the lookup. |
| `data.symbol` | string | Ticker symbol returned for the company. |
| `data.website` | string | Company website URL. |

## finance symbol.snapshot

Show real quote and company metadata for a symbol.

### What it does

`finance symbol.snapshot` shows real quote and company metadata for a symbol. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `company_name`, `sector`, `industry`, `last_price`, `market_cap`, `currency`, `cik`.

### When to use it

Use this command when you need a compact company snapshot for display, routing, or quick context and do not need the full `market.quote` payload.

### Usage

```bash
finance symbol.snapshot SYMBOL [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |

### Basic usage

```bash
finance symbol.snapshot NVDA --output json
```

### Example output

This output was generated with `finance symbol.snapshot NVDA --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "NVDA",
    "company_name": "NVIDIA Corporation",
    "sector": "Technology",
    "industry": "Semiconductors",
    "last_price": 235.74,
    "market_cap": 5709746405376,
    "currency": "USD",
    "cik": "0001045810",
    "sources": [
      "yfinance",
      "sec_edgar"
    ],
    "website": "https://www.nvidia.com",
    "ir_website": "http://phx.corporate-ir.net/phoenix.zhtml?c=116466&p=irol-IRHome"
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
| `data.cik` | string | SEC Central Index Key when available. |
| `data.company_name` | string | Company name returned by the provider. |
| `data.currency` | string | Trading or reporting currency. |
| `data.industry` | string | Company industry classification. |
| `data.ir_website` | string | Investor-relations website URL. |
| `data.last_price` | number | Latest provider price. |
| `data.market_cap` | integer | Market capitalization. |
| `data.sector` | string | Company or market sector. |
| `data.sources` | array | Provider handles used to assemble the result. |
| `data.sources[]` | string | Individual provider handle used in the lookup. |
| `data.symbol` | string | Ticker symbol returned for the company. |
| `data.website` | string | Company website URL. |
