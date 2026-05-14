---
title: price
description: Price moves and temporal news context around a date.
---

Use `price.*` when the question starts with a price move or a date.

## Parameters

### `price.moves`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Symbol to scan. |
| `window` | No | `1d` | `1d`, `3d`, `1w`, `1m` | Trading-day move window. `1w` means 5 trading days; `1m` means 21 trading days. |
| `years` | No | `3` | Integer | Historical lookback in years. |
| `threshold` | No | `8%` | Decimal or percent, such as `0.08`, `8`, `8%` | Absolute move threshold. |
| `limit` | No | `20` | Integer | Maximum moves returned. |
| `provider` | No | `auto` | `auto`, provider name | OHLCV provider selection. |

### `price.context`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Symbol to contextualize. |
| `date` / `target_date` | Yes | None | `YYYY-MM-DD` | Center date for the evidence window. |
| `lookback` | No | `3D` | Calendar window such as `2D`, `1W`, `1M` | Days/weeks/months before and after the target date. |
| `news_limit` | No | `5` | Integer | Maximum news items. |
| `filing_limit` | No | `80` | Integer | Maximum filings considered while building context. |
| `transcript_limit` | No | `12` | Integer | Maximum transcripts considered while building context. |

## Move Scanner

```bash
finance price.moves NVDA years=1 threshold=8% limit=3
```

A tested run returned an empty move list because no close-to-close move crossed the requested threshold in the sampled window:

```json
{
  "symbol": "NVDA",
  "threshold": 0.08,
  "moves": [],
  "count": 0,
  "notes": ["Close-to-close scanner; does not assign causality."]
}
```

Empty results are valid. Lower the threshold or extend the window if you need more candidates.

## Context Around A Date

```bash
finance price.context NVDA date=2025-01-27 lookback=2D news_limit=3
```

A tested run returned three timeline entries around the requested date. The command labels temporal proximity only; it does not claim the articles caused the price move.
