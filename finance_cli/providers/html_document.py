"""HTML document text extraction for SEC filings and web documents."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import httpx

from finance_cli.providers.base import ProviderError, quiet_call, require_dependency


class HTMLDocumentProvider:
    """Extract readable text and offset-bearing blocks from HTML documents."""

    name = "beautifulsoup"

    def __init__(self, *, timeout: float = 60.0, user_agent: str | None = None) -> None:
        self.timeout = timeout
        self.user_agent = user_agent or "FinanceCLI/0.1 contact@example.com"

    def read_document(
        self,
        source: str,
        *,
        max_chars: int = 12000,
        max_pages: int | None = None,
    ) -> dict[str, Any]:
        """Read an HTML path/URL and return text plus searchable blocks."""
        raw, final_url = self._read_source(source)
        text = html_to_text(raw)
        text, returned_chars, truncated = _truncate_text(text, max_chars=max_chars)
        blocks = _text_blocks(text)
        page = {
            "page": 1,
            "text": text,
            "char_count": len(text),
            "returned_chars": returned_chars,
            "truncated": truncated,
            "blocks": blocks,
        }
        warnings = []
        if len(text) < 500:
            warnings.append("HTML extraction returned very short text; document may be a wrapper or script-rendered.")
        return {
            "source": source,
            "url": final_url,
            "engine": self.name,
            "format": "html",
            "text": text or None,
            "pages": [page],
            "char_count": len(text),
            "returned_chars": returned_chars,
            "truncated": truncated,
            "warnings": warnings,
        }

    def _read_source(self, source: str) -> tuple[str, str]:
        if source.startswith(("http://", "https://")):
            try:
                response = httpx.get(
                    source,
                    headers={"User-Agent": self.user_agent},
                    timeout=self.timeout,
                    follow_redirects=True,
                )
                response.raise_for_status()
            except Exception as exc:
                raise ProviderError(f"HTML document download failed: {exc}") from exc
            return response.text, str(response.url)
        path = Path(source).expanduser()
        if not path.exists():
            raise ProviderError(f"document not found: {source}")
        return path.read_text(encoding="utf-8", errors="replace"), str(path)


def html_to_text(raw: str) -> str:
    """Convert HTML into readable text while preserving table-ish line breaks."""
    beautiful_soup = quiet_call(
        require_dependency,
        "bs4",
        "Install or repair Finance CLI with: python -m pip install -U finance-cli",
    )
    soup = beautiful_soup.BeautifulSoup(raw, "html.parser")
    _remove_non_readable_tags(soup)
    for tag in soup.find_all(["br", "p", "div", "section", "article", "tr", "li", "h1", "h2", "h3", "h4"]):
        tag.append("\n")
    for tag in soup.find_all(["td", "th"]):
        tag.append(" ")
    text = soup.get_text(separator="\n")
    return clean_text(text)


def _remove_non_readable_tags(soup: Any) -> None:
    """Drop scripts and hidden inline-XBRL metadata while preserving visible facts."""
    for tag in soup(["script", "style", "meta", "link", "noscript"]):
        tag.decompose()
    for tag in list(soup.find_all(["ix:header", "ix:hidden", "ix:references", "ix:resources"])):
        tag.decompose()
    for tag in list(soup.find_all(True)):
        name = str(getattr(tag, "name", "") or "").lower()
        if name in {"ix:header", "ix:hidden", "ix:references", "ix:resources"}:
            tag.decompose()
            continue
        if tag.has_attr("hidden") or str(tag.get("aria-hidden", "")).lower() == "true":
            tag.decompose()
            continue
        style = str(tag.get("style", "")).replace(" ", "").lower()
        if "display:none" in style or "visibility:hidden" in style:
            tag.decompose()


def clean_text(text: str) -> str:
    """Normalize HTML text without erasing SEC table boundaries."""
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"[ \t\r\f\v]+", " ", raw_line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def _truncate_text(text: str, *, max_chars: int) -> tuple[str, int, bool]:
    if max_chars <= 0 or len(text) <= max_chars:
        return text, len(text), False
    returned = text[:max_chars].rstrip()
    return returned, len(returned), True


def _text_blocks(text: str, *, max_block_chars: int = 3200, max_block_lines: int = 45) -> list[dict[str, Any]]:
    blocks = []
    pattern = rf"[^\n]+(?:\n[^\n]+){{0,{max_block_lines - 1}}}"
    for index, match in enumerate(re.finditer(pattern, text)):
        block_text = match.group(0).strip()
        if not block_text:
            continue
        start = match.start()
        while len(block_text) > max_block_chars:
            raw_chunk = block_text[:max_block_chars]
            chunk = raw_chunk.rstrip()
            if chunk:
                blocks.append(
                    {
                        "index": len(blocks),
                        "text": chunk,
                        "start_char": start,
                        "end_char": start + len(chunk),
                        "bbox": None,
                    }
                )
            start += len(raw_chunk)
            block_text = block_text[max_block_chars:]
            skipped = len(block_text) - len(block_text.lstrip())
            start += skipped
            block_text = block_text.lstrip()
        blocks.append(
            {
                "index": len(blocks),
                "text": block_text,
                "start_char": start,
                "end_char": start + len(block_text),
                "bbox": None,
            }
        )
    return blocks
