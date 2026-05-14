"""Market data services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.alphavantage import AlphaVantageProvider
from finance_cli.providers.base import ProviderError
from finance_cli.providers.historical import HistoricalMarketDataService
from finance_cli.providers.yahoo import YahooFinanceProvider


def fetch_quote(symbol: str, *, provider: YahooFinanceProvider | None = None) -> dict[str, Any]:
    """Fetch quote/company metadata for a symbol."""
    client = provider or YahooFinanceProvider()
    return client.quote(symbol)


def fetch_market_status(market: str = "US", *, provider: YahooFinanceProvider | None = None) -> dict[str, Any]:
    """Fetch market status and major index summary."""
    client = provider or YahooFinanceProvider()
    return client.market_status(market)


def fetch_ohlcv(
    symbol: str,
    *,
    timeframe: str = "1d",
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = 200,
    provider: str = "auto",
    service: HistoricalMarketDataService | None = None,
    include_attempts: bool = False,
) -> dict[str, Any]:
    """Fetch normalized OHLCV rows with synchronous provider fallback."""
    market_data = service or HistoricalMarketDataService()
    rows, winning_attempt, attempts = market_data.load_ohlcv(
        symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        provider=provider,
    )
    data = {
        "symbol": symbol.upper(),
        "timeframe": timeframe,
        "rows": rows,
        "count": len(rows),
        "source": winning_attempt.provider,
    }
    if include_attempts:
        data["attempts"] = [attempt.to_dict() for attempt in attempts]
    return data


def fetch_ohlcv_batch(
    symbols: list[str],
    *,
    timeframe: str = "1d",
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = 200,
    provider: str = "auto",
    service: HistoricalMarketDataService | None = None,
    include_attempts: bool = False,
) -> dict[str, Any]:
    """Fetch normalized OHLCV rows for multiple symbols synchronously."""
    market_data = service or HistoricalMarketDataService()
    results = market_data.load_ohlcv_batch(
        symbols,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        provider=provider,
    )
    payload: dict[str, Any] = {
        "timeframe": timeframe,
        "symbols": {},
    }
    for symbol, (rows, winning_attempt, attempts) in results.items():
        entry = {
            "symbol": symbol,
            "rows": rows,
            "count": len(rows),
            "source": winning_attempt.provider,
        }
        if include_attempts:
            entry["attempts"] = [attempt.to_dict() for attempt in attempts]
        payload["symbols"][symbol] = entry
    payload["count"] = sum(entry["count"] for entry in payload["symbols"].values())
    return payload


def fetch_realtime_quote(
    symbol: str,
    *,
    provider: AlphaVantageProvider | None = None,
    fallback_provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    """Fetch a realtime-ish quote with Alpha Vantage, falling back to Yahoo metadata."""
    client = provider or AlphaVantageProvider()
    try:
        return client.realtime_quote(symbol)
    except ProviderError as exc:
        fallback = fallback_provider or YahooFinanceProvider()
        quote = fallback.quote(symbol)
        quote["source"] = quote.get("source", "yfinance")
        quote["fallback_reason"] = str(exc)
        return quote
