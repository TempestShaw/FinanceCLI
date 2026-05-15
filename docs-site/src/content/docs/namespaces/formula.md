---
title: formula
description: Deterministic finance formulas.
---

# finance formula

The `formula.*` commands are deterministic calculators. They do not fetch provider data and only use numeric inputs supplied on the command line.

Use this namespace after you have explicit, cited inputs from filings, documents, transcripts, or your own model assumptions.

Large numeric inputs can use raw numbers or suffixes such as `K`, `M`, and `B` where the command accepts scaled numbers. Rate inputs accept decimals or percentages such as `0.10` and `10%`.

## finance formula.adjusted_ebitda

Calculate adjusted EBITDA from explicit addbacks.

### What it does

`finance formula.adjusted_ebitda` calculates adjusted EBITDA from explicit addbacks. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when EBIT, depreciation/amortization, and addbacks are explicit and you need adjusted EBITDA.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.adjusted_ebitda ebit=9285 d_and_a=2237 addbacks=284,163
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `ebit` | Yes | None | Number or K/M/B/T-suffixed number | Earnings before interest and taxes. |
| `d_and_a` | Yes | None | Number or K/M/B/T-suffixed number | Depreciation and amortization. |
| `addbacks` | No | `[]` | Comma-separated values | Comma-separated adjustment addbacks. |

### Basic usage

```bash
finance formula.adjusted_ebitda ebit=9285 d_and_a=2237 addbacks=284,163 --output json
```

### Example output

This output was generated with `finance formula.adjusted_ebitda ebit=9285 d_and_a=2237 addbacks=284,163 --output json`.

```json
{
  "ok": true,
  "data": {
    "adjusted_ebitda": 11969.0,
    "inputs": {
      "ebit": 9285.0,
      "d_and_a": 2237.0,
      "addbacks": [
        284.0,
        163.0
      ]
    },
    "method": "ebit + d_and_a + sum(addbacks)"
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
| `data.adjusted_ebitda` | number | Calculated adjusted EBITDA. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.ebit` | number | Parsed input value used by the formula. |
| `data.inputs.d_and_a` | number | Parsed input value used by the formula. |
| `data.inputs.addbacks` | array | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.cagr

Calculate compound annual growth rate.

### What it does

`finance formula.cagr` calculates compound annual growth rate. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when start value, end value, and periods are explicit.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.cagr start=100 end=150 periods=3
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `start` | Yes | None | Number or K/M/B/T-suffixed number | Beginning value. |
| `end` | Yes | None | Number or K/M/B/T-suffixed number | Ending value. |
| `periods` | Yes | None | Number or K/M/B/T-suffixed number | Number of compounding periods. |

### Basic usage

```bash
finance formula.cagr start=100 end=150 periods=3 --output json
```

### Example output

This output was generated with `finance formula.cagr start=100 end=150 periods=3 --output json`.

```json
{
  "ok": true,
  "data": {
    "cagr": 0.14471424255333187,
    "cagr_pct": 14.471424255333186,
    "inputs": {
      "start": 100.0,
      "end": 150.0,
      "periods": 3.0
    },
    "method": "(end / start) ** (1 / periods) - 1"
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
| `data.cagr` | number | Compound annual growth rate as a decimal. |
| `data.cagr_pct` | number | Compound annual growth rate as a percentage. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.start` | number | Parsed input value used by the formula. |
| `data.inputs.end` | number | Parsed input value used by the formula. |
| `data.inputs.periods` | number | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.capm

Calculate CAPM cost of equity.

### What it does

`finance formula.capm` calculates CAPM cost of equity. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when risk-free rate, beta, and market return are explicit.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.capm risk_free=4.617% beta=0.79 market_return=11%
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `risk_free` | Yes | None | Decimal rate or percent string | Risk-free rate. Percent strings such as `4.617%` are accepted. |
| `beta` | Yes | None | Number or K/M/B/T-suffixed number | Equity beta. |
| `market_return` | Yes | None | Decimal rate or percent string | Expected market return. Percent strings are accepted. |

### Basic usage

```bash
finance formula.capm risk_free=4.617% beta=0.79 market_return=11% --output json
```

