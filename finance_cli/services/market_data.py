"""Market data services."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from finance_cli.providers.alphavantage import AlphaVantageProvider
from finance_cli.providers.base import ProviderError
from finance_cli.providers.config import SECTOR_ETFS
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


def relative_price_performance(
    symbol: str,
    *,
    benchmarks: list[str] | None = None,
    peers: list[str] | None = None,
    sector_etfs: list[str] | None = None,
    periods: list[str] | None = None,
    market: str = "US",
    provider: str = "auto",
    service: HistoricalMarketDataService | None = None,
    quote_provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    """Compare a symbol's price returns against benchmarks, sector ETFs, and explicit peers."""
    normalized_symbol = symbol.strip().upper()
    period_keys = periods or ["1M", "3M", "6M", "1Y"]
    comparison_specs = [(item.strip().upper(), "benchmark") for item in (benchmarks or ["SPY", "QQQ"]) if item.strip()]
    warnings: list[str] = []

    if sector_etfs is None:
        sector_etf = _auto_sector_etf(normalized_symbol, market=market, quote_provider=quote_provider, warnings=warnings)
        if sector_etf:
            comparison_specs.append((sector_etf, "sector_etf"))
    else:
        comparison_specs.extend((item.strip().upper(), "sector_etf") for item in sector_etfs if item.strip())

    comparison_specs.extend((item.strip().upper(), "peer") for item in (peers or []) if item.strip())
    comparison_specs = _dedupe_comparison_specs(comparison_specs, excluded_symbol=normalized_symbol)

    windows = {period: _performance_window(period) for period in period_keys}
    max_window = max(windows.values())
    limit = max_window + 5
    start = date.today() - timedelta(days=int(max_window * 1.8) + 10)
    common = {
        "timeframe": "1d",
        "start_date": start.isoformat(),
        "limit": limit,
        "provider": provider,
        "service": service,
    }
    symbol_data = fetch_ohlcv(normalized_symbol, **common)
    symbol_rows = _sorted_price_rows(symbol_data.get("rows") or [])
    output_rows: list[dict[str, Any]] = []

    for comparison, comparison_type in comparison_specs:
        comparison_data = fetch_ohlcv(comparison, **common)
        comparison_rows = _sorted_price_rows(comparison_data.get("rows") or [])
        for period, window in windows.items():
            symbol_return = _window_return(symbol_rows, window)
            comparison_return = _window_return(comparison_rows, window)
            output_rows.append({
                "symbol": normalized_symbol,
                "period": period,
                **{f"symbol_{key}": value for key, value in symbol_return.items()},
                "comparison": comparison,
                "comparison_type": comparison_type,
                **{f"comparison_{key}": value for key, value in comparison_return.items()},
                "relative_return_pct": _return_gap(symbol_return.get("return_pct"), comparison_return.get("return_pct")),
                "source": symbol_data.get("source"),
                "comparison_source": comparison_data.get("source"),
            })

    return {
        "symbol": normalized_symbol,
        "market": market.upper(),
        "periods": period_keys,
        "relative_performance": output_rows,
        "count": len(output_rows),
        "source": symbol_data.get("source"),
        "warnings": warnings,
    }


def market_trend(
    market: str = "US",
    *,
    symbols: list[str] | None = None,
    periods: list[str] | None = None,
    provider: str = "auto",
    service: HistoricalMarketDataService | None = None,
) -> dict[str, Any]:
    """Return raw major-index and volatility trend evidence."""
    market_key = market.strip().upper() or "US"
    period_keys = periods or ["1M", "3M", "6M", "1Y"]
    role_symbols = _market_trend_symbols(symbols)
    max_window = max([_performance_window(period) for period in period_keys] + [200])
    limit = max_window + 5
    market_data = service or HistoricalMarketDataService()
    trend_rows: list[dict[str, Any]] = []

    for symbol, role in role_symbols:
        rows, attempt, _attempts = market_data.load_ohlcv(symbol, timeframe="1d", limit=limit, provider=provider)
        price_rows = _sorted_price_rows(rows)
        if role == "volatility":
            trend_rows.append(_volatility_trend_row(symbol, role, price_rows, source=attempt.provider))
        else:
            trend_rows.append(_market_trend_row(symbol, role, price_rows, periods=period_keys, source=attempt.provider))

    return {
        "market": market_key,
        "trend": trend_rows,
        "market_direction_state": _market_direction_state(trend_rows),
        "count": len(trend_rows),
        "source": "historical_market_data",
    }


