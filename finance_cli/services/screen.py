"""Yahoo screener services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.yahoo import YahooFinanceProvider


def list_predefined_screens(*, provider: YahooFinanceProvider | None = None) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    return client.predefined_screens()


def run_predefined_screen(
    query: str,
    *,
    count: int = 25,
    offset: int | None = None,
    sort_field: str | None = None,
    sort_asc: bool | None = None,
    provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    return client.run_screen(
        query,
        count=count,
        offset=offset,
        sort_field=sort_field,
        sort_asc=sort_asc,
    )