### Example output

This output was generated with `finance formula.capm risk_free=4.617% beta=0.79 market_return=11% --output json`.

```json
{
  "ok": true,
  "data": {
    "cost_of_equity": 0.0965957,
    "inputs": {
      "risk_free": 0.04617,
      "beta": 0.79,
      "market_return": 0.11
    },
    "method": "risk_free + beta * (market_return - risk_free)",
    "warnings": []
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
| `data.cost_of_equity` | number | CAPM cost of equity as a decimal. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.risk_free` | number | Parsed input value used by the formula. |
| `data.inputs.beta` | number | Parsed input value used by the formula. |
| `data.inputs.market_return` | number | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |

## finance formula.days

Calculate average-balance days.

### What it does

`finance formula.days` calculates average-balance days. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when you need days-sales, days-inventory, or another average-balance days metric from explicit balances and denominator.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.days current=2721 prior=2285 denominator=254453 [days=365]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `current` | Yes | None | Number or K/M/B/T-suffixed number | Current-period balance. |
| `prior` | Yes | None | Number or K/M/B/T-suffixed number | Prior-period balance. |
| `denominator` | Yes | None | Number or K/M/B/T-suffixed number | Denominator used for the days or margin calculation. |
| `days` | No | `365` | Number or K/M/B/T-suffixed number | Day-count basis. |

### Basic usage

```bash
finance formula.days current=2721 prior=2285 denominator=254453 --output json
```

### Example output

This output was generated with `finance formula.days current=2721 prior=2285 denominator=254453 --output json`.

```json
{
  "ok": true,
  "data": {
    "days": 3.5904273087760807,
    "average_balance": 2503.0,
    "inputs": {
      "current": 2721.0,
      "prior": 2285.0,
      "denominator": 254453.0,
      "days": 365.0
    },
    "method": "((current + prior) / 2) / denominator * days"
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
| `data.days` | number | Average-balance days result. |
| `data.average_balance` | number | Average of current and prior balances. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.current` | number | Parsed input value used by the formula. |
| `data.inputs.prior` | number | Parsed input value used by the formula. |
| `data.inputs.denominator` | number | Parsed input value used by the formula. |
| `data.inputs.days` | number | Average-balance days result. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.ebitda

Calculate EBITDA from explicit EBIT and D&A inputs.

### What it does

`finance formula.ebitda` calculates EBITDA from explicit EBIT and D&A inputs. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when EBIT and depreciation/amortization are explicit and you need EBITDA.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.ebitda ebit=9285 d_and_a=2237
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `ebit` | Yes | None | Number or K/M/B/T-suffixed number | Earnings before interest and taxes. |
| `d_and_a` | Yes | None | Number or K/M/B/T-suffixed number | Depreciation and amortization. |

### Basic usage

```bash
finance formula.ebitda ebit=9285 d_and_a=2237 --output json
```

### Example output

This output was generated with `finance formula.ebitda ebit=9285 d_and_a=2237 --output json`.

```json
{
  "ok": true,
  "data": {
    "ebitda": 11522.0,
    "inputs": {
      "ebit": 9285.0,
      "d_and_a": 2237.0
    },
    "method": "ebit + d_and_a"
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
| `data.ebitda` | number | Calculated EBITDA. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.ebit` | number | Parsed input value used by the formula. |
| `data.inputs.d_and_a` | number | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.enterprise_value

Calculate enterprise value with explicit operating cash.

### What it does

`finance formula.enterprise_value` calculates enterprise value with explicit operating cash. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when market equity, debt, cash, and operating cash are explicit and you need enterprise value.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.enterprise_value market_equity=418856 debt=11415 cash=11144 operating_cash=5089
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `market_equity` | Yes | None | Number or K/M/B/T-suffixed number | Market value of equity. |
| `debt` | No | `0` | Number or K/M/B/T-suffixed number | Debt value. |
| `cash` | No | `0` | Number or K/M/B/T-suffixed number | Cash and cash-like assets. |
| `operating_cash` | No | `0` | Number or K/M/B/T-suffixed number | Cash treated as operating rather than excess. |

