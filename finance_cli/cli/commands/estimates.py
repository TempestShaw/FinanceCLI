"""Consensus estimate CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.providers.base import ProviderError
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.estimates import compare_estimates, consensus_estimates


def _estimates_consensus(args: list[str]) -> FinanceCommandResult:
    symbol = args[0] if args and "=" not in args[0] else None
    kv = KVArgs(args[1:] if symbol else args)
    symbol = symbol or kv.str("symbol")
    if not symbol:
        return FinanceCommandResult(ok=False, error="usage: estimates.consensus SYMBOL [period=annual|quarter limit=10 page=0]; symbol is required")
    try:
        data = consensus_estimates(
            symbol,
            period=kv.str("period", "annual") or "annual",
            page=kv.int("page", 0),
            limit=kv.int("limit", 10),
        )
        return FinanceCommandResult(ok=True, data=data)
    except ProviderError as exc:
        return FinanceCommandResult(ok=False, error=str(exc))


def _estimates_compare(args: list[str]) -> FinanceCommandResult:
    symbol = args[0] if args and "=" not in args[0] else None
    kv = KVArgs(args[1:] if symbol else args)
    try:
        return FinanceCommandResult(ok=True, data=compare_estimates(symbol or kv.str("symbol"), **kv.values))
    except ValueError as exc:
        return FinanceCommandResult(ok=False, error=f"usage: estimates.compare [SYMBOL] revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027; {exc}")


def register_estimates_commands() -> None:
    register_command(FinanceCommand(
        "estimates.consensus",
        "Fetch FMP analyst consensus estimates when configured",
        _estimates_consensus,
        usage="estimates.consensus SYMBOL [period=annual|quarter limit=10 page=0]",
        examples=("finance estimates.consensus IOT period=annual limit=5",),
        notes=("Requires FMP_API_KEY. Makes one short FMP request and returns a structured configuration error when unconfigured.",),
    ))
    register_command(FinanceCommand(
        "estimates.compare",
        "Compare user assumptions against explicit consensus inputs",
        _estimates_compare,
        usage="estimates.compare [SYMBOL] revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027",
        examples=("finance estimates.compare IOT revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027",),
        notes=("No network calls. Compares only values explicitly supplied by the user or agent.",),
    ))
