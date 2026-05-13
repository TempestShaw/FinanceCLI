"""Financial Modeling Prep provider."""
from __future__ import annotations

import os
from typing import Any

import httpx

from finance_cli.core.common import normalize_symbol
from finance_cli.providers.base import ProviderError


class FMPProvider:
    """Small client for FMP analyst estimate endpoints."""

    BASE_URL = "https://financialmodelingprep.com/stable"

    def __init__(self, *, api_key: str | None = None, timeout: float = 20.0) -> None:
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        self.timeout = timeout

    def analyst_estimates(
        self,
        symbol: str,
        *,
        period: str = "annual",
        page: int = 0,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        if not self.api_key:
            raise ProviderError("FMP API key is required. Set FMP_API_KEY.")
        normalized = normalize_symbol(symbol)
        period_key = period.strip().lower()
        if period_key not in {"annual", "quarter"}:
            raise ProviderError("period must be annual or quarter")
        try:
            response = httpx.get(
                f"{self.BASE_URL}/analyst-estimates",
                params={
                    "symbol": normalized,
                    "period": period_key,
                    "page": page,
                    "limit": limit,
                    "apikey": self.api_key,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ProviderError(f"FMP analyst estimates request failed: {exc}") from exc
        if isinstance(payload, dict) and payload.get("Error Message"):
            raise ProviderError(f"FMP error: {payload['Error Message']}")
        if not isinstance(payload, list):
            raise ProviderError("FMP analyst estimates returned an unexpected payload")
        return [_estimate_row(row, symbol=normalized, period=period_key) for row in payload if isinstance(row, dict)]


def _estimate_row(row: dict[str, Any], *, symbol: str, period: str) -> dict[str, Any]:
    return {
        "symbol": row.get("symbol") or symbol,
        "date": row.get("date"),
        "period": row.get("period") or period,
        "fiscal_year": _first(row, "fiscalYear", "calendarYear", "year"),
        "revenue": _metric(row, "revenue"),
        "eps": _metric(row, "eps"),
        "ebitda": _metric(row, "ebitda"),
        "ebit": _metric(row, "ebit"),
        "net_income": _metric(row, "netIncome"),
        "sga_expense": _metric(row, "sgaExpense"),
        "analyst_count": {
            "revenue": _first(row, "numAnalystsRevenue", "numberAnalystEstimatedRevenue"),
            "eps": _first(row, "numAnalystsEps", "numberAnalystsEstimatedEps"),
        },
        "provider": "fmp",
        "source_url": "https://financialmodelingprep.com/stable/analyst-estimates",
    }


def _metric(row: dict[str, Any], prefix: str) -> dict[str, Any]:
    return {
        "avg": _first(row, f"{prefix}Avg", f"{prefix}_avg"),
        "low": _first(row, f"{prefix}Low", f"{prefix}_low"),
        "high": _first(row, f"{prefix}High", f"{prefix}_high"),
    }


def _first(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if row.get(key) is not None:
            return row[key]
    return None
