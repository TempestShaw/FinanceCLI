"""Symbol finance CLI commands."""
from __future__ import annotations

from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.symbols import fetch_symbol_profile


def _symbol_snapshot(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="symbol is required")
    return FinanceCommandResult(ok=True, data=fetch_symbol_profile(args[0]))


def register_symbol_commands() -> None:
    register_command(FinanceCommand(
        "symbol.snapshot",
        "Show real quote and company metadata for a symbol",
        _symbol_snapshot,
        usage="symbol.snapshot SYMBOL",
        examples=("finance symbol.snapshot NVDA",),
    ))
    register_command(FinanceCommand(
        "symbol.profile",
        "Show real quote and SEC company metadata for a symbol",
        _symbol_snapshot,
        usage="symbol.profile SYMBOL",
        examples=("finance symbol.profile IOT",),
        notes=("Uses yfinance for market metadata and SEC ticker metadata for CIK/company identity.",),
    ))