### Basic usage

```bash
finance formula.enterprise_value market_equity=418856 debt=11415 cash=11144 operating_cash=5089 --output json
```

### Example output

This output was generated with `finance formula.enterprise_value market_equity=418856 debt=11415 cash=11144 operating_cash=5089 --output json`.

```json
{
  "ok": true,
  "data": {
    "enterprise_value": 424216.0,
    "excess_cash": 6055.0,
    "inputs": {
      "market_equity": 418856.0,
      "debt": 11415.0,
      "cash": 11144.0,
      "operating_cash": 5089.0
    },
    "method": "market_equity + debt - max(cash - operating_cash, 0)"
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
| `data.enterprise_value` | number | Calculated enterprise value. |
| `data.excess_cash` | number | Cash above operating cash. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.market_equity` | number | Parsed input value used by the formula. |
| `data.inputs.debt` | number | Parsed input value used by the formula. |
| `data.inputs.cash` | number | Parsed input value used by the formula. |
| `data.inputs.operating_cash` | number | Calculated operating cash. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.lease_equivalent

Estimate lease equivalent from cost ratio.

### What it does

`finance formula.lease_equivalent` estimates lease equivalent from cost ratio. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when base lease liability and lease cost components are explicit and you want a proportional lease equivalent.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.lease_equivalent base_liability=2554 variable_cost=163 operating_cost=284
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `base_liability` | Yes | None | Number or K/M/B/T-suffixed number | Base lease liability. |
| `variable_cost` | Yes | None | Number or K/M/B/T-suffixed number | Variable lease cost. |
| `operating_cost` | Yes | None | Number or K/M/B/T-suffixed number | Operating lease cost. |

### Basic usage

```bash
finance formula.lease_equivalent base_liability=2554 variable_cost=163 operating_cost=284 --output json
```

### Example output

This output was generated with `finance formula.lease_equivalent base_liability=2554 variable_cost=163 operating_cost=284 --output json`.

```json
{
  "ok": true,
  "data": {
    "lease_equivalent": 1465.8521126760563,
    "ratio": 0.573943661971831,
    "inputs": {
      "base_liability": 2554.0,
      "variable_cost": 163.0,
      "operating_cost": 284.0
    },
    "method": "base_liability * (variable_cost / operating_cost)"
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
| `data.lease_equivalent` | number | Calculated lease-equivalent liability. |
| `data.ratio` | number | Lease cost ratio used by the calculation. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.base_liability` | number | Parsed input value used by the formula. |
| `data.inputs.variable_cost` | number | Parsed input value used by the formula. |
| `data.inputs.operating_cost` | number | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.margin

Calculate numerator / denominator.

### What it does

`finance formula.margin` calculates numerator / denominator. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when you need a ratio such as margin, yield, conversion rate, or any explicit numerator divided by denominator.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.margin numerator=11969 denominator=254453
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `numerator` | Yes | None | Number or K/M/B/T-suffixed number | Numerator for the ratio. |
| `denominator` | Yes | None | Number or K/M/B/T-suffixed number | Denominator used for the days or margin calculation. |

### Basic usage

```bash
finance formula.margin numerator=11969 denominator=254453 --output json
```

### Example output

This output was generated with `finance formula.margin numerator=11969 denominator=254453 --output json`.

```json
{
  "ok": true,
  "data": {
    "margin": 0.04703815635893466,
    "margin_pct": 4.7038156358934655,
    "inputs": {
      "numerator": 11969.0,
      "denominator": 254453.0
    },
    "method": "numerator / denominator"
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
| `data.margin` | number | Ratio as a decimal. |
| `data.margin_pct` | number | Ratio as a percentage. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.numerator` | number | Parsed input value used by the formula. |
| `data.inputs.denominator` | number | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.net_debt

Calculate net debt with explicit operating cash.

### What it does

