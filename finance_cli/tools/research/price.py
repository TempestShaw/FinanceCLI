"""Price move finance LLM tool specs.
"""
from __future__ import annotations

from finance_cli.services.price import price_context, price_moves
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.types import FinanceToolSpec


def _finance_price(params: dict, _config: dict) -> str:
    action = str(params.get("action", "moves")).lower()
    if action not in {"moves", "context"}:
        raise ValueError("action must be one of: moves, context")
    if not params.get("symbol"):
        raise ValueError("symbol is required")
    if action == "moves":
        return as_tool_json(
            price_moves(
                params["symbol"],
                window=params.get("window", "1d"),
                years=int(params.get("years", 3)),
                threshold=params.get("threshold", "8%"),
                limit=int(params.get("limit", 20)),
                provider=params.get("provider", "auto"),
            )
        )
    target_date = params.get("date") or params.get("target_date")
    if not target_date:
        raise ValueError("context requires date or target_date")
    return as_tool_json(
        price_context(
            params["symbol"],
            target_date=target_date,
            lookback=params.get("lookback", "3D"),
            news_limit=int(params.get("news_limit", 5)),
            filing_limit=int(params.get("filing_limit", 80)),
            transcript_limit=int(params.get("transcript_limit", 12)),
        )
    )


TOOL_DEFS = [
FinanceToolSpec(
        name="FinancePrice",
        schema={
            "name": "FinancePrice",
            "description": "Find large close-to-close price moves or return a temporal evidence timeline around a date. Does not infer causality.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["moves", "context"]},
                    "symbol": {"type": "string"},
                    "window": {"type": ["string", "integer"], "description": "For moves only: trading-day window, e.g. 1D=1 trading day, 1W=5 trading days, 1M=21 trading days."},
                    "lookback": {"type": ["string", "integer"], "description": "For context only: calendar lookback around date, e.g. 3D=3 calendar days before and after, 1W=7 calendar days, 1M=30 calendar days."},
                    "years": {"type": "integer"},
                    "threshold": {"type": ["string", "number"], "description": "Decimal or percentage-point input. 0.08, 8, and 8% all mean 8%."},
                    "limit": {"type": "integer"},
                    "provider": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD for context"},
                    "target_date": {"type": "string", "description": "YYYY-MM-DD for context"},
                    "news_limit": {"type": "integer"},
                    "filing_limit": {"type": "integer"},
                    "transcript_limit": {"type": "integer"},
                },
                "required": ["symbol"],
            },
        },
        handler=_finance_price,
        read_only=True,
        concurrent_safe=False,
    )
]
