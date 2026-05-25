"""Ownership and holder data services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.yahoo import YahooFinanceProvider


def fetch_holders(
    symbol: str,
    *,
    limit: int = 10,
    provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    """Fetch holder and insider tables for a symbol."""
    client = provider or YahooFinanceProvider()
    return client.holders(symbol, limit=limit)
