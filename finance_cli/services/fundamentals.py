"""Fundamental data services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.sec_edgar import SecEdgarProvider
from finance_cli.providers.yahoo import YahooFinanceProvider


def fetch_financial_statement(
    symbol: str,
    *,
    statement: str = "income",
    period: str = "annual",
    provider: str | SecEdgarProvider | YahooFinanceProvider | None = "sec",
) -> dict[str, Any]:
    """Fetch a normalized financial statement table."""
    if provider is None:
        provider = "sec"
    if isinstance(provider, str):
        provider_key = provider.strip().lower()
        if provider_key == "sec":
            client = SecEdgarProvider()
        elif provider_key == "yahoo":
            client = YahooFinanceProvider()
        else:
            raise ValueError("provider must be sec or yahoo")
    else:
        client = provider
    return client.financial_statement(symbol, statement=statement, period=period)


def fetch_financial_metrics(
    symbol: str,
    *,
    period: str = "quarterly",
    metrics: list[str] | None = None,
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """Fetch standard financial metrics using SEC/edgartools financial getters."""
    client = provider or SecEdgarProvider()
    return client.financial_metrics(symbol, period=period, metrics=metrics)
