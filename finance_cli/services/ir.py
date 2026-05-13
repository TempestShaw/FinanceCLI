"""IR presentation discovery and text extraction services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.company_ir import CompanyIRProvider
from finance_cli.providers.paddle_ocr import PaddleOCRProvider
from finance_cli.providers.sec_edgar import SecEdgarProvider
from finance_cli.providers.yahoo import YahooFinanceProvider
from finance_cli.services.documents import ocr_document


IR_SOURCES = {"auto", "sec", "company_ir", "all"}


def list_ir_presentations(
    symbol: str,
    *,
    limit: int = 20,
    source: str = "auto",
    provider: SecEdgarProvider | None = None,
    company_ir_provider: CompanyIRProvider | None = None,
    quote_provider: YahooFinanceProvider | None = None,
) -> dict[str, Any]:
    """Discover IR presentations from SEC exhibits and optional company IR pages."""
    normalized = symbol.strip().upper()
    normalized_source = source.strip().lower()
    if normalized_source not in IR_SOURCES:
        raise ValueError(f"source must be one of: {', '.join(sorted(IR_SOURCES))}")

    sources_used: list[str] = []
    errors: list[str] = []
    presentations: list[dict[str, Any]] = []

    if normalized_source in {"auto", "sec", "all"}:
        client = provider or SecEdgarProvider()
        try:
            sec_rows = client.list_exhibit_candidates(normalized, limit=limit)
            presentations.extend(sec_rows)
            sources_used.append("sec_edgar")
        except Exception as exc:
            errors.append(f"sec_edgar: {exc}")

    should_try_company_ir = normalized_source in {"company_ir", "all"} or (
        normalized_source == "auto" and not presentations
    )
    if should_try_company_ir:
        profile = _quote_profile(normalized, quote_provider=quote_provider)
        company_client = company_ir_provider or CompanyIRProvider()
        try:
            company_rows = company_client.list_presentations(
                normalized,
                company_name=profile.get("company_name"),
                website=profile.get("website"),
                ir_website=profile.get("ir_website"),
                limit=limit,
            )
            presentations.extend(company_rows)
            sources_used.append("company_ir")
        except Exception as exc:
            errors.append(f"company_ir: {exc}")

    presentations = _dedupe_presentations(presentations)[:limit]
    return {
        "symbol": normalized,
        "presentations": presentations,
        "count": len(presentations),
        "source": normalized_source,
        "sources_used": sources_used,
        "notes": [
            "SEC candidates are scored from Exhibit 99 description and filename keywords.",
            "Company IR fallback is conservative and only crawls company/IR domains.",
            "Press releases and earnings releases are filtered unless a distinct deck/slides signal is present.",
            "Confidence 'high' = strong presentation signal; 'medium' = weaker or conflicting signal.",
            "kind: investor_day | earnings_presentation | ir_presentation | exhibit_99",
        ],
        "warnings": errors,
    }


def read_ir_presentation(
    url: str,
    *,
    max_chars: int = 12000,
    ocr: str = "off",
    provider: SecEdgarProvider | None = None,
    ocr_provider: PaddleOCRProvider | None = None,
) -> dict[str, Any]:
    """Fetch and extract text from an IR presentation URL."""
    ocr_mode = ocr.strip().lower()
    if ocr_mode not in {"off", "auto", "force"}:
        raise ValueError("ocr must be one of: off, auto, force")
    client = provider or SecEdgarProvider()
    extracted = client.read_exhibit_text(url, max_chars=max_chars)
    if ocr_mode == "off":
        return extracted
    if ocr_mode == "auto" and not _needs_ocr(extracted):
        extracted["ocr"] = {"attempted": False, "reason": "native extraction returned enough text"}
        return extracted
    try:
        ocr_result = ocr_document(url, max_chars=max_chars, provider=ocr_provider)
    except Exception as exc:
        extracted.setdefault("warnings", []).append(f"OCR unavailable or failed: {exc}")
        extracted["ocr"] = {"attempted": True, "ok": False, "error": str(exc), "mode": ocr_mode}
        return extracted
    ocr_result["native_extraction"] = {
        "format": extracted.get("format"),
        "char_count": extracted.get("char_count"),
        "returned_chars": extracted.get("returned_chars"),
        "warnings": extracted.get("warnings") or [],
    }
    ocr_result["ocr"] = {"attempted": True, "ok": True, "mode": ocr_mode}
    return ocr_result


def _quote_profile(symbol: str, *, quote_provider: YahooFinanceProvider | None) -> dict[str, Any]:
    client = quote_provider or YahooFinanceProvider()
    try:
        return client.quote(symbol)
    except Exception as exc:
        return {"symbol": symbol, "warning": f"quote profile unavailable: {exc}"}


def _dedupe_presentations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        url = str(row.get("url") or "")
        if not url or url in seen:
            continue
        seen.add(url)
        result.append(row)
    return result


def _needs_ocr(result: dict[str, Any]) -> bool:
    returned_chars = int(result.get("returned_chars") or 0)
    if returned_chars < 500:
        return True
    warnings = " ".join(str(item).lower() for item in result.get("warnings") or [])
    return any(term in warnings for term in ("image", "short", "no text", "incomplete"))
