"""Earnings-call transcript providers."""
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from finance_cli.providers.base import ProviderError, quiet_call
from finance_cli.providers.config import (
    TRANSCRIPT_MARKER_THRESHOLD,
    TRANSCRIPT_OPERATOR_TURN_TERMS,
    TRANSCRIPT_QA_START_TERMS,
)
from finance_cli.providers.fuzzy_terms import has_fuzzy_term


@dataclass(frozen=True)
class TranscriptTurn:
    speaker: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {"speaker": self.speaker, "text": self.text}


class MotleyFoolTranscriptProvider:
    """Lightweight scraper for public Motley Fool earnings call transcripts."""

    name = "motley_fool"
    BASE_URL = "https://www.fool.com"
    QUOTE_EXCHANGES = ("nyse", "nasdaq", "amex")

    def __init__(self, *, timeout: float = 30.0, user_agent: str | None = None) -> None:
        self.timeout = timeout
        self.user_agent = user_agent or "FinanceCLI/0.1 contact@example.com"

    def search(self, symbol: str, *, limit: int = 4, debug: bool = False) -> dict[str, Any]:
        """Search recent public transcripts listed on Motley Fool quote pages."""
        normalized = _normalize_symbol(symbol)
        transcripts: list[dict[str, Any]] = []
        attempts = []
        seen_urls: set[str] = set()
        for exchange in self.QUOTE_EXCHANGES:
            url = f"{self.BASE_URL}/quote/{exchange}/{normalized.lower()}/"
            try:
                page = self._get_text(url)
            except ProviderError as exc:
                attempts.append({"url": url, "success": False, "error": str(exc)})
                continue
            attempts.append({"url": url, "success": True})
            for item in _parse_quote_page_transcripts(page, symbol=normalized):
                if item["url"] in seen_urls:
                    continue
                seen_urls.add(item["url"])
                transcripts.append(item)
                if len(transcripts) >= limit:
                    break
            if transcripts:
                break
        transcripts.sort(key=lambda item: item.get("published_at") or "", reverse=True)
        result: dict[str, Any] = {
            "symbol": normalized,
            "transcripts": transcripts[:limit],
            "count": min(len(transcripts), limit),
            "source": self.name,
        }
        if debug:
            result["attempts"] = attempts
        return result

    def read(
        self,
        symbol: str | None = None,
        *,
        url: str | None = None,
        quarter: str = "latest",
        max_chars: int = 12000,
        include_turns: bool = False,
    ) -> dict[str, Any]:
        """Read a transcript by URL or by resolving a symbol's latest transcript."""
        resolved_url = url or self._resolve_transcript_url(symbol, quarter=quarter)
        page = self._get_text(resolved_url)
        parsed = _parse_transcript_page(
            page,
            url=resolved_url,
            source=self.name,
            max_chars=max_chars,
            include_turns=include_turns,
        )
        if symbol:
            parsed["symbol"] = _normalize_symbol(symbol)
        return parsed

    def qa(
        self,
        symbol: str | None = None,
        *,
        url: str | None = None,
        quarter: str = "latest",
        limit: int = 10,
    ) -> dict[str, Any]:
        """Extract Q&A pairs from a transcript."""
        data = self.read(symbol, url=url, quarter=quarter, max_chars=0, include_turns=True)
        pairs = data.get("qa_pairs", [])[:limit]
        return {
            "symbol": data.get("symbol") or (symbol.upper() if symbol else None),
            "transcript": data.get("transcript"),
            "qa_pairs": pairs,
            "count": len(pairs),
            "source": self.name,
        }

    def _resolve_transcript_url(self, symbol: str | None, *, quarter: str) -> str:
        if not symbol:
            raise ProviderError("symbol or url is required")
        results = self.search(symbol, limit=8)["transcripts"]
        if not results:
            raise ProviderError(f"no Motley Fool transcripts found for {symbol}")
        quarter_key = quarter.strip().lower()
        if quarter_key in {"", "latest"}:
            return results[0]["url"]
        for result in results:
            haystack = f"{result.get('title', '')} {result.get('quarter', '')}".lower()
            if quarter_key in haystack:
                return result["url"]
        raise ProviderError(f"no transcript matched quarter={quarter!r} for {symbol}")

    def _get_text(self, url: str) -> str:
        headers = {"User-Agent": self.user_agent}
        try:
            response = quiet_call(httpx.get, url, headers=headers, timeout=self.timeout, follow_redirects=True)
            response.raise_for_status()
        except Exception as exc:
            raise ProviderError(f"transcript request failed: {exc}") from exc
        return response.text


