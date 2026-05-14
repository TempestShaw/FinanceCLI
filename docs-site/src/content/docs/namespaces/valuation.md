---
title: valuation
description: Valuation math, multiples, DCF, NPV, IRR, WACC, and scenarios.
---

Use `valuation.*` for valuation workflows that combine deterministic math with optional live market or fundamental inputs.

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