`finance formula.net_debt` calculates net debt with explicit operating cash. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when debt, cash, and operating cash are explicit and you need debt net of excess cash.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.net_debt debt=11415 cash=11144 [operating_cash=5089]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `debt` | Yes | None | Number or K/M/B/T-suffixed number | Debt value. |
| `cash` | Yes | None | Number or K/M/B/T-suffixed number | Cash and cash-like assets. |
| `operating_cash` | No | `5089` | Number or K/M/B/T-suffixed number | Cash treated as operating rather than excess. |

### Basic usage

```bash
finance formula.net_debt debt=11415 cash=11144 operating_cash=5089 --output json
```

### Example output

This output was generated with `finance formula.net_debt debt=11415 cash=11144 operating_cash=5089 --output json`.

```json
{
  "ok": true,
  "data": {
    "net_debt": 5360.0,
    "excess_cash": 6055.0,
    "inputs": {
      "debt": 11415.0,
      "cash": 11144.0,
      "operating_cash": 5089.0
    },
    "method": "debt - max(cash - operating_cash, 0)"
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
| `data.net_debt` | number | Debt minus excess cash. |
| `data.excess_cash` | number | Cash above operating cash. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.debt` | number | Parsed input value used by the formula. |
| `data.inputs.cash` | number | Parsed input value used by the formula. |
| `data.inputs.operating_cash` | number | Calculated operating cash. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.operating_cash

Calculate operating cash as min(percent of revenue, cash-like assets).

### What it does

`finance formula.operating_cash` calculates operating cash as min(percent of revenue, cash-like assets). It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when you want to cap operating cash at a percentage of revenue, limited by available cash-like assets.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.operating_cash revenue=254453 cash_like_assets=11144 [percent_revenue=2%]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `revenue` | Yes | None | Number or K/M/B/T-suffixed number | Revenue input or assumption. |
| `cash_like_assets` | Yes | None | Number or K/M/B/T-suffixed number | Cash and cash-like assets. |
| `percent_revenue` | No | `2%` | Decimal rate or percent string | Revenue percentage used as the operating-cash cap. |

### Basic usage

```bash
finance formula.operating_cash revenue=254453 cash_like_assets=11144 percent_revenue=2% --output json
```

### Example output

This output was generated with `finance formula.operating_cash revenue=254453 cash_like_assets=11144 percent_revenue=2% --output json`.

```json
{
  "ok": true,
  "data": {
    "operating_cash": 5089.06,
    "revenue_cap": 5089.06,
    "cash_like_assets": 11144.0,
    "inputs": {
      "revenue": 254453.0,
      "cash_like_assets": 11144.0,
      "percent_revenue": 0.02
    },
    "method": "min(revenue * percent_revenue, cash_like_assets)",
    "warnings": []
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
| `data.operating_cash` | number | Calculated operating cash. |
| `data.revenue_cap` | number | Revenue multiplied by percent-of-revenue cap. |
| `data.cash_like_assets` | number | Cash like assets returned by the command. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.revenue` | number | Revenue input or provider revenue value. |
| `data.inputs.cash_like_assets` | number | Parsed input value used by the formula. |
| `data.inputs.percent_revenue` | number | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |

## finance formula.operating_current_assets

Calculate operating current assets.

### What it does

`finance formula.operating_current_assets` calculates operating current assets. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when current assets, cash-like assets, and operating cash are explicit.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.operating_current_assets current_assets=34246 [cash_like_assets=11144 operating_cash=5089]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `current_assets` | Yes | None | Number or K/M/B/T-suffixed number | Current assets. |
| `cash_like_assets` | No | `11144` | Number or K/M/B/T-suffixed number | Cash and cash-like assets. |
| `operating_cash` | No | `5089` | Number or K/M/B/T-suffixed number | Cash treated as operating rather than excess. |

### Basic usage

```bash
finance formula.operating_current_assets current_assets=34246 cash_like_assets=11144 operating_cash=5089 --output json
```

### Example output

This output was generated with `finance formula.operating_current_assets current_assets=34246 cash_like_assets=11144 operating_cash=5089 --output json`.

