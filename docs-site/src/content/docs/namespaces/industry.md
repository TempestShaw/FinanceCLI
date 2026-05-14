---
title: industry
description: Yahoo industry keys, overviews, and top company lists.
---

Use `industry.*` after `sector.industries` or `industry.keys` to inspect narrower peer groups.

## Commands

```bash
finance industry.keys sector=technology
finance industry.overview software-infrastructure
finance industry.table software-infrastructure table=top_companies limit=10
finance industry.table software-infrastructure table=top_growth_companies limit=10
```

## Parameters

### `industry.keys`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `sector` | No | All sectors | Sector key | Filter industries to one Yahoo sector key. |

### `industry.overview`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `KEY` | Yes | None | Industry key | Yahoo industry key such as `software-infrastructure`. |

### `industry.table`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `KEY` | Yes | None | Industry key | Yahoo industry key. |
| `table` | No | `top_companies` | `top_companies`, `top_growth_companies`, `top_performing_companies`, `research_reports` | Industry table to return. |
| `limit` | No | `25` | Integer | Maximum rows. |

## Key Discovery

```bash
finance industry.keys
finance industry.keys sector=technology
```

`industry.keys` uses the sector/industry mapping shipped with the installed yfinance version, so keys line up with Yahoo's `Industry` endpoint.

## Result Shape

```json
{
  "key": "software-infrastructure",
  "sector_key": "technology",
  "sector_name": "Technology",
  "rows": [
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation"
    }
  ],
  "source": "yfinance"
}
```
