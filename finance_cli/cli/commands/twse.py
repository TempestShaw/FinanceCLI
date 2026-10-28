"""Taiwan issuer revenue and disclosure commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.providers.twse import TWSEProvider
from finance_cli.schemas import FinanceCommandResult


def _monthly_revenue(args: list[str]) -> FinanceCommandResult:
    if not args or "=" in args[0]:
        return FinanceCommandResult(ok=False, error="usage: fundamentals.revenue SYMBOL [period=monthly source=twse]")
    kv = KVArgs(args[1:])
    if kv.str("period", "monthly") != "monthly" or kv.str("source", "twse") != "twse":
        return FinanceCommandResult(ok=False, error="period must be monthly and source must be twse")
    data = TWSEProvider().monthly_revenue(args[0])
    return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])


def _recent_disclosures(args: list[str]) -> FinanceCommandResult:
    if not args or "=" in args[0]:
        return FinanceCommandResult(ok=False, error="usage: disclosures.recent SYMBOL [source=twse limit=20]")
    kv = KVArgs(args[1:])
    if kv.str("source", "twse") != "twse":
        return FinanceCommandResult(ok=False, error="source must be twse")
    data = TWSEProvider().recent_disclosures(args[0], limit=kv.int("limit", 20))
    return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])


def register_twse_commands() -> None:
    register_command(FinanceCommand(
        "fundamentals.revenue", "Read Taiwan listed-company monthly revenue from the official snapshot", _monthly_revenue,
        usage="fundamentals.revenue SYMBOL [period=monthly source=twse]",
        examples=("finance fundamentals.revenue 2330.TW period=monthly source=twse",),
        notes=("TWSE-listed issuers only; latest snapshot, not historical monthly data. Amounts are thousands of TWD.",),
    ))
    register_command(FinanceCommand(
        "disclosures.recent", "Read Taiwan listed-company material disclosures from the daily snapshot", _recent_disclosures,
        usage="disclosures.recent SYMBOL [source=twse limit=20]",
        examples=("finance disclosures.recent 2330.TW source=twse limit=5",),
        notes=("Daily snapshot only; empty output does not establish that no earlier announcements exist.",),
    ))
