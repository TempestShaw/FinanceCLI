---
title: estimates
description: Analyst estimate comparison and FMP consensus data.
---

Use `estimates.*` for comparing your assumptions with consensus or pulling FMP estimate records.

## Compare Your Inputs

```bash
finance estimates.compare IOT revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027
```

Tested result:

```json
{
  "symbol": "IOT",
  "fiscal_year": 2027,
  "revenue": {
    "actual": 2200000000.0,
    "consensus": 2000000000.0,
    "gap_pct": 10.0,
    "direction": "above_consensus"
  },
  "eps": {
    "actual": 0.5,
    "consensus": 0.45,
    "gap_pct": 11.11111111111111,
    "direction": "above_consensus"
  }
}
```

## Consensus

```bash
finance estimates.consensus IOT period=annual limit=5
```

`estimates.consensus` requires `FMP_API_KEY`. A tested run without the key failed clearly:

```json
{
  "ok": false,
  "error": "FMP API key is required. Set FMP_API_KEY."
}
```
