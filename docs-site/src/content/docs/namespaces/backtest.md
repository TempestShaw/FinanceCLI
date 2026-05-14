---
title: backtest
description: VectorBT strategy runs, tuning, and factor payload helpers.
---

Use `backtest.*` to inspect built-in strategies, run historical strategy tests, tune parameters, or prepare factor weights.

## Parameters

### `backtest.strategies`

No parameters. Lists built-in strategy presets and their declared parameters.

### `backtest.describe`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `STRATEGY` | Yes | None | Built-in strategy name or `custom` | Strategy to describe. |

### `backtest.run`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `STRATEGY` | Yes | None | Built-in strategy name or `custom` | Strategy to run. |
| `SYMBOLS` | Yes | None | Ticker or comma-separated tickers | Backtest universe. |
| `START_DATE` | Yes | None | `YYYY-MM-DD` | Backtest start date. |
| `END_DATE` | Yes | None | `YYYY-MM-DD` | Backtest end date. |
| `timeframe` | No | `1d` | Provider-supported timeframe | OHLCV bar interval. |
| `initial_cash` | No | `100000.0` | Number | Starting portfolio cash. |
| `fees` | No | `0.001` | Decimal | Percentage trading fee used by the VectorBT engine. |
| `fixed_fees` | No | `0.0` | Number | Fixed fee per trade/order. |
| `slippage` | No | `0.0` | Decimal | Slippage assumption. |
| `provider` | No | `auto` | `auto`, provider name | OHLCV provider. |
| `params` | No | `{}` | JSON object | Strategy parameters as one JSON object. |
| `strategy_file` / `path` | No | None | Python file path | Custom strategy file. |
| `plot_path` | No | None | File path | Optional plot output path. |
| Other `key=value` args | No | None | Scalars | Any non-reserved key is passed as a strategy parameter. For `sma_cross`, use `fast=` and `slow=`. |

### `backtest.tune`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `STRATEGY` | Yes | None | Built-in strategy name or `custom` | Strategy to tune. |
| `SYMBOLS` | Yes | None | Ticker or comma-separated tickers | Backtest universe. |
| `START_DATE` | Yes | None | `YYYY-MM-DD` | Backtest start date. |
| `END_DATE` | Yes | None | `YYYY-MM-DD` | Backtest end date. |
| `grid` | Yes | None | JSON object | Parameter grid, such as `{"fast":[5,10],"slow":[30]}`. |
| `metric` | No | `sharpe_ratio` | Metric name | Ranking metric for best run. |
| `max_runs` | No | `100` | Integer | Hard cap on grid evaluations. |
| `timeframe` | No | `1d` | Provider-supported timeframe | OHLCV bar interval. |
| `initial_cash` | No | `100000.0` | Number | Starting portfolio cash. |
| `fees` | No | `0.001` | Decimal | Percentage trading fee. |
| `fixed_fees` | No | `0.0` | Number | Fixed fee per trade/order. |
| `slippage` | No | `0.0` | Decimal | Slippage assumption. |
| `provider` | No | `auto` | `auto`, provider name | OHLCV provider. |
| `strategy_file` / `path` | No | None | Python file path | Custom strategy file. |

### `backtest.strategy.payload`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `STRATEGY_ID` | Yes | None | Text | Strategy identifier to place in the normalized payload. |
| `START_DATE` | Yes | None | `YYYY-MM-DD` | Payload start date. |
| `END_DATE` | Yes | None | `YYYY-MM-DD` | Payload end date. |
| `initial_cash` | No | `100000.0` | Number | Starting cash. |
| `parameters` | No | `{}` | JSON object | Strategy parameter payload. |
| `fee_mode` | No | `mixed` | Text | Fee model label in payload. |
| `fixed_fee` | No | `2.0` | Number | Fixed fee in payload. |
| `fees_pct` | No | `0.001` | Decimal | Percentage fee in payload. |

### `backtest.factor.payload`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `FACTOR_NAME` | Yes | None | Text | Factor identifier. |
| `SYMBOLS` | Yes | None | Comma-separated tickers | Factor universe. |
| `START_DATE` | Yes | None | `YYYY-MM-DD` | Payload start date. |
| `END_DATE` | Yes | None | `YYYY-MM-DD` | Payload end date. |
| `timeframe` | No | `1d` | Provider-supported timeframe | Bar interval. |
| `initial_cash` | No | `100000.0` | Number | Starting cash. |
| `direction` | No | `long_short` | `long_short` or strategy-supported value | Factor direction. |
| `top_pct` | No | `0.2` | Decimal | Long basket quantile share. |
| `bottom_pct` | No | `0.2` | Decimal | Short basket quantile share. |
| `rebalance_freq` | No | `monthly` | Text | Rebalance frequency label. |
| `fixed_fee` | No | `2.0` | Number | Fixed fee in payload. |
| `fees_pct` | No | `0.001` | Decimal | Percentage fee in payload. |

### `backtest.factor.weights`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `FACTOR_NAME` | Yes | None | Text | Factor identifier. |
| `scores` | Yes | None | JSON object of `{symbol: score}` | Cross-sectional factor scores. |
| `timestamp` | No | `preview` | Text | Timestamp label in preview output. |
| `direction` | No | `long_short` | `long_short` or strategy-supported value | Weighting direction. |
| `top_pct` | No | `0.2` | Decimal | Long basket quantile share. |
| `bottom_pct` | No | `0.2` | Decimal | Short basket quantile share. |

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
