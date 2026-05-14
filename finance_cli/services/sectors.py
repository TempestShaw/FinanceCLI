"""Sector and industry intelligence services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.yahoo import YahooFinanceProvider


def list_sector_keys(*, provider: YahooFinanceProvider | None = None) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    return client.sector_keys()


def fetch_sector_overview(key: str, *, provider: YahooFinanceProvider | None = None) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    return client.sector_overview(key)


def fetch_sector_industries(key: str, *, provider: YahooFinanceProvider | None = None) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    return client.sector_industries(key)


def fetch_sector_table(
    key: str,
    *,
    table: str = "top_companies",
    limit: int = 25,
    provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    if table == "top_companies":
        return client.sector_top_companies(key, limit=limit)
    if table == "top_etfs":
        return client.sector_top_etfs(key, limit=limit)
    if table == "top_mutual_funds":
        return client.sector_top_mutual_funds(key, limit=limit)
    if table == "research_reports":
        return client.sector_research_reports(key, limit=limit)
    raise ValueError("table must be one of top_companies, top_etfs, top_mutual_funds, research_reports")


def list_industry_keys(
    *,
    sector: str | None = None,
    provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    return client.industry_keys(sector=sector)


def fetch_industry_overview(key: str, *, provider: YahooFinanceProvider | None = None) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    return client.industry_overview(key)


def fetch_industry_table(
    key: str,
    *,
    table: str = "top_companies",
    limit: int = 25,
    provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    client = provider or YahooFinanceProvider()
    if table == "top_companies":
        return client.industry_top_companies(key, limit=limit)
    if table == "top_growth_companies":
        return client.industry_top_growth_companies(key, limit=limit)
    if table == "top_performing_companies":
        return client.industry_top_performing_companies(key, limit=limit)
    if table == "research_reports":
        return client.industry_research_reports(key, limit=limit)
    raise ValueError(
        "table must be one of top_companies, top_growth_companies, "
        "top_performing_companies, research_reports"
    )
