"""SEC filing finance LLM tool specs.
"""
from __future__ import annotations

from finance_cli.services.filings import fetch_filings, list_filing_sections, read_filing_section
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.research.common import _bool_value, _csv_list
from finance_cli.tools.types import FinanceToolSpec


def _finance_filings(params: dict, _config: dict) -> str:
    action = str(params.get("action", "recent")).lower()
    if action not in {"recent", "sections", "read"}:
        raise ValueError("action must be one of: recent, sections, read")
    if action == "read":
        if not (params.get("symbol") or params.get("accession") or params.get("accession_no") or params.get("url")):
            raise ValueError("read requires symbol, accession, accession_no, or url")
        return as_tool_json(
            read_filing_section(
                symbol=params.get("symbol"),
                accession_no=params.get("accession") or params.get("accession_no"),
                url=params.get("url"),
                form=params.get("form", "10-K"),
                section=params.get("section", "business"),
                max_chars=int(params.get("max_chars", 8000)),
            )
        )
    if action == "sections":
        if not (params.get("symbol") or params.get("accession") or params.get("accession_no") or params.get("url")):
            raise ValueError("sections requires symbol, accession, accession_no, or url")
        return as_tool_json(
            list_filing_sections(
                symbol=params.get("symbol"),
                accession_no=params.get("accession") or params.get("accession_no"),
                url=params.get("url"),
                form=params.get("form", "10-K"),
            )
        )
    if not params.get("symbol"):
        raise ValueError("symbol is required for recent filings")
    return as_tool_json(
        fetch_filings(
            params["symbol"],
            forms=_csv_list(params.get("forms")) or None,
            limit=int(params.get("limit", 20)),
            classify=_bool_value(params.get("classify")),
        )
    )


TOOL_DEFS = [
FinanceToolSpec(
        name="FinanceFilings",
        schema={
            "name": "FinanceFilings",
            "description": "Fetch recent SEC filings, list sections, or read canonical 10-K sections. Use action=recent with symbol; action=sections/read with symbol, accession, accession_no, or url.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["recent", "sections", "read"]},
                    "symbol": {"type": "string"},
                    "accession": {"type": "string"},
                    "accession_no": {"type": "string"},
                    "url": {"type": "string"},
                    "form": {"type": "string"},
                    "section": {"type": "string", "description": "business, risk_factors, mda, or segments"},
                    "max_chars": {"type": "integer"},
                    "forms": {"type": "array", "items": {"type": "string"}},
                    "limit": {"type": "integer"},
                    "classify": {"type": "boolean"},
                },
                "required": [],
            },
        },
        handler=_finance_filings,
        read_only=True,
        concurrent_safe=True,
    )
]
