---
title: price
description: Price moves and temporal news context around a date.
---

Use `price.*` when the question starts with a price move or a date.

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
