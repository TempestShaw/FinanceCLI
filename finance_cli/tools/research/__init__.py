"""Aggregated LLM tool specs for finance research capabilities."""
from __future__ import annotations

from finance_cli.tools.research.backtest import TOOL_DEFS as BACKTEST_TOOL_DEFS
from finance_cli.tools.research.filings import TOOL_DEFS as FILING_TOOL_DEFS
from finance_cli.tools.research.ir import TOOL_DEFS as IR_TOOL_DEFS
from finance_cli.tools.research.kpi import TOOL_DEFS as KPI_TOOL_DEFS
from finance_cli.tools.research.market_data import TOOL_DEFS as MARKET_DATA_TOOL_DEFS
from finance_cli.tools.research.news import TOOL_DEFS as NEWS_TOOL_DEFS
from finance_cli.tools.research.plan import TOOL_DEFS as RESEARCH_PLAN_TOOL_DEFS
from finance_cli.tools.research.price import TOOL_DEFS as PRICE_TOOL_DEFS
from finance_cli.tools.research.transcripts import TOOL_DEFS as TRANSCRIPT_TOOL_DEFS
from finance_cli.tools.research.valuation import TOOL_DEFS as VALUATION_TOOL_DEFS

TOOL_DEFS = [
    *NEWS_TOOL_DEFS,
    *FILING_TOOL_DEFS,
    *MARKET_DATA_TOOL_DEFS,
    *TRANSCRIPT_TOOL_DEFS,
    *KPI_TOOL_DEFS,
    *VALUATION_TOOL_DEFS,
    *PRICE_TOOL_DEFS,
    *RESEARCH_PLAN_TOOL_DEFS,
    *BACKTEST_TOOL_DEFS,
    *IR_TOOL_DEFS,
]
