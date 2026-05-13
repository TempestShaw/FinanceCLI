"""Generic finance formula helpers.

These helpers intentionally accept explicit numeric inputs. They do not fetch
company data or decide which filing facts belong in a formula.
"""
from __future__ import annotations

from typing import Any

from finance_cli.core.common import parse_rate, parse_scaled_number


def formula_ebitda(*, ebit: float | int | str, d_and_a: float | int | str) -> dict[str, Any]:
    ebit_value = parse_scaled_number(ebit)
    da_value = parse_scaled_number(d_and_a)
    return {
        "ebitda": ebit_value + da_value,
        "inputs": {"ebit": ebit_value, "d_and_a": da_value},
        "method": "ebit + d_and_a",
    }


def formula_adjusted_ebitda(
    *,
    ebit: float | int | str,
    d_and_a: float | int | str,
    addbacks: list[float | int | str] | None = None,
) -> dict[str, Any]:
    base = formula_ebitda(ebit=ebit, d_and_a=d_and_a)
    parsed_addbacks = [parse_scaled_number(value) for value in (addbacks or [])]
    return {
        "adjusted_ebitda": base["ebitda"] + sum(parsed_addbacks),
        "inputs": {**base["inputs"], "addbacks": parsed_addbacks},
        "method": "ebit + d_and_a + sum(addbacks)",
    }


def formula_margin(*, numerator: float | int | str, denominator: float | int | str) -> dict[str, Any]:
    numerator_value = parse_scaled_number(numerator)
    denominator_value = parse_scaled_number(denominator)
    ratio = _safe_div(numerator_value, denominator_value)
    return {
        "margin": ratio,
        "margin_pct": ratio * 100 if ratio is not None else None,
        "inputs": {"numerator": numerator_value, "denominator": denominator_value},
        "method": "numerator / denominator",
    }


def formula_days(
    *,
    current: float | int | str,
    prior: float | int | str,
    denominator: float | int | str,
    days: float | int | str = 365,
) -> dict[str, Any]:
    current_value = parse_scaled_number(current)
    prior_value = parse_scaled_number(prior)
    denominator_value = parse_scaled_number(denominator)
    days_value = parse_scaled_number(days)
    average_balance = (current_value + prior_value) / 2
    value = _safe_div(average_balance, denominator_value)
    return {
        "days": value * days_value if value is not None else None,
        "average_balance": average_balance,
        "inputs": {
            "current": current_value,
            "prior": prior_value,
            "denominator": denominator_value,
            "days": days_value,
        },
        "method": "((current + prior) / 2) / denominator * days",
    }


def formula_turnover(
    *,
    numerator: float | int | str,
    current: float | int | str,
    prior: float | int | str,
) -> dict[str, Any]:
    numerator_value = parse_scaled_number(numerator)
    current_value = parse_scaled_number(current)
    prior_value = parse_scaled_number(prior)
    average_balance = (current_value + prior_value) / 2
    return {
        "turnover": _safe_div(numerator_value, average_balance),
        "average_balance": average_balance,
        "inputs": {"numerator": numerator_value, "current": current_value, "prior": prior_value},
        "method": "numerator / ((current + prior) / 2)",
    }


def formula_operating_cash(
    *,
    revenue: float | int | str,
    cash_like_assets: float | int | str,
    percent_revenue: float | int | str = "2%",
) -> dict[str, Any]:
    revenue_value = parse_scaled_number(revenue)
    cash_like_value = parse_scaled_number(cash_like_assets)
    warnings: list[str] = []
    percent = parse_rate(percent_revenue, warnings=warnings)
    revenue_cap = revenue_value * percent
    return {
        "operating_cash": min(revenue_cap, cash_like_value),
        "revenue_cap": revenue_cap,
        "cash_like_assets": cash_like_value,
        "inputs": {"revenue": revenue_value, "cash_like_assets": cash_like_value, "percent_revenue": percent},
        "method": "min(revenue * percent_revenue, cash_like_assets)",
        "warnings": warnings,
    }


