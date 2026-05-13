"""SEC Exhibit 99 discovery and classification helpers.
"""
from __future__ import annotations

import re
from typing import Any
from finance_cli.providers.config import PRESENTATION_RULES
from finance_cli.providers.fuzzy_terms import best_fuzzy_term, has_fuzzy_term, normalize_fuzzy_text


def _parse_filing_index_html(soup: Any) -> list[dict[str, Any]]:
    """Parse the EDGAR filing index HTML table into exhibit dicts."""
    docs = []
    table = soup.find("table", class_="tableFile")
    if table is None:
        return []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        a_tag = cells[2].find("a")
        filename = ""
        if a_tag and a_tag.get("href"):
            filename = str(a_tag["href"]).split("/")[-1]
        docs.append({
            "sequence": cells[0].get_text(strip=True),
            "description": cells[1].get_text(strip=True),
            "document": filename,
            "type": cells[3].get_text(strip=True),
            "size": cells[4].get_text(strip=True) if len(cells) > 4 else "",
        })
    return docs


def _normalize_match_text(value: Any) -> str:
    return normalize_fuzzy_text(value)


def _has_presentation_override(text: str) -> bool:
    return has_fuzzy_term(text, PRESENTATION_RULES.override_terms, threshold=PRESENTATION_RULES.override_threshold)


def _score_exhibit_candidate(exhibit: dict[str, Any]) -> dict[str, Any] | None:
    """Return scoring dict or None if this exhibit is not a presentation candidate."""
    doc_type = str(exhibit.get("type") or "").upper()
    if not doc_type.startswith("EX-99"):
        return None

    description = _normalize_match_text(exhibit.get("description"))
    filename = _normalize_match_text(exhibit.get("document"))
    combined = f"{description} {filename}"
    exclude = best_fuzzy_term(combined, PRESENTATION_RULES.exclude_terms)
    high = best_fuzzy_term(combined, PRESENTATION_RULES.high_terms)
    medium = best_fuzzy_term(combined, PRESENTATION_RULES.medium_terms)
    has_exclude = exclude.score >= PRESENTATION_RULES.exclude_threshold

    if high.score >= PRESENTATION_RULES.match_threshold:
        if has_exclude:
            if not _has_presentation_override(combined):
                return None
            return {
                "confidence": "medium",
                "reason": f"description/filename fuzzy-matches '{high.term}' with conflicting release language",
                "warnings": ["candidate also contains press-release or release-result language"],
            }
        return {"confidence": "high", "reason": f"description/filename fuzzy-matches '{high.term}'"}

    if has_exclude:
        return None

    if medium.score >= PRESENTATION_RULES.match_threshold:
        return {"confidence": "medium", "reason": f"description/filename fuzzy-matches '{medium.term}'"}

    return None


def _classify_exhibit_kind(description: str, filename: str) -> str:
    """Classify exhibit as investor_day, earnings_presentation, ir_presentation, or exhibit_99."""
    combined = _normalize_match_text(f"{description} {filename}")
    if has_fuzzy_term(combined, PRESENTATION_RULES.investor_day_terms, threshold=PRESENTATION_RULES.match_threshold):
        return "investor_day"
    if has_fuzzy_term(combined, PRESENTATION_RULES.earnings_terms, threshold=PRESENTATION_RULES.match_threshold):
        return "earnings_presentation"
    if has_fuzzy_term(combined, PRESENTATION_RULES.ir_terms, threshold=PRESENTATION_RULES.match_threshold):
        return "ir_presentation"
    return "exhibit_99"


def _exhibit_display_title(description: str, filename: str) -> str:
    """Prefer SEC descriptions, but avoid generic EX-99 labels when a filename is clearer."""
    cleaned_description = str(description or "").strip()
    cleaned_filename = str(filename or "").strip()
    if cleaned_description and not re.fullmatch(r"EX-\d+(?:\.\d+)?", cleaned_description, re.IGNORECASE):
        return cleaned_description
    return cleaned_filename or cleaned_description


def _candidate_sort_key(candidate: dict[str, Any]) -> tuple[int, str, str]:
    confidence_rank = {"high": 0, "medium": 1}
    return (
        confidence_rank.get(str(candidate.get("confidence")), 2),
        _reverse_date_key(candidate.get("date")),
        str(candidate.get("document") or ""),
    )


def _reverse_date_key(value: Any) -> str:
    digits = re.sub(r"[^0-9]", "", str(value or ""))
    if len(digits) < 8:
        return "99999999"
    return "".join(str(9 - int(char)) for char in digits[:8])
