"""Alpaca market-data provider for synchronous OHLCV requests."""
from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import httpx

from finance_cli.providers.base import ProviderError


TIMEFRAME_MAP = {
    "5m": "5Min",
    "15m": "15Min",
    "1h": "1Hour",
    "1d": "1Day",
    "1wk": "1Week",
}


class AlpacaMarketDataProvider:
    """Direct Alpaca data API client with no background runtime."""

    name = "alpaca"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str | None = None,
        feed: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.getenv("ALPACA_API_KEY") or os.getenv("APCA_API_KEY_ID")
        self.api_secret = api_secret or os.getenv("ALPACA_API_SECRET") or os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY")
        self.base_url = (base_url or os.getenv("ALPACA_DATA_BASE_URL") or "https://data.alpaca.markets").rstrip("/")
        self.feed = feed or os.getenv("ALPACA_DATA_FEED") or "iex"
        self.timeout = timeout

    def ohlcv(
        self,
        symbol: str,
        *,
        timeframe: str = "1d",
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = 200,
    ) -> list[dict[str, Any]]:
        """Fetch normalized OHLCV rows from Alpaca's stock bars endpoint."""
        if not self.api_key or not self.api_secret:
            raise ProviderError("Alpaca API credentials are required. Set ALPACA_API_KEY and ALPACA_API_SECRET.")
        symbol = symbol.strip().upper()
        if not symbol:
            raise ProviderError("symbol is required")
        alpaca_timeframe = TIMEFRAME_MAP.get(timeframe)
        if alpaca_timeframe is None:
            raise ProviderError(f"Unsupported Alpaca timeframe: {timeframe}")

        start, end = _resolve_window(timeframe, start_date=start_date, end_date=end_date, limit=limit)
        params = {
            "symbols": symbol,
            "timeframe": alpaca_timeframe,
            "adjustment": "split",
            "feed": self.feed,
            "sort": "desc",
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if limit:
            params["limit"] = str(limit)

        headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
        }
        try:
            response = httpx.get(f"{self.base_url}/v2/stocks/bars", params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ProviderError(f"Alpaca OHLCV request failed: {exc}") from exc

        bars_by_symbol = payload.get("bars") or {}
        bars = bars_by_symbol.get(symbol) or bars_by_symbol.get(symbol.upper()) or []
        if not isinstance(bars, list):
            return []
        rows = [_normalize_bar(symbol, bar) for bar in bars if isinstance(bar, dict)]
        rows = [row for row in rows if row["date"] and row["open"] is not None and row["close"] is not None]
        rows = sorted(rows, key=lambda row: row["date"])
        return rows[-int(limit):] if limit is not None else rows


def _resolve_window(
    timeframe: str,
    *,
    start_date: str | None,
    end_date: str | None,
    limit: int | None,
) -> tuple[str | None, str | None]:
    if start_date or end_date:
        return start_date, end_date or date.today().isoformat()
    if not limit:
        return None, None
    end = date.today()
    start = end - timedelta(days=estimated_lookback_days(timeframe, limit))
    return start.isoformat(), end.isoformat()


def estimated_lookback_days(timeframe: str, limit: int | None) -> int:
    """Estimate a bounded lookback window for recent-bar requests."""
    if not limit:
        return 730
    bars_per_trading_day = {
        "5m": 78,
        "15m": 26,
        "1h": 7,
        "1d": 1,
        "1wk": 1 / 5,
        "1mo": 1 / 21,
    }
    per_day = bars_per_trading_day.get(timeframe, 1)
    trading_days = max(1, int((limit + per_day - 1) // per_day))
    return min(730, int((trading_days * 7) / 5) + 14)


def _normalize_bar(symbol: str, bar: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "date": str(bar.get("t") or bar.get("timestamp") or ""),
        "open": _number_or_none(bar.get("o") if "o" in bar else bar.get("open")),
        "high": _number_or_none(bar.get("h") if "h" in bar else bar.get("high")),
        "low": _number_or_none(bar.get("l") if "l" in bar else bar.get("low")),
        "close": _number_or_none(bar.get("c") if "c" in bar else bar.get("close")),
        "volume": _number_or_none(bar.get("v") if "v" in bar else bar.get("volume")),
        "adjusted_close": _number_or_none(bar.get("c") if "c" in bar else bar.get("close")),
        "source": "alpaca",
    }


def _number_or_none(value: Any) -> float | int | None:
    try:
        if value != value:
            return None
        numeric = float(value)
    except Exception:
        return None
    return int(numeric) if numeric.is_integer() else numeric
