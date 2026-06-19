"""Fundamental data CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.fundamentals import fetch_financial_metrics, fetch_financial_statement_with_display, fundamentals_growth


def _financial_statement(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: fundamentals.statement SYMBOL [statement=income|balance|cashflow period=annual|quarterly provider=sec|yahoo]")
    kv = KVArgs(args[1:])
    data, display = fetch_financial_statement_with_display(
        args[0],
        statement=kv.str("statement", "income"),
        period=kv.str("period", "annual"),
        provider=kv.str("provider", "sec"),
    )
    return FinanceCommandResult(ok=True, data=data, display=display)


def _financial_metrics(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: fundamentals.metrics SYMBOL [period=annual|quarterly metrics=revenue,eps,net_income,operating_income]")
    kv = KVArgs(args[1:])
    statement = (kv.str("statement", "income") or "income").strip().lower()
    if statement != "income":
        return FinanceCommandResult(ok=False, error="statement currently must be income")
    data = fetch_financial_metrics(
        args[0],
        period=kv.str("period", "quarterly"),
        metrics=kv.csv("metrics") or None,
    )
    return FinanceCommandResult(ok=True, data=data)


def _fundamentals_growth(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: fundamentals.growth SYMBOL [metrics=revenue,eps,operating_margin,net_margin,roe periods=quarterly,annual years=5 provider=sec]")
    kv = KVArgs(args[1:])
    data = fundamentals_growth(
        args[0],
        metrics=kv.csv("metrics") or None,
        periods=kv.csv("periods") or None,
        years=kv.int("years", 5),
        provider=kv.str("provider", "sec"),
    )
    return FinanceCommandResult(ok=True, data=data, warnings=data.get("warnings", []))


def register_fundamentals_commands() -> None:
    register_command(FinanceCommand(
        "fundamentals.statement",
        "Fetch income/balance/cashflow statement data",
        _financial_statement,
        usage="fundamentals.statement SYMBOL [statement=income|balance|cashflow period=annual|quarterly provider=sec|yahoo]",
        examples=(
            "finance fundamentals.statement NVDA statement=income period=quarterly provider=sec",
            "finance fundamentals.statement NVDA statement=income period=quarterly provider=yahoo",
        ),
        notes=("Supports SEC/edgartools standard XBRL rows and Yahoo Finance statement tables.",),
    ))
    register_command(FinanceCommand(
        "fundamentals.metrics",
        "Fetch standard SEC financial metrics with edgartools getters",
        _financial_metrics,
        usage="fundamentals.metrics SYMBOL [period=annual|quarterly metrics=revenue,eps,net_income,operating_income]",
        examples=("finance fundamentals.metrics NVDA period=quarterly metrics=revenue,eps,net_income,operating_income",),
        notes=("Uses edgartools financial getters for standard metrics; EPS is net_income / diluted_shares.",),
    ))
    register_command(FinanceCommand(
        "fundamentals.growth",
        "Return raw fundamental history plus YoY and CAGR calculations",
        _fundamentals_growth,
        usage="fundamentals.growth SYMBOL [metrics=revenue,eps,operating_margin,net_margin,roe periods=quarterly,annual years=5 provider=sec]",
        examples=("finance fundamentals.growth NVDA metrics=revenue,eps periods=quarterly,annual years=5",),
        notes=(
            "Returns auditable raw period values together with deterministic YoY and CAGR calculations.",
            "EPS prefers reported diluted EPS when available and otherwise uses net_income / diluted_shares.",
            "CAGR is returned for positive revenue/EPS start and end values; margin and ROE comparisons are returned as deltas.",
        ),
    ))
