"""Market-level finance capabilities."""
from __future__ import annotations

from finance_cli.core.common import utc_now
from finance_cli.providers.config import MARKET_BENCHMARKS, SECTOR_ETFS
from finance_cli.providers.historical import HistoricalMarketDataService
from finance_cli.schemas import FinanceMeta, MarketRegime, SectorHeat


def get_market_regime(
    market: str = "US",
    timeframe: str = "swing",
    *,
    service: HistoricalMarketDataService | None = None,
) -> MarketRegime:
    """Return a deterministic market regime snapshot from benchmark OHLCV."""
    market_key = market.upper()
    benchmarks = MARKET_BENCHMARKS.get(market_key)
    if not benchmarks:
        return _unavailable_regime(market_key, timeframe, f"unsupported market: {market_key}")

    market_data = service or HistoricalMarketDataService()
    symbols = list(dict.fromkeys(benchmarks.values()))
    results = market_data.load_ohlcv_batch(symbols, timeframe="1d", limit=260, provider="auto")
    primary = _series_stats(results.get(benchmarks["primary"], ([], None, []))[0])
    growth = _series_stats(results.get(benchmarks["growth"], ([], None, []))[0])
    small_caps = _series_stats(results.get(benchmarks["small_caps"], ([], None, []))[0])
    volatility = _series_stats(results.get(benchmarks["volatility"], ([], None, []))[0])

    if not primary:
        return _unavailable_regime(market_key, timeframe, "primary benchmark returned no OHLCV rows")

    benchmark_stats = {
        "primary": primary,
        "growth": growth,
        "small_caps": small_caps,
    }
    available_risk_assets = [row for row in benchmark_stats.values() if row]
    positive_count = sum(1 for row in available_risk_assets if row["return_pct"] is not None and row["return_pct"] > 0)
    above_50_count = sum(1 for row in available_risk_assets if row["above_sma_50"])
    breadth_value = _breadth_label(positive_count=positive_count, above_50_count=above_50_count, total=len(available_risk_assets))
    volatility_value = _volatility_label(volatility.get("last_close") if volatility else None)
    primary_above_200 = bool(primary["above_sma_200"])
    regime = _regime_label(primary_above_200=primary_above_200, breadth_value=breadth_value, volatility_value=volatility_value)
    confidence = _regime_confidence(primary_above_200=primary_above_200, breadth_value=breadth_value, volatility_value=volatility_value)

    return MarketRegime(
        market=market_key,
        timeframe=timeframe,
        regime=regime,
        confidence=confidence,
        signals=[
            {
                "name": "index_trend",
                "symbol": benchmarks["primary"],
                "value": "above_200dma" if primary_above_200 else "below_200dma",
                "direction": "bullish" if primary_above_200 else "bearish",
                "last_close": primary["last_close"],
                "sma_50": primary["sma_50"],
                "sma_200": primary["sma_200"],
                "return_pct": primary["return_pct"],
            },
            {
                "name": "breadth",
                "value": breadth_value,
                "direction": "bullish" if breadth_value == "constructive" else "bearish" if breadth_value == "weak" else "neutral",
                "positive_benchmark_count": positive_count,
                "above_50dma_count": above_50_count,
                "total_benchmarks": len(available_risk_assets),
            },
            {
                "name": "volatility",
                "symbol": benchmarks["volatility"],
                "value": volatility_value,
                "direction": "bearish" if volatility_value == "stressed" else "neutral",
                "last_close": volatility.get("last_close") if volatility else None,
            },
        ],
        meta=FinanceMeta(
            source="historical_market_data",
            as_of=utc_now(),
            notes="Deterministic regime from configured benchmark ETFs/indexes; not an investment conclusion.",
        ),
    )


