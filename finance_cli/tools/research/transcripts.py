"""Transcript-related finance LLM tool specs.
"""
from __future__ import annotations

from finance_cli.services.transcripts import read_transcript, search_transcripts, transcript_qa
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.research.common import _bool_value
from finance_cli.tools.types import FinanceToolSpec


def _finance_transcripts(params: dict, _config: dict) -> str:
    action = str(params.get("action", "search")).lower()
    if action not in {"search", "read", "qa"}:
        raise ValueError("action must be one of: search, read, qa")
    if action == "search":
        if not params.get("symbol"):
            raise ValueError("search requires symbol")
        return as_tool_json(
            search_transcripts(
                params["symbol"],
                limit=int(params.get("limit", 4)),
                debug=_bool_value(params.get("debug")),
            )
        )
    if not (params.get("symbol") or params.get("url")):
        raise ValueError(f"{action} requires symbol or url")
    if action == "read":
        return as_tool_json(
            read_transcript(
                params.get("symbol"),
                url=params.get("url"),
                quarter=params.get("quarter", "latest"),
                max_chars=int(params.get("max_chars", 12000)),
                include_turns=_bool_value(params.get("include_turns")),
            )
        )
    return as_tool_json(
        transcript_qa(
            params.get("symbol"),
            url=params.get("url"),
            quarter=params.get("quarter", "latest"),
            limit=int(params.get("limit", 10)),
        )
    )


TOOL_DEFS = [
FinanceToolSpec(
        name="FinanceTranscripts",
        schema={
            "name": "FinanceTranscripts",
            "description": "Search, read, or extract Q&A from earnings-call transcripts. Use action=search with symbol; action=read/qa with symbol or url.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["search", "read", "qa"]},
                    "symbol": {"type": "string"},
                    "url": {"type": "string"},
                    "quarter": {"type": "string", "description": "latest or a quarter string such as Q4 2026"},
                    "limit": {"type": "integer"},
                    "max_chars": {"type": "integer"},
                    "include_turns": {"type": "boolean"},
                    "debug": {"type": "boolean"},
                },
                "required": [],
            },
        },
        handler=_finance_transcripts,
        read_only=True,
        concurrent_safe=False,
    )
]
