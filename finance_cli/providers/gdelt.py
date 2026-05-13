"""GDELT news provider."""
from __future__ import annotations

import threading
import time
import re
from typing import Any

import httpx

from finance_cli.providers.base import ProviderError
from finance_cli.providers.config import (
    GDELT_GEO_MAX_TIMESPAN_MINUTES,
    GDELT_GEO_MIN_TIMESPAN_MINUTES,
    GDELT_GEO_MODE_ALIASES,
    GDELT_TIMESPAN_UNIT_MINUTES,
    SECTOR_QUERY_EXPANSIONS,
)


class GdeltNewsProvider:
    """Fetch global news/events directly from GDELT."""

    DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
    CONTEXT_API = "https://api.gdeltproject.org/api/v2/context/context"
    GEO2_API = "https://api.gdeltproject.org/api/v2/geo/geo"
    GKG_GEOJSON_API = "https://api.gdeltproject.org/api/v1/gkg_geojson"
    EVENT_API = "https://api.gdeltproject.org/api/v2/events/events"
    GKG_API = "https://api.gdeltproject.org/api/v2/gkg/gkg"
    USER_AGENT = "FinanceCLI/0.1 (+https://github.com/TempestShaw/FinanceCLI)"
    DOC_MODES = {
        "artgallery",
        "artlist",
        "imagecollageinfo",
        "imagegallery",
        "timelinevol",
        "timelinevolinfo",
        "timelinelang",
        "timelinesourcecountry",
        "timelinetone",
        "timelinevolraw",
        "tonechart",
        "wordcloudenglish",
        "wordcloudimagetags",
        "wordcloudimagewebtags",
    }
    TIMELINE_MODES = {
        "timelinevol",
        "timelinevolinfo",
        "timelinelang",
        "timelinesourcecountry",
        "timelinetone",
        "timelinevolraw",
    }
    TONE_MODES = {"timelinetone", "tonechart"}
    GEO_MODES = {"article", "locationtime"}
    SECTOR_QUERY_EXPANSIONS = SECTOR_QUERY_EXPANSIONS

    _rate_lock = threading.Lock()
    _last_request_at = 0.0

    def __init__(
        self,
        *,
        max_records: int = 50,
        timeout: float = 60.0,
        timespan: str | None = "1d",
        source_language: str | None = "english",
        min_interval_seconds: float = 6.0,
        retry_count: int = 1,
        retry_delay_seconds: float = 6.0,
    ) -> None:
        self.max_records = max_records
        self.timeout = timeout
        self.timespan = timespan
        self.source_language = source_language
        self.min_interval_seconds = min_interval_seconds
        self.retry_count = retry_count
        self.retry_delay_seconds = retry_delay_seconds

    def search(
        self,
        query: str,
        *,
        max_records: int | None = None,
        mode: str = "artlist",
        sort: str = "DateDesc",
        endpoint: str = "doc",
        timespan: str | None = None,
        start_datetime: str | None = None,
        end_datetime: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search GDELT articles/events and return normalized records."""
        extra_params = _date_range_params(start_datetime=start_datetime, end_datetime=end_datetime)
        if endpoint != "doc":
            payload = self._query_endpoint(
                endpoint=endpoint,
                query=query,
                mode=mode,
                max_records=max_records,
                sort=sort,
                timespan=timespan,
                apply_source_language=False,
                extra_params=extra_params,
            )
        else:
            payload = self.doc_mode(
                query,
                mode=mode,
                max_records=max_records,
                sort=sort,
                timespan=timespan,
                extra_params=extra_params,
            )

        rows = payload.get("articles") or payload.get("events") or []
        if not isinstance(rows, list):
            return []
        return [
            row for row in rows
            if isinstance(row, dict) and str(row.get("language", "English")).lower() == "english"
        ]

    def symbol_news(self, symbol: str, *, max_records: int | None = None) -> list[dict[str, Any]]:
        """Search English-language news mentions for a ticker string."""
        return self.search(f'"{symbol.upper()}" stock', max_records=max_records)

    def sector_news(self, sector: str, *, max_records: int | None = None) -> list[dict[str, Any]]:
        """Search a rough GDELT sector topic."""
        topic = self.SECTOR_QUERY_EXPANSIONS.get(sector.upper(), sector)
        return self.search(topic, max_records=max_records)

    def doc_mode(
        self,
        query: str,
        *,
        mode: str,
        max_records: int | None = None,
        sort: str = "DateDesc",
        timespan: str | None = None,
        timeline_smooth: int | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run a supported GDELT DOC 2.0 JSON mode and return its raw payload."""
        normalized_mode = self._normalize_mode(mode, self.DOC_MODES, "DOC")
        params = extra_params.copy() if extra_params else {}
        if timeline_smooth is not None:
            params["timelinesmooth"] = max(0, min(int(timeline_smooth), 30))
        return self._query_endpoint(
            endpoint="doc",
            query=query,
            mode=normalized_mode,
            max_records=max_records,
            sort=sort,
            timespan=timespan,
            apply_source_language=True,
            extra_params=params,
        )

    def timeline(
        self,
        query: str,
        *,
        mode: str = "timelinevolraw",
        timespan: str | None = None,
        timeline_smooth: int | None = None,
    ) -> dict[str, Any]:
        """Run a DOC timeline mode such as timelinevolraw or timelinetone."""
        normalized_mode = self._normalize_mode(mode, self.TIMELINE_MODES, "DOC timeline")
        return self.doc_mode(query, mode=normalized_mode, timespan=timespan, timeline_smooth=timeline_smooth)

    def tone(
        self,
        query: str,
        *,
        mode: str = "tonechart",
        timespan: str | None = None,
        timeline_smooth: int | None = None,
    ) -> dict[str, Any]:
        """Run a DOC tone mode such as tonechart or timelinetone."""
        normalized_mode = self._normalize_mode(mode, self.TONE_MODES, "DOC tone")
        return self.doc_mode(query, mode=normalized_mode, timespan=timespan, timeline_smooth=timeline_smooth)

    def context(
        self,
        query: str,
        *,
        max_records: int | None = None,
        timespan: str | None = "24h",
        sort: str = "DateDesc",
        is_quote: bool = False,
        search_language: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Search GDELT Context 2.0 sentence snippets."""
        params = extra_params.copy() if extra_params else {}
        if is_quote:
            params["isquote"] = 1
        if search_language:
            params["searchlang"] = search_language
        return self._query_endpoint(
            endpoint="context",
            query=query,
            mode="artlist",
            max_records=max_records,
            sort=sort,
            timespan=timespan,
            apply_source_language=False,
            extra_params=params,
        )

    def geo(
        self,
        query: str,
        *,
        mode: str = "article",
        timespan: str | None = "1d",
        max_points: int | None = None,
        geo_resolution: str | None = None,
    ) -> dict[str, Any]:
        """Search GDELT GKG GeoJSON and return georeferenced coverage."""
        normalized_mode = self._normalize_geo_mode(mode)
        extra_params: dict[str, Any] = {}
        if max_points is not None:
            extra_params["MAXROWS"] = max(1, int(max_points))
        if geo_resolution:
            extra_params["GEORES"] = geo_resolution
        params: dict[str, Any] = {
            "QUERY": query.strip(),
            "TIMESPAN": self._timespan_to_minutes(timespan or "60min"),
            "OUTPUTTYPE": 2 if normalized_mode == "locationtime" else 1,
            "OUTPUTFIELDS": "url,name,sharingimage,tone,lang,themes,names,domain",
        }
        params.update(extra_params)
        return self._request_json(self.GKG_GEOJSON_API, params)

    def _query_endpoint(
        self,
        *,
        endpoint: str,
        query: str,
        mode: str,
        format_value: str = "json",
        max_records: int | None = None,
        sort: str | None = None,
        timespan: str | None = None,
        apply_source_language: bool,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not query.strip():
            raise ProviderError("query is required")
        url = self._endpoint_url(endpoint)
        search_query = self._apply_source_language(query.strip()) if apply_source_language else query.strip()
        params: dict[str, Any] = {
            "query": search_query,
            "mode": mode,
            "format": format_value,
        }
        if max_records is not None or endpoint in {"doc", "context"}:
            params["maxrecords"] = self._normalize_max_records(max_records or self.max_records, endpoint=endpoint)
        if sort:
            params["sort"] = sort
        has_fixed_date_range = bool(
            extra_params
            and (extra_params.get("startdatetime") or extra_params.get("enddatetime"))
        )
        requested_timespan = (
            None
            if has_fixed_date_range
            else self.timespan if timespan is None and endpoint == "doc" else timespan
        )
        if requested_timespan:
            params["timespan"] = requested_timespan
        if extra_params:
            params.update(extra_params)
        return self._request_json(url, params)

    def _request_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.retry_count + 1):
            self._wait_for_rate_limit()
            try:
                response = httpx.get(
                    url,
                    params=params,
                    headers={"User-Agent": self.USER_AGENT},
                    timeout=self.timeout,
                    trust_env=False,
                )
                if response.status_code == 429:
                    raise ProviderError("GDELT rate limit returned HTTP 429")
                response.raise_for_status()
                return self._parse_json_response(response)
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError, ValueError, ProviderError) as exc:
                last_error = exc
                if attempt >= self.retry_count:
                    break
                time.sleep(self.retry_delay_seconds * (attempt + 1))
        raise ProviderError(f"GDELT request failed after retries: {last_error}") from last_error

    def _wait_for_rate_limit(self) -> None:
        if self.min_interval_seconds <= 0:
            return
        with self._rate_lock:
            elapsed = time.monotonic() - self.__class__._last_request_at
            wait_seconds = self.min_interval_seconds - elapsed
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            self.__class__._last_request_at = time.monotonic()

    @staticmethod
    def _parse_json_response(response: httpx.Response) -> dict[str, Any]:
        text = response.text
        if "rate limit" in text.lower():
            raise ProviderError(f"GDELT rate limit response: {text[:200]}")
        payload = response.json()
        if not isinstance(payload, dict):
            raise ProviderError("GDELT response was not a JSON object")
        return payload

    @staticmethod
    def _normalize_max_records(value: int, *, endpoint: str = "doc") -> int:
        max_allowed = 200 if endpoint == "context" else 250
        return max(1, min(int(value), max_allowed))

    def _apply_source_language(self, query: str) -> str:
        if not self.source_language or "sourcelang:" in query.lower():
            return query
        return f"{query} sourcelang:{self.source_language}"

    def _endpoint_url(self, endpoint: str) -> str:
        endpoints = {
            "context": self.CONTEXT_API,
            "doc": self.DOC_API,
            "events": self.EVENT_API,
            "geo": self.GEO2_API,
            "gkg": self.GKG_API,
            "gkg_geojson": self.GKG_GEOJSON_API,
        }
        if endpoint not in endpoints:
            raise ProviderError(f"Unsupported GDELT endpoint: {endpoint}")
        return endpoints[endpoint]

    @staticmethod
    def _normalize_mode(mode: str, allowed: set[str], label: str) -> str:
        normalized = mode.replace("_", "").lower()
        if normalized not in allowed:
            supported = ", ".join(sorted(allowed))
            raise ProviderError(f"Unsupported GDELT {label} mode '{mode}'. Supported: {supported}")
        return normalized

    @staticmethod
    def _normalize_geo_mode(mode: str) -> str:
        normalized = mode.replace("_", "").replace("-", "").lower()
        if normalized not in GDELT_GEO_MODE_ALIASES:
            supported = ", ".join(sorted(GDELT_GEO_MODE_ALIASES))
            raise ProviderError(f"Unsupported GDELT GeoJSON mode '{mode}'. Supported: {supported}")
        return GDELT_GEO_MODE_ALIASES[normalized]

    @staticmethod
    def _timespan_to_minutes(timespan: str) -> int:
        match = re.fullmatch(r"\s*(\d+)\s*([a-zA-Z]+)?\s*", timespan)
        if not match:
            supported = "15min, 1h, 24h, 1d"
            raise ProviderError(f"Unsupported GDELT GeoJSON timespan '{timespan}'. Use {supported}.")
        amount = int(match.group(1))
        unit = (match.group(2) or "min").lower()
        if unit not in GDELT_TIMESPAN_UNIT_MINUTES:
            supported_units = ", ".join(sorted(GDELT_TIMESPAN_UNIT_MINUTES))
            raise ProviderError(f"Unsupported GDELT timespan unit '{unit}'. Supported units: {supported_units}")
        minutes = amount * GDELT_TIMESPAN_UNIT_MINUTES[unit]
        return max(GDELT_GEO_MIN_TIMESPAN_MINUTES, min(minutes, GDELT_GEO_MAX_TIMESPAN_MINUTES))


def _date_range_params(*, start_datetime: str | None, end_datetime: str | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if start_datetime:
        params["startdatetime"] = start_datetime
    if end_datetime:
        params["enddatetime"] = end_datetime
    return params
