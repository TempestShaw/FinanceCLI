"""Alpha Vantage provider for realtime-ish market quotes."""
from __future__ import annotations

import os
import time
from typing import Any

import httpx

from finance_cli.providers.base import ProviderError


class AlphaVantageProvider:
    """Small Alpha Vantage quote client."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, *, api_key: str | None = None, timeout: float = 30.0, rate_limit: int = 5) -> None:
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY") or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.timeout = timeout
        self.rate_limit = rate_limit
        self._last_request_time = 0.0
        self._requests_this_minute = 0

    def realtime_quote(self, symbol: str) -> dict[str, Any]:
        """Fetch Alpha Vantage GLOBAL_QUOTE and normalize field names."""
        if not self.api_key:
            raise ProviderError("Alpha Vantage API key is required. Set ALPHAVANTAGE_API_KEY.")
        symbol = symbol.strip().upper()
        if not symbol:
            raise ProviderError("symbol is required")
        self._rate_limit_wait()
        try:
            response = httpx.get(
                self.BASE_URL,
                params={"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": self.api_key},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ProviderError(f"Alpha Vantage quote request failed: {exc}") from exc

        if "Note" in payload:
            raise ProviderError(f"Alpha Vantage rate limit: {payload['Note']}")
        if "Error Message" in payload:
            raise ProviderError(f"Alpha Vantage error: {payload['Error Message']}")

        raw = payload.get("Global Quote") or {}
        if not raw:
            raise ProviderError(f"Alpha Vantage returned no quote for {symbol}")
        return {
            "symbol": raw.get("01. symbol") or symbol,
            "open": _float_or_none(raw.get("02. open")),
            "high": _float_or_none(raw.get("03. high")),
            "low": _float_or_none(raw.get("04. low")),
            "price": _float_or_none(raw.get("05. price")),
            "volume": _int_or_none(raw.get("06. volume")),
            "latest_trading_day": raw.get("07. latest trading day"),
            "previous_close": _float_or_none(raw.get("08. previous close")),
            "change": _float_or_none(raw.get("09. change")),
            "change_percent": _percent_or_none(raw.get("10. change percent")),
            "source": "alphavantage",
        }

    def _rate_limit_wait(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < 60 and self._requests_this_minute >= self.rate_limit:
            time.sleep(max(0.0, 60 - elapsed))
            self._requests_this_minute = 0
        elif elapsed >= 60:
            self._requests_this_minute = 0
        self._last_request_time = time.time()
        self._requests_this_minute += 1


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _percent_or_none(value: Any) -> float | None:
    if value is None:
        return None
    return _float_or_none(str(value).replace("%", ""))
