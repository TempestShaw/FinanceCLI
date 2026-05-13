"""Research plan finance LLM tool specs.
"""
from __future__ import annotations

from finance_cli.services.research import research_plan
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.types import FinanceToolSpec


def _finance_research_plan(params: dict, _config: dict) -> str:
    if not params.get("symbol"):
        raise ValueError("symbol is required")
    return as_tool_json(research_plan(params["symbol"], style=params.get("style", "fundamental")))


TOOL_DEFS = [
FinanceToolSpec(
        name="FinanceResearchPlan",
        schema={
            "name": "FinanceResearchPlan",
            "description": "Return a deterministic CLI checklist for a research workflow. Does not execute commands or form conclusions.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "style": {"type": "string", "description": "fundamental"},
                },
                "required": ["symbol"],
            },
        },
        handler=_finance_research_plan,
        read_only=True,
        concurrent_safe=True,
    )
]
