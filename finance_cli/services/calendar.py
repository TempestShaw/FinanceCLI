"""Company calendar services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.yahoo import YahooFinanceProvider


def fetch_company_calendar(symbol: str, *, provider: YahooFinanceProvider | None = None) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    return client.company_calendar(symbol)


def fetch_earnings_dates(
    symbol: str,
    *,
    limit: int = 12,
    provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    return client.earnings_dates(symbol, limit=limit)