def get_sector_heat(
    market: str = "US",
    lookback_days: int = 20,
    group_by: str = "sector",
    *,
    service: HistoricalMarketDataService | None = None,
) -> SectorHeat:
    """Return deterministic sector heat rankings from configured sector ETFs."""
    market_key = market.upper()
    sector_map = SECTOR_ETFS.get(market_key, {})
    if not sector_map:
        return SectorHeat(
            market=market_key,
            group_by=group_by,
            lookback_days=lookback_days,
            leaders=[],
            laggards=[],
            meta=FinanceMeta(source="historical_market_data", as_of=utc_now(), notes=f"unsupported market: {market_key}"),
        )

    market_data = service or HistoricalMarketDataService()
    symbols = list(sector_map.values())
    limit = max(int(lookback_days) + 5, 30)
    results = market_data.load_ohlcv_batch(symbols, timeframe="1d", limit=limit, provider="auto")
    rows = []
    symbol_to_sector = {symbol: sector for sector, symbol in sector_map.items()}
    for symbol, (ohlcv_rows, _attempt, _attempts) in results.items():
        stats = _series_stats(ohlcv_rows, lookback_days=int(lookback_days))
        if not stats or stats["return_pct"] is None:
            continue
        rows.append(
            {
                "name": symbol_to_sector.get(symbol, symbol),
                "symbol": symbol,
                "heat_score": round(float(stats["return_pct"]), 2),
                "return_pct": stats["return_pct"],
                "last_close": stats["last_close"],
                "source": "historical_market_data",
            }
        )
    rows.sort(key=lambda row: row["heat_score"], reverse=True)
    return SectorHeat(
        market=market_key,
        group_by=group_by,
        lookback_days=lookback_days,
        leaders=rows[:5],
        laggards=list(reversed(rows[-5:])),
        meta=FinanceMeta(
            source="historical_market_data",
            as_of=utc_now(),
            notes="Heat score is lookback return percentage for configured public sector ETFs.",
        ),
    )


def _series_stats(rows: list[dict] | None, *, lookback_days: int = 60) -> dict | None:
    prices = [float(row["close"]) for row in rows or [] if row.get("close") is not None]
    if not prices:
        return None
    lookback = max(1, min(int(lookback_days), len(prices) - 1)) if len(prices) > 1 else 1
    start_price = prices[-lookback - 1] if len(prices) > lookback else prices[0]
    last_price = prices[-1]
    return_pct = ((last_price / start_price) - 1) * 100 if start_price else None
    sma_50 = _average(prices[-50:]) if len(prices) >= 50 else _average(prices)
    sma_200 = _average(prices[-200:]) if len(prices) >= 200 else _average(prices)
    return {
        "last_close": round(last_price, 4),
        "return_pct": round(return_pct, 2) if return_pct is not None else None,
        "sma_50": round(sma_50, 4) if sma_50 is not None else None,
        "sma_200": round(sma_200, 4) if sma_200 is not None else None,
        "above_sma_50": bool(sma_50 is not None and last_price >= sma_50),
        "above_sma_200": bool(sma_200 is not None and last_price >= sma_200),
    }


def _average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _breadth_label(*, positive_count: int, above_50_count: int, total: int) -> str:
    if total == 0:
        return "unknown"
    constructive_threshold = max(1, round(total * 0.67))
    weak_threshold = max(1, round(total * 0.34))
    if positive_count >= constructive_threshold and above_50_count >= constructive_threshold:
        return "constructive"
    if positive_count <= weak_threshold and above_50_count <= weak_threshold:
        return "weak"
    return "mixed"


def _volatility_label(vix_close: float | None) -> str:
    if vix_close is None:
        return "unknown"
    if vix_close < 20:
        return "contained"
    if vix_close < 30:
        return "elevated"
    return "stressed"


def _regime_label(*, primary_above_200: bool, breadth_value: str, volatility_value: str) -> str:
    if primary_above_200 and breadth_value == "constructive" and volatility_value in {"contained", "unknown"}:
        return "risk_on"
    if not primary_above_200 and breadth_value == "weak":
        return "bear_trend"
    if volatility_value == "stressed":
        return "risk_off"
    return "mixed"


def _regime_confidence(*, primary_above_200: bool, breadth_value: str, volatility_value: str) -> float:
    score = 0.45
    if primary_above_200:
        score += 0.15
    if breadth_value in {"constructive", "weak"}:
        score += 0.2
    if volatility_value != "unknown":
        score += 0.1
    return round(min(score, 0.9), 2)


def _unavailable_regime(market: str, timeframe: str, reason: str) -> MarketRegime:
    return MarketRegime(
        market=market,
        timeframe=timeframe,
        regime="unavailable",
        confidence=0.0,
        signals=[],
        meta=FinanceMeta(source="historical_market_data", as_of=utc_now(), notes=reason),
    )
