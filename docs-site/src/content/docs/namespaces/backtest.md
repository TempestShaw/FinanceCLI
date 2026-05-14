---
title: backtest
description: VectorBT strategy runs, tuning, and factor payload helpers.
---

Use `backtest.*` to inspect built-in strategies, run historical strategy tests, tune parameters, or prepare factor weights.

## Strategy Inventory

```bash
finance backtest.strategies
finance backtest.describe sma_cross
```

Tested `backtest.strategies` result:

```json
{
  "engine": "vectorbt",
  "strategies": [
    {
      "name": "buy_hold",
      "summary": "Equal-weight buy and hold across all symbols.",
      "parameters": {}
    },
    {
      "name": "sma_cross",
      "parameters": {
        "fast": { "default": 20, "type": "integer" },
        "slow": { "default": 100, "type": "integer" }
      }
    }
  ]
}
```

Tested `backtest.describe sma_cross` result:

```json
{
  "name": "sma_cross",
  "summary": "Long when a fast moving average crosses above a slow moving average.",
  "parameters": {
    "fast": { "default": 20, "type": "integer" },
    "slow": { "default": 100, "type": "integer" }
  },
  "engine": "vectorbt"
}
```

## Run And Tune

```bash
finance backtest.run buy_hold AAPL 2024-01-01 2024-03-31 fees=0
finance backtest.tune sma_cross AAPL 2024-01-01 2024-06-30 grid='{"fast":[5,10],"slow":[30]}' metric=total_return_pct fees=0
```

A tested buy-and-hold run returned 61 Yahoo Finance rows, an equity curve, and `total_return_pct` of `-7.627668` for the requested window. A tested tune run evaluated two parameter combinations and selected fast `5`, slow `30` by `total_return_pct`.

Backtests use historical data from providers. They are research tools, not execution systems or performance guarantees.

## Factor Weights

```bash
finance backtest.factor.weights rsi_14 scores='{"AAPL":1.1,"MSFT":0.3,"NVDA":2.0,"TSLA":-1.0}' top_pct=0.25 bottom_pct=0.25
```

Tested output:

```json
{
  "run_type": "factor_rebalance_preview",
  "factor_name": "rsi_14",
  "weights": {
    "AAPL": 0.0,
    "MSFT": 0.0,
    "NVDA": 0.5,
    "TSLA": -0.5
  },
  "gross_exposure": 1.0,
  "net_exposure": 0.0
}
```
