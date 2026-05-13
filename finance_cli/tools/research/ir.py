"""IR presentation finance LLM tool specs.
"""
from __future__ import annotations

from finance_cli.services.ir import list_ir_presentations, read_ir_presentation
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.types import FinanceToolSpec


def _finance_ir(params: dict, _config: dict) -> str:
    action = str(params.get("action", "")).strip().lower()
    if action == "presentations":
        symbol = str(params.get("symbol") or "").strip()
        if not symbol:
            return as_tool_json({"error": "symbol is required for action=presentations"})
        limit = int(params.get("limit") or 20)
        return as_tool_json(list_ir_presentations(symbol, limit=limit, source=params.get("source", "auto")))
    if action == "read":
        url = str(params.get("url") or "").strip()
        if not url:
            return as_tool_json({"error": "url is required for action=read"})
        max_chars = int(params.get("max_chars") or 12000)
        return as_tool_json(read_ir_presentation(url, max_chars=max_chars, ocr=params.get("ocr", "off")))
    return as_tool_json({"error": f"unknown action: {action}. Use presentations or read."})


TOOL_DEFS = [
FinanceToolSpec(
        name="FinanceIR",
        schema={
            "name": "FinanceIR",
            "description": (
                "Discover investor day decks and earnings presentation exhibits from SEC 8-K filings, "
                "or extract text from a specific presentation URL. "
                "action=presentations: scan recent 8-K Exhibit 99 files for presentation candidates. "
                "action=read: fetch and extract text from a presentation URL."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["presentations", "read"],
                        "description": "presentations=discover candidates, read=extract text from URL",
                    },
                    "symbol": {
                        "type": "string",
                        "description": "Ticker symbol, e.g. IOT. Required for action=presentations.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max 8-K filings to scan. Default 20.",
                    },
                    "source": {
                        "type": "string",
                        "enum": ["auto", "sec", "company_ir", "all"],
                        "description": "auto=SEC first then company IR fallback; all=combine both.",
                    },
                    "url": {
                        "type": "string",
                        "description": "Exhibit URL from ir.presentations output. Required for action=read.",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Max characters to return. Default 12000.",
                    },
                    "ocr": {
                        "type": "string",
                        "enum": ["off", "auto", "force"],
                        "description": "Optional PaddleOCR mode for action=read. Default off.",
                    },
                },
                "required": ["action"],
            },
        },
        handler=_finance_ir,
        read_only=True,
        concurrent_safe=True,
    )
]
