"""Market data and financial statement LLM tool specs.
"""
from __future__ import annotations

from finance_cli.services.fundamentals import fetch_financial_statement
from finance_cli.services.market_data import fetch_ohlcv, fetch_ohlcv_batch, fetch_realtime_quote
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.research.common import _bool_value, _csv_list
from finance_cli.tools.types import FinanceToolSpec


def _finance_quote(params: dict, _config: dict) -> str:
    return as_tool_json(fetch_realtime_quote(params["symbol"]))


def _finance_ohlcv(params: dict, _config: dict) -> str:
    symbols = _csv_list(params.get("symbols")) or _csv_list(params.get("symbol"))
    if not symbols:
        raise ValueError("symbols is required")
    kwargs = {
        "timeframe": params.get("timeframe", "1d"),
        "start_date": params.get("start_date"),
        "end_date": params.get("end_date"),
        "limit": int(params.get("limit", 200)),
        "provider": params.get("provider", "auto"),
        "include_attempts": _bool_value(params.get("include_attempts")),
    }
    if len(symbols) == 1:
        return as_tool_json(fetch_ohlcv(symbols[0], **kwargs))
    return as_tool_json(fetch_ohlcv_batch(symbols, **kwargs))


def _finance_statement(params: dict, _config: dict) -> str:
    return as_tool_json(
        fetch_financial_statement(
            params["symbol"],
            statement=params.get("statement", "income"),
            period=params.get("period", "annual"),
        )
    )


TOOL_DEFS = [
FinanceToolSpec(
        name="FinanceQuote",
        schema={
            "name": "FinanceQuote",
            "description": "Fetch the best available quote and company snapshot for a symbol.",
            "input_schema": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"],
            },
        },
        handler=_finance_quote,
        read_only=True,
        concurrent_safe=True,
    ),
FinanceToolSpec(
        name="FinanceOHLCV",
        schema={
            "name": "FinanceOHLCV",
            "description": "Fetch normalized OHLCV records for one or more symbols.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "symbol": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "limit": {"type": "integer"},
                    "provider": {"type": "string", "description": "auto, alpaca, or yfinance"},
                    "include_attempts": {"type": "boolean"},
                },
                "required": [],
            },
        },
        handler=_finance_ohlcv,
        read_only=True,
        concurrent_safe=True,
    ),
FinanceToolSpec(
        name="FinanceFinancialStatement",
        schema={
            "name": "FinanceFinancialStatement",
            "description": "Fetch income statement, balance sheet, or cashflow data.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "statement": {"type": "string"},
                    "period": {"type": "string"},
                },
                "required": ["symbol"],
            },
        },
        handler=_finance_statement,
        read_only=True,
        concurrent_safe=True,
    )
]