def formula_lease_equivalent(
    *,
    base_liability: float | int | str,
    variable_cost: float | int | str,
    operating_cost: float | int | str,
) -> dict[str, Any]:
    base_value = parse_scaled_number(base_liability)
    variable_value = parse_scaled_number(variable_cost)
    operating_value = parse_scaled_number(operating_cost)
    ratio = _safe_div(variable_value, operating_value)
    return {
        "lease_equivalent": base_value * ratio if ratio is not None else None,
        "ratio": ratio,
        "inputs": {
            "base_liability": base_value,
            "variable_cost": variable_value,
            "operating_cost": operating_value,
        },
        "method": "base_liability * (variable_cost / operating_cost)",
    }


def formula_capm(
    *,
    risk_free: float | int | str,
    beta: float | int | str,
    market_return: float | int | str,
) -> dict[str, Any]:
    warnings: list[str] = []
    risk_free_rate = parse_rate(risk_free, warnings=warnings)
    beta_value = parse_scaled_number(beta)
    market_rate = parse_rate(market_return, warnings=warnings)
    cost_of_equity = risk_free_rate + beta_value * (market_rate - risk_free_rate)
    return {
        "cost_of_equity": cost_of_equity,
        "inputs": {"risk_free": risk_free_rate, "beta": beta_value, "market_return": market_rate},
        "method": "risk_free + beta * (market_return - risk_free)",
        "warnings": warnings,
    }


def formula_wacc(
    *,
    equity_value: float | int | str,
    debt_value: float | int | str,
    cost_of_equity: float | int | str,
    cost_of_debt: float | int | str,
    tax_rate: float | int | str = 0,
    debt_tax: str = "after_tax",
) -> dict[str, Any]:
    warnings: list[str] = []
    equity = parse_scaled_number(equity_value)
    debt = parse_scaled_number(debt_value)
    if equity < 0 or debt < 0:
        raise ValueError("equity_value and debt_value must be greater than or equal to 0")
    total = equity + debt
    if total <= 0:
        raise ValueError("equity_value + debt_value must be greater than 0")
    equity_cost = parse_rate(cost_of_equity, warnings=warnings)
    debt_cost = parse_rate(cost_of_debt, warnings=warnings)
    tax = parse_rate(tax_rate, warnings=warnings)
    debt_tax_key = debt_tax.strip().lower()
    if debt_tax_key not in {"after_tax", "pretax"}:
        raise ValueError("debt_tax must be after_tax or pretax")
    adjusted_debt_cost = debt_cost * (1 - tax) if debt_tax_key == "after_tax" else debt_cost
    wacc = (equity / total) * equity_cost + (debt / total) * adjusted_debt_cost
    return {
        "wacc": wacc,
        "weights": {"equity": equity / total, "debt": debt / total},
        "inputs": {
            "equity_value": equity,
            "debt_value": debt,
            "cost_of_equity": equity_cost,
            "cost_of_debt": debt_cost,
            "tax_rate": tax,
            "debt_tax": debt_tax_key,
        },
        "method": "E/(D+E)*cost_of_equity + D/(D+E)*cost_of_debt, tax-adjusted only when debt_tax=after_tax",
        "warnings": warnings,
    }


def formula_enterprise_value(
    *,
    market_equity: float | int | str,
    debt: float | int | str = 0,
    cash: float | int | str = 0,
    operating_cash: float | int | str = 0,
) -> dict[str, Any]:
    equity_value = parse_scaled_number(market_equity)
    debt_value = parse_scaled_number(debt)
    cash_value = parse_scaled_number(cash)
    operating_cash_value = parse_scaled_number(operating_cash)
    excess_cash = max(cash_value - operating_cash_value, 0)
    return {
        "enterprise_value": equity_value + debt_value - excess_cash,
        "excess_cash": excess_cash,
        "inputs": {
            "market_equity": equity_value,
            "debt": debt_value,
            "cash": cash_value,
            "operating_cash": operating_cash_value,
        },
        "method": "market_equity + debt - max(cash - operating_cash, 0)",
    }


