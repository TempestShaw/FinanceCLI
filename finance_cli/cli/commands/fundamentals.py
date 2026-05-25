"""Fundamental data CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.fundamentals import fetch_financial_metrics, fetch_financial_statement


def _financial_statement(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: fundamentals.statement SYMBOL [statement=income|balance|cashflow period=annual|quarterly provider=sec|yahoo]")
    kv = KVArgs(args[1:])
    data = fetch_financial_statement(
        args[0],
        statement=kv.str("statement", "income"),
        period=kv.str("period", "annual"),
        provider=kv.str("provider", "sec"),
    )
    return FinanceCommandResult(ok=True, data=data)


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
