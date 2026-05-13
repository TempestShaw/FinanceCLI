"""Deterministic price-move detection and evidence timeline helpers."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from finance_cli.core.common import parse_date, parse_rate, parse_window
from finance_cli.services.filings import list_recent_filings
from finance_cli.services.market_data import fetch_ohlcv
from finance_cli.services.news import search_news
from finance_cli.services.transcripts import search_transcripts


def price_moves(
    symbol: str,
    *,
    window: str = "1d",
    years: int = 3,
    threshold: str | float = "8%",
    limit: int = 20,
    provider: str = "auto",
) -> dict[str, Any]:
    """Find large close-to-close moves from one historical OHLCV fetch."""
    lookback_days = max(1, int(years)) * 366
    end = date.today()
    start = end - timedelta(days=lookback_days)
    market_data = fetch_ohlcv(
        symbol,
        timeframe="1d",
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        limit=None,
        provider=provider,
    )
    rows = market_data.get("rows") or []
    moves = detect_price_moves(
        rows,
        symbol=symbol,
        window=window,
        threshold=threshold,
        limit=limit,
    )
    return {
        "symbol": symbol.upper(),
        "window": window,
        "trading_window_days": parse_window(window, mode="trading"),
        "years": years,
        "threshold_pct": parse_rate(threshold) * 100.0,
        "moves": moves,
        "count": len(moves),
        "source": market_data.get("source"),
        "notes": [
            "Moves are close-to-close and deterministic.",
            "No causal explanation is inferred by this command.",
        ],
    }


def detect_price_moves(
    rows: list[dict[str, Any]],
    *,
    symbol: str,
    window: str = "1d",
    threshold: str | float = "8%",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Detect large N-trading-day close-to-close moves from normalized rows."""
    trading_window = parse_window(window, mode="trading")
    threshold_pct = abs(parse_rate(threshold)) * 100.0
    normalized = sorted(
        [row for row in (_normalize_ohlcv_row(row) for row in rows) if row],
        key=lambda row: row["date"],
    )
    daily_returns = _daily_returns(normalized)
    moves: list[dict[str, Any]] = []

    for index in range(trading_window, len(normalized)):
        start_row = normalized[index - trading_window]
        end_row = normalized[index]
        start_close = start_row["close"]
        end_close = end_row["close"]
        if start_close in (None, 0) or end_close is None:
            continue
        return_pct = ((end_close / start_close) - 1.0) * 100.0
        if abs(return_pct) < threshold_pct:
            continue
        avg_volume = _average(
            row.get("volume")
            for row in normalized[max(0, index - 20):index]
            if row.get("volume") is not None
        )
        avg_abs_return = _average(abs(value) for value in daily_returns[max(0, index - 20):index])
        moves.append({
            "symbol": symbol.upper(),
            "end_date": end_row["date"],
            "start_date": start_row["date"],
            "window": f"{trading_window} trading day{'s' if trading_window != 1 else ''}",
            "start_close": _round_number(start_close),
            "end_close": _round_number(end_close),
            "return_pct": round(return_pct, 2),
            "direction": "up" if return_pct > 0 else "down",
            "volume": _round_number(end_row.get("volume")),
            "volume_vs_20d": _safe_ratio(end_row.get("volume"), avg_volume),
            "avg_abs_return_20d_pct": _round_number(avg_abs_return),
            "move_vs_20d_avg_abs_return": _safe_ratio(abs(return_pct), avg_abs_return),
            "source": end_row.get("source"),
        })

    ranked = sorted(moves, key=lambda row: abs(row["return_pct"]), reverse=True)
    return ranked[: max(1, int(limit))]


