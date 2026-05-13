"""Symbol profile services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.base import ProviderError
from finance_cli.providers.sec_edgar import SecEdgarProvider
from finance_cli.providers.yahoo import YahooFinanceProvider


def fetch_symbol_profile(
    symbol: str,
    *,
    quote_provider: YahooFinanceProvider | None = None,
    sec_provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """Fetch a best-effort public-company profile from market and SEC sources."""
    normalized = symbol.strip().upper()
    if not normalized:
        raise ProviderError("symbol is required")

    profile: dict[str, Any] = {
        "symbol": normalized,
        "company_name": None,
        "sector": None,
        "industry": None,
        "last_price": None,
        "market_cap": None,
        "currency": None,
        "cik": None,
        "sources": [],
        "errors": [],
    }

    quote_client = quote_provider or YahooFinanceProvider()
    try:
        quote = quote_client.quote(normalized)
        profile.update({
            "company_name": quote.get("company_name"),
            "sector": quote.get("sector"),
            "industry": quote.get("industry"),
            "website": quote.get("website"),
            "ir_website": quote.get("ir_website"),
            "last_price": quote.get("last_price"),
            "market_cap": quote.get("market_cap"),
            "currency": quote.get("currency"),
        })
        profile["sources"].append(quote.get("source") or "yfinance")
    except Exception as exc:
        profile["errors"].append(f"quote: {exc}")

    sec_client = sec_provider or SecEdgarProvider()
    try:
        company = sec_client.get_company(normalized)
        cik = f"{int(company['cik_str']):010d}"
        sec_name = company.get("title")
        profile["cik"] = cik
        profile["company_name"] = profile["company_name"] or sec_name
        profile["sources"].append("sec_edgar")
    except Exception as exc:
        profile["errors"].append(f"sec: {exc}")

    if not profile["company_name"] and profile["errors"]:
        raise ProviderError("; ".join(profile["errors"]))
    if not profile["errors"]:
        profile.pop("errors")
    return profile
