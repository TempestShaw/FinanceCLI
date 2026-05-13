"""Structured XBRL statement helpers for SEC filings.
"""
from __future__ import annotations

from typing import Any
from finance_cli.providers.base import ProviderError, quiet_call
from finance_cli.providers.sec_edgar.common import _json_number


FILING_STATEMENT_ATTRS = {
    "income": "income_statement",
    "income_statement": "income_statement",
    "balance": "balance_sheet",
    "balance_sheet": "balance_sheet",
    "cashflow": "cash_flow_statement",
    "cash_flow": "cash_flow_statement",
    "cash_flow_statement": "cash_flow_statement",
}


def _get_statement_object(filing: Any, statement: str) -> tuple[str, Any]:
    key = statement.strip().lower().replace("-", "_")
    attr = FILING_STATEMENT_ATTRS.get(key)
    if not attr:
        raise ProviderError("statement must be one of: income, balance, cashflow")
    obj = quiet_call(filing.obj)
    value = getattr(obj, attr, None)
    if value is None:
        raise ProviderError(f"statement not available: {statement}")
    return key, value


def _shape_statement_rows(
    raw_rows: list[dict[str, Any]],
    *,
    query: str | None,
    include_abstract: bool,
    max_rows: int,
) -> list[dict[str, Any]]:
    rows = []
    query_text = str(query or "").strip().lower()
    for item in raw_rows:
        if item.get("is_abstract") and not include_abstract:
            continue
        if query_text and query_text not in _statement_row_search_text(item):
            continue
        rows.append(_shape_statement_row(item))
        if max_rows > 0 and len(rows) >= max_rows:
            break
    return rows


def _statement_row_search_text(item: dict[str, Any]) -> str:
    parts = [
        item.get("concept"),
        item.get("name"),
        item.get("label"),
        item.get("preferred_label"),
        item.get("parent"),
        item.get("calculation_parent"),
    ]
    return " ".join(str(part or "").lower() for part in parts)


def _shape_statement_row(item: dict[str, Any]) -> dict[str, Any]:
    values = item.get("values") or {}
    decimals = item.get("decimals") or {}
    units = item.get("units") or {}
    period_types = item.get("period_types") or {}
    preferred_signs = item.get("preferred_signs") or {}
    return {
        "concept": item.get("concept") or item.get("name"),
        "label": item.get("label"),
        "level": item.get("level"),
        "abstract": bool(item.get("is_abstract")),
        "balance": item.get("balance"),
        "parent": item.get("parent"),
        "calculation_parent": item.get("calculation_parent"),
        "values": {
            _period_label(period): {
                "raw": _json_number(value),
                "reported": _reported_value(value, decimals.get(period)),
                "unit": units.get(period),
                "decimals": decimals.get(period),
                "period_type": period_types.get(period),
                "preferred_sign": preferred_signs.get(period),
            }
            for period, value in values.items()
        },
    }


def _statement_periods(raw_rows: list[dict[str, Any]]) -> list[str]:
    periods = []
    for item in raw_rows:
        for period in (item.get("values") or {}):
            label = _period_label(period)
            if label not in periods:
                periods.append(label)
    return periods


def _period_label(period: str) -> str:
    if period.startswith("instant_"):
        return period.removeprefix("instant_")
    if period.startswith("duration_"):
        return period.removeprefix("duration_").replace("_", " to ")
    return period


def _reported_value(value: Any, decimals: Any) -> int | float | None:
    number = _json_number(value)
    if number is None:
        return None
    try:
        decimal_places = int(decimals)
    except (TypeError, ValueError):
        return number
    if decimal_places >= 0:
        return number
    return _json_number(number / (10 ** abs(decimal_places)))
