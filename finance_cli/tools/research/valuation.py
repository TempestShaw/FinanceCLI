"""Valuation finance LLM tool specs.
"""
from __future__ import annotations

from finance_cli.services.valuation import parse_scaled_number, valuation_multiples, valuation_scenario
from finance_cli.services.valuation import valuation_dcf, valuation_irr, valuation_npv, valuation_wacc
from finance_cli.tools.formatting import as_tool_json
from finance_cli.tools.types import FinanceToolSpec


def _finance_valuation(params: dict, _config: dict) -> str:
    action = str(params.get("action", "multiples")).lower()
    if action not in {"multiples", "scenario", "npv", "irr", "wacc", "dcf"}:
        raise ValueError("action must be one of: multiples, scenario, npv, irr, wacc, dcf")
    if action in {"multiples", "scenario"} and not params.get("symbol"):
        raise ValueError("symbol is required")
    if action == "multiples":
        return as_tool_json(valuation_multiples(params["symbol"]))
    if action == "scenario":
        return as_tool_json(
            valuation_scenario(
                params["symbol"],
                revenue=parse_scaled_number(params["revenue"]),
                bear_multiple=float(params["bear_multiple"]),
                base_multiple=float(params["base_multiple"]),
                bull_multiple=float(params["bull_multiple"]),
                shares=parse_scaled_number(params["shares"]) if params.get("shares") is not None else None,
            )
        )
    if action == "npv":
        return as_tool_json(valuation_npv(cashflows=params["cashflows"], discount_rate=params["discount_rate"]))
    if action == "irr":
        return as_tool_json(valuation_irr(cashflows=params["cashflows"]))
    if action == "wacc":
        return as_tool_json(
            valuation_wacc(
                equity_value=params["equity_value"],
                debt_value=params["debt_value"],
                cost_of_equity=params["cost_of_equity"],
                cost_of_debt=params["cost_of_debt"],
                tax_rate=params.get("tax_rate", 0),
            )
        )
    return as_tool_json(
        valuation_dcf(
            cashflows=params["cashflows"],
            discount_rate=params["discount_rate"],
            terminal_growth=params.get("terminal_growth"),
            exit_multiple=params.get("exit_multiple"),
        )
    )


TOOL_DEFS = [
FinanceToolSpec(
        name="FinanceValuation",
        schema={
            "name": "FinanceValuation",
            "description": "Run deterministic valuation math: multiples, scenario, NPV, IRR, WACC, or DCF.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["multiples", "scenario", "npv", "irr", "wacc", "dcf"]},
                    "symbol": {"type": "string"},
                    "revenue": {"type": "number"},
                    "bear_multiple": {"type": "number"},
                    "base_multiple": {"type": "number"},
                    "bull_multiple": {"type": "number"},
                    "shares": {"type": "number"},
                    "cashflows": {"type": "array", "items": {"type": ["number", "string"]}},
                    "discount_rate": {"type": ["number", "string"]},
                    "terminal_growth": {"type": ["number", "string"]},
                    "exit_multiple": {"type": "number"},
                    "equity_value": {"type": ["number", "string"]},
                    "debt_value": {"type": ["number", "string"]},
                    "cost_of_equity": {"type": ["number", "string"]},
                    "cost_of_debt": {"type": ["number", "string"]},
                    "tax_rate": {"type": ["number", "string"]},
                },
                "required": [],
            },
        },
        handler=_finance_valuation,
        read_only=True,
        concurrent_safe=True,
    )
]
