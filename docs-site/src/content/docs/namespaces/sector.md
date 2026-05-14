---
title: sector
description: Yahoo sector keys, overviews, industries, and top lists.
---

Use `sector.*` to discover Yahoo sector keys and pull sector-level context for research screens.

## Commands

```bash
finance sector.keys
finance sector.overview technology
finance sector.industries technology
finance sector.table technology table=top_companies limit=10
finance sector.table technology table=top_etfs limit=5
```

## Parameters

### `sector.keys`

No parameters. Returns the sector keys known by the installed yfinance version.

### `sector.overview`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `KEY` | Yes | None | Sector key | Yahoo sector key such as `technology`, `healthcare`, or `financial-services`. |

### `sector.industries`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `KEY` | Yes | None | Sector key | Yahoo sector key. |

### `sector.table`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `KEY` | Yes | None | Sector key | Yahoo sector key. |
| `table` | No | `top_companies` | `top_companies`, `top_etfs`, `top_mutual_funds`, `research_reports` | Sector table to return. |
| `limit` | No | `25` | Integer | Maximum rows. |

## Key Discovery

```bash
finance sector.keys
finance sector.industries technology
```

`sector.industries` returns industry keys when the yfinance sector mapping can match the industry name.

## Result Shape

```json
{
  "key": "technology",
  "industries": [
    {
      "key": "semiconductors",
      "name": "Semiconductors",
      "symbol": "^YH31130020",
      "market_weight": 0.4155985
    }
  ],
  "count": 12,
  "source": "yfinance"
}
```
