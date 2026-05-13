"""Filing-summary report helpers for SEC filings.
"""
from __future__ import annotations

import re
from typing import Any
from finance_cli.providers.base import ProviderError, quiet_call
from finance_cli.providers.sec_edgar.common import _clean_text, _json_number


def _get_filing_reports(filing: Any) -> Any:
    obj = quiet_call(filing.obj)
    reports = getattr(obj, "reports", None)
    if reports is None:
        raise ProviderError("filing reports not available")
    return reports


def _shape_report_list(reports: Any, *, query: str | None = None) -> list[dict[str, Any]]:
    shaped = [_shape_report(reports.get_by_short_name(name)) for name in getattr(reports, "short_names", [])]
    query_text = str(query or "").strip().lower()
    if not query_text:
        return shaped
    return [report for report in shaped if query_text in _report_search_text(report)]


def _report_search_text(report: dict[str, Any]) -> str:
    return " ".join(str(report.get(key) or "").lower() for key in ("short_name", "long_name"))


def _find_report(reports: Any, name: str) -> Any:
    requested = name.strip().lower()
    for short_name in getattr(reports, "short_names", []):
        if str(short_name).strip().lower() == requested:
            return reports.get_by_short_name(short_name)
    for short_name in getattr(reports, "short_names", []):
        if requested in str(short_name).strip().lower():
            return reports.get_by_short_name(short_name)
    raise ProviderError(f"report not available: {name}")


def _shape_report(report: Any) -> dict[str, Any]:
    return {
        "short_name": getattr(report, "short_name", None),
        "long_name": getattr(report, "long_name", None),
        "category": getattr(report, "menu_category", None),
        "file_name": getattr(report, "html_file_name", None),
    }


def _report_text(report: Any) -> str:
    text = getattr(report, "text", None)
    if callable(text):
        text = text()
    return _clean_text(str(text or ""))


def _report_rows(report: Any, *, query: str | None = None, max_rows: int = 25) -> list[dict[str, Any]]:
    content = str(getattr(report, "content", "") or "")
    if not content.strip():
        return []
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
    except Exception:
        return []

    query_text = str(query or "").strip().lower()
    rows: list[dict[str, Any]] = []
    tables = soup.find_all("table", class_="report") or soup.find_all("table")
    for table in tables:
        headers = _report_table_headers(table)
        if not headers:
            continue
        title = headers[0]
        value_headers = headers[1:]
        context: list[str] = []
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"], recursive=False)
            if len(cells) < 2:
                continue
            label_cell = cells[0]
            label = _clean_text(label_cell.get_text(" ", strip=True))
            if not label:
                continue
            concept = _report_row_concept(label_cell)
            values = []
            for index, cell in enumerate(cells[1:]):
                text = _clean_text(cell.get_text(" ", strip=True).replace("\xa0", " "))
                values.append({
                    "column": value_headers[index] if index < len(value_headers) else f"value_{index + 1}",
                    "text": text,
                    "number": _parse_report_cell_number(text),
                })
            shaped = {
                "table": title,
                "context": list(context),
                "label": label,
                "concept": concept,
                "abstract": "[Abstract]" in label,
                "values": values,
            }
            if _is_report_context_row(shaped):
                context = [label]
                continue
            if query_text and not _report_row_matches_query(shaped, query_text):
                continue
            rows.append(shaped)
            if max_rows > 0 and len(rows) >= max_rows:
                return rows
    return rows


def _report_table_headers(table: Any) -> list[str]:
    first_row = table.find("tr")
    if first_row is None:
        return []
    headers = []
    for cell in first_row.find_all(["th", "td"], recursive=False):
        text = _clean_text(cell.get_text(" ", strip=True).replace("\xa0", " "))
        headers.append(text)
    return headers


def _report_row_concept(label_cell: Any) -> str | None:
    link = label_cell.find("a")
    onclick = str(link.get("onclick") if link else "")
    match = re.search(r"defref_([^'\", )]+)", onclick)
    if match:
        return match.group(1)
    return None


def _report_row_search_text(row: dict[str, Any]) -> str:
    parts = [row.get("table"), " ".join(row.get("context") or []), row.get("label"), row.get("concept")]
    for value in row.get("values") or []:
        parts.extend([value.get("column"), value.get("text")])
    return " ".join(str(part or "").lower() for part in parts)


def _report_row_matches_query(row: dict[str, Any], query_text: str) -> bool:
    search_text = _report_row_search_text(row)
    return query_text in search_text or all(term in search_text for term in query_text.split())


def _is_report_context_row(row: dict[str, Any]) -> bool:
    values = row.get("values") or []
    if any(value.get("text") for value in values):
        return False
    label = str(row.get("label") or "")
    if "[Line Items]" in label:
        return False
    concept = str(row.get("concept") or "")
    return "Axis=" in concept or "[Abstract]" in label


def _parse_report_cell_number(value: str) -> int | float | None:
    text = value.strip()
    if not text:
        return None
    match = re.search(r"\(?-?\$?\s*\d[\d,]*(?:\.\d+)?\)?%?", text)
    if not match:
        return None
    token = match.group(0).replace("$", "").replace(",", "").replace(" ", "")
    is_percent = token.endswith("%")
    token = token.removesuffix("%")
    is_negative = token.startswith("(") and token.endswith(")")
    if is_negative:
        token = token[1:-1]
    try:
        number = float(token)
    except ValueError:
        return None
    if is_negative:
        number = -number
    if is_percent:
        return number / 100
    return _json_number(number)
