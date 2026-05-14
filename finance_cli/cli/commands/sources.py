"""Provider source health CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.sources import list_sources, sources_status, test_source


def _sources_list(_args: list[str]) -> FinanceCommandResult:
    return FinanceCommandResult(ok=True, data=list_sources())


def _sources_status(_args: list[str]) -> FinanceCommandResult:
    return FinanceCommandResult(ok=True, data=sources_status())


def _sources_test(args: list[str]) -> FinanceCommandResult:
    source = args[0] if args and "=" not in args[0] else None
    kv = KVArgs(args[1:] if source else args)
    data = test_source(
        source or kv.str("source"),
        symbol=kv.str("symbol", "AAPL") or "AAPL",
        timeout=float(kv.str("timeout", "30") or "30"),
    )
    return FinanceCommandResult(ok=True, data=data)


def register_sources_commands() -> None:
    register_command(FinanceCommand(
        "sources.list",
        "List finance data sources and capabilities",
        _sources_list,
        usage="sources.list",
        examples=("finance sources.list",),
        notes=("No network calls; reports known providers and capabilities.",),
    ))
    register_command(FinanceCommand(
        "sources.status",
        "Show package and environment configuration for data sources",
        _sources_status,
        usage="sources.status",
        examples=("finance sources.status",),
        notes=("No network calls; use sources.test for connectivity checks.",),
    ))
    register_command(FinanceCommand(
        "sources.test",
        "Run small connectivity checks against one or all data sources",
        _sources_test,
        usage="sources.test [SOURCE|source=SOURCE] [symbol=AAPL timeout=30]",
        examples=(
            "finance sources.test yfinance symbol=AAPL",
            "finance sources.test sec symbol=AAPL",
            "finance sources.test source=all symbol=AAPL timeout=30",
        ),
        notes=("Returns pass/fail plus latency for configured providers.",),
    ))
