"""Generic formula CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.formulas import (
    formula_adjusted_ebitda,
    formula_capm,
    formula_cagr,
    formula_days,
    formula_ebitda,
    formula_enterprise_value,
    formula_lease_equivalent,
    formula_margin,
    formula_net_debt,
    formula_operating_cash,
    formula_operating_current_assets,
    formula_operating_current_liabilities,
    formula_roic,
    formula_turnover,
    formula_wacc,
    formula_working_capital,
)


def _formula_ebitda(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.ebitda ebit=9285 d_and_a=2237",
        lambda: formula_ebitda(ebit=_required(kv, "ebit"), d_and_a=_required(kv, "d_and_a")),
    )


def _formula_adjusted_ebitda(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.adjusted_ebitda ebit=9285 d_and_a=2237 addbacks=284,163",
        lambda: formula_adjusted_ebitda(
            ebit=_required(kv, "ebit"),
            d_and_a=_required(kv, "d_and_a"),
            addbacks=kv.csv("addbacks"),
        ),
    )


def _formula_margin(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.margin numerator=11969 denominator=254453",
        lambda: formula_margin(numerator=_required(kv, "numerator"), denominator=_required(kv, "denominator")),
    )


def _formula_days(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.days current=2721 prior=2285 denominator=254453 [days=365]",
        lambda: formula_days(
            current=_required(kv, "current"),
            prior=_required(kv, "prior"),
            denominator=_required(kv, "denominator"),
            days=kv.str("days", "365"),
        ),
    )


def _formula_turnover(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.turnover numerator=222358 current=18647 prior=16651",
        lambda: formula_turnover(
            numerator=_required(kv, "numerator"),
            current=_required(kv, "current"),
            prior=_required(kv, "prior"),
        ),
    )


def _formula_operating_cash(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.operating_cash revenue=254453 cash_like_assets=11144 [percent_revenue=2%]",
        lambda: formula_operating_cash(
            revenue=_required(kv, "revenue"),
            cash_like_assets=_required(kv, "cash_like_assets"),
            percent_revenue=kv.str("percent_revenue", "2%"),
        ),
    )


def _formula_lease_equivalent(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.lease_equivalent base_liability=2554 variable_cost=163 operating_cost=284",
        lambda: formula_lease_equivalent(
            base_liability=_required(kv, "base_liability"),
            variable_cost=_required(kv, "variable_cost"),
            operating_cost=_required(kv, "operating_cost"),
        ),
    )


def _formula_capm(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.capm risk_free=4.617% beta=0.79 market_return=11%",
        lambda: formula_capm(
            risk_free=_required(kv, "risk_free"),
            beta=_required(kv, "beta"),
            market_return=_required(kv, "market_return"),
        ),
    )


def _formula_wacc(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.wacc equity_value=418856 debt_value=11415 cost_of_equity=9.66% cost_of_debt=6% tax_rate=24% debt_tax=pretax|after_tax",
        lambda: formula_wacc(
            equity_value=_required(kv, "equity_value"),
            debt_value=_required(kv, "debt_value"),
            cost_of_equity=_required(kv, "cost_of_equity"),
            cost_of_debt=_required(kv, "cost_of_debt"),
            tax_rate=kv.str("tax_rate", "0"),
            debt_tax=kv.str("debt_tax", "after_tax") or "after_tax",
        ),
    )


def _formula_enterprise_value(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.enterprise_value market_equity=418856 debt=11415 cash=11144 operating_cash=5089",
        lambda: formula_enterprise_value(
            market_equity=_required(kv, "market_equity"),
            debt=kv.str("debt", "0"),
            cash=kv.str("cash", "0"),
            operating_cash=kv.str("operating_cash", "0"),
        ),
    )


def _formula_roic(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.roic nopat=7113 invested_capital=28077",
        lambda: formula_roic(nopat=_required(kv, "nopat"), invested_capital=_required(kv, "invested_capital")),
    )


def _formula_cagr(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.cagr start=100 end=150 periods=3",
        lambda: formula_cagr(start=_required(kv, "start"), end=_required(kv, "end"), periods=_required(kv, "periods")),
    )


def _formula_net_debt(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.net_debt debt=11415 cash=11144 operating_cash=5089",
        lambda: formula_net_debt(
            debt=_required(kv, "debt"),
            cash=_required(kv, "cash"),
            operating_cash=kv.str("operating_cash", "0"),
        ),
    )


def _formula_operating_current_assets(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.operating_current_assets current_assets=34246 cash_like_assets=11144 operating_cash=5089",
        lambda: formula_operating_current_assets(
            current_assets=_required(kv, "current_assets"),
            cash_like_assets=kv.str("cash_like_assets", "0"),
            operating_cash=kv.str("operating_cash", "0"),
        ),
    )


def _formula_operating_current_liabilities(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.operating_current_liabilities current_liabilities=35464 interest_bearing_current_debt=103",
        lambda: formula_operating_current_liabilities(
            current_liabilities=_required(kv, "current_liabilities"),
            interest_bearing_current_debt=kv.str("interest_bearing_current_debt", "0"),
        ),
    )


def _formula_working_capital(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    return _formula_result(
        "formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035",
        lambda: formula_working_capital(
            operating_current_assets=_required(kv, "operating_current_assets"),
            operating_current_liabilities=_required(kv, "operating_current_liabilities"),
        ),
    )


def register_formula_commands() -> None:
    register_command(FinanceCommand(
        "formula.ebitda",
        "Calculate EBITDA from explicit EBIT and D&A inputs",
        _formula_ebitda,
        usage="formula.ebitda ebit=9285 d_and_a=2237",
        examples=("finance formula.ebitda ebit=9285 d_and_a=2237",),
    ))
    register_command(FinanceCommand(
        "formula.adjusted_ebitda",
        "Calculate adjusted EBITDA from explicit addbacks",
        _formula_adjusted_ebitda,
        usage="formula.adjusted_ebitda ebit=9285 d_and_a=2237 addbacks=284,163",
        examples=("finance formula.adjusted_ebitda ebit=9285 d_and_a=2237 addbacks=284,163",),
    ))
    register_command(FinanceCommand(
        "formula.margin",
        "Calculate numerator / denominator",
        _formula_margin,
        usage="formula.margin numerator=11969 denominator=254453",
        examples=("finance formula.margin numerator=11969 denominator=254453",),
    ))
    register_command(FinanceCommand(
        "formula.days",
        "Calculate average-balance days",
        _formula_days,
        usage="formula.days current=2721 prior=2285 denominator=254453 [days=365]",
        examples=("finance formula.days current=2721 prior=2285 denominator=254453",),
    ))
    register_command(FinanceCommand(
        "formula.turnover",
        "Calculate turnover using average balance",
        _formula_turnover,
        usage="formula.turnover numerator=222358 current=18647 prior=16651",
        examples=("finance formula.turnover numerator=222358 current=18647 prior=16651",),
    ))
    register_command(FinanceCommand(
        "formula.operating_cash",
        "Calculate operating cash as min(percent of revenue, cash-like assets)",
        _formula_operating_cash,
        usage="formula.operating_cash revenue=254453 cash_like_assets=11144 [percent_revenue=2%]",
        examples=("finance formula.operating_cash revenue=254453 cash_like_assets=11144 percent_revenue=2%",),
    ))
    register_command(FinanceCommand(
        "formula.lease_equivalent",
        "Estimate lease equivalent from cost ratio",
        _formula_lease_equivalent,
        usage="formula.lease_equivalent base_liability=2554 variable_cost=163 operating_cost=284",
        examples=("finance formula.lease_equivalent base_liability=2554 variable_cost=163 operating_cost=284",),
    ))
    register_command(FinanceCommand(
        "formula.capm",
        "Calculate CAPM cost of equity",
        _formula_capm,
        usage="formula.capm risk_free=4.617% beta=0.79 market_return=11%",
        examples=("finance formula.capm risk_free=4.617% beta=0.79 market_return=11%",),
    ))
    register_command(FinanceCommand(
        "formula.wacc",
        "Calculate WACC with explicit debt tax convention",
        _formula_wacc,
        usage="formula.wacc equity_value=418856 debt_value=11415 cost_of_equity=9.66% cost_of_debt=6% tax_rate=24% debt_tax=pretax|after_tax",
        examples=("finance formula.wacc equity_value=418856 debt_value=11415 cost_of_equity=9.66% cost_of_debt=6% tax_rate=24% debt_tax=pretax",),
    ))
    register_command(FinanceCommand(
        "formula.enterprise_value",
        "Calculate enterprise value with explicit operating cash",
        _formula_enterprise_value,
        usage="formula.enterprise_value market_equity=418856 debt=11415 cash=11144 operating_cash=5089",
        examples=("finance formula.enterprise_value market_equity=418856 debt=11415 cash=11144 operating_cash=5089",),
    ))
    register_command(FinanceCommand(
        "formula.roic",
        "Calculate ROIC from NOPAT and invested capital",
        _formula_roic,
        usage="formula.roic nopat=7113 invested_capital=28077",
        examples=("finance formula.roic nopat=7113 invested_capital=28077",),
    ))
    register_command(FinanceCommand(
        "formula.cagr",
        "Calculate compound annual growth rate",
        _formula_cagr,
        usage="formula.cagr start=100 end=150 periods=3",
        examples=("finance formula.cagr start=100 end=150 periods=3",),
    ))
    register_command(FinanceCommand(
        "formula.net_debt",
        "Calculate net debt with explicit operating cash",
        _formula_net_debt,
        usage="formula.net_debt debt=11415 cash=11144 [operating_cash=5089]",
        examples=("finance formula.net_debt debt=11415 cash=11144 operating_cash=5089",),
    ))
    register_command(FinanceCommand(
        "formula.operating_current_assets",
        "Calculate operating current assets",
        _formula_operating_current_assets,
        usage="formula.operating_current_assets current_assets=34246 [cash_like_assets=11144 operating_cash=5089]",
        examples=("finance formula.operating_current_assets current_assets=34246 cash_like_assets=11144 operating_cash=5089",),
    ))
    register_command(FinanceCommand(
        "formula.operating_current_liabilities",
        "Calculate operating current liabilities",
        _formula_operating_current_liabilities,
        usage="formula.operating_current_liabilities current_liabilities=35464 [interest_bearing_current_debt=103]",
        examples=("finance formula.operating_current_liabilities current_liabilities=35464 interest_bearing_current_debt=103",),
    ))
    register_command(FinanceCommand(
        "formula.working_capital",
        "Calculate operating working capital",
        _formula_working_capital,
        usage="formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035",
        examples=("finance formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035",),
    ))


def _required(kv: KVArgs, key: str) -> str:
    value = kv.str(key)
    if value is None:
        raise ValueError(f"{key} is required")
    return value


def _formula_result(usage: str, calculate) -> FinanceCommandResult:
    try:
        return FinanceCommandResult(ok=True, data=calculate())
    except ValueError as exc:
        return FinanceCommandResult(ok=False, error=f"usage: {usage}; {exc}")
