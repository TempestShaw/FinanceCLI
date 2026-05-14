"""Yahoo sector CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.sectors import (
    fetch_sector_industries,
    fetch_sector_overview,
    fetch_sector_table,
    list_sector_keys,
)


def _sector_keys(_args: list[str]) -> FinanceCommandResult:
    return FinanceCommandResult(ok=True, data=list_sector_keys())


def _sector_overview(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: sector.overview KEY")
    return FinanceCommandResult(ok=True, data=fetch_sector_overview(args[0]))


def _sector_industries(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: sector.industries KEY")
    return FinanceCommandResult(ok=True, data=fetch_sector_industries(args[0]))


def _sector_table(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(
            ok=False,
            error="usage: sector.table KEY [table=top_companies|top_etfs|top_mutual_funds|research_reports limit=25]",
        )
    kv = KVArgs(args[1:])
    data = fetch_sector_table(
        args[0],
        table=kv.str("table", "top_companies") or "top_companies",
        limit=kv.int("limit", 25),
    )
    return FinanceCommandResult(ok=True, data=data)


def register_sector_commands() -> None:
    register_command(FinanceCommand(
        "sector.keys",
        "List Yahoo sector keys",
        _sector_keys,
        usage="sector.keys",
        examples=("finance sector.keys",),
    ))
    register_command(FinanceCommand(
        "sector.overview",
        "Fetch sector overview metadata",
        _sector_overview,
        usage="sector.overview KEY",
        examples=("finance sector.overview technology",),
    ))
    register_command(FinanceCommand(
        "sector.industries",
        "List industries in a sector",
        _sector_industries,
        usage="sector.industries KEY",
        examples=("finance sector.industries technology",),
    ))
    register_command(FinanceCommand(
        "sector.table",
        "Fetch sector top companies, funds, or reports",
        _sector_table,
        usage="sector.table KEY [table=top_companies|top_etfs|top_mutual_funds|research_reports limit=25]",
        examples=(
            "finance sector.table technology table=top_companies limit=10",
            "finance sector.table technology table=top_etfs limit=5",
        ),
    ))
