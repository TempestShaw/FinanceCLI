"""KPI extraction CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.kpi import extract_kpis, kpi_history


def _kpi_extract(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: kpi.extract SYMBOL [source=transcripts|filings|both metrics=arr,nrr limit=30 quarter=latest form=10-K]")
    kv = KVArgs(args[1:])
    data = extract_kpis(
        args[0],
        source=kv.str("source", "transcripts"),
        metrics=kv.csv("metrics") or None,
        limit=kv.int("limit", 30),
        quarter=kv.str("quarter", "latest"),
        form=kv.str("form", "10-K"),
    )
    return FinanceCommandResult(ok=True, data=data)


def _kpi_history(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: kpi.history SYMBOL [source=transcripts metrics=arr,nrr limit=4 per_document_limit=20]")
    kv = KVArgs(args[1:])
    data = kpi_history(
        args[0],
        source=kv.str("source", "transcripts"),
        metrics=kv.csv("metrics") or None,
        limit=kv.int("limit", 4),
        per_document_limit=kv.int("per_document_limit", 20),
    )
    return FinanceCommandResult(ok=True, data=data)


def register_kpi_commands() -> None:
    register_command(FinanceCommand(
        "kpi.extract",
        "Extract KPI evidence from filings or transcripts",
        _kpi_extract,
        usage="kpi.extract SYMBOL [source=transcripts|filings|both metrics=arr,nrr limit=30 quarter=latest form=10-K]",
        examples=(
            "finance kpi.extract IOT source=transcripts metrics=arr,net_new_arr,large_customers,nrr",
            "finance kpi.extract IOT source=both metrics=arr,emerging_products,rpo limit=20",
        ),
        notes=("Returns evidence rows, not investment conclusions.",),
    ))
    register_command(FinanceCommand(
        "kpi.history",
        "Extract KPI evidence across recent transcripts",
        _kpi_history,
        usage="kpi.history SYMBOL [source=transcripts metrics=arr,nrr limit=4 per_document_limit=20]",
        examples=("finance kpi.history IOT metrics=arr,large_customers,emerging_products limit=4",),
    ))
