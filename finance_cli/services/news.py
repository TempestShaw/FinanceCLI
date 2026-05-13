"""News services."""
from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from typing import Any

from finance_cli.core.common import parse_date, parse_window
from finance_cli.providers.gdelt import GdeltNewsProvider
from finance_cli.services.symbols import fetch_symbol_profile


def search_news(
    *,
    query: str | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    max_records: int = 50,
    timespan: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    provider: GdeltNewsProvider | None = None,
) -> dict[str, Any]:
    """Search finance-relevant news via a provider."""
    timespan = normalize_news_timespan(timespan)
    start_datetime, end_datetime = resolve_gdelt_date_range(
        date=date,
        start_date=start_date,
        end_date=end_date,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )
    client = provider or GdeltNewsProvider(max_records=max_records, timespan=timespan or "1d")
    if symbol:
        articles = client.search(
            symbol_news_query(symbol),
            max_records=max_records,
            timespan=timespan,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        scope = {"type": "symbol", "value": symbol.upper()}
    elif sector:
        articles = client.search(
            client.SECTOR_QUERY_EXPANSIONS.get(sector.upper(), sector),
            max_records=max_records,
            timespan=timespan,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        scope = {"type": "sector", "value": sector}
    elif query:
        articles = client.search(
            query,
            max_records=max_records,
            timespan=timespan,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        scope = {"type": "query", "value": query}
    else:
        raise ValueError("one of query=, symbol=, or sector= is required")
    return {"scope": scope, "articles": articles, "count": len(articles), "source": "gdelt"}


def gdelt_doc_mode(
    *,
    mode: str,
    query: str | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    max_records: int = 50,
    timespan: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    timeline_smooth: int | None = None,
    provider: GdeltNewsProvider | None = None,
) -> dict[str, Any]:
    """Run any supported GDELT DOC 2.0 JSON mode."""
    timespan = normalize_news_timespan(timespan)
    start_datetime, end_datetime = resolve_gdelt_date_range(
        date=date,
        start_date=start_date,
        end_date=end_date,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )
    client = provider or GdeltNewsProvider(max_records=max_records, timespan=timespan or "1d")
    scope, gdelt_query = _resolve_gdelt_query(client, query=query, symbol=symbol, sector=sector)
    payload = client.doc_mode(
        gdelt_query,
        mode=mode,
        max_records=max_records,
        timespan=timespan,
        timeline_smooth=timeline_smooth,
        extra_params=_date_range_params(start_datetime=start_datetime, end_datetime=end_datetime),
    )
    return {"scope": scope, "mode": mode, "payload": payload, "source": "gdelt_doc"}


def news_timeline(
    *,
    query: str | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    mode: str = "timelinevolraw",
    timespan: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    timeline_smooth: int | None = None,
    provider: GdeltNewsProvider | None = None,
) -> dict[str, Any]:
    """Fetch GDELT DOC timeline data for a finance news query."""
    timespan = normalize_news_timespan(timespan)
    start_datetime, end_datetime = resolve_gdelt_date_range(
        date=date,
        start_date=start_date,
        end_date=end_date,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )
    client = provider or GdeltNewsProvider(timespan=timespan or "1d")
    scope, gdelt_query = _resolve_gdelt_query(client, query=query, symbol=symbol, sector=sector)
    payload = client.doc_mode(
        gdelt_query,
        mode=mode,
        timespan=timespan,
        timeline_smooth=timeline_smooth,
        extra_params=_date_range_params(start_datetime=start_datetime, end_datetime=end_datetime),
    )
    return {"scope": scope, "mode": mode, "payload": payload, "source": "gdelt_doc"}


def news_tone(
    *,
    query: str | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    mode: str = "tonechart",
    timespan: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    timeline_smooth: int | None = None,
    provider: GdeltNewsProvider | None = None,
) -> dict[str, Any]:
    """Fetch GDELT DOC tone data for a finance news query."""
    timespan = normalize_news_timespan(timespan)
    start_datetime, end_datetime = resolve_gdelt_date_range(
        date=date,
        start_date=start_date,
        end_date=end_date,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )
    client = provider or GdeltNewsProvider(timespan=timespan or "1d")
    scope, gdelt_query = _resolve_gdelt_query(client, query=query, symbol=symbol, sector=sector)
    payload = client.doc_mode(
        gdelt_query,
        mode=mode,
        timespan=timespan,
        timeline_smooth=timeline_smooth,
        extra_params=_date_range_params(start_datetime=start_datetime, end_datetime=end_datetime),
    )
    return {"scope": scope, "mode": mode, "payload": payload, "source": "gdelt_doc"}


def news_context(
    *,
    query: str | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    max_records: int = 50,
    timespan: str | None = "24h",
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    is_quote: bool = False,
    provider: GdeltNewsProvider | None = None,
) -> dict[str, Any]:
    """Fetch sentence-level GDELT Context 2.0 snippets."""
    timespan = normalize_news_timespan(timespan)
    start_datetime, end_datetime = resolve_gdelt_date_range(
        date=date,
        start_date=start_date,
        end_date=end_date,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )
    client = provider or GdeltNewsProvider(max_records=max_records)
    scope, gdelt_query = _resolve_gdelt_query(client, query=query, symbol=symbol, sector=sector)
    payload = client.context(
        gdelt_query,
        max_records=max_records,
        timespan=timespan,
        is_quote=is_quote,
        extra_params=_date_range_params(start_datetime=start_datetime, end_datetime=end_datetime),
    )
    rows = payload.get("articles") or []
    count = len(rows) if isinstance(rows, list) else None
    return {"scope": scope, "payload": payload, "count": count, "source": "gdelt_context"}


def news_geo(
    *,
    query: str | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    mode: str = "article",
    timespan: str | None = "1d",
    max_points: int | None = None,
    provider: GdeltNewsProvider | None = None,
) -> dict[str, Any]:
    """Fetch GDELT GKG GeoJSON for a finance news query."""
    timespan = normalize_news_timespan(timespan)
    client = provider or GdeltNewsProvider()
    scope, gdelt_query = _resolve_gdelt_query(client, query=query, symbol=symbol, sector=sector)
    geo_query = _to_gkg_geo_query(gdelt_query)
    payload = client.geo(geo_query, mode=mode, timespan=timespan, max_points=max_points)
    features = payload.get("features") or []
    count = len(features) if isinstance(features, list) else None
    return {
        "scope": scope,
        "mode": mode,
        "payload": payload,
        "count": count,
        "source": "gdelt_geo",
    }


def analyze_news(
    *,
    analysis: str = "timeline",
    query: str | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    mode: str | None = None,
    max_records: int = 50,
    timespan: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    provider: GdeltNewsProvider | None = None,
) -> dict[str, Any]:
    """One high-level entry point for non-article GDELT analysis modes."""
    timespan = normalize_news_timespan(timespan)
    normalized = analysis.replace("_", "").replace("-", "").lower()
    if normalized in {"timeline", "volume", "trend", "trends"}:
        return news_timeline(
            query=query,
            symbol=symbol,
            sector=sector,
            mode=mode or "timelinevolraw",
            timespan=timespan,
            date=date,
            start_date=start_date,
            end_date=end_date,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            provider=provider,
        )
    if normalized in {"tone", "sentiment"}:
        return news_tone(
            query=query,
            symbol=symbol,
            sector=sector,
            mode=mode or "tonechart",
            timespan=timespan,
            date=date,
            start_date=start_date,
            end_date=end_date,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            provider=provider,
        )
    if normalized in {"context", "snippet", "snippets"}:
        return news_context(
            query=query,
            symbol=symbol,
            sector=sector,
            max_records=max_records,
            timespan=timespan or "24h",
            date=date,
            start_date=start_date,
            end_date=end_date,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            provider=provider,
        )
    if normalized in {"geo", "geography", "map"}:
        return news_geo(
            query=query,
            symbol=symbol,
            sector=sector,
            mode=mode or "article",
            timespan=timespan or "1d",
            max_points=max_records,
            provider=provider,
        )
    if normalized in {"doc", "gdelt", "raw"}:
        return gdelt_doc_mode(
            query=query,
            symbol=symbol,
            sector=sector,
            mode=mode or "timelinevolraw",
            max_records=max_records,
            timespan=timespan,
            date=date,
            start_date=start_date,
            end_date=end_date,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            provider=provider,
        )
    raise ValueError("analysis must be one of timeline, tone, context, geo, or doc")


def _resolve_gdelt_query(
    client: GdeltNewsProvider,
    *,
    query: str | None = None,
    symbol: str | None = None,
    sector: str | None = None,
) -> tuple[dict[str, str], str]:
    if symbol:
        normalized = symbol.upper()
        return {"type": "symbol", "value": normalized}, symbol_news_query(normalized)
    if sector:
        return {"type": "sector", "value": sector}, client.SECTOR_QUERY_EXPANSIONS.get(sector.upper(), sector)
    if query:
        return {"type": "query", "value": query}, query
    raise ValueError("one of query=, symbol=, or sector= is required")


def symbol_news_query(symbol: str) -> str:
    """Build a deterministic company-name news query for a ticker."""
    normalized = symbol.strip().upper()
    try:
        profile = fetch_symbol_profile(normalized)
        company_name = str(profile.get("company_name") or "").strip()
        cleaned = _clean_company_name(company_name)
        if cleaned and "Unknown Company" not in cleaned:
            return f'"{cleaned}"'
    except Exception:
        pass
    if len(normalized) <= 3:
        raise ValueError("news query needs company_name for short tickers")
    return f'"{normalized}" stock'


def _clean_company_name(company_name: str) -> str:
    suffixes = (
        " Corporation",
        " Corp.",
        " Corp",
        " Incorporated",
        " Inc.",
        " Inc",
        " Limited",
        " Ltd.",
        " Ltd",
        " PLC",
        " plc",
    )
    cleaned = company_name.strip()
    for suffix in suffixes:
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)].strip()
            break
    return cleaned


def _to_gkg_geo_query(query: str) -> str:
    """Convert a DOC-style query into a GKG GeoJSON-friendly query."""
    converted = query.replace('"', "").replace("(", "").replace(")", "")
    converted = converted.replace(" OR ", ",")
    return ",".join(part.strip() for part in converted.split(",") if part.strip())


def _date_range_params(*, start_datetime: str | None, end_datetime: str | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if start_datetime:
        params["startdatetime"] = start_datetime
    if end_datetime:
        params["enddatetime"] = end_datetime
    return params


def normalize_news_timespan(value: str | None) -> str | None:
    """Normalize human-friendly relative lookbacks for GDELT."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    compact = text.replace(" ", "").replace("_", "").lower()
    aliases = {
        "today": "1d",
        "yesterday": "1d",
        "day": "1d",
        "week": "1w",
        "month": "1m",
    }
    if compact in aliases:
        return aliases[compact]

    index = 0
    while index < len(compact) and compact[index].isdigit():
        index += 1
    if index == 0:
        return compact
    amount = int(compact[:index])
    unit = compact[index:] or "d"
    unit_aliases = {
        "minute": "min",
        "minutes": "min",
        "mins": "min",
        "min": "min",
        "h": "h",
        "hr": "h",
        "hrs": "h",
        "hour": "h",
        "hours": "h",
        "d": "d",
        "day": "d",
        "days": "d",
        "w": "w",
        "wk": "w",
        "wks": "w",
        "week": "w",
        "weeks": "w",
        "m": "m",
        "mo": "m",
        "mon": "m",
        "month": "m",
        "months": "m",
    }
    return f"{amount}{unit_aliases.get(unit, unit)}"


def resolve_gdelt_date_range(
    *,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
) -> tuple[str | None, str | None]:
    """Normalize human-friendly date inputs to GDELT YYYYMMDDHHMMSS values."""
    if date:
        day = parse_date(date)
        if day is None:
            raise ValueError(f"invalid date: {date}")
        return _format_gdelt_datetime(day, end_of_day=False), _format_gdelt_datetime(day, end_of_day=True)
    start = _normalize_gdelt_datetime(start_datetime, end_of_day=False) if start_datetime else None
    end = _normalize_gdelt_datetime(end_datetime, end_of_day=True) if end_datetime else None
    if start_date:
        sd = parse_date(start_date)
        if sd is None:
            raise ValueError(f"invalid start_date: {start_date}")
        start = _format_gdelt_datetime(sd, end_of_day=False)
    if end_date:
        ed = parse_date(end_date)
        if ed is None:
            raise ValueError(f"invalid end_date: {end_date}")
        end = _format_gdelt_datetime(ed, end_of_day=True)
    return start, end


def _normalize_gdelt_datetime(value: str, *, end_of_day: bool) -> str:
    text = value.strip()
    if len(text) == 8 and text.isdigit():
        parsed = datetime.strptime(text, "%Y%m%d").date()
        return _format_gdelt_datetime(parsed, end_of_day=end_of_day)
    if len(text) == 14 and text.isdigit():
        return text
    if "T" in text:
        try:
            parsed_datetime = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return parsed_datetime.strftime("%Y%m%d%H%M%S")
        except ValueError:
            pass
    parsed_date = parse_date(text)
    if parsed_date is None:
        raise ValueError(f"invalid datetime: {value}")
    return _format_gdelt_datetime(parsed_date, end_of_day=end_of_day)


def _format_gdelt_datetime(value: date_type, *, end_of_day: bool) -> str:
    suffix = "235959" if end_of_day else "000000"
    return value.strftime("%Y%m%d") + suffix
