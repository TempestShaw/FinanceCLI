"""RapidFuzz threshold experiments for presentation candidate rules.

These tests intentionally mirror the current SEC/IR presentation heuristics.
They give us a safe place to tune thresholds before replacing production
substring matching.
"""
from __future__ import annotations

from finance_cli.providers.config import PRESENTATION_RULES
from finance_cli.providers.fuzzy_terms import best_fuzzy_term


PRESENTATION_THRESHOLD = 90.0
EXCLUDE_THRESHOLD = 90.0
OVERRIDE_THRESHOLD = 90.0


def _scores(text: str) -> dict[str, float | str]:
    high = best_fuzzy_term(text, PRESENTATION_RULES.high_terms)
    medium = best_fuzzy_term(text, PRESENTATION_RULES.medium_terms)
    exclude = best_fuzzy_term(text, PRESENTATION_RULES.exclude_terms)
    override = best_fuzzy_term(text, PRESENTATION_RULES.override_terms)
    return {
        "high_term": high.term,
        "high_score": high.score,
        "medium_term": medium.term,
        "medium_score": medium.score,
        "exclude_term": exclude.term,
        "exclude_score": exclude.score,
        "override_term": override.term,
        "override_score": override.score,
    }


def _fuzzy_presentation_decision(text: str) -> str | None:
    scores = _scores(text)
    has_high = scores["high_score"] >= PRESENTATION_THRESHOLD
    has_medium = scores["medium_score"] >= PRESENTATION_THRESHOLD
    has_exclude = scores["exclude_score"] >= EXCLUDE_THRESHOLD
    has_override = scores["override_score"] >= OVERRIDE_THRESHOLD
    if has_high:
        if has_exclude:
            return "medium" if has_override else None
        return "high"
    if has_exclude:
        return None
    if has_medium:
        return "medium"
    return None


def test_fuzzy_thresholds_match_existing_sec_presentation_cases():
    cases = {
        "INVESTOR DAY PRESENTATION iot20260305_ex99-1.htm": "high",
        "EXHIBIT 99.1 iot-slides-2026.htm": "medium",
        "PRESS RELEASE iot20260305_pressrelease.htm": None,
        "PRESS RELEASE AND INVESTOR DAY PRESENTATION iot-q4-results-and-investorday.htm": "medium",
        "EX-99.1 ex991-investordaypressrele.htm": None,
        "EXHIBIT 99.1 ex99-1.htm": None,
    }

    assert {text: _fuzzy_presentation_decision(text) for text in cases} == cases


def test_fuzzy_threshold_avoids_exhibit_index_false_positive():
    scores = _scores("EXHIBIT 99.1 iot-slides-2026.htm")

    assert scores["medium_score"] >= PRESENTATION_THRESHOLD
    assert scores["medium_term"] == "slides"
    assert scores["exclude_term"] == "exhibit index"
    assert scores["exclude_score"] < EXCLUDE_THRESHOLD


def test_fuzzy_thresholds_handle_joined_filename_terms():
    scores = _scores("EX-99.1 iot-investorday-capitalmarketsdeck.pdf")

    assert scores["high_score"] >= PRESENTATION_THRESHOLD
    assert scores["high_term"] in {"investor day", "capital markets day"}
    assert scores["override_score"] >= OVERRIDE_THRESHOLD
