"""KPI evidence finance LLM tool specs.
"""
from __future__ import annotations

from finance_cli.services.kpi import extract_kpis, kpi_history
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.research.common import _csv_list
from finance_cli.tools.types import FinanceToolSpec


def _finance_kpi(params: dict, _config: dict) -> str:
    action = str(params.get("action", "extract")).lower()
    if action not in {"extract", "history"}:
        raise ValueError("action must be one of: extract, history")
    if not params.get("symbol"):
        raise ValueError("symbol is required")
    if action == "history":
        return as_tool_json(
            kpi_history(
                params["symbol"],
                source=params.get("source", "transcripts"),
                metrics=_csv_list(params.get("metrics")) or None,
                limit=int(params.get("limit", 4)),
                per_document_limit=int(params.get("per_document_limit", 20)),
            )
        )
    return as_tool_json(
        extract_kpis(
            params["symbol"],
            source=params.get("source", "transcripts"),
            metrics=_csv_list(params.get("metrics")) or None,
            limit=int(params.get("limit", 30)),
            quarter=params.get("quarter", "latest"),
            form=params.get("form", "10-K"),
        )
    )


TOOL_DEFS = [
FinanceToolSpec(
        name="FinanceKPI",
        schema={
            "name": "FinanceKPI",
            "description": "Extract KPI evidence from filings/transcripts, or build KPI evidence history across recent transcripts.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["extract", "history"]},
                    "symbol": {"type": "string"},
                    "source": {"type": "string", "description": "transcripts, filings, or both"},
                    "metrics": {"type": "array", "items": {"type": "string"}},
                    "limit": {"type": "integer"},
                    "per_document_limit": {"type": "integer"},
                    "quarter": {"type": "string"},
                    "form": {"type": "string"},
                },
                "required": ["symbol"],
            },
        },
        handler=_finance_kpi,
        read_only=True,
        concurrent_safe=False,
    )
]
