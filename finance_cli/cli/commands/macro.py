"""FRED and ALFRED economic-series commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.providers.base import ProviderError
from finance_cli.providers.fred import FREDProvider
from finance_cli.schemas import FinanceCommandResult


def _macro_search(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    query = " ".join(arg for arg in args if "=" not in arg) or kv.str("query")
    if not query:
        return FinanceCommandResult(ok=False, error="usage: macro.search QUERY [limit=20]")
    try:
        data = FREDProvider().search(query, limit=kv.int("limit", 20))
        return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])
    except (ProviderError, ValueError) as exc:
        return FinanceCommandResult(ok=False, error=str(exc))


def _macro_series(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    series_id = args[0] if args and "=" not in args[0] else kv.str("series_id")
    if not series_id:
        return FinanceCommandResult(ok=False, error="usage: macro.series SERIES_ID [start=YYYY-MM-DD end=YYYY-MM-DD as_of=YYYY-MM-DD limit=1000]")
    try:
        data = FREDProvider().series(series_id, start=kv.str("start"), end=kv.str("end"),
                                     as_of=kv.str("as_of"), limit=kv.int("limit", 1000))
        return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])
    except (ProviderError, ValueError) as exc:
        return FinanceCommandResult(ok=False, error=str(exc))


def register_macro_commands() -> None:
    register_command(FinanceCommand(
        "macro.search", "Search FRED economic series", _macro_search,
        usage="macro.search QUERY [limit=20]",
        examples=('finance macro.search "consumer price index" limit=5',),
        notes=("Requires FRED_API_KEY. Returns matching series metadata with units and frequency.",),
    ))
    register_command(FinanceCommand(
        "macro.series", "Read economic observations with an optional ALFRED vintage", _macro_series,
        usage="macro.series SERIES_ID [start=YYYY-MM-DD end=YYYY-MM-DD as_of=YYYY-MM-DD limit=1000]",
        examples=("finance macro.series CPIAUCSL start=2020-01-01 limit=1000",
                  "finance macro.series GDP as_of=2024-01-01 limit=8"),
        notes=("Requires FRED_API_KEY. as_of pins both real-time boundaries; missing values stay null.",
               "Returns the latest bounded observations in chronological order; truncated reports omitted history.",),
    ))
