"""Native PDF text/layout extraction using PyMuPDF."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import httpx

from finance_cli.providers.base import ProviderError, quiet_call, require_dependency


DOCUMENTS_INSTALL_HINT = "Install or repair Finance CLI with: python -m pip install -U finresearch-cli"


class NativePDFProvider:
    """Extract text and layout blocks from text-based PDFs without OCR."""

    name = "pymupdf"

    def __init__(self, *, timeout: float = 60.0) -> None:
        self.timeout = timeout

    def read_document(
        self,
        source: str,
        *,
        max_chars: int = 12000,
        max_pages: int | None = None,
    ) -> dict[str, Any]:
        """Read a PDF path/URL and return page text plus positioned blocks."""
        fitz = quiet_call(require_dependency, "fitz", DOCUMENTS_INSTALL_HINT)
        local_path, cleanup = self._local_path(source)
        try:
            document = quiet_call(fitz.open, local_path)
            pages = _extract_pages(document, max_chars=max_chars, max_pages=max_pages)
        except Exception as exc:
            raise ProviderError(f"PyMuPDF document extraction failed: {exc}") from exc
        finally:
            if cleanup:
                Path(local_path).unlink(missing_ok=True)

        text = "\n\n".join(page["text"] for page in pages if page.get("text"))
        char_count = sum(page.get("char_count", 0) for page in pages)
        warnings = []
        if not text:
            warnings.append("Native PDF extraction returned no text; OCR may be required.")
        elif char_count < 500:
            warnings.append("Native PDF extraction returned very short text; document may be image-heavy.")
        return {
            "source": source,
            "engine": "pymupdf",
            "format": "pdf",
            "text": text or None,
            "pages": pages,
            "char_count": char_count,
            "returned_chars": len(text),
            "truncated": any(page.get("truncated") for page in pages),
            "warnings": warnings,
        }

    def read_bytes(
        self,
        source: str,
        raw: bytes,
        *,
        max_chars: int = 12000,
        max_pages: int | None = None,
    ) -> dict[str, Any]:
        """Read PDF bytes and return page text plus positioned blocks."""
        fitz = quiet_call(require_dependency, "fitz", DOCUMENTS_INSTALL_HINT)
        try:
            document = quiet_call(fitz.open, stream=raw, filetype="pdf")
            pages = _extract_pages(document, max_chars=max_chars, max_pages=max_pages)
        except Exception as exc:
            raise ProviderError(f"PyMuPDF document extraction failed: {exc}") from exc
        text = "\n\n".join(page["text"] for page in pages if page.get("text"))
        char_count = sum(page.get("char_count", 0) for page in pages)
        warnings = []
        if not text:
            warnings.append("Native PDF extraction returned no text; OCR may be required.")
        elif char_count < 500:
            warnings.append("Native PDF extraction returned very short text; document may be image-heavy.")
        return {
            "source": source,
            "engine": "pymupdf",
            "format": "pdf",
            "text": text or None,
            "pages": pages,
            "char_count": char_count,
            "returned_chars": len(text),
            "truncated": any(page.get("truncated") for page in pages),
            "warnings": warnings,
        }

    def _local_path(self, source: str) -> tuple[str, bool]:
        if source.startswith(("http://", "https://")):
            return self._download(source), True
        path = Path(source).expanduser()
        if not path.exists():
            raise ProviderError(f"document not found: {source}")
        return str(path), False

    def _download(self, url: str) -> str:
        try:
            response = httpx.get(url, timeout=self.timeout, follow_redirects=True)
            response.raise_for_status()
        except Exception as exc:
            raise ProviderError(f"document download failed: {exc}") from exc
        suffix = Path(url.split("?", 1)[0]).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
            handle.write(response.content)
            return handle.name


def _extract_pages(document: Any, *, max_chars: int, max_pages: int | None) -> list[dict[str, Any]]:
    pages = []
    remaining = max_chars if max_chars > 0 else None
    page_count = len(document)
    for page_index in range(page_count):
        if max_pages is not None and len(pages) >= max_pages:
            break
        page = document[page_index]
        blocks = _extract_blocks(page)
        ordered_blocks = reconstruct_reading_order(blocks)
        full_text = "\n".join(block["text"] for block in ordered_blocks if block.get("text"))
        page_text, remaining = _take_text(full_text, remaining)
        pages.append(
            {
                "page": page_index + 1,
                "text": page_text,
                "char_count": len(full_text),
                "returned_chars": len(page_text),
                "truncated": len(page_text) < len(full_text),
                "blocks": _truncate_blocks(ordered_blocks),
            }
        )
        if remaining is not None and remaining <= 0:
            break
    return pages


def _extract_blocks(page: Any) -> list[dict[str, Any]]:
    rows = page.get_text("blocks") or []
    blocks = []
    for index, row in enumerate(rows):
        if len(row) < 5:
            continue
        x0, y0, x1, y1, text = row[:5]
        cleaned = " ".join(str(text or "").split())
        if not cleaned:
            continue
        blocks.append(
            {
                "index": index,
                "text": cleaned,
                "bbox": [round(float(x0), 2), round(float(y0), 2), round(float(x1), 2), round(float(y1), 2)],
            }
        )
    return blocks


def reconstruct_reading_order(blocks: list[dict[str, Any]], *, column_gap: float = 24.0) -> list[dict[str, Any]]:
    """Sort blocks by rough columns, then top-to-bottom within each column."""
    if len(blocks) <= 1:
        return blocks
    sorted_blocks = sorted(blocks, key=lambda block: (block["bbox"][0], block["bbox"][1]))
    columns: list[list[dict[str, Any]]] = []
    for block in sorted_blocks:
        x0 = float(block["bbox"][0])
        placed = False
        for column in columns:
            column_x0 = _median([float(item["bbox"][0]) for item in column])
            if abs(x0 - column_x0) <= column_gap:
                column.append(block)
                placed = True
                break
        if not placed:
            columns.append([block])
    columns.sort(key=lambda column: _median([float(item["bbox"][0]) for item in column]))
    ordered = []
    for column in columns:
        ordered.extend(sorted(column, key=lambda block: (block["bbox"][1], block["bbox"][0])))
    return ordered


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def _take_text(text: str, remaining: int | None) -> tuple[str, int | None]:
    if remaining is None:
        return text, None
    if remaining <= 0:
        return "", 0
    returned = text[:remaining].rstrip()
    return returned, remaining - len(returned)


def _truncate_blocks(blocks: list[dict[str, Any]], *, limit: int = 80) -> list[dict[str, Any]]:
    return blocks[:limit]
