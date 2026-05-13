"""Backtest result shaping helpers."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Iterable


def normalize_event_time(value: Any) -> str | None:
    """Normalize event timestamps to ISO-ish strings without pandas."""
    if value in (None, ""):
        return None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
        except ValueError:
            return value
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def normalize_events(events: Iterable[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Normalize raw engine events into one stable event schema."""
    normalized: list[dict[str, Any]] = []
    for event in events or []:
        payload = event.get("payload") or {}
        normalized.append(
            {
                "event_time": normalize_event_time(event.get("event_time")),
                "event_type": str(event.get("event_type") or "info"),
                "symbol": event.get("symbol"),
                "side": event.get("side"),
                "quantity": event.get("quantity"),
                "price": event.get("price"),
                "value": event.get("value"),
                "label": event.get("label"),
                "payload": deepcopy(payload),
            }
        )
    return normalized


def shape_backtest_result(
    *,
    run_type: str,
    config: dict[str, Any],
    metrics: dict[str, Any],
    events: Iterable[dict[str, Any]] | None = None,
    equity_curve: list[dict[str, Any]] | None = None,
    returns_ts: list[dict[str, Any]] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a normalized result payload for factor/strategy backtests."""
    result = {
        "run_type": run_type,
        "config": deepcopy(config),
        "equity_curve": equity_curve or [],
        "events": normalize_events(events),
    }
    if returns_ts is not None:
        result["returns_ts"] = returns_ts
    result.update(metrics)
    if extra:
        result.update(extra)
    return result
