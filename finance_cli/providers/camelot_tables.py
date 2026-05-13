"""Camelot table extraction for text-based PDFs."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import httpx

from finance_cli.providers.base import ProviderError, quiet_call, require_dependency


class CamelotTableProvider:
    """Extract vector/text PDF tables with Camelot when optional deps exist."""

    name = "camelot"

    def __init__(self, *, timeout: float = 60.0) -> None:
        self.timeout = timeout

    def extract_tables(
        self,
        source: str,
        *,
        pages: str = "1-end",
        flavor: str = "stream",
        max_tables: int = 20,
        max_rows: int = 25,
    ) -> dict[str, Any]:
        """Extract compact table previews from a local or remote PDF."""
        camelot = quiet_call(
            require_dependency,
            "camelot",
            "Install or repair Finance CLI with: python -m pip install -U finance-cli",
        )
        local_path, cleanup = self._local_path(source)
        try:
            tables = quiet_call(camelot.read_pdf, local_path, pages=pages, flavor=flavor)
        except Exception as exc:
            raise ProviderError(f"Camelot table extraction failed: {exc}") from exc
        finally:
            if cleanup:
                Path(local_path).unlink(missing_ok=True)

        rows = [_table_row(table, index=index + 1, max_rows=max_rows) for index, table in enumerate(tables[:max_tables])]
        warnings = []
        if not rows:
            warnings.append("Camelot returned no tables; PDF may be scanned, image-based, or table lines may not be detectable.")
        if len(tables) > max_tables:
            warnings.append(f"Returned first {max_tables} tables out of {len(tables)} detected tables.")
        return {
            "source": source,
            "engine": "camelot",
            "format": "pdf",
            "pages": pages,
            "flavor": flavor,
            "tables": rows,
            "count": len(rows),
            "total_detected": len(tables),
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


def _table_row(table: Any, *, index: int, max_rows: int) -> dict[str, Any]:
    frame = getattr(table, "df", None)
    shape = list(getattr(frame, "shape", (0, 0))) if frame is not None else [0, 0]
    parsing_report = getattr(table, "parsing_report", {}) or {}
    records = _frame_records(frame, max_rows=max_rows)
    return {
        "table": index,
        "page": str(getattr(table, "page", "") or ""),
        "shape": shape,
        "accuracy": _round_or_none(parsing_report.get("accuracy")),
        "whitespace": _round_or_none(parsing_report.get("whitespace")),
        "rows": records,
        "returned_rows": len(records),
        "truncated": bool(shape and shape[0] > len(records)),
    }


def _frame_records(frame: Any, *, max_rows: int) -> list[list[str]]:
    if frame is None:
        return []
    values = frame.head(max(0, max_rows)).fillna("").astype(str).values.tolist()
    return [[cell.strip() for cell in row] for row in values]


def _round_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (ValueError, TypeError):
        return None
