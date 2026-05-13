"""Optional PaddleOCR / PP-StructureV3 document OCR provider."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import httpx

from finance_cli.providers.base import ProviderError, quiet_call, require_dependency


class PaddleOCRProvider:
    """Run PP-StructureV3 for OCR and layout extraction."""

    name = "paddleocr"

    def __init__(self, *, timeout: float = 60.0, pipeline: Any | None = None) -> None:
        self.timeout = timeout
        self._pipeline = pipeline

    def read_document(
        self,
        source: str,
        *,
        max_chars: int = 12000,
        max_pages: int | None = None,
    ) -> dict[str, Any]:
        """OCR a local path or URL and return markdown/text/page rows."""
        local_path, cleanup = self._local_path(source)
        try:
            records = list(self._predict(local_path))
        finally:
            if cleanup:
                Path(local_path).unlink(missing_ok=True)

        pages = _records_to_pages(records, max_chars=max_chars, max_pages=max_pages)
        text = "\n\n".join(page["text"] for page in pages if page.get("text"))
        markdown = "\n\n".join(page["markdown"] for page in pages if page.get("markdown"))
        total_chars = sum(page.get("char_count", 0) for page in pages)
        warnings = []
        if not text and not markdown:
            warnings.append("PaddleOCR returned no extractable text.")
        return {
            "source": source,
            "engine": "paddleocr_pp_structure_v3",
            "format": _format_from_source(source),
            "text": text or None,
            "markdown": markdown or None,
            "pages": pages,
            "char_count": total_chars,
            "returned_chars": len(text),
            "truncated": any(page.get("truncated") for page in pages),
            "warnings": warnings,
        }

    def _predict(self, local_path: str) -> list[Any]:
        pipeline = self._pipeline or self._create_pipeline()
        try:
            return quiet_call(pipeline.predict, input=local_path)
        except TypeError:
            return quiet_call(pipeline.predict, local_path)
        except Exception as exc:
            raise ProviderError(f"PaddleOCR prediction failed: {exc}") from exc

    def _create_pipeline(self) -> Any:
        try:
            paddleocr = quiet_call(
                require_dependency,
                "paddleocr",
                "Install or repair Finance CLI with: python -m pip install -U finance-cli",
            )
            pp_structure = getattr(paddleocr, "PPStructureV3")
            return quiet_call(pp_structure)
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"PaddleOCR PPStructureV3 is unavailable: {exc}") from exc

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
        suffix = Path(url.split("?", 1)[0]).suffix or ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
            handle.write(response.content)
            return handle.name


def _records_to_pages(records: list[Any], *, max_chars: int, max_pages: int | None) -> list[dict[str, Any]]:
    pages = []
    remaining = max_chars if max_chars > 0 else None
    for index, record in enumerate(records, start=1):
        if max_pages is not None and len(pages) >= max_pages:
            break
        markdown = _record_markdown(record)
        text = _markdown_to_text(markdown) or _record_text(record)
        if not text and not markdown:
            continue
        page_text, remaining_after_text = _take_text(text, remaining)
        page_markdown, remaining_after_markdown = _take_text(markdown, remaining)
        pages.append(
            {
                "page": _record_page_number(record) or index,
                "text": page_text,
                "markdown": page_markdown,
                "char_count": len(text),
                "returned_chars": len(page_text),
                "truncated": len(page_text) < len(text),
                "blocks": _record_blocks(record),
            }
        )
        if remaining is not None:
            remaining = min(remaining_after_text or 0, remaining_after_markdown or 0)
        if remaining is not None and remaining <= 0:
            break
    return pages


def _record_markdown(record: Any) -> str:
    value = _get(record, "markdown") or _get(record, "md") or _get(record, "markdown_text")
    if isinstance(value, dict):
        value = value.get("markdown") or value.get("text")
    if value:
        return str(value).strip()
    for attr in ("markdown", "save_to_markdown"):
        method = getattr(record, attr, None)
        if callable(method):
            try:
                returned = method()
                if returned:
                    return str(returned).strip()
            except Exception:
                pass
    return ""


def _record_text(record: Any) -> str:
    for key in ("text", "ocr_text", "plain_text"):
        value = _get(record, key)
        if value:
            return str(value).strip()
    overall = _get(record, "overall_ocr_res")
    if isinstance(overall, dict):
        texts = overall.get("rec_texts")
        if isinstance(texts, list) and texts:
            return "\n".join(str(text).strip() for text in texts if str(text).strip())
    parsing = _get(record, "parsing_res_list")
    if isinstance(parsing, list) and parsing:
        texts = []
        for item in parsing:
            content = _get(item, "content")
            if content:
                texts.append(str(content).strip())
        if texts:
            return "\n".join(texts)
    return ""


def _record_page_number(record: Any) -> int | None:
    value = _get(record, "page_index") or _get(record, "page") or _get(record, "page_id")
    try:
        number = int(value)
    except Exception:
        return None
    return number + 1 if number == 0 else number


def _record_blocks(record: Any) -> list[dict[str, Any]]:
    blocks = _get(record, "blocks") or _get(record, "layout") or _get(record, "parsing_res_list") or []
    if not isinstance(blocks, list):
        return []
    result = []
    for block in blocks[:50]:
        label = _get(block, "type") or _get(block, "label") or _get(block, "region_label")
        text = _get(block, "text") or _get(block, "content")
        if label or text:
            result.append({"type": label, "text": str(text).strip() if text else None})
    return result


def _get(record: Any, key: str) -> Any:
    if isinstance(record, dict):
        return record.get(key)
    if hasattr(record, "get"):
        try:
            return record.get(key)
        except Exception:
            pass
    return getattr(record, key, None)


def _take_text(text: str, remaining: int | None) -> tuple[str, int | None]:
    if remaining is None:
        return text, None
    if remaining <= 0:
        return "", 0
    returned = text[:remaining].rstrip()
    return returned, remaining - len(returned)


def _markdown_to_text(markdown: str) -> str:
    text = markdown.replace("#", " ")
    text = text.replace("|", " ")
    return " ".join(text.split())


def _format_from_source(source: str) -> str:
    suffix = Path(source.split("?", 1)[0]).suffix.lower().lstrip(".")
    return suffix or "document"
