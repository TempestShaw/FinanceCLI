"""SEC filing event classification helpers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


SUPPORTED_FORMS = ("8-K", "4", "10-K", "10-Q", "13F-HR")


class FilingEventType(str, Enum):
    EARNINGS_RELEASE = "earnings_release"
    CEO_CFO_CHANGE = "ceo_cfo_change"
    MATERIAL_DISCLOSURE = "material_disclosure"
    MATERIAL_CONTRACT = "material_contract"
    BANKRUPTCY_DISTRESS = "bankruptcy_distress"
    BOARD_CHANGE = "board_change"
    FINANCIAL_REPORT = "financial_report"
    FINANCIAL_EXHIBITS = "financial_exhibits"
    OTHER_EVENT = "other_event"
    INSIDER_BUY = "insider_buy"
    INSIDER_SELL = "insider_sell"
    INSIDER_GIFT = "insider_gift"
    OPTION_EXERCISE = "option_exercise"
    ANNUAL_REPORT = "annual_report"
    QUARTERLY_REPORT = "quarterly_report"
    INSTITUTIONAL_HOLDINGS = "institutional_holdings"


_8K_ITEM_MAP: dict[str, FilingEventType] = {
    "2.02": FilingEventType.EARNINGS_RELEASE,
    "5.02": FilingEventType.CEO_CFO_CHANGE,
    "5.07": FilingEventType.BOARD_CHANGE,
    "7.01": FilingEventType.MATERIAL_DISCLOSURE,
    "8.01": FilingEventType.MATERIAL_DISCLOSURE,
    "1.01": FilingEventType.MATERIAL_CONTRACT,
    "1.02": FilingEventType.BANKRUPTCY_DISTRESS,
    "5.01": FilingEventType.BOARD_CHANGE,
    "4.01": FilingEventType.FINANCIAL_REPORT,
    "9.01": FilingEventType.FINANCIAL_EXHIBITS,
}


_ITEM_IMPORTANCE = {
    "2.02": 9,
    "5.02": 8,
    "5.07": 5,
    "1.02": 9,
    "7.01": 5,
    "8.01": 5,
    "1.01": 4,
    "5.01": 5,
    "4.01": 6,
    "9.01": 3,
}


_FORM_TYPE_REPORT_MAP = {
    "10-K": FilingEventType.ANNUAL_REPORT,
    "10-Q": FilingEventType.QUARTERLY_REPORT,
    "13F-HR": FilingEventType.INSTITUTIONAL_HOLDINGS,
}


@dataclass(frozen=True)
class FilingEvent:
    event_type: str
    ticker: str
    cik: str
    filing_id: str
    form_type: str
    event_time: str
    title: str
    description: str
    importance: int
    items: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "ticker": self.ticker,
            "cik": self.cik,
            "filing_id": self.filing_id,
            "form_type": self.form_type,
            "event_time": self.event_time,
            "title": self.title,
            "description": self.description,
            "importance": self.importance,
            "items": self.items,
        }


def classify_filing_event(filing: dict[str, Any]) -> list[FilingEvent]:
    """Classify one normalized SEC filing record into zero or more events."""
    form = str(filing.get("form") or "").strip().upper()
    ticker = str(filing.get("symbol") or "").strip().upper()
    cik = str(filing.get("cik") or "")
    accession = str(filing.get("accession_no") or "")
    filing_date = str(filing.get("filed_at") or "")

    if form == "8-K":
        events: list[FilingEvent] = []
        items = filing.get("items") or []
        if not items:
            items = ["8.01"]
        for raw_code in items:
            code = _parse_8k_item_code(str(raw_code))
            event_type = _8K_ITEM_MAP.get(code, FilingEventType.OTHER_EVENT)
            title_map = {
                FilingEventType.EARNINGS_RELEASE: "Earnings Release",
                FilingEventType.CEO_CFO_CHANGE: "Executive Change",
                FilingEventType.MATERIAL_DISCLOSURE: "Material Disclosure",
                FilingEventType.MATERIAL_CONTRACT: "Material Contract",
                FilingEventType.BANKRUPTCY_DISTRESS: "Bankruptcy / Distress",
                FilingEventType.BOARD_CHANGE: "Board Change",
                FilingEventType.FINANCIAL_REPORT: "Financial Report Update",
                FilingEventType.FINANCIAL_EXHIBITS: "Financial Exhibits",
                FilingEventType.OTHER_EVENT: "Other 8-K Event",
            }
            events.append(
                FilingEvent(
                    event_type=event_type.value,
                    ticker=ticker,
                    cik=cik,
                    filing_id=accession,
                    form_type=form,
                    event_time=filing_date,
                    title=title_map.get(event_type, event_type.value),
                    description=f"8-K Item {code}: {raw_code}",
                    importance=_ITEM_IMPORTANCE.get(code, 3),
                    items=[code],
                )
            )
        return events

    if form in _FORM_TYPE_REPORT_MAP:
        event_type = _FORM_TYPE_REPORT_MAP[form]
        title_map = {
            FilingEventType.ANNUAL_REPORT: "Annual Report (10-K)",
            FilingEventType.QUARTERLY_REPORT: "Quarterly Report (10-Q)",
            FilingEventType.INSTITUTIONAL_HOLDINGS: "Institutional Holdings (13F-HR)",
        }
        return [
            FilingEvent(
                event_type=event_type.value,
                ticker=ticker,
                cik=cik,
                filing_id=accession,
                form_type=form,
                event_time=filing_date,
                title=title_map[event_type],
                description=f"{form} filed on {filing_date}",
                importance=5,
                items=[],
            )
        ]

    if form == "4":
        return [
            FilingEvent(
                event_type=FilingEventType.OTHER_EVENT.value,
                ticker=ticker,
                cik=cik,
                filing_id=accession,
                form_type=form,
                event_time=filing_date,
                title="Form 4 Insider Transaction",
                description="Form 4 filed; transaction-level parsing can be added as a provider plugin.",
                importance=4,
                items=[],
            )
        ]

    return []


def _parse_8k_item_code(raw: str) -> str:
    match = re.search(r"Item\s*(\d+\.\d+)", raw, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"(\d+\.\d+)", raw.strip())
    return match.group(1) if match else raw.strip()


def _split_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in re.split(r"[,;]", str(value)) if part.strip()]


def _zip_recent_filings(recent: dict[str, Any]) -> list[dict[str, Any]]:
    keys = [key for key, value in recent.items() if isinstance(value, list)]
    if not keys:
        return []
    row_count = max(len(recent[key]) for key in keys)
    rows = []
    for index in range(row_count):
        row = {}
        for key in keys:
            values = recent[key]
            row[key] = values[index] if index < len(values) else None
        rows.append(row)
    return rows
