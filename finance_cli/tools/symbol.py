"""Symbol finance tools for the LLM runtime."""
from __future__ import annotations

from finance_cli.services.symbols import fetch_symbol_profile
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.types import FinanceToolSpec


SYMBOL_SNAPSHOT_SCHEMA = {
    "name": "FinanceSymbolSnapshot",
    "description": "Return a structured snapshot for a public market symbol.",
    "input_schema": {
        "type": "object",
        "properties": {
            "symbol": {"type": "string", "description": "Ticker symbol, for example NVDA"},
        },
        "required": ["symbol"],
    },
}


def _finance_symbol_snapshot(params: dict, _config: dict) -> str:
    return as_tool_json(fetch_symbol_profile(params["symbol"]))


TOOL_DEFS = [
    FinanceToolSpec(
        name="FinanceSymbolSnapshot",
        schema=SYMBOL_SNAPSHOT_SCHEMA,
        handler=_finance_symbol_snapshot,
        read_only=True,
        concurrent_safe=True,
    ),
]