def formula_roic(*, nopat: float | int | str, invested_capital: float | int | str) -> dict[str, Any]:
    nopat_value = parse_scaled_number(nopat)
    invested_value = parse_scaled_number(invested_capital)
    ratio = _safe_div(nopat_value, invested_value)
    return {
        "roic": ratio,
        "roic_pct": ratio * 100 if ratio is not None else None,
        "inputs": {"nopat": nopat_value, "invested_capital": invested_value},
        "method": "nopat / invested_capital",
    }


def formula_cagr(
    *,
    start: float | int | str,
    end: float | int | str,
    periods: float | int | str,
) -> dict[str, Any]:
    start_value = parse_scaled_number(start)
    end_value = parse_scaled_number(end)
    periods_value = parse_scaled_number(periods)
    if start_value <= 0 or end_value <= 0:
        raise ValueError("start and end must be greater than 0")
    if periods_value <= 0:
        raise ValueError("periods must be greater than 0")
    cagr = (end_value / start_value) ** (1 / periods_value) - 1
    return {
        "cagr": cagr,
        "cagr_pct": cagr * 100,
        "inputs": {"start": start_value, "end": end_value, "periods": periods_value},
        "method": "(end / start) ** (1 / periods) - 1",
    }


def formula_net_debt(
    *,
    debt: float | int | str,
    cash: float | int | str,
    operating_cash: float | int | str = 0,
) -> dict[str, Any]:
    debt_value = parse_scaled_number(debt)
    cash_value = parse_scaled_number(cash)
    operating_cash_value = parse_scaled_number(operating_cash)
    excess_cash = max(cash_value - operating_cash_value, 0)
    return {
        "net_debt": debt_value - excess_cash,
        "excess_cash": excess_cash,
        "inputs": {"debt": debt_value, "cash": cash_value, "operating_cash": operating_cash_value},
        "method": "debt - max(cash - operating_cash, 0)",
    }


def formula_operating_current_assets(
    *,
    current_assets: float | int | str,
    cash_like_assets: float | int | str = 0,
    operating_cash: float | int | str = 0,
) -> dict[str, Any]:
    current_assets_value = parse_scaled_number(current_assets)
    cash_like_value = parse_scaled_number(cash_like_assets)
    operating_cash_value = parse_scaled_number(operating_cash)
    return {
        "operating_current_assets": current_assets_value - cash_like_value + operating_cash_value,
        "inputs": {
            "current_assets": current_assets_value,
            "cash_like_assets": cash_like_value,
            "operating_cash": operating_cash_value,
        },
        "method": "current_assets - cash_like_assets + operating_cash",
    }


def formula_operating_current_liabilities(
    *,
    current_liabilities: float | int | str,
    interest_bearing_current_debt: float | int | str = 0,
) -> dict[str, Any]:
    current_liabilities_value = parse_scaled_number(current_liabilities)
    debt_value = parse_scaled_number(interest_bearing_current_debt)
    return {
        "operating_current_liabilities": current_liabilities_value - debt_value,
        "inputs": {
            "current_liabilities": current_liabilities_value,
            "interest_bearing_current_debt": debt_value,
        },
        "method": "current_liabilities - interest_bearing_current_debt",
    }


def formula_working_capital(
    *,
    operating_current_assets: float | int | str,
    operating_current_liabilities: float | int | str,
) -> dict[str, Any]:
    assets_value = parse_scaled_number(operating_current_assets)
    liabilities_value = parse_scaled_number(operating_current_liabilities)
    return {
        "working_capital": assets_value - liabilities_value,
        "inputs": {"operating_current_assets": assets_value, "operating_current_liabilities": liabilities_value},
        "method": "operating_current_assets - operating_current_liabilities",
    }


def _safe_div(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator
