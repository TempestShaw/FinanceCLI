"""Market data services."""
from __future__ import annotations

from datetime import date, timedelta
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


def price_performance(
    symbol: str,
    *,
    benchmark: str = "SPY",
    periods: list[str] | None = None,
    provider: str = "auto",
    service: HistoricalMarketDataService | None = None,
) -> dict[str, Any]:
    """Compute deterministic price returns and benchmark-relative returns."""
    period_keys = periods or ["1M", "3M", "6M", "1Y"]
    windows = {period: _performance_window(period) for period in period_keys}
    max_window = max(windows.values())
    limit = max_window + 5
    normalized_symbol = symbol.strip().upper()
    normalized_benchmark = benchmark.strip().upper()
    start = date.today() - timedelta(days=int(max_window * 1.8) + 10)
    common = {
        "timeframe": "1d",
        "start_date": start.isoformat(),
        "limit": limit,
        "provider": provider,
        "service": service,
    }
    symbol_data = fetch_ohlcv(normalized_symbol, **common)
    benchmark_data = fetch_ohlcv(normalized_benchmark, **common) if normalized_benchmark else None
    symbol_rows = _sorted_price_rows(symbol_data.get("rows") or [])
    benchmark_rows = _sorted_price_rows(benchmark_data.get("rows") or []) if benchmark_data else []
    rows = [
        _performance_row(
            period=period,
            window=window,
            symbol=normalized_symbol,
            symbol_rows=symbol_rows,
            benchmark=normalized_benchmark,
            benchmark_rows=benchmark_rows,
        )
        for period, window in windows.items()
    ]
    return {
        "symbol": normalized_symbol,
        "benchmark": normalized_benchmark,
        "periods": period_keys,
        "performance": rows,
        "count": len(rows),
        "source": symbol_data.get("source"),
        "benchmark_source": benchmark_data.get("source") if benchmark_data else None,
    }


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


def _performance_window(period: str) -> int:
    text = str(period).strip().lower()
    aliases = {
        "1m": 21,
        "3m": 63,
        "6m": 126,
        "1y": 252,
    }
    if text in aliases:
        return aliases[text]
    if text.endswith("y") and text[:-1].isdigit():
        return int(text[:-1]) * 252
    if text.endswith("m") and text[:-1].isdigit():
        return int(text[:-1]) * 21
    if text.endswith("d") and text[:-1].isdigit():
        return int(text[:-1])
    raise ValueError(f"unsupported performance period: {period}")


def _sorted_price_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    usable = [
        row for row in rows
        if row.get("date") is not None and _number(row.get("adjusted_close") if row.get("adjusted_close") is not None else row.get("close")) is not None
    ]
    return sorted(usable, key=lambda row: str(row.get("date")))


def _performance_row(
    *,
    period: str,
    window: int,
    symbol: str,
    symbol_rows: list[dict[str, Any]],
    benchmark: str,
    benchmark_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    symbol_return = _window_return(symbol_rows, window)
    benchmark_return = _window_return(benchmark_rows, window) if benchmark else None
    return {
        "period": period,
        "symbol": symbol,
        **{f"symbol_{key}": value for key, value in symbol_return.items()},
        "benchmark": benchmark or None,
        **{f"benchmark_{key}": value for key, value in (benchmark_return or {}).items()},
        "relative_return_pct": _return_gap(symbol_return.get("return_pct"), (benchmark_return or {}).get("return_pct")),
        "distance_from_52w_high_pct": _distance_from_high(symbol_rows, 252),
    }


def _window_return(rows: list[dict[str, Any]], window: int) -> dict[str, Any]:
    if len(rows) < 2:
        return {"return_pct": None, "start_date": None, "end_date": None, "start_close": None, "end_close": None}
    end = rows[-1]
    start = rows[max(0, len(rows) - window - 1)]
    start_close = _price(start)
    end_close = _price(end)
    return {
        "return_pct": _relative_return(end_close, start_close),
        "start_date": start.get("date"),
        "end_date": end.get("date"),
        "start_close": start_close,
        "end_close": end_close,
    }


def _distance_from_high(rows: list[dict[str, Any]], window: int) -> float | None:
    selected = rows[-window:] if len(rows) > window else rows
    prices = [_price(row) for row in selected]
    prices = [price for price in prices if price is not None]
    if not prices:
        return None
    latest = prices[-1]
    high = max(prices)
    if high == 0:
        return None
    return round(((latest / high) - 1.0) * 100.0, 4)


def _price(row: dict[str, Any]) -> float | None:
    return _number(row.get("adjusted_close") if row.get("adjusted_close") is not None else row.get("close"))


def _number(value: Any) -> float | None:
    try:
        if value is None or value != value:
            return None
        return float(value)
    except Exception:
        return None


def _relative_return(numerator: Any, denominator: Any) -> float | None:
    top = _number(numerator)
    bottom = _number(denominator)
    if top is None or bottom in (None, 0):
        return None
    return round(((top / bottom) - 1.0) * 100.0, 4)


def _return_gap(symbol_return: Any, benchmark_return: Any) -> float | None:
    symbol_value = _number(symbol_return)
    benchmark_value = _number(benchmark_return)
    if symbol_value is None or benchmark_value is None:
        return None
    return round(symbol_value - benchmark_value, 4)
