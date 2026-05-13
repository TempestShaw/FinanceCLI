"""Connector-neutral finance capability specs."""
from __future__ import annotations

from finance_cli.tools.market import TOOL_DEFS as MARKET_TOOL_DEFS
from finance_cli.tools.research import TOOL_DEFS as RESEARCH_TOOL_DEFS
from finance_cli.tools.symbol import TOOL_DEFS as SYMBOL_TOOL_DEFS

FINANCE_TOOL_SPECS = [*MARKET_TOOL_DEFS, *SYMBOL_TOOL_DEFS, *RESEARCH_TOOL_DEFS]
TOOL_DEFS = FINANCE_TOOL_SPECS
