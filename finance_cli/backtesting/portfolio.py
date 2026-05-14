"""Portfolio-construction primitives for factor backtests."""
from __future__ import annotations

from math import floor
from typing import Any


def build_quantile_weights(
    scores: dict[str, float],
    *,
    direction: str = "long_short",
    top_pct: float = 0.2,
    bottom_pct: float = 0.2,
) -> dict[str, float]:
    """Build equal-weight long/short baskets from cross-sectional factor scores.

    Scores should already be lagged by the caller when used in a backtest. This
    function is intentionally pure so any engine can use it.
    """
    clean_scores = {
        str(symbol).strip().upper(): float(score)
        for symbol, score in scores.items()
        if str(symbol).strip() and score is not None
    }
    if not clean_scores:
        return {}

    n_valid = len(clean_scores)
    n_long = max(1, int(floor(n_valid * top_pct)))
    n_short = max(1, int(floor(n_valid * bottom_pct))) if direction == "long_short" else 0

    ranked_desc = sorted(clean_scores.items(), key=lambda item: item[1], reverse=True)
    ranked_asc = sorted(clean_scores.items(), key=lambda item: item[1])
    longs = [symbol for symbol, _score in ranked_desc[:n_long]]
    shorts = [symbol for symbol, _score in ranked_asc[:n_short] if symbol not in longs]

    weights = {symbol: 0.0 for symbol in clean_scores}
    if direction == "long_only" or not shorts:
        long_weight = 1.0 / len(longs)
    else:
        long_weight = 0.5 / len(longs)
    for symbol in longs:
        weights[symbol] = long_weight

    if direction == "long_short" and shorts:
        short_weight = -0.5 / len(shorts)
        for symbol in shorts:
            weights[symbol] = short_weight

    return weights


def build_rebalance_snapshot(timestamp: str, weights: dict[str, float]) -> dict[str, Any]:
    """Build a UI- and automation-friendly long-short basket snapshot."""
    longs = sorted(
        [{"symbol": symbol, "weight": float(weight)} for symbol, weight in weights.items() if weight > 0],
        key=lambda row: row["weight"],
        reverse=True,
    )
    shorts = sorted(
        [{"symbol": symbol, "weight": float(weight)} for symbol, weight in weights.items() if weight < 0],
        key=lambda row: row["weight"],
    )
    return {
        "timestamp": timestamp,
        "long": longs,
        "short": shorts,
        "gross_exposure": float(sum(row["weight"] for row in longs) + abs(sum(row["weight"] for row in shorts))),
        "net_exposure": float(sum(weights.values())),
    }


def build_rebalance_events(timestamp: str, weights: dict[str, float]) -> list[dict[str, Any]]:
    """Build normalized rebalance events from a target-weight row."""
    events: list[dict[str, Any]] = []
    long_weights = {symbol: weight for symbol, weight in weights.items() if weight > 0}
    short_weights = {symbol: weight for symbol, weight in weights.items() if weight < 0}

    if long_weights:
        events.append(
            {
                "event_time": timestamp,
                "event_type": "rebalance_long",
                "symbol": None,
                "side": "long",
                "quantity": float(len(long_weights)),
                "price": None,
                "value": float(sum(long_weights.values())),
                "label": f"LONG basket: {', '.join(sorted(long_weights))}",
                "payload": {"weights": dict(sorted(long_weights.items()))},
            }
        )
    if short_weights:
        events.append(
            {
                "event_time": timestamp,
                "event_type": "rebalance_short",
                "symbol": None,
                "side": "short",
                "quantity": float(len(short_weights)),
                "price": None,
                "value": float(sum(short_weights.values())),
                "label": f"SHORT basket: {', '.join(sorted(short_weights))}",
                "payload": {"weights": dict(sorted(short_weights.items()))},
            }
        )
    return events
