"""Nasdaq issue breadth from the exchange's public annual CSV files."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from io import StringIO
from typing import Any

import httpx

from finance_cli.core.common import utc_now
from finance_cli.providers.base import ProviderError


def fetch_breadth(market: str = "NASDAQ", *, year: int | None = None, limit: int = 20, timeout: float = 30.0) -> dict[str, Any]:
    market = market.strip().upper()
    if market != "NASDAQ":
        raise ProviderError("market.breadth currently supports NASDAQ only")
    today = datetime.now(timezone.utc).date()
    year = today.year if year is None else year
    if not 2006 <= year <= today.year:
        raise ProviderError(f"year must be between 2006 and {today.year}")
    if not 1 <= limit <= 366:
        raise ProviderError("limit must be between 1 and 366")
    url = f"https://nasdaqtrader.com/dynamic/dailyfiles/daily{year}.txt"
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ProviderError(f"Nasdaq breadth request failed: {exc}") from exc
    reader = csv.DictReader(StringIO(response.text.lstrip("\ufeff")))
    if not {"Date", "Advances", "Declines", "Unchanged"}.issubset(reader.fieldnames or []):
        raise ProviderError("Nasdaq breadth file is missing required columns")
    rows, missing_dates = [], []
    try:
        for raw in reader:
            day = datetime.strptime(raw["Date"].split()[0], "%m/%d/%Y").date()
            if day.year != year or day > today:
                raise ValueError("unexpected observation date")
            if any(raw[key] in {None, ""} for key in ("Advances", "Declines", "Unchanged")):
                missing_dates.append(day.isoformat())
                continue
            counts = [float(raw[key]) for key in ("Advances", "Declines", "Unchanged")]
            if any(value < 0 or not value.is_integer() for value in counts):
                raise ValueError("invalid issue count")
            advances, declines, unchanged = map(int, counts)
            rows.append({
                "date": day.isoformat(), "period": day.isoformat(),
                "advances": advances, "declines": declines, "unchanged": unchanged,
                "net_advances": advances - declines,
                "advance_decline_ratio": advances / declines if declines else None,
                "total_issues": advances + declines + unchanged, "source_url": url,
            })
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise ProviderError(f"Invalid Nasdaq breadth row: {exc}") from exc
    if not rows:
        raise ProviderError(f"Nasdaq breadth file contains no observations for {year}")
    rows.sort(key=lambda row: row["date"], reverse=True)
    latest = rows[0]["date"]
    age = (today - datetime.strptime(latest, "%Y-%m-%d").date()).days
    warnings = ["Nasdaq-listed issue counts only; excludes NYSE and does not provide moving-average or new-high/new-low breadth."]
    if missing_dates:
        warnings.append("Some file dates omit breadth counts and were excluded; see missing_dates. Missing counts are not zero.")
    if year == today.year and age > 4:
        warnings.append(f"Latest source observation is {latest}, {age} calendar days before retrieval; this is not live breadth.")
    return {
        "market": market, "year": year, "source": "nasdaq", "source_url": url,
        "scope": "Nasdaq-listed issues, across trading venues", "as_of": latest,
        "latest_date": latest, "age_calendar_days": age, "retrieved_at": utc_now(),
        "rows": rows[:limit], "count": min(len(rows), limit),
        "available_count": len(rows), "missing_dates": sorted(missing_dates, reverse=True), "warnings": warnings,
    }