def _parse_quote_page_transcripts(page: str, *, symbol: str) -> list[dict[str, Any]]:
    transcripts: list[dict[str, Any]] = []
    for match in re.finditer(r'\\?"path\\?":\\?"(?P<path>/earnings/call-transcripts/[^"\\]+/)\\?"', page):
        start = max(0, match.start() - 1200)
        end = min(len(page), match.end() + 1200)
        segment = page[start:end]
        path = _unescape_jsonish(match.group("path"))
        title = _extract_jsonish_value(segment, "headline", stop_key="slug") or _title_from_path(path)
        published = (
            _extract_jsonish_value(segment, "published", stop_key="created")
            or _extract_jsonish_value(segment, "publish_at", stop_key="created")
            or _extract_jsonish_value(segment, "last_updated", stop_key="path")
        )
        url = urljoin(MotleyFoolTranscriptProvider.BASE_URL, path)
        transcripts.append({
            "symbol": symbol,
            "title": _unescape_jsonish(title),
            "quarter": _infer_quarter(title),
            "published_at": _normalize_datetime(published),
            "url": url,
            "source": MotleyFoolTranscriptProvider.name,
        })
    return transcripts


def _parse_transcript_page(
    page: str,
    *,
    url: str,
    source: str,
    max_chars: int,
    include_turns: bool = False,
) -> dict[str, Any]:
    soup = BeautifulSoup(page, "html.parser")
    metadata = _article_metadata(soup)
    body = soup.select_one("#article-body-transcript")
    if body is None:
        raise ProviderError("transcript body not found")

    sections = _extract_article_sections(body)
    full_text = sections.get("Full Conference Call Transcript") or _join_sections(sections)
    turns = _parse_turns(full_text)
    qa_start = _find_qa_start(turns)
    prepared_turns = turns[:qa_start] if qa_start is not None else turns
    qa_turns = turns[qa_start:] if qa_start is not None else []
    management_speakers = _management_speakers(prepared_turns)
    qa_pairs = _extract_qa_pairs(qa_turns, management_speakers)
    text = _truncate_text(full_text, max_chars=max_chars)

    result: dict[str, Any] = {
        "transcript": {
            "title": metadata.get("headline") or _page_title(soup),
            "quarter": _infer_quarter(metadata.get("headline") or ""),
            "published_at": _normalize_datetime(metadata.get("datePublished")),
            "url": url,
        },
        "date": sections.get("Date"),
        "summary": sections.get("Summary"),
        "text": text,
        "char_count": len(full_text),
        "returned_chars": len(text),
        "truncated": len(text) < len(full_text),
        "prepared_speakers": sorted({turn.speaker for turn in prepared_turns}),
        "prepared_turn_count": len(prepared_turns),
        "qa_pair_count": len(qa_pairs),
        "source": source,
    }
    if include_turns:
        result["prepared_remarks"] = [turn.to_dict() for turn in prepared_turns]
        result["qa_pairs"] = qa_pairs
    return result


def _extract_article_sections(body: Any) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for tag in body.find_all(["h2", "h3", "p"]):
        text = _clean_text(tag.get_text(" ", strip=True))
        if not text or text == "Image source: The Motley Fool.":
            continue
        if tag.name in {"h2", "h3"}:
            current = text
            sections.setdefault(current, [])
            continue
        if current:
            sections.setdefault(current, []).append(text)
    return {key: "\n\n".join(values).strip() for key, values in sections.items() if values}


