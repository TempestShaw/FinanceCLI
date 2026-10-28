"""Taiwan Stock Exchange public issuer snapshots."""
from __future__ import annotations

from datetime import date, datetime, timezone
import re
from typing import Any

import httpx

from finance_cli.providers.base import ProviderError


BASE_URL = "https://openapi.twse.com.tw/v1/opendata"


class TWSEProvider:
    """Read official listed-company snapshots without credentials."""

    name = "twse"

    def __init__(self, *, timeout: float = 30.0) -> None:
        self.timeout = timeout

    def monthly_revenue(self, symbol: str) -> dict[str, Any]:
        code, normalized = _symbol(symbol)
        source_url = f"{BASE_URL}/t187ap05_L"
        retrieved_at = datetime.now(timezone.utc).isoformat()
        rows = []
        for row in self._snapshot(source_url):
            if row.get("公司代號") != code:
                continue
            rows.append({
                "symbol": normalized,
                "company_name": row.get("公司名稱"),
                "period": _roc_date(row.get("資料年月"), monthly=True),
                "date": _roc_date(row.get("出表日期")),
                "date_kind": "snapshot_generated_date",
                "revenue": _number(row.get("營業收入-當月營收")),
                "previous_month_revenue": _number(row.get("營業收入-上月營收")),
                "previous_year_revenue": _number(row.get("營業收入-去年當月營收")),
                "mom_pct": _number(row.get("營業收入-上月比較增減(%)")),
                "yoy_pct": _number(row.get("營業收入-去年同月增減(%)")),
                "ytd_revenue": _number(row.get("累計營業收入-當月累計營收")),
                "previous_year_ytd_revenue": _number(row.get("累計營業收入-去年累計營收")),
                "ytd_yoy_pct": _number(row.get("累計營業收入-前期比較增減(%)")),
                "currency": "TWD",
                "unit": "TWD_thousands",
                "notes": row.get("備註") or None,
                "source_url": source_url,
                "retrieved_at": retrieved_at,
            })
        return self._result(normalized, source_url, rows, retrieved_at, [
            "Latest published snapshot only; this endpoint does not provide a queryable monthly history.",
            "Amounts are in thousands of TWD; percentage values use 10 for 10%, not 0.10.",
            "The snapshot generation date is not the issuer's original announcement time.",
        ])

    def recent_disclosures(self, symbol: str, *, limit: int = 20) -> dict[str, Any]:
        code, normalized = _symbol(symbol)
        if limit < 1:
            raise ProviderError("limit must be positive")
        source_url = f"{BASE_URL}/t187ap04_L"
        retrieved_at = datetime.now(timezone.utc).isoformat()
        rows = []
        for row in self._snapshot(source_url):
            if row.get("公司代號") != code:
                continue
            published_date = _roc_date(row.get("發言日期"))
            published_time = str(row.get("發言時間") or "").strip()
            rows.append({
                "symbol": normalized,
                "company_name": row.get("公司名稱"),
                "date": published_date,
                "timestamp": f"{published_date}T{published_time}+08:00" if published_date and re.fullmatch(r"\d{2}:\d{2}:\d{2}", published_time) else published_date,
                "time": published_time or None,
                "timezone": "Asia/Taipei",
                "event_date": _roc_date(row.get("事實發生日")),
                "snapshot_generated_date": _roc_date(row.get("出表日期")),
                "title": row.get("主旨"),
                "text": row.get("說明"),
                "clause": row.get("符合條款"),
                "source_url": source_url,
                "retrieved_at": retrieved_at,
            })
        rows.sort(key=lambda row: (row["date"] or "", row["time"] or ""), reverse=True)
        return self._result(normalized, source_url, rows[:limit], retrieved_at, [
            "Daily listed-company snapshot only; an empty result does not establish that no earlier disclosures exist.",
            "source_url identifies the official dataset; the dataset does not supply individual announcement URLs.",
        ])

    def _snapshot(self, url: str) -> list[dict[str, Any]]:
        try:
            response = httpx.get(url, timeout=self.timeout, follow_redirects=True)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"TWSE snapshot request failed: {exc}") from exc
        if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
            raise ProviderError("TWSE returned an unexpected snapshot format")
        return [{str(key).strip(): value for key, value in row.items()} for row in data]

    @staticmethod
    def _result(symbol: str, url: str, rows: list[dict[str, Any]], retrieved_at: str, warnings: list[str]) -> dict[str, Any]:
        if not rows:
            warnings.append("No matching issuer rows in the current snapshot; TWSE-listed companies only, excluding TPEx.")
        return {"symbol": symbol, "source": "twse", "source_url": url, "rows": rows,
                "count": len(rows), "retrieved_at": retrieved_at, "warnings": warnings}


def _symbol(symbol: str) -> tuple[str, str]:
    code = symbol.strip().upper().removesuffix(".TW")
    if not re.fullmatch(r"\d{4,6}", code):
        raise ProviderError("TWSE symbol must be a listed-company code such as 2330 or 2330.TW")
    return code, f"{code}.TW"


def _roc_date(value: Any, *, monthly: bool = False) -> str | None:
    if value is None or not str(value).strip():
        return None
    text = str(value).strip()
    parts = re.split(r"[/.-]", text)
    if len(parts) == 1:
        year_length = len(text) - (2 if monthly else 4)
        parts = [text[:year_length], text[year_length:year_length + 2]]
        if not monthly:
            parts.append(text[-2:])
    try:
        year, month = int(parts[0]), int(parts[1])
        year = year + 1911 if year < 1911 else year
        parsed = date(year, month, 1 if monthly else int(parts[2]))
    except (ValueError, IndexError) as exc:
        raise ProviderError(f"Invalid TWSE date: {value}") from exc
    return parsed.strftime("%Y-%m" if monthly else "%Y-%m-%d")


def _number(value: Any) -> int | float | None:
    text = str(value if value is not None else "").strip().replace(",", "")
    if text in {"", "-", "--", "N/A"}:
        return None
    try:
        return float(text) if "." in text else int(text)
    except ValueError as exc:
        raise ProviderError(f"Invalid TWSE numeric value: {value}") from exc
