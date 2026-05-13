"""Shared helpers for SEC EDGAR provider modules.
"""
from __future__ import annotations

import math
import re
from typing import Any


def _clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]{2,}", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _shape_text_pages(raw_pages: list[str], *, max_chars: int) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    remaining = max_chars if max_chars > 0 else sum(len(page) for page in raw_pages)
    for index, raw_text in enumerate(raw_pages, start=1):
        text = _clean_text(raw_text)
        if not text:
            continue
        returned = _truncate_text(text, max_chars=remaining)
        pages.append(
            {
                "page": index,
                "text": returned,
                "char_count": len(text),
                "returned_chars": len(returned),
                "truncated": len(returned) < len(text),
            }
        )
        remaining -= len(returned)
        if max_chars > 0 and remaining <= 0:
            break
    return pages


def _empty_pdf_result(url: str, warning: str) -> dict[str, Any]:
    return {
        "url": url,
        "text": None,
        "char_count": 0,
        "returned_chars": 0,
        "truncated": False,
        "format": "pdf",
        "pages": [],
        "warnings": [warning],
    }


def _truncate_text(text: str, *, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip()


def _filing_metadata(filing: Any) -> dict[str, Any]:
    return {
        "company": getattr(filing, "company", None),
        "cik": str(getattr(filing, "cik", "") or ""),
        "form": getattr(filing, "form", None),
        "filing_date": str(getattr(filing, "filing_date", "") or ""),
        "period_of_report": str(getattr(filing, "period_of_report", "") or ""),
        "accession_no": getattr(filing, "accession_no", None),
        "filing_url": getattr(filing, "filing_url", None),
        "homepage_url": getattr(filing, "homepage_url", None),
        "text_url": getattr(filing, "text_url", None),
    }


def _json_number(value: Any) -> int | float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    if number.is_integer():
        return int(number)
    return number
