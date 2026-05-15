---
title: estimates
description: Compare company fundamentals against consensus estimates when the required provider credentials are configured.
---

# finance estimates

The `estimates.*` commands compare reported or provider fundamentals against consensus estimate data. Use this namespace when the user asks for beat/miss analysis or consensus context and the required provider credentials are available.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance estimates.compare

Compare user assumptions against explicit consensus inputs.

### What it does

`finance estimates.compare` compares user assumptions against explicit consensus inputs. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `fiscal_year`, `period`, `comparisons`, `count`, `method`.

### When to use it

Use this command when you already have reported or assumed revenue/EPS and matching consensus inputs and want deterministic beat/miss math without a network call.

Behavior details: No network calls. Compares only values explicitly supplied by the caller.

### Usage

```bash
finance estimates.compare [SYMBOL] revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027 [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `consensus_eps` | Yes | None | Number | Consensus EPS input for the comparison. |
| `consensus_revenue` | Yes | None | String | Consensus revenue input. K/M/B suffixes are accepted. |
| `eps` | Yes | None | Number | Reported, assumed, or user-supplied EPS input. |
| `fiscal_year` | Yes | None | Integer | Fiscal year label attached to the comparison. |
| `revenue` | Yes | None | String | Reported, assumed, or user-supplied revenue input. K/M/B suffixes are accepted. |
| `symbol` | No | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |

### Basic usage

```bash
finance estimates.compare IOT revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027 --output json
```

### Example output

This output was generated with `finance estimates.compare IOT revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027 --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "fiscal_year": "2027",
    "period": null,
    "comparisons": [
      {
        "metric": "revenue",
        "user_value": 2200000000.0,
        "consensus_value": 2000000000.0,
        "absolute_gap": 200000000.0,
        "percent_gap": 0.1,
        "percent_gap_pct": 10.0,
        "valuation_input_hint": "above_consensus"
      },
      {
        "metric": "eps",
        "user_value": 0.5,
        "consensus_value": 0.45,
        "absolute_gap": 0.05,
        "percent_gap": 0.1111111111,
        "percent_gap_pct": 11.11111111,
        "valuation_input_hint": "above_consensus"
      }
    ],
    "count": 2,
    "method": "user_metric - consensus_metric"
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
| `data.comparisons` | array | Explicit value-vs-consensus comparisons. |
| `data.comparisons[]` | object | Explicit value-vs-consensus comparisons. |
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.fiscal_year` | string | Fiscal year label. |
| `data.method` | string | Calculation or comparison method. |
| `data.period` | null | Reporting or estimate period. |
| `data.symbol` | string | Ticker symbol attached to the comparison. |
| `data.comparisons[].absolute_gap` | number | Difference between user and consensus values. |
| `data.comparisons[].consensus_value` | number | Consensus value after parsing. |
| `data.comparisons[].metric` | string | Metric name. |
| `data.comparisons[].percent_gap` | number | Difference as a decimal percentage. |
| `data.comparisons[].percent_gap_pct` | number | Difference as a percentage value. |
| `data.comparisons[].user_value` | number | User-supplied value after parsing. |
| `data.comparisons[].valuation_input_hint` | string | Direction label for valuation assumptions. |

## finance estimates.consensus

Fetch FMP analyst consensus estimates when configured.

### What it does

`finance estimates.consensus` fetches FMP analyst consensus estimates when configured. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The example below shows the structured failure envelope returned when a required provider credential or dependency is unavailable.

### When to use it

Use this command when you need consensus estimate rows from FMP and have `FMP_API_KEY` configured.

Behavior details: Requires FMP_API_KEY. Makes one short FMP request and returns a structured configuration error when unconfigured.

### Usage

```bash
finance estimates.consensus SYMBOL [period=annual|quarter limit=10 page=0] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `limit` | No | `10` | Integer | Maximum number of records returned. |
| `page` | No | `0` | Integer | FMP result page offset. |
| `period` | No | None | `annual`, `quarter` | Consensus period requested from FMP. |

### Basic usage

```bash
finance estimates.consensus IOT period=annual limit=5 --output json
```

### Example output

This output was generated with `finance estimates.consensus IOT period=annual limit=5 --output json`.

```json
{
  "ok": false,
  "data": null,
  "error": "FMP API key is required. Set FMP_API_KEY.",
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
