---
title: estimates
description: Analyst estimate comparison and FMP consensus data.
---

Use `estimates.*` for comparing your assumptions with consensus or pulling FMP estimate records.

## Parameters

### `estimates.compare`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` / `symbol` | No | None | Public ticker | Symbol label included in the output. |
| `revenue` | Required for revenue comparison | None | Number with optional `K/M/B` suffix | Your revenue assumption or reported value. |
| `consensus_revenue` | Required when `revenue` is set | None | Number with optional `K/M/B` suffix | Consensus revenue value to compare against. |
| `eps` | Required for EPS comparison | None | Number | Your EPS assumption or reported value. |
| `consensus_eps` | Required when `eps` is set | None | Number | Consensus EPS value to compare against. |
| `fiscal_year` | No | None | Year | Fiscal-year label in the output. |

`estimates.compare` accepts only explicit values you provide. It does not call a provider.

### `estimates.consensus`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` / `symbol` | Yes | None | Public ticker | Symbol to request from FMP. |
| `period` | No | `annual` | `annual`, `quarter` | Estimate period. |
| `limit` | No | `10` | Integer | Maximum rows returned. |
| `page` | No | `0` | Integer | FMP pagination page. |

Requires `FMP_API_KEY`.

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
