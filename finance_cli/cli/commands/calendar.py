"""Company calendar CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.calendar import fetch_company_calendar, fetch_earnings_dates


def _calendar_company(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: calendar.company SYMBOL")
    return FinanceCommandResult(ok=True, data=fetch_company_calendar(args[0]))


def _calendar_earnings(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: calendar.earnings SYMBOL [limit=12]")
    kv = KVArgs(args[1:])
    return FinanceCommandResult(ok=True, data=fetch_earnings_dates(args[0], limit=kv.int("limit", 12)))


def register_calendar_commands() -> None:
    register_command(FinanceCommand(
        "calendar.company",
        "Fetch company earnings/dividend calendar fields",
        _calendar_company,
        usage="calendar.company SYMBOL",
        examples=("finance calendar.company AAPL",),
    ))
    register_command(FinanceCommand(
        "calendar.earnings",
        "Fetch earnings-date rows for a company",
        _calendar_earnings,
        usage="calendar.earnings SYMBOL [limit=12]",
        examples=("finance calendar.earnings AAPL limit=8",),
    ))
