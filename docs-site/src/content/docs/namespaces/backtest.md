---
title: backtest
description: Run and inspect strategy and factor backtests with structured inputs and JSON results.
---

# finance backtest

The `backtest.*` commands create backtest payloads, inspect built-in strategies, preview factor weights, run strategy simulations, and tune parameter grids. Use this namespace when the user has explicit symbols, date ranges, and strategy assumptions that should be tested reproducibly.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance backtest.describe

Describe a backtest strategy and its parameters.

### What it does

`finance backtest.describe` describes a backtest strategy and its parameters. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `name`, `summary`, `parameters`, `engine`.

### When to use it

Use this command before `backtest.run` when you need to know what a built-in strategy does and which parameters it accepts.

Do not present backtests as live trading recommendations.

### Usage

```bash
finance backtest.describe STRATEGY [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `strategy` | Yes | None | String | Built-in strategy key, such as `sma_cross`, or `custom` when using `strategy_file`. |

### Basic usage

```bash
finance backtest.describe sma_cross --output json
```

### Example output

This output was generated with `finance backtest.describe sma_cross --output json`.

```json
{
  "ok": true,
  "data": {
    "name": "sma_cross",
    "summary": "Long when a fast moving average crosses above a slow moving average.",
    "parameters": {
      "fast": {
        "default": 20,
        "type": "integer"
      },
      "slow": {
        "default": 100,
        "type": "integer"
      }
    },
    "engine": "vectorbt"
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
| `data.engine` | string | Backtest engine used. |
| `data.name` | string | Strategy or result display name. |
| `data.parameters` | object | Strategy parameters included in the payload. |
| `data.summary` | string | Short human-readable summary. |
| `data.parameters.fast` | object | Fast moving-average parameter or value. |
| `data.parameters.slow` | object | Slow moving-average parameter or value. |
| `data.parameters.fast.default` | integer | Default parameter value. |
| `data.parameters.fast.type` | string | Parameter type accepted by the strategy. |
| `data.parameters.slow.default` | integer | Default parameter value. |
| `data.parameters.slow.type` | string | Parameter type accepted by the strategy. |

## finance backtest.factor.payload

Build a normalized factor backtest payload.

### What it does

`finance backtest.factor.payload` builds a normalized factor backtest payload. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `factor_name`, `symbols`, `start_date`, `end_date`, `timeframe`, `initial_cash`, `direction`, `top_pct`.

### When to use it

Use this command when you want to construct a normalized factor-backtest request before running or saving it elsewhere.

Do not present backtests as live trading recommendations.

### Usage

```bash
finance backtest.factor.payload FACTOR_NAME SYMBOLS START_DATE END_DATE [timeframe=1d top_pct=0.2 bottom_pct=0.2] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `factor_name` | Yes | None | String | Factor identifier used to label the payload or rebalance preview. |
| `symbols` | Yes | None | String | Ticker symbol or comma-separated ticker list, such as `AAPL,MSFT,NVDA`. |
| `start_date` | Yes | None | `YYYY-MM-DD` | Start date in `YYYY-MM-DD` format. |
| `end_date` | Yes | None | `YYYY-MM-DD` | End date in `YYYY-MM-DD` format. |
| `bottom_pct` | No | `0.2` | Number | Fraction of symbols assigned to the short basket. |
| `timeframe` | No | `1d` | String | Bar interval used by the factor backtest. |
| `top_pct` | No | `0.2` | Number | Fraction of symbols assigned to the long basket. |

### Basic usage

```bash
finance backtest.factor.payload rsi_14 AAPL,MSFT,NVDA 2024-01-01 2024-12-31 --output json
```

### Example output

This output was generated with `finance backtest.factor.payload rsi_14 AAPL,MSFT,NVDA 2024-01-01 2024-12-31 --output json`.

```json
{
  "ok": true,
  "data": {
    "factor_name": "rsi_14",
    "symbols": [
      "AAPL",
      "MSFT",
      "NVDA"
    ],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "timeframe": "1d",
    "initial_cash": 100000.0,
    "direction": "long_short",
    "top_pct": 0.2,
    "bottom_pct": 0.2,
    "rebalance_freq": "monthly",
    "fixed_fee": 2.0,
    "fees_pct": 0.001
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
| `data.bottom_pct` | number | Bottom quantile percentage for factor selection. |
| `data.direction` | string | Long/short ranking direction. |
| `data.end_date` | string | End date used by the command. |
| `data.factor_name` | string | Factor identifier used in the request. |
| `data.fees_pct` | number | Percentage fee rate. |
| `data.fixed_fee` | number | Fixed fee per order. |
| `data.initial_cash` | number | Starting cash for the backtest. |
| `data.rebalance_freq` | string | Rebalance frequency. |
| `data.start_date` | string | Start date used by the command. |
| `data.symbols` | array | Ticker symbols included in the request. |
| `data.symbols[]` | string | Ticker symbols included in the request. |
| `data.timeframe` | string | Bar interval used by the backtest. |
| `data.top_pct` | number | Top quantile percentage for factor selection. |

## finance backtest.factor.weights

Preview quantile factor target weights.

### What it does

`finance backtest.factor.weights` previews quantile factor target weights. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `run_type`, `config`, `equity_curve`, `events`, `factor_name`, `symbols`, `weights`, `gross_exposure`.

### When to use it

Use this command when you have factor scores and want to preview long/short target weights without downloading market data or running a full backtest.

Do not present backtests as live trading recommendations.

### Usage

```bash
finance backtest.factor.weights FACTOR_NAME scores='{"AAPL":1.2,"MSFT":0.4}' [top_pct=0.2 bottom_pct=0.2] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `factor_name` | Yes | None | String | Factor identifier used to label the payload or rebalance preview. |
| `scores` | Yes | None | String | JSON object mapping symbols to factor scores, for example `{"AAPL":1.1,"MSFT":0.3}`. |
| `bottom_pct` | No | `0.2` | Number | Fraction of symbols assigned to the short basket. |
| `top_pct` | No | `0.2` | Number | Fraction of symbols assigned to the long basket. |

### Basic usage

```bash
finance backtest.factor.weights rsi_14 scores='{"AAPL":1.1,"MSFT":0.3,"NVDA":2.0}' --output json
```

### Example output

This output was generated with `finance backtest.factor.weights rsi_14 scores='{"AAPL":1.1,"MSFT":0.3,"NVDA":2.0}' --output json`.

```json
{
  "ok": true,
  "data": {
    "run_type": "factor_rebalance_preview",
    "config": {
      "factor_name": "rsi_14",
      "timestamp": "preview",
      "direction": "long_short",
      "top_pct": 0.2,
      "bottom_pct": 0.2
    },
    "equity_curve": [],
    "events": [
      {
        "event_time": "preview",
        "event_type": "rebalance_long",
        "symbol": null,
        "side": "long",
        "quantity": 1.0,
        "price": null,
        "value": 0.5,
        "label": "LONG basket: NVDA",
        "payload": {
          "weights": {
            "NVDA": 0.5
          }
        }
      },
      {
        "event_time": "preview",
        "event_type": "rebalance_short",
        "symbol": null,
        "side": "short",
        "quantity": 1.0,
        "price": null,
        "value": -0.5,
        "label": "SHORT basket: MSFT",
        "payload": {
          "weights": {
            "MSFT": -0.5
          }
        }
      }
    ],
    "factor_name": "rsi_14",
    "symbols": [
      "AAPL",
      "MSFT",
      "NVDA"
    ],
    "weights": {
      "AAPL": 0.0,
      "MSFT": -0.5,
      "NVDA": 0.5
    },
    "gross_exposure": 1.0,
    "net_exposure": 0.0,
    "rebalance_snapshot": {
      "timestamp": "preview",
      "long": [
        {
          "symbol": "NVDA",
          "weight": 0.5
        }
      ],
      "short": [
        {
          "symbol": "MSFT",
          "weight": -0.5
        }
      ],
      "gross_exposure": 1.0,
      "net_exposure": 0.0
    }
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
| `data.config` | object | Run configuration used by the command. |
| `data.equity_curve` | array | Equity curve observations. |
| `data.events` | array | Backtest or factor preview events. |
| `data.events[]` | object | Backtest or factor preview events. |
| `data.factor_name` | string | Factor identifier used in the request. |
| `data.gross_exposure` | number | Sum of absolute target weights. |
| `data.net_exposure` | number | Net long minus short exposure. |
| `data.rebalance_snapshot` | object | Point-in-time factor rebalance preview. |
| `data.run_type` | string | Type of backtest or preview run. |
| `data.symbols` | array | Ticker symbols included in the request. |
| `data.symbols[]` | string | Ticker symbols included in the request. |
| `data.weights` | object | Symbol-to-weight mapping. |
| `data.config.bottom_pct` | number | Bottom quantile percentage for factor selection. |
| `data.config.direction` | string | Long/short ranking direction. |
| `data.config.factor_name` | string | Factor identifier used in the request. |
| `data.config.timestamp` | string | Timestamp for the record or calculation step. |
| `data.config.top_pct` | number | Top quantile percentage for factor selection. |
| `data.events[].event_time` | string | Timestamp for the backtest or rebalance event. |
| `data.events[].event_type` | string | Backtest event type. |
| `data.events[].label` | string | Display label for the event or row. |
| `data.events[].payload` | object | Mode-specific payload. |
| `data.events[].price` | null | Price associated with the event, quote, summary row, or order. |
| `data.events[].quantity` | number | Order or event quantity. |
| `data.events[].side` | string | Long/short side for the event. |
| `data.events[].symbol` | string or null | Symbol associated with the event when the event is symbol-specific. |
| `data.events[].value` | number | Event value, such as target exposure or trade value. |
| `data.rebalance_snapshot.gross_exposure` | number | Sum of absolute target weights. |
| `data.rebalance_snapshot.long` | array | Long basket or long-side entries in the rebalance snapshot. |
| `data.rebalance_snapshot.long[]` | object | Long basket or long-side entries in the rebalance snapshot. |
| `data.rebalance_snapshot.net_exposure` | number | Net long minus short exposure. |
| `data.rebalance_snapshot.short` | array | Short label or short-side basket, depending on the enclosing object. |
| `data.rebalance_snapshot.short[]` | object | Short label or short-side basket, depending on the enclosing object. |
| `data.rebalance_snapshot.timestamp` | string | Timestamp for the record or calculation step. |
| `data.weights.AAPL` | number | Value associated with `AAPL` in the symbol-keyed mapping. |
| `data.weights.MSFT` | number | Value associated with `MSFT` in the symbol-keyed mapping. |
| `data.weights.NVDA` | number | Value associated with `NVDA` in the symbol-keyed mapping. |
| `data.events[].payload.weights` | object | Symbol-to-weight mapping. |
| `data.rebalance_snapshot.long[].symbol` | string | Symbol in the long basket. |
| `data.rebalance_snapshot.long[].weight` | number | Portfolio weight for one symbol. |
| `data.rebalance_snapshot.short[].symbol` | string | Symbol in the short basket. |
| `data.rebalance_snapshot.short[].weight` | number | Portfolio weight for one symbol. |
| `data.events[].payload.weights.MSFT` | number | Value associated with `MSFT` in the symbol-keyed mapping. |
| `data.events[].payload.weights.NVDA` | number | Value associated with `NVDA` in the symbol-keyed mapping. |

## finance backtest.run

Run a VectorBT strategy backtest.

### What it does

`finance backtest.run` runs a VectorBT strategy backtest. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `run_type`, `engine`, `config`, `metrics`, `data`, `equity_curve`, `trades`, `orders`.

### When to use it

Use when the user asks to run a named strategy over explicit symbols and dates.

Do not use this command as proof a strategy will work in live trading.

### Usage

```bash
finance backtest.run STRATEGY SYMBOLS START_DATE END_DATE [params='{}' strategy_file=./rule.py] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `strategy` | Yes | None | String | Built-in strategy key, such as `sma_cross`, or `custom` when using `strategy_file`. |
| `symbols` | Yes | None | String | Ticker symbol or comma-separated ticker list, such as `AAPL,MSFT,NVDA`. |
| `start_date` | Yes | None | `YYYY-MM-DD` | Start date in `YYYY-MM-DD` format. |
| `end_date` | Yes | None | `YYYY-MM-DD` | End date in `YYYY-MM-DD` format. |
| `params` | No | `{}` | JSON object or key-value parameters | Strategy parameters. You can pass JSON or key-value pairs such as `fast=20 slow=100`. |
| `strategy_file` | No | `./rule.py` | String | Local Python strategy file used only with custom strategies. |

### Basic usage

```bash
finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31 fast=20 slow=100 --output json
```

### Example output

This output was generated with `finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31 fast=20 slow=100 --output json`.

```json
{
  "ok": true,
  "data": {
    "run_type": "vectorbt_backtest",
    "engine": "vectorbt",
    "config": {
      "strategy": "sma_cross",
      "symbols": [
        "AAPL"
      ],
      "start_date": "2020-01-01",
      "end_date": "2024-12-31",
      "timeframe": "1d",
      "initial_cash": 100000.0,
      "fees": 0.001,
      "fixed_fees": 0.0,
      "slippage": 0.0,
      "provider": "auto",
      "params": {
        "fast": 20,
        "slow": 100
      },
      "strategy_file": null,
      "plot_path": null,
      "engine": "vectorbt"
    },
    "metrics": {
      "start_value": 100000.0,
      "end_value": 100000.0,
      "total_return_pct": 0.0,
      "benchmark_return_pct": 235.874802,
      "max_drawdown_pct": null,
      "total_trades": 0,
      "win_rate_pct": null,
      "profit_factor": null,
      "expectancy": null,
      "sharpe_ratio": null,
      "calmar_ratio": null,
      "omega_ratio": null,
      "sortino_ratio": null,
      "total_fees_paid": 0.0,
      "total_return_decimal": 0.0
    },
    "data": {
      "symbols": [
        "AAPL"
      ],
      "rows": 1257,
      "start": "2020-01-02T05:00:00",
      "end": "2024-12-30T05:00:00",
      "sources": {
        "AAPL": "yfinance"
      }
    },
    "equity_curve": [
      {
        "date": "2020-01-02T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-02-07T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-03-16T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-04-21T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-05-27T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-07-01T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-08-06T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-09-11T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-10-16T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-11-20T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2020-12-29T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-02-04T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-03-12T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-04-19T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-05-24T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-06-29T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-08-04T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-09-09T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-10-14T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-11-18T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2021-12-27T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-02-01T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-03-09T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-04-13T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-05-19T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-06-27T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-08-02T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-09-07T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-10-12T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-11-16T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2022-12-22T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-01-31T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-03-08T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-04-13T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-05-18T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-06-26T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-08-01T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-09-06T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-10-11T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-11-15T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2023-12-21T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-01-30T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-03-06T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-04-11T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-05-16T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-06-24T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-07-30T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-09-04T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-10-09T04:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-11-13T05:00:00",
        "value": 100000.0
      },
      {
        "date": "2024-12-19T05:00:00",
        "value": 100000.0
      }
    ],
    "trades": [],
    "orders": [],
    "target_weights": [],
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
| `data.config` | object | Run configuration used by the command. |
| `data.data` | object | Downloaded market-data summary used by the backtest. |
| `data.engine` | string | Backtest engine used. |
| `data.equity_curve` | array | Equity curve observations. |
| `data.equity_curve[]` | object | Equity curve observations. |
| `data.metrics` | object | Metrics requested by the caller. |
| `data.orders` | array | Generated order records. |
| `data.run_type` | string | Type of backtest or preview run. |
| `data.target_weights` | array | Target portfolio weights. |
| `data.trades` | array | Executed trade records. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |
| `data.config.end_date` | string | End date used by the command. |
| `data.config.engine` | string | Backtest engine used. |
| `data.config.fees` | number | Fee amount for an order or trade. |
| `data.config.fixed_fees` | number | Fixed fee amount used by the backtest engine. |
| `data.config.initial_cash` | number | Starting cash for the backtest. |
| `data.config.params` | object | Strategy parameters supplied by the caller. |
| `data.config.plot_path` | null | Path to a generated plot when requested. |
| `data.config.provider` | string | Provider identifier. |
| `data.config.slippage` | number | Slippage assumption used by the backtest engine. |
| `data.config.start_date` | string | Start date used by the command. |
| `data.config.strategy` | string | Strategy key requested by the command. |
| `data.config.strategy_file` | null | Custom strategy file path when a custom strategy is used. |
| `data.config.symbols` | array | Ticker symbols included in the request. |
| `data.config.symbols[]` | string | Ticker symbols included in the request. |
| `data.config.timeframe` | string | Bar interval used by the backtest. |
| `data.data.end` | string | End timestamp in the downloaded backtest data. |
| `data.data.rows` | integer | Structured rows returned by the command. |
| `data.data.sources` | object | Provider/source handles used in the result. |
| `data.data.start` | string | Start timestamp in the downloaded backtest data. |
| `data.data.symbols` | array | Ticker symbols included in the request. |
| `data.data.symbols[]` | string | Ticker symbols included in the request. |
| `data.equity_curve[].date` | string | Event, bar, filing, or publication date. |
| `data.equity_curve[].value` | number | Portfolio equity value at that date. |
| `data.metrics.benchmark_return_pct` | number | Benchmark return percentage. |
| `data.metrics.calmar_ratio` | null | Calmar ratio. |
| `data.metrics.end_value` | number | Portfolio value at the end of the run. |
| `data.metrics.expectancy` | null | Average expected trade result. |
| `data.metrics.max_drawdown_pct` | null | Maximum drawdown percentage. |
| `data.metrics.omega_ratio` | null | Omega ratio. |
| `data.metrics.profit_factor` | null | Gross profit divided by gross loss. |
| `data.metrics.sharpe_ratio` | null | Sharpe ratio. |
| `data.metrics.sortino_ratio` | null | Sortino ratio. |
| `data.metrics.start_value` | number | Portfolio value at the start of the run. |
| `data.metrics.total_fees_paid` | number | Total fees paid in the run. |
| `data.metrics.total_return_decimal` | number | Total return as a decimal. |
| `data.metrics.total_return_pct` | number | Total return percentage. |
| `data.metrics.total_trades` | integer | Number of trades. |
| `data.metrics.win_rate_pct` | null | Winning trade percentage. |
| `data.config.params.fast` | integer | Fast moving-average parameter or value. |
| `data.config.params.slow` | integer | Slow moving-average parameter or value. |
| `data.data.sources.AAPL` | string | Value associated with `AAPL` in the symbol-keyed mapping. |

## finance backtest.strategies

List VectorBT-backed strategy presets.

### What it does

`finance backtest.strategies` lists VectorBT-backed strategy presets. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `engine`, `strategies`.

### When to use it

Use this command when you need to see which built-in strategy keys are available before describing, running, or tuning one.

Do not present backtests as live trading recommendations.

### Usage

```bash
finance backtest.strategies [--output json]
```

### Arguments

No arguments.

### Basic usage

```bash
finance backtest.strategies --output json
```

### Example output

This output was generated with `finance backtest.strategies --output json`.

```json
{
  "ok": true,
  "data": {
    "engine": "vectorbt",
    "strategies": [
      {
        "name": "buy_hold",
        "summary": "Equal-weight buy and hold across all symbols.",
        "parameters": {}
      },
      {
        "name": "sma_cross",
        "summary": "Long when a fast moving average crosses above a slow moving average.",
        "parameters": {
          "fast": {
            "default": 20,
            "type": "integer"
          },
          "slow": {
            "default": 100,
            "type": "integer"
          }
        }
      },
      {
        "name": "rsi_reversion",
        "summary": "Long when RSI is below lower threshold; exit above upper threshold.",
        "parameters": {
          "window": {
            "default": 14,
            "type": "integer"
          },
          "lower": {
            "default": 30,
            "type": "number"
          },
          "upper": {
            "default": 55,
            "type": "number"
          }
        }
      },
      {
        "name": "momentum_top_n",
        "summary": "Rebalance into the top N symbols by trailing return.",
        "parameters": {
          "lookback": {
            "default": 63,
            "type": "integer"
          },
          "top_n": {
            "default": 3,
            "type": "integer"
          },
          "rebalance": {
            "default": "M",
            "type": "string",
            "allowed": [
              "D",
              "W",
              "M"
            ]
          }
        }
      }
    ]
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
| `data.engine` | string | Backtest engine used. |
| `data.strategies` | array | Built-in strategy definitions. |
| `data.strategies[]` | object | Built-in strategy definitions. |
| `data.strategies[].name` | string | Strategy or result display name. |
| `data.strategies[].parameters` | object | Parameter definitions accepted by this strategy. |
| `data.strategies[].summary` | string | Short human-readable summary. |
| `data.strategies[].parameters.fast` | object | Fast moving-average parameter or value. |
| `data.strategies[].parameters.lookback` | object | Calendar lookback window requested by the command. |
| `data.strategies[].parameters.lower` | object | Lower threshold parameter for the strategy. |
| `data.strategies[].parameters.rebalance` | object | Rebalance parameter definition. |
| `data.strategies[].parameters.slow` | object | Slow moving-average parameter or value. |
| `data.strategies[].parameters.top_n` | object | Top-N selection parameter for the strategy. |
| `data.strategies[].parameters.upper` | object | Upper threshold parameter for the strategy. |
| `data.strategies[].parameters.window` | object | Window size used for the calculation. |
| `data.strategies[].parameters.fast.default` | integer | Default parameter value. |
| `data.strategies[].parameters.fast.type` | string | Parameter type accepted by the strategy. |
| `data.strategies[].parameters.lookback.default` | integer | Default parameter value. |
| `data.strategies[].parameters.lookback.type` | string | Parameter type accepted by the strategy. |
| `data.strategies[].parameters.lower.default` | integer | Default parameter value. |
| `data.strategies[].parameters.lower.type` | string | Parameter type accepted by the strategy. |
| `data.strategies[].parameters.rebalance.allowed` | array | Whether a screen field or value is allowed by the provider. |
| `data.strategies[].parameters.rebalance.allowed[]` | string | Whether a screen field or value is allowed by the provider. |
| `data.strategies[].parameters.rebalance.default` | string | Default parameter value. |
| `data.strategies[].parameters.rebalance.type` | string | Parameter type accepted by the strategy. |
| `data.strategies[].parameters.slow.default` | integer | Default parameter value. |
| `data.strategies[].parameters.slow.type` | string | Parameter type accepted by the strategy. |
| `data.strategies[].parameters.top_n.default` | integer | Default parameter value. |
| `data.strategies[].parameters.top_n.type` | string | Parameter type accepted by the strategy. |
| `data.strategies[].parameters.upper.default` | integer | Default parameter value. |
| `data.strategies[].parameters.upper.type` | string | Parameter type accepted by the strategy. |
| `data.strategies[].parameters.window.default` | integer | Default parameter value. |
| `data.strategies[].parameters.window.type` | string | Parameter type accepted by the strategy. |

## finance backtest.strategy.payload

Build a normalized strategy backtest payload.

### What it does

`finance backtest.strategy.payload` builds a normalized strategy backtest payload. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `strategy_id`, `start_date`, `end_date`, `initial_cash`, `parameters`, `fee_mode`, `fixed_fee`, `fees_pct`.

### When to use it

Use this command when you need a normalized strategy payload but do not want to run the backtest yet.

Do not present backtests as live trading recommendations.

### Usage

```bash
finance backtest.strategy.payload STRATEGY_ID START_DATE END_DATE [initial_cash=100000 parameters='{}'] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `start_date` | Yes | None | `YYYY-MM-DD` | Start date in `YYYY-MM-DD` format. |
| `end_date` | Yes | None | `YYYY-MM-DD` | End date in `YYYY-MM-DD` format. |
| `strategy_id` | Yes | None | String | Strategy identifier to place in the payload. |
| `initial_cash` | No | `100000` | Integer | Starting cash used by the payload or backtest. |
| `parameters` | No | `{}` | JSON object or key-value parameters | Strategy parameter object to include in the payload. |

### Basic usage

```bash
finance backtest.strategy.payload mean_reversion 2024-01-01 2024-12-31 --output json
```

### Example output

This output was generated with `finance backtest.strategy.payload mean_reversion 2024-01-01 2024-12-31 --output json`.

```json
{
  "ok": true,
  "data": {
    "strategy_id": "mean_reversion",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_cash": 100000.0,
    "parameters": {},
    "fee_mode": "mixed",
    "fixed_fee": 2.0,
    "fees_pct": 0.001
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
| `data.end_date` | string | End date used by the command. |
| `data.fee_mode` | string | Fee calculation mode. |
| `data.fees_pct` | number | Percentage fee rate. |
| `data.fixed_fee` | number | Fixed fee per order. |
| `data.initial_cash` | number | Starting cash for the backtest. |
| `data.parameters` | object | Strategy parameters included in the payload. |
| `data.start_date` | string | Start date used by the command. |
| `data.strategy_id` | string | Strategy identifier in the payload. |

## finance backtest.tune

Run a bounded VectorBT parameter grid.

### What it does

`finance backtest.tune` runs a bounded VectorBT parameter grid. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `run_type`, `engine`, `strategy`, `symbols`, `start_date`, `end_date`, `timeframe`, `metric`.

### When to use it

Use this command when you have a bounded parameter grid and want Finance CLI to run each candidate combination against the same symbols and date range.

Do not present backtests as live trading recommendations.

### Usage

```bash
finance backtest.tune STRATEGY SYMBOLS START_DATE END_DATE grid='{}' [metric=sharpe_ratio max_runs=100] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `strategy` | Yes | None | String | Built-in strategy key, such as `sma_cross`, or `custom` when using `strategy_file`. |
| `symbols` | Yes | None | String | Ticker symbol or comma-separated ticker list, such as `AAPL,MSFT,NVDA`. |
| `end_date` | Yes | None | `YYYY-MM-DD` | End date in `YYYY-MM-DD` format. |
| `grid` | Yes | None | JSON object or key-value parameters | Parameter grid where each key maps to a list of candidate values. |
| `start_date` | Yes | None | `YYYY-MM-DD` | Start date in `YYYY-MM-DD` format. |
| `max_runs` | No | `100` | Integer | Safety cap on parameter combinations evaluated. |
| `metric` | No | `sharpe_ratio` | String | Metric used to rank grid-search results. |

### Basic usage

```bash
finance backtest.tune sma_cross AAPL 2020-01-01 2024-12-31 grid='{"fast":[10,20],"slow":[50,100]}' --output json
```

### Example output

This output was generated with `finance backtest.tune sma_cross AAPL 2020-01-01 2024-12-31 grid='{"fast":[10,20],"slow":[50,100]}' --output json`.

```json
{
  "ok": true,
  "data": {
    "run_type": "vectorbt_tune",
    "engine": "vectorbt",
    "strategy": "sma_cross",
    "symbols": [
      "AAPL"
    ],
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "timeframe": "1d",
    "metric": "sharpe_ratio",
    "runs": 4,
    "best": {
      "params": {
        "fast": 10,
        "slow": 50
      },
      "metrics": {
        "start_value": 100000.0,
        "end_value": 100000.0,
        "total_return_pct": 0.0,
        "benchmark_return_pct": 235.874802,
        "max_drawdown_pct": null,
        "total_trades": 0,
        "win_rate_pct": null,
        "profit_factor": null,
        "expectancy": null,
        "sharpe_ratio": null,
        "calmar_ratio": null,
        "omega_ratio": null,
        "sortino_ratio": null,
        "total_fees_paid": 0.0,
        "total_return_decimal": 0.0
      },
      "score": null
    },
    "results": [
      {
        "params": {
          "fast": 10,
          "slow": 50
        },
        "metrics": {
          "start_value": 100000.0,
          "end_value": 100000.0,
          "total_return_pct": 0.0,
          "benchmark_return_pct": 235.874802,
          "max_drawdown_pct": null,
          "total_trades": 0,
          "win_rate_pct": null,
          "profit_factor": null,
          "expectancy": null,
          "sharpe_ratio": null,
          "calmar_ratio": null,
          "omega_ratio": null,
          "sortino_ratio": null,
          "total_fees_paid": 0.0,
          "total_return_decimal": 0.0
        },
        "score": null
      },
      {
        "params": {
          "fast": 10,
          "slow": 100
        },
        "metrics": {
          "start_value": 100000.0,
          "end_value": 100000.0,
          "total_return_pct": 0.0,
          "benchmark_return_pct": 235.874802,
          "max_drawdown_pct": null,
          "total_trades": 0,
          "win_rate_pct": null,
          "profit_factor": null,
          "expectancy": null,
          "sharpe_ratio": null,
          "calmar_ratio": null,
          "omega_ratio": null,
          "sortino_ratio": null,
          "total_fees_paid": 0.0,
          "total_return_decimal": 0.0
        },
        "score": null
      },
      {
        "params": {
          "fast": 20,
          "slow": 50
        },
        "metrics": {
          "start_value": 100000.0,
          "end_value": 100000.0,
          "total_return_pct": 0.0,
          "benchmark_return_pct": 235.874802,
          "max_drawdown_pct": null,
          "total_trades": 0,
          "win_rate_pct": null,
          "profit_factor": null,
          "expectancy": null,
          "sharpe_ratio": null,
          "calmar_ratio": null,
          "omega_ratio": null,
          "sortino_ratio": null,
          "total_fees_paid": 0.0,
          "total_return_decimal": 0.0
        },
        "score": null
      },
      {
        "params": {
          "fast": 20,
          "slow": 100
        },
        "metrics": {
          "start_value": 100000.0,
          "end_value": 100000.0,
          "total_return_pct": 0.0,
          "benchmark_return_pct": 235.874802,
          "max_drawdown_pct": null,
          "total_trades": 0,
          "win_rate_pct": null,
          "profit_factor": null,
          "expectancy": null,
          "sharpe_ratio": null,
          "calmar_ratio": null,
          "omega_ratio": null,
          "sortino_ratio": null,
          "total_fees_paid": 0.0,
          "total_return_decimal": 0.0
        },
        "score": null
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
| `data.best` | object | Best parameter set according to the requested metric. |
| `data.end_date` | string | End date used by the command. |
| `data.engine` | string | Backtest engine used. |
| `data.metric` | string | Metric name. |
| `data.results` | array | Per-run or per-provider result records. |
| `data.results[]` | object | Per-run or per-provider result records. |
| `data.run_type` | string | Type of backtest or preview run. |
| `data.runs` | integer | Parameter-grid runs executed. |
| `data.start_date` | string | Start date used by the command. |
| `data.strategy` | string | Strategy key requested by the command. |
| `data.symbols` | array | Ticker symbols included in the request. |
| `data.symbols[]` | string | Ticker symbols included in the request. |
| `data.timeframe` | string | Bar interval used by the backtest. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |
| `data.best.metrics` | object | Metrics requested by the caller. |
| `data.best.params` | object | Strategy parameters supplied by the caller. |
| `data.best.score` | null | Optimization score for the run; `null` when the selected metric is unavailable. |
| `data.results[].metrics` | object | Metrics requested by the caller. |
| `data.results[].params` | object | Strategy parameters supplied by the caller. |
| `data.results[].score` | null | Optimization score for the run; `null` when the selected metric is unavailable. |
| `data.best.metrics.benchmark_return_pct` | number | Benchmark return percentage. |
| `data.best.metrics.calmar_ratio` | null | Calmar ratio. |
| `data.best.metrics.end_value` | number | Portfolio value at the end of the run. |
| `data.best.metrics.expectancy` | null | Average expected trade result. |
| `data.best.metrics.max_drawdown_pct` | null | Maximum drawdown percentage. |
| `data.best.metrics.omega_ratio` | null | Omega ratio. |
| `data.best.metrics.profit_factor` | null | Gross profit divided by gross loss. |
| `data.best.metrics.sharpe_ratio` | null | Sharpe ratio. |
| `data.best.metrics.sortino_ratio` | null | Sortino ratio. |
| `data.best.metrics.start_value` | number | Portfolio value at the start of the run. |
| `data.best.metrics.total_fees_paid` | number | Total fees paid in the run. |
| `data.best.metrics.total_return_decimal` | number | Total return as a decimal. |
| `data.best.metrics.total_return_pct` | number | Total return percentage. |
| `data.best.metrics.total_trades` | integer | Number of trades. |
| `data.best.metrics.win_rate_pct` | null | Winning trade percentage. |
| `data.best.params.fast` | integer | Fast moving-average parameter or value. |
| `data.best.params.slow` | integer | Slow moving-average parameter or value. |
| `data.results[].metrics.benchmark_return_pct` | number | Benchmark return percentage. |
| `data.results[].metrics.calmar_ratio` | null | Calmar ratio. |
| `data.results[].metrics.end_value` | number | Portfolio value at the end of the run. |
| `data.results[].metrics.expectancy` | null | Average expected trade result. |
| `data.results[].metrics.max_drawdown_pct` | null | Maximum drawdown percentage. |
| `data.results[].metrics.omega_ratio` | null | Omega ratio. |
| `data.results[].metrics.profit_factor` | null | Gross profit divided by gross loss. |
| `data.results[].metrics.sharpe_ratio` | null | Sharpe ratio. |
| `data.results[].metrics.sortino_ratio` | null | Sortino ratio. |
| `data.results[].metrics.start_value` | number | Portfolio value at the start of the run. |
| `data.results[].metrics.total_fees_paid` | number | Total fees paid in the run. |
| `data.results[].metrics.total_return_decimal` | number | Total return as a decimal. |
| `data.results[].metrics.total_return_pct` | number | Total return percentage. |
| `data.results[].metrics.total_trades` | integer | Number of trades. |
| `data.results[].metrics.win_rate_pct` | null | Winning trade percentage. |
| `data.results[].params.fast` | integer | Fast moving-average parameter or value. |
| `data.results[].params.slow` | integer | Slow moving-average parameter or value. |
