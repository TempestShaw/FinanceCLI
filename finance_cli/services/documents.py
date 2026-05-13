"""Document text extraction services shared by finance workflows."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.camelot_tables import CamelotTableProvider
from finance_cli.providers.html_document import HTMLDocumentProvider
from finance_cli.providers.native_pdf import NativePDFProvider
from finance_cli.providers.paddle_ocr import PaddleOCRProvider
from finance_cli.services.document_match import fuzzy_match_topics


def read_document(
    source: str,
    *,
    max_chars: int = 12000,
    max_pages: int | None = None,
    doc_format: str | None = None,
    provider: NativePDFProvider | None = None,
) -> dict[str, Any]:
    """Extract native text/layout from a local or remote document."""
    client = provider or _document_provider(source, doc_format=doc_format)
    return client.read_document(source, max_chars=max_chars, max_pages=max_pages)


def scan_document(
    source: str,
    *,
    topics: list[str] | None = None,
    threshold: float = 80.0,
    max_chars: int = 12000,
    max_pages: int | None = None,
    limit: int = 50,
    window_chars: int = 0,
    match_mode: str = "fuzzy",
    start_char: int | None = None,
    end_char: int | None = None,
    doc_format: str | None = None,
    provider: NativePDFProvider | None = None,
) -> dict[str, Any]:
    """Extract document text/layout and return fuzzy topic matches."""
    extracted = read_document(
        source,
        max_chars=max_chars,
        max_pages=max_pages,
        doc_format=doc_format,
        provider=provider,
    )
    scanned_pages = _filter_pages_by_offsets(extracted.get("pages") or [], start_char=start_char, end_char=end_char)
    matches = fuzzy_match_topics(
        scanned_pages,
        topics=topics,
        threshold=threshold,
        limit=limit,
        match_mode=match_mode,
    )
    matches = _attach_windows(matches, extracted.get("text") or "", window_chars=window_chars)
    return {
        "source": source,
        "engine": extracted.get("engine"),
        "format": extracted.get("format"),
        "topics": topics or "default",
        "threshold": threshold,
        "match_mode": match_mode,
        "start_char": start_char,
        "end_char": end_char,
        "window_chars": window_chars,
        "matches": matches,
        "count": len(matches),
        "pages_scanned": len(scanned_pages),
        "char_count": extracted.get("char_count"),
        "warnings": extracted.get("warnings") or [],
    }


def window_document(
    source: str,
    *,
    start_char: int | None = None,
    match_id: str | None = None,
    chars: int = 4000,
    direction: str = "around",
    doc_format: str | None = None,
    provider: NativePDFProvider | None = None,
) -> dict[str, Any]:
    """Return a bounded text window from a document using offsets or a match id."""
    if chars <= 0:
        raise ValueError("chars must be greater than zero")
    match_start, match_end = _parse_match_id(match_id)
    if start_char is None:
        start_char = match_start
    if start_char is None:
        raise ValueError("start_char= or match_id=char_START_END is required")

    extracted = read_document(source, max_chars=0, doc_format=doc_format, provider=provider)
    text = extracted.get("text") or ""
    start, end = _window_bounds(
        text_length=len(text),
        start_char=start_char,
        match_end=match_end,
        chars=chars,
        direction=direction,
    )
    window_text = text[start:end]
    return {
        "source": source,
        "engine": extracted.get("engine"),
        "format": extracted.get("format"),
        "start_char": start,
        "end_char": end,
        "returned_chars": len(window_text),
        "char_count": len(text),
        "direction": direction,
        "text": window_text,
        "warnings": extracted.get("warnings") or [],
    }


def extract_document_tables(
    source: str,
    *,
    pages: str = "1-end",
    flavor: str = "stream",
    max_tables: int = 20,
    max_rows: int = 25,
    provider: CamelotTableProvider | None = None,
) -> dict[str, Any]:
    """Extract compact table previews from a text-based PDF."""
    client = provider or CamelotTableProvider()
    return client.extract_tables(
        source,
        pages=pages,
        flavor=flavor,
        max_tables=max_tables,
        max_rows=max_rows,
    )


def ocr_document(
    source: str,
    *,
    max_chars: int = 12000,
    max_pages: int | None = None,
    provider: PaddleOCRProvider | None = None,
) -> dict[str, Any]:
    """Run OCR/layout parsing on a local path or URL."""
    client = provider or PaddleOCRProvider()
    return client.read_document(source, max_chars=max_chars, max_pages=max_pages)


def _document_provider(source: str, *, doc_format: str | None) -> Any:
    requested = (doc_format or "").strip().lower()
    if requested == "html" or (not requested and _looks_like_html(source)):
        return HTMLDocumentProvider()
    return NativePDFProvider()


def _looks_like_html(source: str) -> bool:
    clean_source = source.split("?", 1)[0].split("#", 1)[0].lower()
    return clean_source.endswith((".htm", ".html"))


def _attach_windows(matches: list[dict[str, Any]], text: str, *, window_chars: int) -> list[dict[str, Any]]:
    if window_chars <= 0 or not text:
        return matches
    shaped = []
    for match in matches:
        start_char = match.get("start_char")
        end_char = match.get("end_char")
        if not isinstance(start_char, int) or not isinstance(end_char, int):
            shaped.append(match)
            continue
        start = max(0, start_char - window_chars // 2)
        end = min(len(text), end_char + window_chars // 2)
        updated = dict(match)
        updated["window_start_char"] = start
        updated["window_end_char"] = end
        updated["snippet"] = text[start:end].strip()
        shaped.append(updated)
    return shaped


def _filter_pages_by_offsets(
    pages: list[dict[str, Any]],
    *,
    start_char: int | None,
    end_char: int | None,
) -> list[dict[str, Any]]:
    if start_char is None and end_char is None:
        return pages
    filtered_pages = []
    lower = start_char if start_char is not None else 0
    upper = end_char if end_char is not None else float("inf")
    for page in pages:
        blocks = []
        for block in page.get("blocks") or []:
            block_start = block.get("start_char")
            block_end = block.get("end_char")
            if not isinstance(block_start, int) or not isinstance(block_end, int):
                continue
            if block_end >= lower and block_start <= upper:
                blocks.append(_clip_block(block, lower=lower, upper=upper))
        if blocks:
            updated = dict(page)
            updated["blocks"] = blocks
            filtered_pages.append(updated)
    return filtered_pages


def _clip_block(block: dict[str, Any], *, lower: int, upper: float) -> dict[str, Any]:
    block_start = block["start_char"]
    block_end = block["end_char"]
    clipped_start = max(block_start, lower)
    clipped_end = min(block_end, int(upper)) if upper != float("inf") else block_end
    if clipped_start == block_start and clipped_end == block_end:
        return block
    text = str(block.get("text") or "")
    relative_start = max(0, clipped_start - block_start)
    relative_end = max(relative_start, clipped_end - block_start)
    updated = dict(block)
    updated["text"] = text[relative_start:relative_end].strip()
    updated["start_char"] = clipped_start
    updated["end_char"] = clipped_end
    return updated


def _parse_match_id(match_id: str | None) -> tuple[int | None, int | None]:
    if not match_id:
        return None, None
    parts = match_id.split("_")
    if len(parts) == 3 and parts[0] == "char":
        return int(parts[1]), int(parts[2])
    raise ValueError("match_id must use char_START_END format")


def _window_bounds(
    *,
    text_length: int,
    start_char: int,
    match_end: int | None,
    chars: int,
    direction: str,
) -> tuple[int, int]:
    direction = direction.strip().lower()
    if direction in {"next", "after", "forward"}:
        start = match_end if match_end is not None else start_char
        end = start + chars
    elif direction in {"previous", "prev", "before", "back"}:
        end = start_char
        start = end - chars
    else:
        start = start_char - chars // 2
        end = start + chars
    start = max(0, min(start, text_length))
    end = max(start, min(end, text_length))
    return start, end
