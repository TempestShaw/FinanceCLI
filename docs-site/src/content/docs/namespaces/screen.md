---
title: screen
description: Run predefined Yahoo equity screens.
---

Use `screen.*` to discover and run Yahoo's predefined equity screens from the same JSON command surface as filings and market data.

## Commands

```bash
finance screen.predefined
finance screen.run day_gainers count=10
```

## Parameters

### `screen.predefined`

No parameters. Returns predefined Yahoo screen query keys.

### `screen.run`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `QUERY` | Yes | None | Predefined screen key | Query key from `screen.predefined`, such as `day_gainers` or `most_actives`. |
| `count` | No | `25` | Integer | Maximum number of quotes requested. |
| `offset` | No | None | Integer | Result offset. |
| `sort_field` | No | Provider default | Field name | Optional Yahoo sort field. |
| `sort_asc` | No | Provider default | Boolean | Sort ascending when set. |

## Result Shape

```json
{
  "query": "day_gainers",
  "title": "Day Gainers",
  "quotes": [
    {
      "symbol": "NVDA",
      "name": "NVIDIA Corporation",
      "price": 120.5,
      "change_pct": 3.2,
      "market_cap": 2900000000000
    }
  ],
  "count": 1,
  "source": "yfinance"
}
```
