"""Consensus estimate helpers."""
from __future__ import annotations

from typing import Any

from finance_cli.core.common import normalize_symbol, parse_scaled_number
from finance_cli.providers.fmp import FMPProvider


COMPARABLE_METRICS = (
    "revenue",
    "eps",
    "ebitda",
    "ebit",
    "net_income",
    "fcf",
    "free_cash_flow",
    "operating_income",
)


def consensus_estimates(
    symbol: str,
    *,
    period: str = "annual",
    page: int = 0,
    limit: int = 10,
    provider: FMPProvider | None = None,
) -> dict[str, Any]:
    client = provider or FMPProvider()
    normalized = normalize_symbol(symbol)
    rows = client.analyst_estimates(normalized, period=period, page=page, limit=limit)
    return {
        "symbol": normalized,
        "period": period,
        "provider": "fmp",
        "estimates": rows,
        "count": len(rows),
    }


def compare_estimates(symbol: str | None = None, **values: str) -> dict[str, Any]:
    rows = []
    for metric in COMPARABLE_METRICS:
        if metric not in values:
            continue
        consensus_key = f"consensus_{metric}"
        if consensus_key not in values:
            continue
        user_value = parse_scaled_number(values[metric])
        consensus_value = parse_scaled_number(values[consensus_key])
        gap = _round_float(user_value - consensus_value)
        pct_gap = _round_float(gap / abs(consensus_value)) if consensus_value else None
        rows.append({
            "metric": metric,
            "user_value": user_value,
            "consensus_value": consensus_value,
            "absolute_gap": gap,
            "percent_gap": pct_gap,
            "percent_gap_pct": _round_float(pct_gap * 100) if pct_gap is not None else None,
            "valuation_input_hint": _gap_hint(gap),
        })
    if not rows:
        raise ValueError("provide at least one metric plus consensus_<metric>, for example revenue=2.2B consensus_revenue=2.0B")
    return {
        "symbol": normalize_symbol(symbol) if symbol else None,
        "fiscal_year": values.get("fiscal_year"),
        "period": values.get("period"),
        "comparisons": rows,
        "count": len(rows),
        "method": "user_metric - consensus_metric",
    }


def _gap_hint(gap: float) -> str:
    if gap > 0:
        return "above_consensus"
    if gap < 0:
        return "below_consensus"
    return "in_line"


def _round_float(value: float) -> float:
    return round(value, 10)
