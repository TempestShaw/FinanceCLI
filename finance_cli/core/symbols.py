"""Symbol-level finance capabilities."""
from __future__ import annotations

from finance_cli.core.common import normalize_symbol, utc_now
from finance_cli.schemas import FinanceMeta, SymbolSnapshot
from finance_cli.services.symbols import fetch_symbol_profile


def get_symbol_snapshot(symbol: str) -> SymbolSnapshot:
    """Return a provider-backed symbol snapshot."""
    normalized = normalize_symbol(symbol)
    profile = fetch_symbol_profile(normalized)
    sources = profile.get("sources") or ["symbol_profile"]
    return SymbolSnapshot(
        symbol=normalized,
        company_name=profile.get("company_name") or "",
        sector=profile.get("sector") or "",
        industry=profile.get("industry") or "",
        last_price=profile.get("last_price"),
        change_pct=None,
        key_stats={
            "market_cap": profile.get("market_cap"),
            "currency": profile.get("currency"),
            "cik": profile.get("cik"),
            "sources": sources,
        },
        meta=FinanceMeta(
            source=";".join(str(source) for source in sources),
            as_of=utc_now(),
            notes="Provider-backed symbol metadata; change_pct is not populated by this snapshot wrapper.",
        ),
    )
