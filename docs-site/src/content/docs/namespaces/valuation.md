---
title: valuation
description: Valuation math, multiples, DCF, NPV, IRR, WACC, and scenarios.
---

# finance valuation

The `valuation.*` commands calculate valuation outputs from explicit assumptions and, for selected commands, provider-attributed market context.

These commands are calculators and data shapers. They do not decide whether a security is attractive and should not be presented as investment advice.

Large numeric inputs can use raw numbers or suffixes such as `K`, `M`, and `B` where the command accepts scaled numbers. Rate inputs accept decimals or percentages such as `0.10` and `10%`.

## finance valuation.dcf

Calculate DCF enterprise value from forecast cash flows.

### What it does

`finance valuation.dcf` calculates DCF enterprise value from forecast cash flows. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use it when forecast free cash flows and terminal assumptions are explicit.

Use either `terminal_growth` or `exit_multiple` for the terminal value assumption. Do not use this output as investment advice or infer assumptions silently.

### Usage

```bash
finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% [terminal_growth=3%|exit_multiple=15]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `cashflows` | Yes | None | Comma-separated values | Comma-separated cash-flow series. K/M/B suffixes are accepted. |
| `discount_rate` | Yes | None | Decimal rate or percent string | Discount rate. Percent strings are accepted. |
| `terminal_growth` | No | None | Decimal rate or percent string | Perpetuity growth rate for Gordon-growth terminal value. |
| `exit_multiple` | No | None | Number | Exit multiple alternative to terminal growth. |

### Basic usage

```bash
finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% terminal_growth=3% --output json
```

### Example output

This output was generated with `finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% terminal_growth=3% --output json`.

```json
{
  "ok": true,
  "data": {
    "cashflows": [
      100000000.0,
      120000000.0,
      140000000.0
    ],
    "discount_rate": 0.1,
    "terminal_growth": 0.03,
    "exit_multiple": null,
    "terminal_value": 2059999999.9999998,
    "terminal_method": "gordon_growth",
    "discounted_cashflows": [
      {
        "t": 1,
        "cashflow": 100000000.0,
        "present_value": 90909090.9090909
      },
      {
        "t": 2,
        "cashflow": 120000000.0,
        "present_value": 99173553.71900825
      },
      {
        "t": 3,
        "cashflow": 140000000.0,
        "present_value": 105184072.12622085
      }
    ],
    "pv_cashflows": 295266716.75432,
    "pv_terminal_value": 1547708489.8572495,
    "enterprise_value": 1842975206.6115694,
    "method": "forecast FCF only, discounted from t=1; do not include an initial t=0 investment cash flow",
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
| `data.cashflows` | array | Parsed cash-flow series after K/M/B suffix handling. |
| `data.discount_rate` | number | Parsed discount rate as a decimal. |
| `data.terminal_growth` | number | Parsed terminal growth rate as a decimal. |
| `data.exit_multiple` | null | Exit multiple terminal assumption when used. |
| `data.terminal_value` | number | Undiscounted terminal value. |
| `data.terminal_method` | string | Terminal value method. |
| `data.discounted_cashflows` | array | Per-period present values for forecast cash flows. |
| `data.discounted_cashflows[].t` | integer | Forecast period index, starting at 1. |
| `data.discounted_cashflows[].cashflow` | number | Forecast cash flow for that period. |
| `data.discounted_cashflows[].present_value` | number | Discounted present value for that period. |
| `data.pv_cashflows` | number | Present value of forecast-period cash flows. |
| `data.pv_terminal_value` | number | Present value of terminal value. |
| `data.enterprise_value` | number | Calculated enterprise value. |
| `data.method` | string | Formula or calculation convention used. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |

## finance valuation.irr

Calculate IRR for periodic cash flows.

### What it does

`finance valuation.irr` calculates IRR for periodic cash flows. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use for deterministic valuation math once assumptions are explicit.

Do not present valuation output as investment advice.

### Usage

```bash
finance valuation.irr cashflows=-100M,30M,40M,50M
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `cashflows` | Yes | None | Comma-separated values | Comma-separated cash-flow series. K/M/B suffixes are accepted. |

### Basic usage

```bash
finance valuation.irr cashflows=-100M,30M,40M,50M --output json
```

### Example output

This output was generated with `finance valuation.irr cashflows=-100M,30M,40M,50M --output json`.

```json
{
  "ok": true,
  "data": {
    "cashflows": [
      -100000000.0,
      30000000.0,
      40000000.0,
      50000000.0
    ],
    "irr": 0.08896339469334985,
    "method": "rate r where sum(cashflow_t / (1 + r)^t) = 0",
    "solver": "bisection_numeric_approximation",
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
| `data.cashflows` | array | Parsed cash-flow series after K/M/B suffix handling. |
| `data.irr` | number | Internal rate of return as a decimal. |
| `data.method` | string | Formula or calculation convention used. |
| `data.solver` | string | Numerical solver used for IRR. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |

## finance valuation.multiples

Calculate current sales multiples from market cap and revenue.

### What it does

`finance valuation.multiples` fetches current quote context and fundamental revenue, then calculates price-to-sales and enterprise-value-to-sales.

### When to use it

Use it when you need provider-attributed price-to-sales and EV-to-sales from current market context and provider revenue.

Do not present valuation output as investment advice.

### Usage

```bash
finance valuation.multiples SYMBOL
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | Text | Ticker symbol to value. |

### Basic usage

```bash
finance valuation.multiples IOT --output json
```

### Example output

This output was generated with `finance valuation.multiples IOT --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "price": 27.99,
    "market_cap": 16310054912.0,
    "enterprise_value": 15493225472.0,
    "cash": 833792000.0,
    "debt": 72768000.0,
    "net_debt": -761024000.0,
    "currency": "USD",
    "revenue": 1618635000.0,
    "revenue_period": "2026-01-31",
    "revenue_period_type": "FY",
    "multiples": {
      "price_to_sales": 10.076425452310126,
      "ev_to_sales": 9.571784541913402
    },
    "sources": [
      "market.quote",
      "fundamentals.statement"
    ],
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
| `data.symbol` | string | Ticker symbol used by the command. |
| `data.price` | number | Current provider quote price. |
| `data.market_cap` | number | Market capitalization returned by the provider. |
| `data.enterprise_value` | number | Calculated enterprise value. |
| `data.cash` | number | Cash returned by the command. |
| `data.debt` | number | Debt returned by the command. |
| `data.net_debt` | number | Debt minus excess cash. |
| `data.currency` | string | Currency code returned by the provider. |
| `data.revenue` | number | Revenue input or provider revenue value. |
| `data.revenue_period` | string | Period associated with provider revenue. |
| `data.revenue_period_type` | string | Revenue period type. |
| `data.multiples` | object | Calculated valuation multiples. |
| `data.multiples.price_to_sales` | number | Calculated multiple. |
| `data.multiples.ev_to_sales` | number | Calculated multiple. |
| `data.sources` | array | Provider/source commands used to shape the result. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |

## finance valuation.npv

Calculate NPV for periodic cash flows.

### What it does

`finance valuation.npv` calculates NPV for periodic cash flows. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use for deterministic valuation math once assumptions are explicit.

Do not present valuation output as investment advice.

### Usage

```bash
finance valuation.npv cashflows=-100M,30M,40M,50M discount_rate=10%
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `cashflows` | Yes | None | Comma-separated values | Comma-separated cash-flow series. K/M/B suffixes are accepted. |
| `discount_rate` | Yes | None | Decimal rate or percent string | Discount rate. Percent strings are accepted. |

### Basic usage

```bash
finance valuation.npv cashflows=-100M,30M,40M,50M discount_rate=10% --output json
```

### Example output

This output was generated with `finance valuation.npv cashflows=-100M,30M,40M,50M discount_rate=10% --output json`.

```json
{
  "ok": true,
  "data": {
    "cashflows": [
      -100000000.0,
      30000000.0,
      40000000.0,
      50000000.0
    ],
    "discount_rate": 0.1,
    "npv": -2103681.442524448,
    "method": "sum(cashflow_t / (1 + discount_rate)^t), with first cash flow at t=0",
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
| `data.cashflows` | array | Parsed cash-flow series after K/M/B suffix handling. |
| `data.discount_rate` | number | Parsed discount rate as a decimal. |
| `data.npv` | number | Net present value. |
| `data.method` | string | Formula or calculation convention used. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |

## finance valuation.scenario

Build a simple bull/base/bear sales-multiple scenario table.

### What it does

`finance valuation.scenario` combines user-supplied revenue, sales multiples, and share count with current quote context when available.

### When to use it

Use it when you have explicit revenue and sales-multiple assumptions and want bear/base/bull implied market caps or prices.

This is an assumption table, not a recommendation. Use it after documenting the source or rationale for revenue, multiple, and share-count inputs.

### Usage

```bash
finance valuation.scenario SYMBOL revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 [shares=580M]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | Text | Ticker symbol used for current quote context. |
| `revenue` | Yes | None | Number or K/M/B/T-suffixed number | Revenue input or assumption. |
| `bear_multiple` | Yes | None | Number | Bear-case sales multiple. |
| `base_multiple` | Yes | None | Number | Base-case sales multiple. |
| `bull_multiple` | Yes | None | Number | Bull-case sales multiple. |
| `shares` | No | `580M` | Number or K/M/B/T-suffixed number | Share count override. K/M/B suffixes are accepted. |

### Basic usage

```bash
finance valuation.scenario IOT revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 shares=580M --output json
```

### Example output

This output was generated with `finance valuation.scenario IOT revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 shares=580M --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "currency": "USD",
    "current_price": 27.99,
    "market_cap": 16310054912.0,
    "shares": 580000000.0,
    "shares_source": {
      "source": "user_input"
    },
    "assumptions": {
      "revenue": 2200000000.0,
      "multiple_basis": "price_to_sales"
    },
    "cases": [
      {
        "case": "bear",
        "revenue": 2200000000.0,
        "multiple": 7.0,
        "implied_market_cap": 15400000000.0,
        "implied_price": 26.551724137931036,
        "upside_pct": -5.1385346983528475
      },
      {
        "case": "base",
        "revenue": 2200000000.0,
        "multiple": 10.0,
        "implied_market_cap": 22000000000.0,
        "implied_price": 37.93103448275862,
        "upside_pct": 35.51637900235305
      },
      {
        "case": "bull",
        "revenue": 2200000000.0,
        "multiple": 13.0,
        "implied_market_cap": 28600000000.0,
        "implied_price": 49.310344827586206,
        "upside_pct": 76.17129270305898
      }
    ],
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
| `data.symbol` | string | Ticker symbol used by the command. |
| `data.currency` | string | Currency code returned by the provider. |
| `data.current_price` | number | Current provider quote price used for scenario upside. |
| `data.market_cap` | number | Market capitalization returned by the provider. |
| `data.shares` | number | Share count used in scenario calculations. |
| `data.shares_source` | object | Source of the share count. |
| `data.shares_source.source` | string | Source of the share-count input, such as `user_input` or provider context. |
| `data.assumptions` | object | User-supplied scenario assumptions after parsing. |
| `data.assumptions.revenue` | number | Revenue input or provider revenue value. |
| `data.assumptions.multiple_basis` | string | Multiple basis used for the scenario, such as `price_to_sales`. |
| `data.cases` | array | Bear/base/bull scenario rows. |
| `data.cases[].case` | string | Scenario label: `bear`, `base`, or `bull`. |
| `data.cases[].revenue` | number | Revenue input or provider revenue value. |
| `data.cases[].multiple` | number | Sales multiple used for the scenario row. |
| `data.cases[].implied_market_cap` | number | Revenue multiplied by the scenario multiple. |
| `data.cases[].implied_price` | number | Implied market cap divided by share count. |
| `data.cases[].upside_pct` | number | Implied price change versus current provider quote. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |

## finance valuation.wacc

Calculate weighted average cost of capital.

### What it does

`finance valuation.wacc` calculates weighted average cost of capital. It returns parsed inputs, calculated outputs, method metadata, and warnings in the standard JSON envelope.

### When to use it

Use for deterministic valuation math once assumptions are explicit.

Do not present valuation output as investment advice.

### Usage

```bash
finance valuation.wacc equity_value=10B debt_value=1B cost_of_equity=10% cost_of_debt=5% tax_rate=21%
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `equity_value` | Yes | None | Number or K/M/B/T-suffixed number | Market value of equity. |
| `debt_value` | Yes | None | Number or K/M/B/T-suffixed number | Debt value. |
| `cost_of_equity` | Yes | None | Decimal rate or percent string | Cost of equity. Percent strings are accepted. |
| `cost_of_debt` | Yes | None | Decimal rate or percent string | Cost of debt. Percent strings are accepted. |
| `tax_rate` | No | `0` | Decimal rate or percent string | Tax rate. Percent strings are accepted. |

### Basic usage

```bash
finance valuation.wacc equity_value=10B debt_value=1B cost_of_equity=10% cost_of_debt=5% tax_rate=21% --output json
```

### Example output

This output was generated with `finance valuation.wacc equity_value=10B debt_value=1B cost_of_equity=10% cost_of_debt=5% tax_rate=21% --output json`.

```json
{
  "ok": true,
  "data": {
    "wacc": 0.0945,
    "weights": {
      "equity": 0.9090909090909091,
      "debt": 0.09090909090909091
    },
    "inputs": {
      "equity_value": 10000000000.0,
      "debt_value": 1000000000.0,
      "cost_of_equity": 0.1,
      "cost_of_debt": 0.05,
      "tax_rate": 0.21
    },
    "method": "E/(D+E)*cost_of_equity + D/(D+E)*cost_of_debt*(1-tax_rate)",
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
| `data.method` | string | Formula or calculation convention used. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |
