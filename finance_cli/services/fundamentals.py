"""Fundamental data services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.yahoo import YahooFinanceProvider


def fetch_financial_statement(
    symbol: str,
    *,
    statement: str = "income",
    period: str = "annual",
    provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    """Fetch a normalized financial statement table."""
    client = provider or YahooFinanceProvider()
    return client.financial_statement(symbol, statement=statement, period=period)
