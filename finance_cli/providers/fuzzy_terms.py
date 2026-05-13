"""Reusable deterministic fuzzy term matching."""
from __future__ import annotations

import re
from dataclasses import dataclass
from importlib import import_module

from finance_cli.providers.base import ProviderError, quiet_call


@dataclass(frozen=True)
class FuzzyTermMatch:
    term: str
    score: float
    scorer: str


def normalize_fuzzy_text(value: object) -> str:
    """Normalize text for deterministic fuzzy matching."""
    return re.sub(r"[_\-.]+", " ", str(value or "").lower()).strip()


def compact_fuzzy_text(value: object) -> str:
    """Remove non-alphanumerics so joined filenames still match phrases."""
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def best_fuzzy_term(text: str, terms: tuple[str, ...] | list[str]) -> FuzzyTermMatch:
    """Return the best fuzzy match across configured terms."""
    fuzz = _rapidfuzz()
    normalized_text = normalize_fuzzy_text(text)
    compact_text = compact_fuzzy_text(normalized_text)
    best = FuzzyTermMatch(term="", score=0.0, scorer="none")
    for term in terms:
        normalized_term = normalize_fuzzy_text(term)
        compact_term = compact_fuzzy_text(normalized_term)
        scores = {
            "substring": 100.0 if normalized_term and normalized_term in normalized_text else 0.0,
            "compact": 100.0 if compact_term and compact_term in compact_text else 0.0,
            "partial": float(fuzz.partial_ratio(normalized_term, normalized_text)),
            "token_set": float(fuzz.token_set_ratio(normalized_term, normalized_text)),
            "wratio": float(fuzz.WRatio(normalized_term, normalized_text)),
        }
        scorer, score = max(scores.items(), key=lambda item: item[1])
        if score > best.score:
            best = FuzzyTermMatch(term=term, score=round(score, 2), scorer=scorer)
    return best


def has_fuzzy_term(text: str, terms: tuple[str, ...] | list[str], *, threshold: float = 90.0) -> bool:
    """Return whether any term matches at or above threshold."""
    return best_fuzzy_term(text, terms).score >= threshold


def _rapidfuzz():
    try:
        return quiet_call(import_module, "rapidfuzz.fuzz")
    except Exception as exc:
        raise ProviderError("RapidFuzz is unavailable. Install with: python -m pip install rapidfuzz") from exc
