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

Tested inventory returned `buy_hold`, `sma_cross`, `rsi_reversion`, and `momentum_top_n`. `sma_cross` described default windows of fast `20` and slow `100`.

## Run And Tune

```bash
finance backtest.run buy_hold AAPL 2024-01-01 2024-03-31 fees=0
finance backtest.tune sma_cross AAPL 2024-01-01 2024-06-30 grid='{"fast":[5,10],"slow":[30]}' metric=total_return_pct fees=0
```

A tested buy-and-hold run returned 61 rows from Yahoo Finance with total return and an equity curve. A tested tune run evaluated two parameter combinations and selected fast `5`, slow `30` by `total_return_pct`.

Backtests use historical data from providers. They are research tools, not execution systems or performance guarantees.

## Factor Weights

```bash
finance backtest.factor.weights rsi_14 scores='{"AAPL":1.1,"MSFT":0.3,"NVDA":2.0,"TSLA":-1.0}' top_pct=0.25 bottom_pct=0.25
```

Tested output assigned `NVDA` a long weight, `TSLA` a short weight, and zero weight to the middle names, with gross exposure `1.0` and net exposure `0.0`.
