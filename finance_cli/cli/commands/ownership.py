"""Ownership data CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.ownership import fetch_holders


def _ownership_holders(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: ownership.holders SYMBOL [limit=10]")
    kv = KVArgs(args[1:])
    return FinanceCommandResult(ok=True, data=fetch_holders(args[0], limit=kv.int("limit", 10)))


def register_ownership_commands() -> None:
    register_command(FinanceCommand(
        "ownership.holders",
        "Fetch major, institutional, fund, and insider holder tables",
        _ownership_holders,
        usage="ownership.holders SYMBOL [limit=10]",
        examples=("finance ownership.holders NVDA limit=5",),
        notes=("Uses yfinance holder tables; field availability can vary by ticker.",),
    ))
