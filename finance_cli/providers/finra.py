"""FINRA short positions and daily off-exchange short-sale activity."""
from __future__ import annotations

import csv
import math
import os
import re
from datetime import datetime, timedelta
from io import StringIO
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from finance_cli.core.common import utc_now
from finance_cli.providers.base import ProviderError


SHORT_INTEREST_URL = "https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"
DAILY_FILE_URL = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{date}.txt"


def _symbol(value: str) -> str:
    symbol = value.strip().upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9.\-/^]{0,19}", symbol):
        raise ProviderError("a valid FINRA symbol is required")
    return symbol


def _number(value: Any) -> int | float | None:
    if value is None or value == "":
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite numeric field")
    return int(number) if number.is_integer() else number


def fetch_short_interest(symbol: str, *, periods: int = 6, timeout: float = 30.0) -> dict[str, Any]:
    symbol = _symbol(symbol)
    if not 1 <= periods <= 500:
        raise ProviderError("periods must be between 1 and 500")
    headers = {"Accept": "application/json"}
    token = os.getenv("FINRA_ACCESS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    # Sorting requires FINRA partition filters; one symbol's history fits in one bounded response.
    payload = {"limit": 5000, "compareFilters": [
        {"compareType": "equal", "fieldName": "symbolCode", "fieldValue": symbol},
    ]}
    try:
        response = httpx.post(SHORT_INTEREST_URL, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        raise ProviderError(f"FINRA short-interest request failed (HTTP {exc.response.status_code}); access may require FINRA_ACCESS_TOKEN") from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise ProviderError("FINRA short-interest request failed or returned invalid JSON") from exc
    if not isinstance(data, list) or len(data) >= 5000:
        raise ProviderError("FINRA short-interest response is invalid or reaches the 5,000-row bound; latest coverage cannot be established")
    rows = []
    try:
        for raw in data:
            if raw["symbolCode"] != symbol:
                raise ValueError("response symbol differs from requested symbol")
            day = datetime.strptime(raw["settlementDate"], "%Y-%m-%d").date().isoformat()
            current = _number(raw["currentShortPositionQuantity"])
            if current is None or current < 0:
                raise ValueError("missing or negative short position")
            rows.append({
                "symbol": symbol, "settlement_date": day, "period": day,
                "company_name": raw.get("issueName"), "market_class": raw.get("marketClassCode"),
                "short_interest": current,
                "previous_short_interest": _number(raw.get("previousShortPositionQuantity")),
                "change_shares": _number(raw.get("changePreviousNumber")),
                "change_pct": _number(raw.get("changePercent")),
                "average_daily_volume": _number(raw.get("averageDailyVolumeQuantity")),
                "days_to_cover": _number(raw.get("daysToCoverQuantity")),
                "stock_split_flag": raw.get("stockSplitFlag"), "revision_flag": raw.get("revisionFlag"),
                "source_url": SHORT_INTEREST_URL,
            })
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise ProviderError(f"Invalid FINRA short-interest row: {exc}") from exc
    rows.sort(key=lambda row: row["settlement_date"], reverse=True)
    warnings = [
        "Settlement dates are position snapshot dates, not publication dates. FINRA normally publishes on the seventh business day after settlement; publication timestamps are not supplied here.",
        "Short interest is outstanding positions, not daily short-sale volume. Symbol changes and corporate actions can affect comparisons.",
    ]
    if not rows:
        warnings.append(f"FINRA returned no short-interest observations for {symbol}.")
    age = (_today() - datetime.strptime(rows[0]["settlement_date"], "%Y-%m-%d").date()).days if rows else None
    if age is not None and age > 45:
        warnings.append(f"Latest settlement snapshot is {age} calendar days old; a current position cannot be inferred.")
    return {
        "symbol": symbol, "source": "finra", "dataset": "consolidatedShortInterest",
        "source_url": SHORT_INTEREST_URL, "retrieved_at": utc_now(),
        "as_of": rows[0]["settlement_date"] if rows else None, "age_calendar_days": age,
        "rows": rows[:periods], "count": min(len(rows), periods),
        "available_count": len(rows), "warnings": warnings,
    }


def _today():
    return datetime.now(ZoneInfo("America/New_York")).date()


def fetch_short_volume(symbol: str, *, days: int = 20, timeout: float = 15.0) -> dict[str, Any]:
    symbol = _symbol(symbol)
    if not 1 <= days <= 60:
        raise ProviderError("days must be between 1 and 60")
    day = _today()
    dates = []
    while len(dates) < days:
        day -= timedelta(days=1)
        if day.weekday() < 5:
            dates.append(day)
    rows, unavailable, no_symbol_dates = [], [], []
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        for day in dates:
            url = DAILY_FILE_URL.format(date=day.strftime("%Y%m%d"))
            try:
                response = client.get(url)
                if response.status_code in {403, 404}:
                    unavailable.append({"date": day.isoformat(), "status": response.status_code, "url": url})
                    continue
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise ProviderError(f"FINRA short-volume file request failed for {day.isoformat()}: {exc}") from exc
            reader = csv.DictReader(StringIO(response.text), delimiter="|")
            required = {"Date", "Symbol", "ShortVolume", "ShortExemptVolume", "TotalVolume", "Market"}
            if not required.issubset(reader.fieldnames or []):
                raise ProviderError(f"FINRA short-volume file has invalid columns for {day.isoformat()}")
            found = False
            try:
                for raw in reader:
                    if raw.get("Symbol") != symbol:
                        continue
                    if raw["Date"] != day.strftime("%Y%m%d"):
                        raise ValueError("file date differs from observation date")
                    short = _number(raw["ShortVolume"])
                    exempt = _number(raw["ShortExemptVolume"])
                    total = _number(raw["TotalVolume"])
                    if any(value is None or value < 0 for value in (short, exempt, total)):
                        raise ValueError("missing or negative volume")
                    rows.append({
                        "symbol": symbol, "trade_date": day.isoformat(), "period": day.isoformat(),
                        "short_volume": short, "short_exempt_volume": exempt, "total_volume": total,
                        "short_volume_pct": short / total * 100 if total else None,
                        "reporting_markets": raw["Market"], "source_url": url,
                    })
                    found = True
            except (ValueError, TypeError, KeyError) as exc:
                raise ProviderError(f"Invalid FINRA short-volume row for {day.isoformat()}: {exc}") from exc
            if not found:
                no_symbol_dates.append(day.isoformat())
    if len(unavailable) == days:
        raise ProviderError(f"All {days} FINRA short-volume files were unavailable (HTTP 403/404); no coverage can be established")
    warnings = [
        "CNMS consolidated off-exchange NMS activity only; exchange trades and non-publicly disseminated trades are excluded. This is not total US market volume.",
        "Daily short-sale volume is trading activity, not outstanding short interest. short_volume_pct is ShortVolume / TotalVolume * 100 within this file only.",
        "days bounds prior weekday file requests, excluding today in New York; holidays and unavailable files are not replaced with older dates.",
    ]
    if unavailable:
        warnings.append(f"{len(unavailable)} requested files were unavailable (HTTP 403/404); see unavailable_files. These may reflect holidays, unpublished files, or access restrictions.")
    if no_symbol_dates:
        warnings.append("The symbol was absent from some downloaded files; see no_symbol_dates. Absence does not establish zero short volume.")
    return {
        "symbol": symbol, "source": "finra", "dataset": "CNMS daily short-sale volume",
        "scope": "FINRA consolidated off-exchange NMS reporting", "retrieved_at": utc_now(),
        "as_of": rows[0]["trade_date"] if rows else None, "requested_weekdays": days,
        "request_count": len(dates), "queried_dates": [day.isoformat() for day in dates],
        "unavailable_files": unavailable, "no_symbol_dates": no_symbol_dates,
        "rows": rows, "count": len(rows), "warnings": warnings,
    }
