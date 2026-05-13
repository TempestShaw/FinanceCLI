"""Reusable fuzzy document topic matching."""
from __future__ import annotations

import re
from typing import Any

from finance_cli.providers.config import DOCUMENT_TOPIC_QUERIES
from finance_cli.providers.fuzzy_terms import FuzzyTermMatch, best_fuzzy_term


def fuzzy_match_topics(
    pages: list[dict[str, Any]],
    *,
    topics: list[str] | None = None,
    threshold: float = 80.0,
    limit: int = 50,
    match_mode: str = "fuzzy",
) -> list[dict[str, Any]]:
    """Return topic matches from page blocks using RapidFuzz."""
    resolved = resolve_topic_queries(topics)
    match_mode = match_mode.strip().lower()
    matches = []
    for page in pages:
        page_number = page.get("page")
        blocks = page.get("blocks") or []
        if not blocks and page.get("text"):
            blocks = [{"index": 0, "text": page["text"], "bbox": None}]
        for block in blocks:
            text = str(block.get("text") or "").strip()
            if not text:
                continue
            for topic, queries in resolved.items():
                best_query = None
                best_score = 0.0
                for query in queries:
                    match = _score_query(text, query, match_mode=match_mode)
                    if match.score > best_score:
                        best_score = match.score
                        best_query = match.term
                if best_score >= threshold:
                    start_char = block.get("start_char")
                    end_char = block.get("end_char")
                    matches.append(
                        {
                            "match_id": _match_id(start_char, end_char),
                            "topic": topic,
                            "score": round(best_score, 2),
                            "query": best_query,
                            "match_mode": match_mode,
                            "page": page_number,
                            "block_index": block.get("index"),
                            "bbox": block.get("bbox"),
                            "start_char": start_char,
                            "end_char": end_char,
                            "snippet": text,
                            "text": text,
                        }
                    )
    matches.sort(key=lambda row: (-float(row["score"]), int(row.get("page") or 0), int(row.get("block_index") or 0)))
    return matches[:limit]


def resolve_topic_queries(topics: list[str] | None) -> dict[str, tuple[str, ...]]:
    """Resolve topic aliases to configured queries; unknown topics match themselves."""
    if not topics:
        return DOCUMENT_TOPIC_QUERIES
    resolved: dict[str, tuple[str, ...]] = {}
    for raw_topic in topics:
        topic = raw_topic.strip().lower()
        if not topic:
            continue
        resolved[topic] = DOCUMENT_TOPIC_QUERIES.get(topic, (raw_topic.strip(),))
    return resolved


def _match_id(start_char: Any, end_char: Any) -> str | None:
    if isinstance(start_char, int) and isinstance(end_char, int):
        return f"char_{start_char}_{end_char}"
    return None


def _score_query(text: str, query: str, *, match_mode: str) -> Any:
    if match_mode == "all_terms":
        tokens = _content_tokens(query)
        text_tokens = set(_normalize_search_text(text).split())
        matched = [token for token in tokens if token in text_tokens]
        score = round(100.0 * len(matched) / len(tokens), 2) if tokens else 0.0
        return FuzzyTermMatch(term=query, score=score, scorer="all_terms")
    return best_fuzzy_term(text, (query,))


def _content_tokens(query: str) -> list[str]:
    stopwords = {"a", "an", "and", "or", "the", "of", "in", "to", "for", "with"}
    normalized = _normalize_search_text(query)
    return sorted({token for token in normalized.split() if token and token not in stopwords})


def _normalize_search_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(text or "").lower().replace("-", " ").replace("_", " ")))
