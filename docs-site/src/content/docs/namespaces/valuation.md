---
title: valuation
description: Valuation math, multiples, DCF, NPV, IRR, WACC, and scenarios.
---

Use `valuation.*` for valuation workflows that combine deterministic math with optional live market or fundamental inputs.

## Number Conventions

Large money inputs accept raw numbers or `K`, `M`, and `B` suffixes. Rate inputs accept decimals or percentages, for example `0.10` and `10%`.

## Parameters

### `valuation.multiples`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Symbol used to fetch market cap, enterprise value inputs, and revenue. |

### `valuation.scenario`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Symbol used for current price/share context. |
| `revenue` | Yes | None | Number with optional `K/M/B` suffix | Revenue assumption. |
| `bear_multiple` | Yes | None | Number | Bear-case sales multiple. |
| `base_multiple` | Yes | None | Number | Base-case sales multiple. |
| `bull_multiple` | Yes | None | Number | Bull-case sales multiple. |
| `shares` | No | Provider share count when available | Number with optional `K/M/B` suffix | Share count override. |

### `valuation.npv`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `cashflows` | Yes | None | Comma-separated numbers with optional `K/M/B` suffix | Periodic cash flows. First value is treated as `t=0`. |
| `discount_rate` | Yes | None | Decimal or percent | Discount rate. |

### `valuation.irr`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `cashflows` | Yes | None | Comma-separated numbers with optional `K/M/B` suffix | Periodic cash flows. Must include a sign change for normal IRR solving. |

### `valuation.wacc`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `equity_value` | Yes | None | Number with optional `K/M/B` suffix | Market value of equity. |
| `debt_value` | Yes | None | Number with optional `K/M/B` suffix | Market/book value of debt. |
| `cost_of_equity` | Yes | None | Decimal or percent | Cost of equity. |
| `cost_of_debt` | Yes | None | Decimal or percent | Pre-tax cost of debt. |
| `tax_rate` | No | `0` | Decimal or percent | Tax rate used for after-tax debt cost. |

### `valuation.dcf`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `cashflows` | Yes | None | Comma-separated numbers with optional `K/M/B` suffix | Forecast free cash flows only; do not include a `t=0` investment. |
| `discount_rate` | Yes | None | Decimal or percent | Discount rate. |
| `terminal_growth` | Required unless `exit_multiple` is set | None | Decimal or percent | Gordon-growth terminal assumption. |
| `exit_multiple` | Required unless `terminal_growth` is set | None | Number | Exit multiple terminal assumption. Use either this or `terminal_growth`, not both. |

## NPV And DCF

```bash
finance valuation.npv cashflows=-100M,30M,40M,50M discount_rate=10%
finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% terminal_growth=3%
```

Tested NPV output:

```json
{
  "cashflows": [-100000000.0, 30000000.0, 40000000.0, 50000000.0],
  "discount_rate": 0.1,
  "npv": -2103681.442524448,
  "method": "sum(cashflow_t / (1 + discount_rate)^t), with first cash flow at t=0"
}
```

Tested DCF output:

```json
{
  "cashflows": [100000000.0, 120000000.0, 140000000.0],
  "discount_rate": 0.1,
  "terminal_growth": 0.03,
  "terminal_value": 2059999999.9999998,
  "terminal_method": "gordon_growth",
  "pv_cashflows": 295266716.75432,
  "pv_terminal_value": 1547708489.8572495,
  "enterprise_value": 1842975206.6115694
}
```

## Multiples And Scenario

```bash
finance valuation.multiples NVDA
finance valuation.scenario IOT revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 shares=580M
```

A live NVIDIA multiples run returned market cap, enterprise value, revenue, P/S, and EV/S with source attribution from `market.quote` and `fundamentals.statement`.

A tested IOT scenario run used the provided share count and returned bear, base, and bull implied prices. Market-derived current prices are time-sensitive; do not hard-code them into tests.
