"""Synchronous historical market-data fallback service."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any, Protocol

from finance_cli.providers.alpaca import AlpacaMarketDataProvider
from finance_cli.providers.yahoo import YahooFinanceProvider


class HistoricalOHLCVProvider(Protocol):
    """Provider contract for synchronous OHLCV fetches."""

    name: str

    def ohlcv(
        self,
        symbol: str,
        *,
        timeframe: str = "1d",
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = 200,
    ) -> list[dict[str, Any]]:
        """Fetch normalized OHLCV rows."""


@dataclass(frozen=True)
class ProviderAttempt:
    provider: str
    duration_ms: float
    rows: int
    success: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HistoricalMarketDataService:
    """Synchronous provider fallback for market-data reads."""

    def __init__(self, providers: list[HistoricalOHLCVProvider] | None = None) -> None:
        self.providers = providers or [
            AlpacaMarketDataProvider(),
            YahooFinanceProvider(),
        ]

    def load_ohlcv(
        self,
        symbol: str,
        *,
        timeframe: str = "1d",
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = 200,
        provider: str = "auto",
    ) -> tuple[list[dict[str, Any]], ProviderAttempt, list[ProviderAttempt]]:
        """Load OHLCV rows from one provider or ordered fallback providers."""
        selected = self._select_providers(provider)
        attempts: list[ProviderAttempt] = []
        last_rows: list[dict[str, Any]] = []

        for candidate in selected:
            started = perf_counter()
            try:
                rows = candidate.ohlcv(
                    symbol,
                    timeframe=timeframe,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                )
                attempt = ProviderAttempt(
                    provider=candidate.name,
                    duration_ms=round((perf_counter() - started) * 1000, 2),
                    rows=len(rows),
                    success=bool(rows),
                )
                attempts.append(attempt)
                if rows:
                    return rows, attempt, attempts
                last_rows = rows
            except Exception as exc:
                attempts.append(
                    ProviderAttempt(
                        provider=candidate.name,
                        duration_ms=round((perf_counter() - started) * 1000, 2),
                        rows=0,
                        success=False,
                        error=str(exc),
                    )
                )

        final_attempt = attempts[-1] if attempts else ProviderAttempt(provider=provider, duration_ms=0.0, rows=0, success=False)
        return last_rows, final_attempt, attempts

    def load_ohlcv_batch(
        self,
        symbols: list[str],
        *,
        timeframe: str = "1d",
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = 200,
        provider: str = "auto",
    ) -> dict[str, tuple[list[dict[str, Any]], ProviderAttempt, list[ProviderAttempt]]]:
        """Load OHLCV rows for symbols synchronously, one symbol at a time."""
        return {
            symbol.strip().upper(): self.load_ohlcv(
                symbol.strip().upper(),
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                provider=provider,
            )
            for symbol in symbols
            if symbol.strip()
        }

    def _select_providers(self, provider: str) -> list[HistoricalOHLCVProvider]:
        if provider == "auto":
            return list(self.providers)
        selected = [candidate for candidate in self.providers if candidate.name == provider]
        if not selected:
            available = ", ".join(candidate.name for candidate in self.providers)
            raise ValueError(f"unknown market data provider: {provider}. Available: {available}")
        return selected
