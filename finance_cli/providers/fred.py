"""Bounded FRED searches and vintage-aware economic observations."""
from __future__ import annotations

from datetime import date
import math
import os
import re
from typing import Any

import httpx

from finance_cli.core.common import utc_now
from finance_cli.providers.base import ProviderError


class FREDProvider:
    BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(self, *, api_key: str | None = None, timeout: float = 20.0) -> None:
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        self.timeout = timeout

    def search(self, query: str, *, limit: int = 20) -> dict[str, Any]:
        if not query.strip():
            raise ProviderError("query is required")
        _limit(limit, 1000)
        payload = self._request("series/search", {"search_text": query, "limit": limit})
        rows = [_metadata(row) for row in _rows(payload, "seriess")]
        return self._result(rows, payload, entity=query, query=query)

    def series(
        self, series_id: str, *, start: str | None = None, end: str | None = None,
        as_of: str | None = None, limit: int = 1000,
    ) -> dict[str, Any]:
        series_id = series_id.strip().upper()
        if not re.fullmatch(r"[A-Z0-9_.-]+", series_id):
            raise ProviderError("series_id must be a FRED series identifier")
        _limit(limit, 100000)
        for value in (start, end, as_of):
            if value is not None:
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                        raise ValueError("invalid date format")
                    date.fromisoformat(value)
                except ValueError as exc:
                    raise ProviderError("start, end and as_of must use YYYY-MM-DD") from exc
        if start and end and start > end:
            raise ProviderError("start must be on or before end")
        params: dict[str, Any] = {"series_id": series_id}
        if as_of:
            params.update(realtime_start=as_of, realtime_end=as_of)
        metadata_rows = _rows(self._request("series", params), "seriess")
        if not metadata_rows:
            raise ProviderError(f"FRED series metadata not found for {series_id}")
        metadata = _metadata(metadata_rows[0])
        if len(metadata_rows) != 1 or metadata["series_id"] != series_id:
            raise ProviderError("FRED metadata does not match the requested series")
        params.update(limit=limit, sort_order="desc", offset=0)
        if start:
            params["observation_start"] = start
        if end:
            params["observation_end"] = end
        payload = self._request("series/observations", params)
        rows = []
        for row in _rows(payload, "observations"):
            try:
                if not isinstance(row.get("date"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["date"]):
                    raise ValueError("missing observation date")
                date.fromisoformat(row["date"])
                value = _number(row["value"])
            except (KeyError, TypeError, ValueError):
                raise ProviderError("FRED returned an invalid observation date or value") from None
            rows.append({
                "series_id": series_id, "period": row["date"], "value": value,
                "units": metadata.get("units"), "frequency": metadata.get("frequency"),
                "realtime_start": row.get("realtime_start"), "realtime_end": row.get("realtime_end"),
                "source_url": metadata["source_url"],
            })
        rows.sort(key=lambda row: row["period"] or "")
        return self._result(
            rows, payload, entity=series_id, series_id=series_id, metadata=metadata,
            as_of=as_of, realtime_start=payload.get("realtime_start"),
            realtime_end=payload.get("realtime_end"), start=start, end=end,
        )

    def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise ProviderError("FRED API key is required. Set FRED_API_KEY.")
        try:
            response = httpx.get(f"{self.BASE_URL}/{endpoint}",
                                 params={**params, "api_key": self.api_key, "file_type": "json"},
                                 timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"FRED request failed (HTTP {exc.response.status_code})") from None
        except (httpx.RequestError, ValueError):
            raise ProviderError("FRED request failed or returned invalid JSON") from None
        if not isinstance(payload, dict) or payload.get("error_code"):
            raise ProviderError("FRED API returned an error or unexpected payload")
        return payload

    def _result(self, rows: list[dict[str, Any]], payload: dict[str, Any], **context: Any) -> dict[str, Any]:
        total = int(payload.get("count", len(rows)))
        return {**context, "rows": rows, "count": len(rows), "total_available": total,
                "truncated": total > len(rows), "source": "fred",
                "source_url": "https://fred.stlouisfed.org/", "retrieved_at": utc_now(),
                "warnings": ["Only the requested limit is returned."] if total > len(rows) else []}


def _metadata(row: dict[str, Any]) -> dict[str, Any]:
    if (not isinstance(row.get("id"), str) or not re.fullmatch(r"[A-Z0-9_.-]+", row["id"])
            or any(not isinstance(row.get(key), str) or not row[key].strip() for key in ("units", "frequency"))):
        raise ProviderError("FRED returned invalid series identity, units or frequency metadata")
    return {**row, "series_id": row.get("id"),
            "source_url": f"https://fred.stlouisfed.org/series/{row.get('id', '')}"}


def _number(value: Any) -> float | None:
    if value in (None, "."):
        return None
    if isinstance(value, bool):
        raise ValueError("invalid observation value")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite observation value")
    return number


def _rows(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    rows = payload.get(key)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ProviderError(f"FRED returned an unexpected {key} payload")
    return rows


def _limit(limit: int, maximum: int) -> None:
    if not 1 <= limit <= maximum:
        raise ProviderError(f"limit must be between 1 and {maximum}")
