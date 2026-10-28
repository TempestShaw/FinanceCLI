"""FINRA short-position and daily short-sale volume commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.providers.finra import fetch_short_interest, fetch_short_volume
from finance_cli.schemas import FinanceCommandResult


def _short_interest(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: short.interest SYMBOL [periods=6]")
    data = fetch_short_interest(args[0], periods=KVArgs(args[1:]).int("periods", 6))
    return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])


def _short_volume(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: short.volume SYMBOL [days=20]")
    data = fetch_short_volume(args[0], days=KVArgs(args[1:]).int("days", 20))
    return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])


def register_short_commands() -> None:
    register_command(FinanceCommand(
        "short.interest", "Fetch FINRA settlement-date short positions and changes",
        _short_interest, usage="short.interest SYMBOL [periods=6]",
        examples=("finance short.interest AAPL periods=6",),
        notes=(
            "Twice-monthly position snapshots, not daily short-sale volume. Settlement dates are not publication dates.",
            "Uses the official consolidatedShortInterest API; optional FINRA_ACCESS_TOKEN supplies a Bearer token.",
            "FINRA access and reuse terms apply; anonymous access may change.",
        ),
    ))
    register_command(FinanceCommand(
        "short.volume", "Fetch FINRA daily off-exchange NMS short-sale volume",
        _short_volume, usage="short.volume SYMBOL [days=20]",
        examples=("finance short.volume AAPL days=5",),
        notes=(
            "Requests at most days prior weekday files, excluding today in New York; days must be 1–60.",
            "Holidays and HTTP 403/404 files remain explicit gaps; no older replacement files are requested.",
            "CNMS off-exchange activity excludes exchange trades and is not outstanding short interest.",
            "Source data is free for non-commercial use under FINRA's terms.",
        ),
    ))
