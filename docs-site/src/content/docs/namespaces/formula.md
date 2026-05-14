---
title: formula
description: Deterministic finance formulas.
---

Use `formula.*` for calculator-style outputs. These commands do not fetch market data and are suitable for repeatable scripts and tests.

## Input Conventions

Most formula inputs accept plain numbers, percentages like `9.66%`, and scaled values such as `10B` when the underlying calculator parses money-like inputs. Missing required inputs fail with a usage error.

## Parameters

| Command | Required Parameters | Optional Parameters | Formula |
| --- | --- | --- | --- |
| `formula.ebitda` | `ebit`, `d_and_a` | None | `ebit + d_and_a` |
| `formula.adjusted_ebitda` | `ebit`, `d_and_a` | `addbacks` comma list | `ebit + d_and_a + sum(addbacks)` |
| `formula.margin` | `numerator`, `denominator` | None | `numerator / denominator` |
| `formula.days` | `current`, `prior`, `denominator` | `days=365` | Average balance days using the supplied day count. |
| `formula.turnover` | `numerator`, `current`, `prior` | None | Turnover using average balance. |
| `formula.operating_cash` | `revenue`, `cash_like_assets` | `percent_revenue=2%` | Operating cash is capped by cash-like assets. |
| `formula.lease_equivalent` | `base_liability`, `variable_cost`, `operating_cost` | None | Estimates lease equivalent from cost ratio. |
| `formula.capm` | `risk_free`, `beta`, `market_return` | None | CAPM cost of equity. |
| `formula.wacc` | `equity_value`, `debt_value`, `cost_of_equity`, `cost_of_debt` | `tax_rate=0`, `debt_tax=after_tax` | Weighted average cost of capital. `debt_tax` can be `pretax` or `after_tax`. |
| `formula.enterprise_value` | `market_equity` | `debt=0`, `cash=0`, `operating_cash=0` | Market equity plus debt minus excess cash. |
| `formula.roic` | `nopat`, `invested_capital` | None | `nopat / invested_capital` |
| `formula.cagr` | `start`, `end`, `periods` | None | Compound annual growth rate. |
| `formula.net_debt` | `debt`, `cash` | `operating_cash=0` | Debt minus excess cash. |
| `formula.operating_current_assets` | `current_assets` | `cash_like_assets=0`, `operating_cash=0` | Removes excess cash from current assets. |
| `formula.operating_current_liabilities` | `current_liabilities` | `interest_bearing_current_debt=0` | Removes interest-bearing current debt. |
| `formula.working_capital` | `operating_current_assets`, `operating_current_liabilities` | None | Operating current assets minus operating current liabilities. |

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

Tested result highlights:

```json
{
  "formula.ebitda": { "ebitda": 11522.0, "method": "ebit + d_and_a" },
  "formula.wacc": {
    "wacc": 0.0945,
    "weights": { "equity": 0.9090909090909091, "debt": 0.09090909090909091 }
  },
  "formula.roic": { "roic": 0.2533390319478577, "roic_pct": 25.33390319478577 },
  "formula.working_capital": { "working_capital": -6844.0 }
}
```

Run `finance help formula` for the complete calculator list.
