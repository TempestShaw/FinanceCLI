"""Public futures positioning commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.providers.base import ProviderError
from finance_cli.providers.cftc import CFTCProvider
from finance_cli.schemas import FinanceCommandResult


def _positioning_cot(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    try:
        data = CFTCProvider().cot(kv.str("market", "gold") or "gold",
                                  report=kv.str("report", "disaggregated") or "disaggregated",
                                  weeks=kv.int("weeks", 52))
        return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])
    except (ProviderError, ValueError) as exc:
        return FinanceCommandResult(ok=False, error=str(exc))


def register_positioning_commands() -> None:
    register_command(FinanceCommand(
        "positioning.cot", "Read CFTC futures-only trader positioning by category", _positioning_cot,
        usage="positioning.cot [market=gold report=disaggregated|tff|legacy weeks=52]",
        examples=("finance positioning.cot market=gold weeks=8",
                  "finance positioning.cot market=sp500 report=tff weeks=8",
                  "finance positioning.cot market=088691 report=legacy weeks=8"),
        notes=("No API key required. market accepts gold, sp500 or an exact six-character CFTC contract code.",
               "as_of_date is the position date, not the publication date. Futures-only reports; report categories differ.",
               "weeks bounds the number of latest weekly reports; each produces one row per trader category.",),
    ))
