"""Market finance tools for the LLM runtime."""
from __future__ import annotations

from finance_cli.core.market import get_market_regime, get_sector_heat
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.types import FinanceToolSpec


MARKET_REGIME_SCHEMA = {
    "name": "FinanceMarketRegime",
    "description": "Return current market regime context for a market and timeframe.",
    "input_schema": {
        "type": "object",
        "properties": {
            "market": {"type": "string", "description": "Market code, default US"},
            "timeframe": {"type": "string", "description": "Research horizon, default swing"},
        },
        "required": [],
    },
}

SECTOR_HEAT_SCHEMA = {
    "name": "FinanceSectorHeat",
    "description": "Return sector or industry heat rankings for a market.",
    "input_schema": {
        "type": "object",
        "properties": {
            "market": {"type": "string", "description": "Market code, default US"},
            "lookback_days": {"type": "integer", "description": "Lookback window in days"},
            "group_by": {"type": "string", "description": "Grouping level, default sector"},
        },
        "required": [],
    },
}


def _finance_market_regime(params: dict, _config: dict) -> str:
    result = get_market_regime(
        market=params.get("market", "US"),
        timeframe=params.get("timeframe", "swing"),
    )
    return as_tool_json(result.to_dict())


def _finance_sector_heat(params: dict, _config: dict) -> str:
    result = get_sector_heat(
        market=params.get("market", "US"),
        lookback_days=int(params.get("lookback_days", 20)),
        group_by=params.get("group_by", "sector"),
    )
    return as_tool_json(result.to_dict())


TOOL_DEFS = [
    FinanceToolSpec(
        name="FinanceMarketRegime",
        schema=MARKET_REGIME_SCHEMA,
        handler=_finance_market_regime,
        read_only=True,
        concurrent_safe=True,
    ),
    FinanceToolSpec(
        name="FinanceSectorHeat",
        schema=SECTOR_HEAT_SCHEMA,
        handler=_finance_sector_heat,
        read_only=True,
        concurrent_safe=True,
    ),
]
