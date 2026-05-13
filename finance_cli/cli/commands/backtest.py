"""Backtest CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs, parse_csv
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.backtest import (
    available_backtest_strategies,
    build_factor_backtest_payload,
    build_strategy_backtest_payload,
    describe_backtest_strategy,
    preview_factor_rebalance,
    run_backtest,
    tune_backtest,
)


def _strategies(_args: list[str]) -> FinanceCommandResult:
    return FinanceCommandResult(ok=True, data=available_backtest_strategies())


def _describe(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: backtest.describe STRATEGY")
    return FinanceCommandResult(ok=True, data=describe_backtest_strategy(args[0]))


def _run(args: list[str]) -> FinanceCommandResult:
    if len(args) < 4:
        return FinanceCommandResult(ok=False, error="usage: backtest.run STRATEGY SYMBOLS START_DATE END_DATE [key=value]")
    kv = KVArgs(args[4:])
    data = run_backtest(
        strategy=args[0],
        symbols=parse_csv(args[1]),
        start_date=args[2],
        end_date=args[3],
        timeframe=kv.str("timeframe", "1d") or "1d",
        initial_cash=kv.float("initial_cash", 100000.0),
        fees=kv.float("fees", 0.001),
        fixed_fees=kv.float("fixed_fees", 0.0),
        slippage=kv.float("slippage", 0.0),
        provider=kv.str("provider", "auto") or "auto",
        params=kv.json_object("params") or _strategy_params(kv),
        strategy_file=kv.str("strategy_file") or kv.str("path"),
        plot_path=kv.str("plot_path"),
    )
    return FinanceCommandResult(ok=True, data=data, warnings=data.get("warnings", []))


def _tune(args: list[str]) -> FinanceCommandResult:
    if len(args) < 4:
        return FinanceCommandResult(ok=False, error="usage: backtest.tune STRATEGY SYMBOLS START_DATE END_DATE grid='{}' [key=value]")
    kv = KVArgs(args[4:])
    grid = kv.json_object("grid")
    if not grid:
        return FinanceCommandResult(ok=False, error="grid JSON object is required")
    data = tune_backtest(
        strategy=args[0],
        symbols=parse_csv(args[1]),
        start_date=args[2],
        end_date=args[3],
        grid=grid,
        metric=kv.str("metric", "sharpe_ratio") or "sharpe_ratio",
        max_runs=kv.int("max_runs", 100),
        timeframe=kv.str("timeframe", "1d") or "1d",
        initial_cash=kv.float("initial_cash", 100000.0),
        fees=kv.float("fees", 0.001),
        fixed_fees=kv.float("fixed_fees", 0.0),
        slippage=kv.float("slippage", 0.0),
        provider=kv.str("provider", "auto") or "auto",
        strategy_file=kv.str("strategy_file") or kv.str("path"),
    )
    return FinanceCommandResult(ok=True, data=data, warnings=data.get("warnings", []))


def _strategy_payload(args: list[str]) -> FinanceCommandResult:
    if len(args) < 3:
        return FinanceCommandResult(ok=False, error="usage: backtest.strategy.payload STRATEGY_ID START_DATE END_DATE [key=value]")
    kv = KVArgs(args[3:])
    payload = build_strategy_backtest_payload(
        strategy_id=args[0],
        start_date=args[1],
        end_date=args[2],
        initial_cash=kv.float("initial_cash", 100000.0),
        parameters=kv.json_object("parameters"),
        fee_mode=kv.str("fee_mode", "mixed"),
        fixed_fee=kv.float("fixed_fee", 2.0),
        fees_pct=kv.float("fees_pct", 0.001),
    )
    return FinanceCommandResult(ok=True, data=payload)


def _factor_payload(args: list[str]) -> FinanceCommandResult:
    if len(args) < 4:
        return FinanceCommandResult(ok=False, error="usage: backtest.factor.payload FACTOR_NAME SYMBOLS START_DATE END_DATE [key=value]")
    kv = KVArgs(args[4:])
    payload = build_factor_backtest_payload(
        factor_name=args[0],
        symbols=parse_csv(args[1]),
        start_date=args[2],
        end_date=args[3],
        timeframe=kv.str("timeframe", "1d"),
        initial_cash=kv.float("initial_cash", 100000.0),
        direction=kv.str("direction", "long_short"),
        top_pct=kv.float("top_pct", 0.2),
        bottom_pct=kv.float("bottom_pct", 0.2),
        rebalance_freq=kv.str("rebalance_freq", "monthly"),
        fixed_fee=kv.float("fixed_fee", 2.0),
        fees_pct=kv.float("fees_pct", 0.001),
    )
    return FinanceCommandResult(ok=True, data=payload)


def _factor_weights(args: list[str]) -> FinanceCommandResult:
    if len(args) < 2:
        return FinanceCommandResult(ok=False, error='usage: backtest.factor.weights FACTOR_NAME scores=\'{"AAPL":1.2,"MSFT":0.4}\' [key=value]')
    kv = KVArgs(args[1:])
    scores = kv.json_object("scores")
    if not scores:
        return FinanceCommandResult(ok=False, error="scores JSON object is required")
    data = preview_factor_rebalance(
        factor_name=args[0],
        scores={symbol: float(score) for symbol, score in scores.items()},
        timestamp=kv.str("timestamp", "preview"),
        direction=kv.str("direction", "long_short"),
        top_pct=kv.float("top_pct", 0.2),
        bottom_pct=kv.float("bottom_pct", 0.2),
    )
    return FinanceCommandResult(ok=True, data=data)


def _strategy_params(kv: KVArgs) -> dict[str, object]:
    reserved = {
        "timeframe",
        "initial_cash",
        "fees",
        "fixed_fees",
        "slippage",
        "provider",
        "strategy_file",
        "path",
        "plot_path",
        "grid",
        "metric",
        "max_runs",
        "params",
    }
    params: dict[str, object] = {}
    for key, value in kv.values.items():
        if key in reserved:
            continue
        params[key] = _parse_scalar(value)
    return params


def _parse_scalar(value: str) -> object:
    normalized = value.strip()
    if normalized.lower() in {"true", "false"}:
        return normalized.lower() == "true"
    try:
        if "." not in normalized:
            return int(normalized)
        return float(normalized)
    except ValueError:
        return value


def register_backtest_commands() -> None:
    register_command(FinanceCommand(
        "backtest.strategies",
        "List VectorBT-backed strategy presets",
        _strategies,
        usage="backtest.strategies",
        examples=("finance backtest.strategies",),
    ))
    register_command(FinanceCommand(
        "backtest.describe",
        "Describe a backtest strategy and its parameters",
        _describe,
        usage="backtest.describe STRATEGY",
        examples=("finance backtest.describe sma_cross", "finance backtest.describe custom"),
    ))
    register_command(FinanceCommand(
        "backtest.run",
        "Run a VectorBT strategy backtest",
        _run,
        usage="backtest.run STRATEGY SYMBOLS START_DATE END_DATE [params='{}' strategy_file=./rule.py]",
        examples=(
            "finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31 fast=20 slow=100",
            "finance backtest.run custom AAPL 2020-01-01 2024-12-31 strategy_file=./rule.py params='{}'",
        ),
    ))
    register_command(FinanceCommand(
        "backtest.tune",
        "Run a bounded VectorBT parameter grid",
        _tune,
        usage="backtest.tune STRATEGY SYMBOLS START_DATE END_DATE grid='{}' [metric=sharpe_ratio max_runs=100]",
        examples=("finance backtest.tune sma_cross AAPL 2020-01-01 2024-12-31 grid='{\"fast\":[10,20],\"slow\":[50,100]}'",),
    ))
    register_command(FinanceCommand(
        "backtest.strategy.payload",
        "Build a normalized strategy backtest payload",
        _strategy_payload,
        usage="backtest.strategy.payload STRATEGY_ID START_DATE END_DATE [initial_cash=100000 parameters='{}']",
        examples=("finance backtest.strategy.payload mean_reversion 2024-01-01 2024-12-31",),
    ))
    register_command(FinanceCommand(
        "backtest.factor.payload",
        "Build a normalized factor backtest payload",
        _factor_payload,
        usage="backtest.factor.payload FACTOR_NAME SYMBOLS START_DATE END_DATE [timeframe=1d top_pct=0.2 bottom_pct=0.2]",
        examples=("finance backtest.factor.payload rsi_14 AAPL,MSFT,NVDA 2024-01-01 2024-12-31",),
    ))
    register_command(FinanceCommand(
        "backtest.factor.weights",
        "Preview quantile factor target weights",
        _factor_weights,
        usage='backtest.factor.weights FACTOR_NAME scores=\'{"AAPL":1.2,"MSFT":0.4}\' [top_pct=0.2 bottom_pct=0.2]',
        examples=('finance backtest.factor.weights rsi_14 scores=\'{"AAPL":1.1,"MSFT":0.3,"NVDA":2.0}\'',),
    ))
