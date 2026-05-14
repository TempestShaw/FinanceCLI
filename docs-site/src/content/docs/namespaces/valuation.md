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
  "npv": -2103681.442524448,
  "method": "First cash flow is treated as t=0; later cash flows are discounted by period."
}
```

Tested DCF output returned enterprise value `1842975206.6115694` using the Gordon-growth terminal method.

## Multiples And Scenario

```bash
finance valuation.multiples NVDA
finance valuation.scenario IOT revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 shares=580M
```

A live NVIDIA multiples run returned market cap, enterprise value, revenue, P/S, and EV/S with source attribution from `market.quote` and `fundamentals.statement`.

A tested IOT scenario run used the provided share count and returned bear, base, and bull implied prices. Market-derived current prices are time-sensitive; do not hard-code them into tests.
