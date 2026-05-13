"""News-related finance LLM tool specs.
"""
from __future__ import annotations

from finance_cli.services.news import analyze_news, search_news
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.types import FinanceToolSpec


def _finance_news(params: dict, _config: dict) -> str:
    return as_tool_json(
        search_news(
            query=params.get("query"),
            symbol=params.get("symbol"),
            sector=params.get("sector"),
            max_records=int(params.get("max_records", 20)),
            timespan=params.get("timespan"),
            date=params.get("date"),
            start_date=params.get("start_date"),
            end_date=params.get("end_date"),
            start_datetime=params.get("start_datetime"),
            end_datetime=params.get("end_datetime"),
        )
    )


def _finance_news_analytics(params: dict, _config: dict) -> str:
    return as_tool_json(
        analyze_news(
            analysis=params.get("analysis", "timeline"),
            query=params.get("query"),
            symbol=params.get("symbol"),
            sector=params.get("sector"),
            mode=params.get("mode"),
            max_records=int(params.get("max_records", 50)),
            timespan=params.get("timespan"),
            date=params.get("date"),
            start_date=params.get("start_date"),
            end_date=params.get("end_date"),
            start_datetime=params.get("start_datetime"),
            end_datetime=params.get("end_datetime"),
        )
    )


TOOL_DEFS = [
FinanceToolSpec(
        name="FinanceNews",
        schema={
            "name": "FinanceNews",
            "description": "Search finance news by query, symbol, or sector.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "symbol": {"type": "string"},
                    "sector": {"type": "string"},
                    "max_records": {"type": "integer"},
                    "timespan": {"type": "string", "description": "Relative lookback from now, such as 30D, 1W, 1M, 24H, or 90min"},
                    "date": {"type": "string", "description": "One full UTC day, YYYY-MM-DD"},
                    "start_date": {"type": "string", "description": "Full-day range start, YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "Full-day range end, YYYY-MM-DD"},
                    "start_datetime": {"type": "string", "description": "Optional precise start, YYYYMMDDHHMMSS"},
                    "end_datetime": {"type": "string", "description": "Optional precise end, YYYYMMDDHHMMSS"},
                },
                "required": [],
            },
        },
        handler=_finance_news,
        read_only=True,
        concurrent_safe=True,
    ),
FinanceToolSpec(
        name="FinanceNewsAnalytics",
        schema={
            "name": "FinanceNewsAnalytics",
            "description": "Analyze news with GDELT modes: timeline, tone, context, geo, or doc.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "analysis": {"type": "string", "description": "timeline, tone, context, geo, or doc"},
                    "query": {"type": "string"},
                    "symbol": {"type": "string"},
                    "sector": {"type": "string"},
                    "mode": {"type": "string", "description": "Optional provider-specific mode"},
                    "max_records": {"type": "integer"},
                    "timespan": {"type": "string", "description": "Relative lookback from now, such as 30D, 1W, 1M, 24H, or 90min"},
                    "date": {"type": "string", "description": "One full UTC day, YYYY-MM-DD"},
                    "start_date": {"type": "string", "description": "Full-day range start, YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "Full-day range end, YYYY-MM-DD"},
                    "start_datetime": {"type": "string", "description": "Optional precise start, YYYYMMDDHHMMSS"},
                    "end_datetime": {"type": "string", "description": "Optional precise end, YYYYMMDDHHMMSS"},
                },
                "required": [],
            },
        },
        handler=_finance_news_analytics,
        read_only=True,
        concurrent_safe=False,
    )
]
