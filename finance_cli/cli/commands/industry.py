"""Yahoo industry CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.sectors import fetch_industry_overview, fetch_industry_table, list_industry_keys


def _industry_keys(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return FinanceCommandResult(ok=True, data=list_industry_keys(sector=kv.str("sector")))


def _industry_overview(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: industry.overview KEY")
    return FinanceCommandResult(ok=True, data=fetch_industry_overview(args[0]))


def _industry_table(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(
            ok=False,
            error="usage: industry.table KEY [table=top_companies|top_growth_companies|top_performing_companies|research_reports limit=25]",
        )
    kv = KVArgs(args[1:])
    data = fetch_industry_table(
        args[0],
        table=kv.str("table", "top_companies") or "top_companies",
        limit=kv.int("limit", 25),
    )
    return FinanceCommandResult(ok=True, data=data)


def register_industry_commands() -> None:
    register_command(FinanceCommand(
        "industry.keys",
        "List Yahoo industry keys, optionally filtered by sector",
        _industry_keys,
        usage="industry.keys [sector=SECTOR_KEY]",
        examples=("finance industry.keys sector=technology",),
    ))
    register_command(FinanceCommand(
        "industry.overview",
        "Fetch industry overview metadata",
        _industry_overview,
        usage="industry.overview KEY",
        examples=("finance industry.overview software-infrastructure",),
    ))
    register_command(FinanceCommand(
        "industry.table",
        "Fetch industry top companies or reports",
        _industry_table,
        usage="industry.table KEY [table=top_companies|top_growth_companies|top_performing_companies|research_reports limit=25]",
        examples=(
            "finance industry.table software-infrastructure table=top_companies limit=10",
            "finance industry.table software-infrastructure table=top_growth_companies limit=10",
        ),
    ))
