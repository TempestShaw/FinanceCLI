"""Fundamental data CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.fundamentals import fetch_financial_statement


def _financial_statement(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: fundamentals.statement SYMBOL [statement=income|balance|cashflow period=annual|quarterly]")
    kv = KVArgs(args[1:])
    data = fetch_financial_statement(
        args[0],
        statement=kv.str("statement", "income"),
        period=kv.str("period", "annual"),
    )
    return FinanceCommandResult(ok=True, data=data)


def register_fundamentals_commands() -> None:
    register_command(FinanceCommand(
        "fundamentals.statement",
        "Fetch income/balance/cashflow statement data",
        _financial_statement,
        usage="fundamentals.statement SYMBOL [statement=income|balance|cashflow period=annual|quarterly]",
        examples=("finance fundamentals.statement NVDA statement=income period=quarterly",),
    ))
