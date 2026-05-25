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
            "shares_outstanding": quote.get("shares_outstanding"),
            "float_shares": quote.get("float_shares"),
            "average_volume": quote.get("average_volume"),
            "average_volume_10d": quote.get("average_volume_10d"),
            "regular_market_volume": quote.get("regular_market_volume"),
            "volume_vs_average": quote.get("volume_vs_average"),
            "fifty_two_week_high": quote.get("fifty_two_week_high"),
            "fifty_two_week_low": quote.get("fifty_two_week_low"),
            "fifty_day_average": quote.get("fifty_day_average"),
            "two_hundred_day_average": quote.get("two_hundred_day_average"),
            "trailing_eps": quote.get("trailing_eps"),
            "forward_eps": quote.get("forward_eps"),
            "earnings_quarterly_growth": quote.get("earnings_quarterly_growth"),
            "profit_margins": quote.get("profit_margins"),
            "operating_margins": quote.get("operating_margins"),
            "return_on_equity": quote.get("return_on_equity"),
            "held_percent_institutions": quote.get("held_percent_institutions"),
            "held_percent_insiders": quote.get("held_percent_insiders"),
            "short_ratio": quote.get("short_ratio"),
            "beta": quote.get("beta"),
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
