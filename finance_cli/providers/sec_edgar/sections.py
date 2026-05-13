"""SEC filing section navigation helpers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from finance_cli.providers.base import ProviderError, quiet_call
from finance_cli.providers.sec_edgar.common import _clean_text


@dataclass(frozen=True)
class FilingSectionSpec:
    key: str
    title: str
    edgar_section: str | None
    tenk_attr: str | None = None


FILING_SECTION_SPECS: dict[str, FilingSectionSpec] = {
    "business": FilingSectionSpec("business", "Business", "part_i_item_1", "business"),
    "risk_factors": FilingSectionSpec("risk_factors", "Risk Factors", "part_i_item_1a", "risk_factors"),
    "mda": FilingSectionSpec("mda", "Management's Discussion and Analysis", "part_ii_item_7", "management_discussion"),
    "financial_statements": FilingSectionSpec("financial_statements", "Financial Statements and Supplementary Data", "part_ii_item_8", None),
    "segments": FilingSectionSpec("segments", "Segments", None, None),
}


_SECTION_ALIASES = {
    "business": "business",
    "item_1": "business",
    "1": "business",
    "risk": "risk_factors",
    "risks": "risk_factors",
    "risk_factors": "risk_factors",
    "item_1a": "risk_factors",
    "1a": "risk_factors",
    "mda": "mda",
    "md&a": "mda",
    "management_discussion": "mda",
    "management_discussion_and_analysis": "mda",
    "item_7": "mda",
    "7": "mda",
    "financial_statements": "financial_statements",
    "financials": "financial_statements",
    "item_8": "financial_statements",
    "8": "financial_statements",
    "segments": "segments",
    "segment": "segments",
    "segment_information": "segments",
}


def _normalize_section(section: str) -> FilingSectionSpec:
    key = section.strip().lower().replace("-", "_").replace(" ", "_")
    normalized = _SECTION_ALIASES.get(key)
    if not normalized:
        choices = ", ".join(FILING_SECTION_SPECS)
        raise ProviderError(f"unsupported section '{section}'. Choose one of: {choices}")
    return FILING_SECTION_SPECS[normalized]


def _normalize_accession(accession_no: str | None) -> str | None:
    if not accession_no:
        return None
    compact = re.sub(r"[^0-9]", "", accession_no)
    if len(compact) == 18:
        return f"{compact[:10]}-{compact[10:12]}-{compact[12:]}"
    return accession_no.strip()


def _accession_from_url(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"/Archives/edgar/data/\d+/(\d{18})/", url)
    if match:
        return _normalize_accession(match.group(1))
    match = re.search(r"(\d{10}-\d{2}-\d{6})", url)
    if match:
        return match.group(1)
    return None


def _available_sections(doc: Any) -> list[str]:
    try:
        sections = doc.get_available_sec_sections()
    except Exception:
        sections = []
    return [str(section) for section in sections]


def _extract_segments_text(filing: Any) -> str:
    doc = quiet_call(filing.parse)
    item_8 = ""
    if hasattr(doc, "get_sec_section"):
        item_8 = doc.get_sec_section("part_ii_item_8") or ""
    segment_note = _extract_segment_note(item_8)
    if segment_note:
        return _clean_text(segment_note)

    snippets = []
    try:
        results = doc.search("segment", top_k=8)
    except Exception:
        results = []
    for result in results:
        context = getattr(result, "context", None)
        node = getattr(result, "node", None)
        content = getattr(node, "content", None)
        snippet = context or content
        if snippet and snippet not in snippets:
            snippets.append(str(snippet))
    if snippets:
        return _clean_text("\n\n".join(snippets))
    raise ProviderError("segments section not available")


def _extract_segment_note(text: str) -> str:
    if not text:
        return ""
    pattern = re.compile(
        r"(?is)(?:^|\n)\s*(?:\d+\.\s*)?Segment Information\s*(.+?)(?=\n\s*\d+\.\s+[A-Z][^\n]{2,160}\n|\Z)"
    )
    match = pattern.search(text)
    if not match:
        return ""
    return "Segment Information\n\n" + match.group(1)
