"""Valuation CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.valuation import parse_cashflows, parse_scaled_number
from finance_cli.services.valuation import valuation_dcf, valuation_irr, valuation_multiples, valuation_npv, valuation_scenario, valuation_wacc


def _valuation_multiples(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: valuation.multiples SYMBOL")
    return FinanceCommandResult(ok=True, data=valuation_multiples(args[0]))


def _valuation_scenario(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(
            ok=False,
            error="usage: valuation.scenario SYMBOL revenue=... bear_multiple=... base_multiple=... bull_multiple=... [shares=...]",
        )
    kv = KVArgs(args[1:])
    data = valuation_scenario(
        args[0],
        revenue=_required_number(kv, "revenue"),
        bear_multiple=_required_float(kv, "bear_multiple"),
        base_multiple=_required_float(kv, "base_multiple"),
        bull_multiple=_required_float(kv, "bull_multiple"),
        shares=parse_scaled_number(kv.values["shares"]) if "shares" in kv.values else None,
    )
    return FinanceCommandResult(ok=True, data=data)


def _valuation_npv(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    data = valuation_npv(
        cashflows=_required_cashflows(kv),
        discount_rate=_required_rate(kv, "discount_rate"),
    )
    return FinanceCommandResult(ok=True, data=data)


def _valuation_irr(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    data = valuation_irr(cashflows=_required_cashflows(kv))
    return FinanceCommandResult(ok=True, data=data)


def _valuation_wacc(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    data = valuation_wacc(
        equity_value=_required_number(kv, "equity_value"),
        debt_value=_required_number(kv, "debt_value"),
        cost_of_equity=_required_rate(kv, "cost_of_equity"),
        cost_of_debt=_required_rate(kv, "cost_of_debt"),
        tax_rate=kv.values.get("tax_rate", "0"),
    )
    return FinanceCommandResult(ok=True, data=data)


def _valuation_dcf(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    data = valuation_dcf(
        cashflows=_required_cashflows(kv),
        discount_rate=_required_rate(kv, "discount_rate"),
        terminal_growth=kv.values["terminal_growth"] if "terminal_growth" in kv.values else None,
        exit_multiple=float(kv.values["exit_multiple"]) if "exit_multiple" in kv.values else None,
    )
    return FinanceCommandResult(ok=True, data=data)


def register_valuation_commands() -> None:
    register_command(FinanceCommand(
        "valuation.multiples",
        "Calculate current sales multiples from market cap and revenue",
        _valuation_multiples,
        usage="valuation.multiples SYMBOL",
        examples=("finance valuation.multiples IOT",),
        notes=("Deterministic math only; does not judge whether the multiple is fair.",),
    ))
    register_command(FinanceCommand(
        "valuation.scenario",
        "Build a simple bull/base/bear sales-multiple scenario table",
        _valuation_scenario,
        usage="valuation.scenario SYMBOL revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 [shares=580M]",
        examples=(
            "finance valuation.scenario IOT revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 shares=580M",
            "finance valuation.scenario IOT revenue=2200000000 bear_multiple=7 base_multiple=10 bull_multiple=13",
        ),
        notes=(
            "Uses current quote for price/share count when available; assumptions remain user-supplied.",
            "Revenue and shares accept raw numbers or K/M/B suffixes.",
        ),
    ))
    register_command(FinanceCommand(
        "valuation.npv",
        "Calculate NPV for periodic cash flows",
        _valuation_npv,
        usage="valuation.npv cashflows=-100M,30M,40M,50M discount_rate=10%",
        examples=("finance valuation.npv cashflows=-100M,30M,40M,50M discount_rate=10%",),
        notes=("First cash flow is treated as t=0. Use this for project-level NPV including initial investment.",),
    ))
    register_command(FinanceCommand(
        "valuation.irr",
        "Calculate IRR for periodic cash flows",
        _valuation_irr,
        usage="valuation.irr cashflows=-100M,30M,40M,50M",
        examples=("finance valuation.irr cashflows=-100M,30M,40M,50M",),
        notes=("Cash flows are periodic; returns null with a warning when no IRR solution is bracketed.",),
    ))
    register_command(FinanceCommand(
        "valuation.wacc",
        "Calculate weighted average cost of capital",
        _valuation_wacc,
        usage="valuation.wacc equity_value=10B debt_value=1B cost_of_equity=10% cost_of_debt=5% tax_rate=21%",
        examples=("finance valuation.wacc equity_value=10B debt_value=1B cost_of_equity=10% cost_of_debt=5% tax_rate=21%",),
        notes=("Formula: E/(D+E)*Re + D/(D+E)*Rd*(1-tax). Inputs are user-supplied.",),
    ))
    register_command(FinanceCommand(
        "valuation.dcf",
        "Calculate DCF enterprise value from forecast cash flows",
        _valuation_dcf,
        usage="valuation.dcf cashflows=100M,120M,140M discount_rate=10% [terminal_growth=3%|exit_multiple=15]",
        examples=(
            "finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% terminal_growth=3%",
            "finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% exit_multiple=15",
        ),
        notes=(
            "Pass forecast FCF only; do not include an initial t=0 investment cash flow.",
            "Forecast cash flows are discounted from t=1.",
            "Use either terminal_growth or exit_multiple, not both.",
        ),
    ))


def _required_float(kv: KVArgs, key: str) -> float:
    if key not in kv.values:
        raise ValueError(f"{key} is required")
    return kv.float(key, 0.0)


def _required_number(kv: KVArgs, key: str) -> float:
    if key not in kv.values:
        raise ValueError(f"{key} is required")
    return parse_scaled_number(kv.values[key])


def _required_rate(kv: KVArgs, key: str) -> str:
    if key not in kv.values:
        raise ValueError(f"{key} is required")
    return kv.values[key]


def _required_cashflows(kv: KVArgs) -> list[float]:
    if "cashflows" not in kv.values:
        raise ValueError("cashflows is required")
    return parse_cashflows(kv.csv("cashflows"))
