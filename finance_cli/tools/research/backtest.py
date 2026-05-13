"""Backtest finance LLM tool specs."""
from __future__ import annotations

from finance_cli.services.backtest import (
    available_backtest_strategies,
    build_factor_backtest_payload,
    build_strategy_backtest_payload,
    describe_backtest_strategy,
    run_backtest,
    tune_backtest,
)
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.research.common import _csv_list
from finance_cli.tools.types import FinanceToolSpec


def _finance_backtest(params: dict, _config: dict) -> str:
    action = str(params.get("action", "run")).lower()
    if action == "strategies":
        return as_tool_json(available_backtest_strategies())
    if action == "describe":
        return as_tool_json(describe_backtest_strategy(str(params["strategy"])))
    if action == "tune":
        return as_tool_json(
            tune_backtest(
                strategy=str(params["strategy"]),
                symbols=_csv_list(params.get("symbols")),
                start_date=str(params["start_date"]),
                end_date=str(params["end_date"]),
                grid=params.get("grid") or {},
                metric=params.get("metric", "sharpe_ratio"),
                max_runs=int(params.get("max_runs", 100)),
                timeframe=params.get("timeframe", "1d"),
                initial_cash=float(params.get("initial_cash", 100000.0)),
                fees=float(params.get("fees", 0.001)),
                fixed_fees=float(params.get("fixed_fees", 0.0)),
                slippage=float(params.get("slippage", 0.0)),
                provider=params.get("provider", "auto"),
                strategy_file=params.get("strategy_file"),
            )
        )
    if action != "run":
        raise ValueError("action must be one of: strategies, describe, run, tune")
    return as_tool_json(
        run_backtest(
            strategy=str(params["strategy"]),
            symbols=_csv_list(params.get("symbols")),
            start_date=str(params["start_date"]),
            end_date=str(params["end_date"]),
            timeframe=params.get("timeframe", "1d"),
            initial_cash=float(params.get("initial_cash", 100000.0)),
            fees=float(params.get("fees", 0.001)),
            fixed_fees=float(params.get("fixed_fees", 0.0)),
            slippage=float(params.get("slippage", 0.0)),
            provider=params.get("provider", "auto"),
            params=params.get("params") or {},
            strategy_file=params.get("strategy_file"),
            plot_path=params.get("plot_path"),
        )
    )


def _finance_backtest_payload(params: dict, _config: dict) -> str:
    kind = str(params.get("kind", "factor")).lower()
    if kind == "strategy":
        return as_tool_json(
            build_strategy_backtest_payload(
                strategy_id=params["strategy_id"],
                start_date=params["start_date"],
                end_date=params["end_date"],
                initial_cash=float(params.get("initial_cash", 100000.0)),
                parameters=params.get("parameters") or {},
                fee_mode=params.get("fee_mode", "mixed"),
                fixed_fee=float(params.get("fixed_fee", 2.0)),
                fees_pct=float(params.get("fees_pct", 0.001)),
            )
        )
    return as_tool_json(
        build_factor_backtest_payload(
            factor_name=params["factor_name"],
            symbols=_csv_list(params.get("symbols")),
            start_date=params["start_date"],
            end_date=params["end_date"],
            timeframe=params.get("timeframe", "1d"),
            initial_cash=float(params.get("initial_cash", 100000.0)),
            direction=params.get("direction", "long_short"),
            top_pct=float(params.get("top_pct", 0.2)),
            bottom_pct=float(params.get("bottom_pct", 0.2)),
            rebalance_freq=params.get("rebalance_freq", "monthly"),
            fixed_fee=float(params.get("fixed_fee", 2.0)),
            fees_pct=float(params.get("fees_pct", 0.001)),
        )
    )


TOOL_DEFS = [
    FinanceToolSpec(
        name="FinanceBacktest",
        schema={
            "name": "FinanceBacktest",
            "description": "List, describe, run, or tune VectorBT-backed backtest strategies.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["strategies", "describe", "run", "tune"]},
                    "strategy": {"type": "string"},
                    "symbols": {"type": ["array", "string"], "items": {"type": "string"}},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "initial_cash": {"type": "number"},
                    "fees": {"type": "number"},
                    "fixed_fees": {"type": "number"},
                    "slippage": {"type": "number"},
                    "provider": {"type": "string"},
                    "params": {"type": "object"},
                    "plot_path": {"type": "string"},
                    "grid": {"type": "object"},
                    "metric": {"type": "string"},
                    "max_runs": {"type": "integer"},
                    "strategy_file": {"type": "string"},
                },
                "required": ["action"],
            },
        },
        handler=_finance_backtest,
        read_only=True,
        concurrent_safe=False,
    ),
    FinanceToolSpec(
        name="FinanceBacktestPayload",
        schema={
            "name": "FinanceBacktestPayload",
            "description": "Build a normalized strategy or factor backtest payload.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "description": "factor or strategy"},
                    "strategy_id": {"type": "string"},
                    "factor_name": {"type": "string"},
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "initial_cash": {"type": "number"},
                    "direction": {"type": "string"},
                    "top_pct": {"type": "number"},
                    "bottom_pct": {"type": "number"},
                    "rebalance_freq": {"type": "string"},
                    "parameters": {"type": "object"},
                },
                "required": ["kind", "start_date", "end_date"],
            },
        },
        handler=_finance_backtest_payload,
        read_only=True,
        concurrent_safe=True,
    )
]
