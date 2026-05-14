---
title: formula
description: Deterministic finance formulas.
---

Use `formula.*` for calculator-style outputs. These commands do not fetch market data and are suitable for repeatable scripts and tests.

## Margin

```bash
finance formula.margin numerator=11969 denominator=254453
```

Tested result:

```json
{
  "margin": 0.04703815635893466,
  "margin_pct": 4.7038156358934655,
  "inputs": {
    "numerator": 11969.0,
    "denominator": 254453.0
  },
  "method": "numerator / denominator"
}
```

## Net Debt

```bash
finance formula.net_debt debt=11415 cash=11144 operating_cash=5089
```

Tested result:

```json
{
  "net_debt": 5360.0,
  "excess_cash": 6055.0,
  "method": "debt - max(cash - operating_cash, 0)"
}
```

## Other Calculators

```bash
finance formula.ebitda ebit=9285 d_and_a=2237
finance formula.wacc equity_value=10B debt_value=1B cost_of_equity=10% cost_of_debt=5% tax_rate=21%
finance formula.roic nopat=7113 invested_capital=28077
finance formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035
```

Run `finance help formula` for the complete calculator list.
