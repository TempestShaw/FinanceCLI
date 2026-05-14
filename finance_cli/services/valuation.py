"""Valuation helper services.

These functions intentionally perform simple deterministic math. They do not
decide whether an assumption is reasonable; that judgment belongs to the caller
or human analyst using the CLI.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from finance_cli.core.common import normalize_symbol, parse_rate, parse_scaled_number
from finance_cli.services.fundamentals import fetch_financial_statement
from finance_cli.services.market_data import fetch_realtime_quote


def valuation_multiples(symbol: str) -> dict[str, Any]:
    """Calculate current sales multiples from quote and latest revenue data."""
    normalized = normalize_symbol(symbol)
    quote = fetch_realtime_quote(normalized)
    latest_revenue = _latest_revenue_from_statement(normalized)
    revenue = latest_revenue.get("revenue") or _number_or_none(quote.get("total_revenue"))
    revenue_period_type = "FY" if latest_revenue.get("revenue") is not None else "TTM"
    market_cap = _number_or_none(quote.get("market_cap"))
    enterprise_value = _number_or_none(quote.get("enterprise_value"))

    multiples = {
        "price_to_sales": _safe_div(market_cap, revenue),
        "ev_to_sales": _safe_div(enterprise_value, revenue),
    }
    warnings = []
    if revenue is None:
        warnings.append("revenue unavailable; provide revenue manually in valuation.scenario")
    if market_cap is None:
        warnings.append("market_cap unavailable")
    if enterprise_value is None:
        warnings.append("enterprise_value unavailable; ev_to_sales omitted")

    return {
        "symbol": normalized,
        "price": quote.get("price") or quote.get("last_price"),
        "market_cap": market_cap,
        "enterprise_value": enterprise_value,
        "cash": _number_or_none(quote.get("cash")),
        "debt": _number_or_none(quote.get("debt")),
        "net_debt": _number_or_none(quote.get("net_debt")),
        "currency": quote.get("currency"),
        "revenue": revenue,
        "revenue_period": latest_revenue.get("period"),
        "revenue_period_type": revenue_period_type if revenue is not None else None,
        "multiples": {key: value for key, value in multiples.items() if value is not None},
        "sources": ["market.quote", "fundamentals.statement"],
        "warnings": warnings,
    }


def valuation_scenario(
    symbol: str,
    *,
    revenue: float | int | str,
    bull_multiple: float,
    base_multiple: float,
    bear_multiple: float,
    shares: float | int | str | None = None,
) -> dict[str, Any]:
    """Build a bull/base/bear sales-multiple scenario table."""
    normalized = normalize_symbol(symbol)
    revenue_value = parse_scaled_number(revenue)
    if revenue_value <= 0:
        raise ValueError("revenue must be greater than 0")
    for name, multiple in {
        "bear_multiple": bear_multiple,
        "base_multiple": base_multiple,
        "bull_multiple": bull_multiple,
    }.items():
        if multiple < 0:
            raise ValueError(f"{name} must be greater than or equal to 0")
    quote = fetch_realtime_quote(normalized)
    current_price = _number_or_none(quote.get("price") or quote.get("last_price"))
    market_cap = _number_or_none(quote.get("market_cap"))
    user_shares = parse_scaled_number(shares) if shares is not None else None
    if user_shares is not None and user_shares <= 0:
        raise ValueError("shares must be greater than 0")
    share_count = user_shares or _number_or_none(quote.get("shares_outstanding"))
    if share_count is None and market_cap is not None and current_price:
        share_count = market_cap / current_price

    cases = [
        _scenario_case("bear", revenue_value, bear_multiple, share_count, current_price),
        _scenario_case("base", revenue_value, base_multiple, share_count, current_price),
        _scenario_case("bull", revenue_value, bull_multiple, share_count, current_price),
    ]
    warnings = []
    if share_count is None:
        warnings.append("shares unavailable; implied_price and upside_pct omitted")
    if current_price is None:
        warnings.append("current_price unavailable; upside_pct omitted")

    return {
        "symbol": normalized,
        "currency": quote.get("currency"),
        "current_price": current_price,
        "market_cap": market_cap,
        "shares": share_count,
        "shares_source": _shares_source(user_shares, quote, market_cap, current_price),
        "assumptions": {
            "revenue": revenue_value,
            "multiple_basis": "price_to_sales",
        },
        "cases": cases,
        "warnings": warnings,
    }


def valuation_npv(*, cashflows: list[float | int | str], discount_rate: float | int | str) -> dict[str, Any]:
    """Calculate NPV using cash flow 0 at t=0."""
    warnings = []
    parsed_cashflows = parse_cashflows(cashflows)
    rate = parse_rate(discount_rate, warnings=warnings)
    return {
        "cashflows": parsed_cashflows,
        "discount_rate": rate,
        "npv": _npv(parsed_cashflows, rate),
        "method": "sum(cashflow_t / (1 + discount_rate)^t), with first cash flow at t=0",
        "warnings": warnings,
    }


def valuation_irr(*, cashflows: list[float | int | str]) -> dict[str, Any]:
    """Calculate IRR for periodic cash flows."""
    parsed_cashflows = parse_cashflows(cashflows)
    irr = _irr(parsed_cashflows)
    return {
        "cashflows": parsed_cashflows,
        "irr": irr,
        "method": "rate r where sum(cashflow_t / (1 + r)^t) = 0",
        "solver": "bisection_numeric_approximation",
        "warnings": [] if irr is not None else ["IRR unavailable; cash flows may not bracket a solution"],
    }


def valuation_wacc(
    *,
    equity_value: float | int | str,
    debt_value: float | int | str,
    cost_of_equity: float | int | str,
    cost_of_debt: float | int | str,
    tax_rate: float | int | str = 0.0,
) -> dict[str, Any]:
    """Calculate weighted average cost of capital."""
    warnings = []
    equity = parse_scaled_number(equity_value)
    debt = parse_scaled_number(debt_value)
    total_capital = equity + debt
    if equity < 0 or debt < 0:
        raise ValueError("equity_value and debt_value must be greater than or equal to 0")
    if total_capital <= 0:
        raise ValueError("equity_value + debt_value must be greater than 0")
    equity_weight = equity / total_capital
    debt_weight = debt / total_capital
    equity_cost = parse_rate(cost_of_equity, warnings=warnings)
    debt_cost = parse_rate(cost_of_debt, warnings=warnings)
    tax = parse_rate(tax_rate, warnings=warnings)
    if not 0 <= tax <= 1:
        raise ValueError("tax_rate must be between 0 and 1")
    wacc = equity_weight * equity_cost + debt_weight * debt_cost * (1 - tax)
    return {
        "wacc": wacc,
        "weights": {
            "equity": equity_weight,
            "debt": debt_weight,
        },
        "inputs": {
            "equity_value": equity,
            "debt_value": debt,
            "cost_of_equity": equity_cost,
            "cost_of_debt": debt_cost,
            "tax_rate": tax,
        },
        "method": "E/(D+E)*cost_of_equity + D/(D+E)*cost_of_debt*(1-tax_rate)",
        "warnings": warnings,
    }


def valuation_dcf(
    *,
    cashflows: list[float | int | str],
    discount_rate: float | int | str,
    terminal_growth: float | int | str | None = None,
    exit_multiple: float | int | str | None = None,
) -> dict[str, Any]:
    """Calculate enterprise value from forecast cash flows and one terminal value method."""
    warnings = []
    parsed_cashflows = parse_cashflows(cashflows)
    if not parsed_cashflows:
        raise ValueError("cashflows are required")
    rate = parse_rate(discount_rate, warnings=warnings)
    growth = parse_rate(terminal_growth, warnings=warnings) if terminal_growth is not None else None
    multiple = float(exit_multiple) if exit_multiple is not None else None
    if growth is not None and multiple is not None:
        raise ValueError("choose either terminal_growth or exit_multiple, not both")
    if growth is not None and rate <= growth:
        raise ValueError("discount_rate must be greater than terminal_growth")
    terminal_value = None
    terminal_method = None
    if growth is not None:
        terminal_value = parsed_cashflows[-1] * (1 + growth) / (rate - growth)
        terminal_method = "gordon_growth"
    elif multiple is not None:
        terminal_value = parsed_cashflows[-1] * multiple
        terminal_method = "exit_multiple"

    discounted_cashflows = [
        {"t": index, "cashflow": cashflow, "present_value": cashflow / ((1 + rate) ** index)}
        for index, cashflow in enumerate(parsed_cashflows, start=1)
    ]
    pv_cashflows = sum(row["present_value"] for row in discounted_cashflows)
    pv_terminal = terminal_value / ((1 + rate) ** len(parsed_cashflows)) if terminal_value is not None else None
    enterprise_value = pv_cashflows + (pv_terminal or 0.0)
    return {
        "cashflows": parsed_cashflows,
        "discount_rate": rate,
        "terminal_growth": growth,
        "exit_multiple": multiple,
        "terminal_value": terminal_value,
        "terminal_method": terminal_method,
        "discounted_cashflows": discounted_cashflows,
        "pv_cashflows": pv_cashflows,
        "pv_terminal_value": pv_terminal,
        "enterprise_value": enterprise_value,
        "method": "forecast FCF only, discounted from t=1; do not include an initial t=0 investment cash flow",
        "warnings": warnings,
    }


def _latest_revenue_from_statement(symbol: str) -> dict[str, Any]:
    try:
        statement = fetch_financial_statement(symbol, statement="income", period="annual")
    except Exception:
        return {}
    for row in statement.get("rows", []):
        if str(row.get("field", "")).strip().lower() not in {"total revenue", "revenue"}:
            continue
        dated_values = [
            (key, _number_or_none(value))
            for key, value in row.items()
            if key != "field" and _number_or_none(value) is not None
        ]
        if not dated_values:
            continue
        period, revenue = sorted(dated_values, key=lambda item: _period_sort_key(item[0]), reverse=True)[0]
        return {"period": period, "revenue": revenue}
    return {}


def _scenario_case(
    name: str,
    revenue: float,
    multiple: float,
    shares: float | None,
    current_price: float | None,
) -> dict[str, Any]:
    implied_market_cap = revenue * multiple
    implied_price = implied_market_cap / shares if shares else None
    return {
        "case": name,
        "revenue": revenue,
        "multiple": multiple,
        "implied_market_cap": implied_market_cap,
        "implied_price": implied_price,
        "upside_pct": _pct_change(implied_price, current_price),
    }


def _safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in {None, 0}:
        return None
    return numerator / denominator


def _pct_change(value: float | None, base: float | None) -> float | None:
    if value is None or base in {None, 0}:
        return None
    return (value / base - 1.0) * 100.0


def _number_or_none(value: Any) -> float | None:
    try:
        if value is None or value != value:
            return None
        return float(value)
    except Exception:
        return None


def _period_sort_key(period: str) -> tuple[int, str]:
    try:
        return (1, date.fromisoformat(period).isoformat())
    except Exception:
        return (0, period)


def parse_cashflows(values: list[float | int | str]) -> list[float]:
    if not values:
        raise ValueError("cashflows are required")
    return [parse_scaled_number(value) for value in values]


def _npv(cashflows: list[float], rate: float) -> float:
    return sum(cashflow / ((1 + rate) ** index) for index, cashflow in enumerate(cashflows))


def _irr(cashflows: list[float]) -> float | None:
    if not any(cashflow < 0 for cashflow in cashflows) or not any(cashflow > 0 for cashflow in cashflows):
        return None
    low = -0.999999
    high = 10.0
    low_value = _npv(cashflows, low)
    high_value = _npv(cashflows, high)
    while low_value * high_value > 0 and high < 1_000_000:
        high *= 2
        high_value = _npv(cashflows, high)
    if low_value * high_value > 0:
        return None
    for _ in range(200):
        mid = (low + high) / 2
        mid_value = _npv(cashflows, mid)
        if abs(mid_value) < 1e-7:
            return mid
        if low_value * mid_value <= 0:
            high = mid
            high_value = mid_value
        else:
            low = mid
            low_value = mid_value
    return (low + high) / 2


def _shares_source(
    user_shares: float | None,
    quote: dict[str, Any],
    market_cap: float | None,
    current_price: float | None,
) -> dict[str, Any] | None:
    if user_shares is not None:
        return {"source": "user_input"}
    if quote.get("shares_outstanding") is not None:
        return {
            "source": "yfinance.sharesOutstanding",
            "as_of": None,
            "note": "provider metadata does not include a filing date",
        }
    if market_cap is not None and current_price:
        return {
            "source": "derived_market_cap_div_price",
            "as_of": None,
            "note": "derived from current market cap and price",
        }
    return None