```json
{
  "ok": true,
  "data": {
    "operating_current_assets": 28191.0,
    "inputs": {
      "current_assets": 34246.0,
      "cash_like_assets": 11144.0,
      "operating_cash": 5089.0
    },
    "method": "current_assets - cash_like_assets + operating_cash"
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
| `data.operating_current_assets` | number | Calculated operating current assets. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.current_assets` | number | Parsed input value used by the formula. |
| `data.inputs.cash_like_assets` | number | Parsed input value used by the formula. |
| `data.inputs.operating_cash` | number | Calculated operating cash. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.operating_current_liabilities

Calculate operating current liabilities.

### What it does

`finance formula.operating_current_liabilities` calculates operating current liabilities. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when current liabilities and interest-bearing current debt are explicit.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.operating_current_liabilities current_liabilities=35464 [interest_bearing_current_debt=103]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `current_liabilities` | Yes | None | Number or K/M/B/T-suffixed number | Current liabilities. |
| `interest_bearing_current_debt` | No | `103` | Number or K/M/B/T-suffixed number | Interest-bearing debt included in current liabilities. |

### Basic usage

```bash
finance formula.operating_current_liabilities current_liabilities=35464 interest_bearing_current_debt=103 --output json
```

### Example output

This output was generated with `finance formula.operating_current_liabilities current_liabilities=35464 interest_bearing_current_debt=103 --output json`.

```json
{
  "ok": true,
  "data": {
    "operating_current_liabilities": 35361.0,
    "inputs": {
      "current_liabilities": 35464.0,
      "interest_bearing_current_debt": 103.0
    },
    "method": "current_liabilities - interest_bearing_current_debt"
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
| `data.operating_current_liabilities` | number | Calculated operating current liabilities. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.current_liabilities` | number | Parsed input value used by the formula. |
| `data.inputs.interest_bearing_current_debt` | number | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.roic

Calculate ROIC from NOPAT and invested capital.

### What it does

`finance formula.roic` calculates ROIC from NOPAT and invested capital. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when NOPAT and invested capital are explicit.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.roic nopat=7113 invested_capital=28077
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `nopat` | Yes | None | Number or K/M/B/T-suffixed number | Net operating profit after tax. |
| `invested_capital` | Yes | None | Number or K/M/B/T-suffixed number | Invested capital. |

### Basic usage

```bash
finance formula.roic nopat=7113 invested_capital=28077 --output json
```

### Example output

This output was generated with `finance formula.roic nopat=7113 invested_capital=28077 --output json`.

```json
{
  "ok": true,
  "data": {
    "roic": 0.2533390319478577,
    "roic_pct": 25.33390319478577,
    "inputs": {
      "nopat": 7113.0,
      "invested_capital": 28077.0
    },
    "method": "nopat / invested_capital"
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
| `data.roic` | number | ROIC as a decimal. |
| `data.roic_pct` | number | ROIC as a percentage. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.nopat` | number | Parsed input value used by the formula. |
| `data.inputs.invested_capital` | number | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.turnover

Calculate turnover using average balance.

### What it does

`finance formula.turnover` calculates turnover using average balance. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when you need a turnover ratio using an average balance.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.turnover numerator=222358 current=18647 prior=16651
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `numerator` | Yes | None | Number or K/M/B/T-suffixed number | Numerator for the ratio. |
| `current` | Yes | None | Number or K/M/B/T-suffixed number | Current-period balance. |
| `prior` | Yes | None | Number or K/M/B/T-suffixed number | Prior-period balance. |

### Basic usage

```bash
finance formula.turnover numerator=222358 current=18647 prior=16651 --output json
```

### Example output

This output was generated with `finance formula.turnover numerator=222358 current=18647 prior=16651 --output json`.

```json
{
  "ok": true,
  "data": {
    "turnover": 12.598900787580034,
    "average_balance": 17649.0,
    "inputs": {
      "numerator": 222358.0,
      "current": 18647.0,
      "prior": 16651.0
    },
    "method": "numerator / ((current + prior) / 2)"
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
| `data.turnover` | number | Turnover ratio. |
| `data.average_balance` | number | Average of current and prior balances. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.numerator` | number | Parsed input value used by the formula. |
| `data.inputs.current` | number | Parsed input value used by the formula. |
| `data.inputs.prior` | number | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |

## finance formula.wacc

Calculate WACC with explicit debt tax convention.

### What it does

`finance formula.wacc` calculates WACC with explicit debt tax convention. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when cost of equity, cost of debt, capital structure, tax rate, and debt-tax convention are explicit.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.wacc equity_value=418856 debt_value=11415 cost_of_equity=9.66% cost_of_debt=6% tax_rate=24% debt_tax=pretax|after_tax
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `equity_value` | Yes | None | Number or K/M/B/T-suffixed number | Market value of equity. |
| `debt_value` | Yes | None | Number or K/M/B/T-suffixed number | Debt value. |
| `cost_of_equity` | Yes | None | Decimal rate or percent string | Cost of equity. Percent strings are accepted. |
| `cost_of_debt` | Yes | None | Decimal rate or percent string | Cost of debt. Percent strings are accepted. |
| `tax_rate` | No | `0` | Decimal rate or percent string | Tax rate. Percent strings are accepted. |
| `debt_tax` | No | `after_tax` | `pretax`, `after_tax` | Whether `cost_of_debt` is pre-tax or already after-tax. |

### Basic usage

```bash
finance formula.wacc equity_value=418856 debt_value=11415 cost_of_equity=9.66% cost_of_debt=6% tax_rate=24% debt_tax=pretax --output json
```

### Example output

This output was generated with `finance formula.wacc equity_value=418856 debt_value=11415 cost_of_equity=9.66% cost_of_debt=6% tax_rate=24% debt_tax=pretax --output json`.

```json
{
  "ok": true,
  "data": {
    "wacc": 0.09562900962416711,
    "weights": {
      "equity": 0.9734702083105764,
      "debt": 0.026529791689423644
    },
    "inputs": {
      "equity_value": 418856.0,
      "debt_value": 11415.0,
      "cost_of_equity": 0.0966,
      "cost_of_debt": 0.06,
      "tax_rate": 0.24,
      "debt_tax": "pretax"
    },
    "method": "E/(D+E)*cost_of_equity + D/(D+E)*cost_of_debt, tax-adjusted only when debt_tax=after_tax",
    "warnings": []
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
| `data.wacc` | number | Weighted average cost of capital as a decimal. |
| `data.weights` | object | Capital structure weights used by WACC calculations. |
| `data.weights.equity` | number | Capital structure weight. |
| `data.weights.debt` | number | Capital structure weight. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.equity_value` | number | Parsed input value used by the formula. |
| `data.inputs.debt_value` | number | Parsed input value used by the formula. |
| `data.inputs.cost_of_equity` | number | CAPM cost of equity as a decimal. |
| `data.inputs.cost_of_debt` | number | Parsed input value used by the formula. |
| `data.inputs.tax_rate` | number | Parsed input value used by the formula. |
| `data.inputs.debt_tax` | string | Parsed input value used by the formula. |
| `data.method` | string | Formula or calculation convention used. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |

## finance formula.working_capital

Calculate operating working capital.

### What it does

`finance formula.working_capital` calculates operating working capital. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it after calculating operating current assets and operating current liabilities.

If an input is missing, provide it explicitly or extract it with another command before running the calculator.

### Usage

```bash
finance formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `operating_current_assets` | Yes | None | Number or K/M/B/T-suffixed number | Operating current assets. |
| `operating_current_liabilities` | Yes | None | Number or K/M/B/T-suffixed number | Operating current liabilities. |

### Basic usage

```bash
finance formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035 --output json
```

### Example output

This output was generated with `finance formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035 --output json`.

```json
{
  "ok": true,
  "data": {
    "working_capital": -6844.0,
    "inputs": {
      "operating_current_assets": 28191.0,
      "operating_current_liabilities": 35035.0
    },
    "method": "operating_current_assets - operating_current_liabilities"
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
| `data.working_capital` | number | Operating current assets minus operating current liabilities. |
| `data.inputs` | object | Parsed numeric inputs used by the calculation. |
| `data.inputs.operating_current_assets` | number | Calculated operating current assets. |
| `data.inputs.operating_current_liabilities` | number | Calculated operating current liabilities. |
| `data.method` | string | Formula or calculation convention used. |