def _market_trend_symbols(symbols: list[str] | None) -> list[tuple[str, str]]:
    if symbols:
        default_roles = {
            "SPY": "primary",
            "QQQ": "growth",
            "DIA": "dow",
            "IWM": "small_caps",
            "^VIX": "volatility",
        }
        return [(symbol.strip().upper(), default_roles.get(symbol.strip().upper(), "comparison")) for symbol in symbols if symbol.strip()]
    return [
        ("SPY", "primary"),
        ("QQQ", "growth"),
        ("DIA", "dow"),
        ("IWM", "small_caps"),
        ("^VIX", "volatility"),
    ]


def _market_trend_row(symbol: str, role: str, rows: list[dict[str, Any]], *, periods: list[str], source: str) -> dict[str, Any]:
    prices = [_price(row) for row in rows]
    prices = [price for price in prices if price is not None]
    latest = prices[-1] if prices else None
    sma_50 = _average(prices[-50:])
    sma_200 = _average(prices[-200:])
    period_returns = {}
    for period in periods:
        period_returns[f"return_{period.lower()}_pct"] = _window_return(rows, _performance_window(period)).get("return_pct")
    return {
        "kind": "market_trend",
        "symbol": symbol,
        "role": role,
        "last_close": _round_number(latest),
        "sma_50": _round_number(sma_50),
        "sma_200": _round_number(sma_200),
        "above_sma_50": bool(latest is not None and sma_50 is not None and latest >= sma_50),
        "above_sma_200": bool(latest is not None and sma_200 is not None and latest >= sma_200),
        **period_returns,
        "source": source,
    }


def _volatility_trend_row(symbol: str, role: str, rows: list[dict[str, Any]], *, source: str) -> dict[str, Any]:
    prices = [_price(row) for row in rows]
    prices = [price for price in prices if price is not None]
    latest = prices[-1] if prices else None
    sma_20 = _average(prices[-20:])
    sma_50 = _average(prices[-50:])
    return {
        "kind": "market_volatility",
        "symbol": symbol,
        "role": role,
        "last_close": _round_number(latest),
        "sma_20": _round_number(sma_20),
        "sma_50": _round_number(sma_50),
        "volatility_trend": "rising" if latest is not None and sma_20 is not None and latest > sma_20 else "falling_or_flat",
        "volatility_state": _volatility_state(latest),
        "source": source,
    }


def _market_direction_state(rows: list[dict[str, Any]]) -> str:
    primary = next((row for row in rows if row.get("role") == "primary"), None)
    growth = next((row for row in rows if row.get("role") == "growth"), None)
    volatility = next((row for row in rows if row.get("role") == "volatility"), None)
    if primary and primary.get("above_sma_50") and primary.get("above_sma_200") and growth and growth.get("above_sma_50"):
        if not volatility or volatility.get("volatility_state") in {"contained", "unknown"}:
            return "uptrend"
    if primary and not primary.get("above_sma_200"):
        return "correction"
    return "under_pressure"


def _volatility_state(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value < 20:
        return "contained"
    if value < 30:
        return "elevated"
    return "stressed"


def _auto_sector_etf(
    symbol: str,
    *,
    market: str,
    quote_provider: YahooFinanceProvider | None,
    warnings: list[str],
) -> str | None:
    client = quote_provider or YahooFinanceProvider()
    try:
        quote = client.quote(symbol)
    except Exception as exc:
        warnings.append(f"sector ETF unavailable: quote failed: {exc}")
        return None
    sector = quote.get("sector")
    sector_map = SECTOR_ETFS.get(market.upper(), {})
    etf = sector_map.get(str(sector)) if sector else None
    if not etf:
        warnings.append(f"sector ETF unavailable: no mapping for sector {sector!r}")
    return etf


def _dedupe_comparison_specs(specs: list[tuple[str, str]], *, excluded_symbol: str) -> list[tuple[str, str]]:
    seen = {excluded_symbol}
    deduped: list[tuple[str, str]] = []
    for symbol, comparison_type in specs:
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        deduped.append((symbol, comparison_type))
    return deduped


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


def _average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _round_number(value: Any) -> float | None:
    number = _number(value)
    return round(number, 4) if number is not None else None