def price_context(
    symbol: str,
    *,
    target_date: str,
    lookback: str | int = "3D",
    news_limit: int = 5,
    filing_limit: int = 80,
    transcript_limit: int = 12,
) -> dict[str, Any]:
    """Return source-linked evidence around a price-move date."""
    parsed_move_date = parse_date(target_date)
    if parsed_move_date is None:
        raise ValueError(f"invalid date: {target_date}")
    move_date = parsed_move_date
    calendar_window = parse_window(lookback, mode="calendar")
    start = move_date - timedelta(days=calendar_window)
    end = move_date + timedelta(days=calendar_window)
    warnings: list[str] = []
    timeline: list[dict[str, Any]] = []

    try:
        filings = list_recent_filings(symbol, forms=["8-K", "10-Q", "10-K"], limit=filing_limit).get("filings") or []
        for filing in filings:
            filed_at = parse_date(filing.get("filed_at"))
            if filed_at and start <= filed_at <= end:
                timeline.append(_timeline_row(
                    move_date=move_date,
                    event_date=filed_at,
                    source_type="filing",
                    title=f"{filing.get('form')} filed",
                    url=filing.get("url"),
                    metadata={
                        "form": filing.get("form"),
                        "accession_no": filing.get("accession_no"),
                        "report_date": filing.get("report_date"),
                        "items": filing.get("items"),
                    },
                ))
    except Exception as exc:
        warnings.append(f"filings unavailable: {exc}")

    try:
        for article in _news_rows(symbol, start=start, end=end, limit=news_limit):
            published = parse_date(article.get("seendate") or article.get("date"))
            timeline.append(_timeline_row(
                move_date=move_date,
                event_date=published or move_date,
                source_type="news",
                title=article.get("title") or article.get("name") or "News article",
                url=article.get("url"),
                metadata={
                    "domain": article.get("domain"),
                    "source_country": article.get("sourcecountry"),
                    "language": article.get("language"),
                    "published_at": article.get("seendate") or article.get("date"),
                },
                excerpt=article.get("seendate"),
            ))
    except Exception as exc:
        warnings.append(f"news unavailable: {exc}")

    try:
        transcripts = search_transcripts(symbol, limit=transcript_limit).get("transcripts") or []
        for transcript in transcripts:
            published = parse_date(transcript.get("published_at"))
            if published and start <= published <= end:
                timeline.append(_timeline_row(
                    move_date=move_date,
                    event_date=published,
                    source_type="transcript",
                    title=transcript.get("title") or "Earnings call transcript",
                    url=transcript.get("url"),
                    metadata={
                        "quarter": transcript.get("quarter"),
                        "published_at": transcript.get("published_at"),
                        "source": transcript.get("source"),
                    },
                ))
    except Exception as exc:
        warnings.append(f"transcripts unavailable: {exc}")

    timeline = sorted(timeline, key=lambda row: (row["date"], row["source_type"], row["title"]))
    return {
        "symbol": symbol.upper(),
        "target_date": move_date.isoformat(),
        "lookback": str(lookback),
        "lookback_days": calendar_window,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timeline": timeline,
        "count": len(timeline),
        "warnings": warnings,
        "notes": [
            "Timeline roles are temporal only: before_move, same_day, or after_move.",
            "Event/publication dates are shown explicitly to avoid implied causality.",
        ],
    }


def _news_rows(symbol: str, *, start: date, end: date, limit: int) -> list[dict[str, Any]]:
    payload = search_news(
        symbol=symbol,
        max_records=limit,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
    )
    rows = payload.get("articles") or []
    return [row for row in rows if isinstance(row, dict)][: max(1, int(limit))]


def _timeline_row(
    *,
    move_date: date,
    event_date: date,
    source_type: str,
    title: Any,
    url: Any,
    metadata: dict[str, Any],
    excerpt: Any = None,
) -> dict[str, Any]:
    delta = (event_date - move_date).days
    if delta < 0:
        role = "before_move"
    elif delta > 0:
        role = "after_move"
    else:
        role = "same_day"
    row = {
        "relative_day": delta,
        "date": event_date.isoformat(),
        "evidence_role": role,
        "source_type": source_type,
        "title": str(title or "").strip(),
        "url": url,
        "metadata": metadata,
    }
    if excerpt:
        row["excerpt"] = str(excerpt)
    return row


def _normalize_ohlcv_row(row: dict[str, Any]) -> dict[str, Any] | None:
    row_date = parse_date(row.get("date"))
    close = _number(row.get("adjusted_close") if row.get("adjusted_close") is not None else row.get("close"))
    if row_date is None or close is None:
        return None
    return {
        "date": row_date.isoformat(),
        "close": close,
        "volume": _number(row.get("volume")),
        "source": row.get("source"),
    }


def _daily_returns(rows: list[dict[str, Any]]) -> list[float]:
    returns: list[float] = []
    for index in range(1, len(rows)):
        previous = rows[index - 1]["close"]
        current = rows[index]["close"]
        if previous in (None, 0) or current is None:
            returns.append(0.0)
        else:
            returns.append(((current / previous) - 1.0) * 100.0)
    return returns


def _number(value: Any) -> float | None:
    try:
        if value is None or value != value:
            return None
        return float(value)
    except Exception:
        return None


def _average(values: Any) -> float | None:
    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def _safe_ratio(numerator: Any, denominator: Any) -> float | None:
    top = _number(numerator)
    bottom = _number(denominator)
    if top is None or bottom in (None, 0):
        return None
    return round(top / bottom, 2)


def _round_number(value: Any) -> float | int | None:
    number = _number(value)
    if number is None:
        return None
    rounded = round(number, 4)
    return int(rounded) if rounded.is_integer() else rounded
