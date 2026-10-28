"""Exchange issue breadth CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.providers.nasdaq_breadth import fetch_breadth
from finance_cli.schemas import FinanceCommandResult


def _market_breadth(args: list[str]) -> FinanceCommandResult:
    positional_market = args[0] if args and "=" not in args[0] else None
    kv = KVArgs(args[1:] if positional_market else args)
    market = positional_market or kv.str("market", "NASDAQ") or "NASDAQ"
    year = kv.int("year", 0) if "year" in kv.values else None
    data = fetch_breadth(market, year=year, limit=kv.int("limit", 20))
    return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])


def register_breadth_commands() -> None:
    register_command(FinanceCommand(
        "market.breadth", "Fetch actual Nasdaq advancing, declining, and unchanged issue counts",
        _market_breadth, usage="market.breadth [MARKET=NASDAQ] [year=YYYY limit=20]",
        examples=("finance market.breadth NASDAQ limit=20",),
        notes=(
            "Supports Nasdaq-listed issues only, from the official annual file; newest observations first.",
            "Year defaults to the current UTC year. Source dates and retrieval age are explicit; this is not live breadth.",
            "Does not supply NYSE, 50/200 DMA, new-high/new-low, or up/down volume breadth.",
        ),
    ))