def _parse_turns(text: str) -> list[TranscriptTurn]:
    turns: list[TranscriptTurn] = []
    current_speaker: str | None = None
    current_parts: list[str] = []
    for paragraph in [part.strip() for part in text.split("\n\n") if part.strip()]:
        match = re.match(r"^([A-Z][A-Za-z0-9 .'\-]{1,80}):\s*(.+)$", paragraph, re.S)
        if match:
            if current_speaker and current_parts:
                turns.append(TranscriptTurn(current_speaker, _clean_text(" ".join(current_parts))))
            current_speaker = _clean_text(match.group(1))
            current_parts = [_clean_text(match.group(2))]
            continue
        if current_speaker:
            current_parts.append(_clean_text(paragraph))
    if current_speaker and current_parts:
        turns.append(TranscriptTurn(current_speaker, _clean_text(" ".join(current_parts))))
    return turns


def _find_qa_start(turns: list[TranscriptTurn]) -> int | None:
    for index, turn in enumerate(turns):
        if has_fuzzy_term(turn.text, TRANSCRIPT_QA_START_TERMS, threshold=TRANSCRIPT_MARKER_THRESHOLD):
            return index
    return None


def _management_speakers(prepared_turns: list[TranscriptTurn]) -> set[str]:
    speakers = {turn.speaker for turn in prepared_turns}
    return speakers | {"Operator", "Coordinator"}


def _extract_qa_pairs(turns: list[TranscriptTurn], management_speakers: set[str]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for turn in turns:
        if _is_operator_turn(turn):
            continue
        if turn.speaker not in management_speakers:
            if current:
                pairs.append(current)
            current = {
                "questioner": turn.speaker,
                "question": turn.text,
                "answers": [],
            }
            continue
        if current:
            current["answers"].append({"speaker": turn.speaker, "text": turn.text})
    if current:
        pairs.append(current)
    return [pair for pair in pairs if pair["question"] and pair["answers"]]


def _is_operator_turn(turn: TranscriptTurn) -> bool:
    if turn.speaker.lower() in {"operator", "coordinator"}:
        return True
    return has_fuzzy_term(turn.text, TRANSCRIPT_OPERATOR_TURN_TERMS, threshold=TRANSCRIPT_MARKER_THRESHOLD)


def _article_metadata(soup: BeautifulSoup) -> dict[str, Any]:
    tag = soup.select_one('script[type="application/ld+json"]')
    if not tag or not tag.string:
        return {}
    try:
        payload = json.loads(tag.string)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _extract_jsonish_value(text: str, key: str, *, stop_key: str | None = None) -> str | None:
    if stop_key:
        pattern = rf'\\?"{re.escape(key)}\\?":\\?"(.*?)\\?",\\?"{re.escape(stop_key)}\\?"'
        match = re.search(pattern, text)
        return _unescape_jsonish(match.group(1)) if match else None
    pattern = rf'\\?"{re.escape(key)}\\?":\\?"([^"\\]*)'
    match = re.search(pattern, text)
    return _unescape_jsonish(match.group(1)) if match else None


def _unescape_jsonish(value: str) -> str:
    return html.unescape(value.replace(r"\/", "/").replace(r"\"", '"'))


def _infer_quarter(text: str) -> str | None:
    match = re.search(r"\bQ([1-4])\s+(20\d{2})\b", text, re.I)
    return f"Q{match.group(1)} {match.group(2)}" if match else None


def _title_from_path(path: str) -> str:
    slug = path.rstrip("/").split("/")[-1]
    words = [word.upper() if word.lower() in {"iot", "ai"} else word.capitalize() for word in slug.split("-")]
    return " ".join(words)


def _normalize_datetime(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned).isoformat()
    except ValueError:
        return value


def _page_title(soup: BeautifulSoup) -> str | None:
    heading = soup.find("h1")
    return _clean_text(heading.get_text(" ", strip=True)) if heading else None


def _join_sections(sections: dict[str, str]) -> str:
    return "\n\n".join(value for value in sections.values() if value)


def _truncate_text(text: str, *, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip()


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ProviderError("symbol is required")
    return normalized


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
