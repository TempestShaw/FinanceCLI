"""Provider source inventory and health checks."""
from __future__ import annotations

import importlib.util
import os
from time import perf_counter
from typing import Any, Callable

from finance_cli.providers.alphavantage import AlphaVantageProvider
from finance_cli.providers.alpaca import AlpacaMarketDataProvider
from finance_cli.providers.base import ProviderHealth, ProviderMetadata
from finance_cli.providers.company_ir import CompanyIRProvider
from finance_cli.providers.fmp import FMPProvider
from finance_cli.providers.gdelt import GdeltNewsProvider
from finance_cli.providers.sec_edgar import SecEdgarProvider
from finance_cli.providers.transcripts import MotleyFoolTranscriptProvider
from finance_cli.providers.yahoo import YahooFinanceProvider


Probe = Callable[[], Any]


PROVIDERS: tuple[ProviderMetadata, ...] = (
    ProviderMetadata(
        name="yfinance",
        label="Yahoo Finance via yfinance",
        capabilities=("quote", "ohlcv", "fundamentals", "calendar", "sector", "industry", "screen"),
        package="yfinance",
        notes="Public market, company calendar, sector, industry, and screener data via yfinance.",
    ),
    ProviderMetadata(
        name="sec",
        label="SEC EDGAR",
        capabilities=("filings", "filing_sections", "company_metadata"),
        optional_env=("FINANCE_SEC_USER_AGENT",),
        notes="Public SEC JSON plus edgartools for filing reads.",
    ),
    ProviderMetadata(
        name="gdelt",
        label="GDELT",
        capabilities=("news", "timeline", "tone", "geo"),
        notes="Public global news APIs with article and timeline metadata.",
    ),
    ProviderMetadata(
        name="motley_fool",
        label="Motley Fool transcripts",
        capabilities=("transcripts", "earnings_call_qa"),
        notes="Public transcript pages for earnings-call research.",
    ),
    ProviderMetadata(
        name="company_ir",
        label="Company investor relations websites",
        capabilities=("ir_presentations", "ir_events"),
        notes="Conservative crawl of public company and investor-relations domains.",
    ),
    ProviderMetadata(
        name="fmp",
        label="Financial Modeling Prep",
        capabilities=("analyst_estimates", "consensus_estimates"),
        required_env=("FMP_API_KEY",),
        notes="Analyst estimate provider via FMP stable analyst-estimates endpoint.",
    ),
    ProviderMetadata(
        name="pymupdf",
        label="PyMuPDF native PDF parser",
        capabilities=("document_text", "document_layout", "document_scan"),
        package="fitz",
        notes="Lightweight native text/layout extraction for text-based PDFs; paired with RapidFuzz for topic matching.",
    ),
    ProviderMetadata(
        name="camelot",
        label="Camelot PDF table extraction",
        capabilities=("document_tables",),
        package="camelot",
        notes="Table parser for text/vector PDFs. May require Ghostscript for some lattice workflows.",
    ),
    ProviderMetadata(
        name="paddleocr",
        label="PaddleOCR PP-StructureV3",
        capabilities=("document_ocr", "layout_parsing"),
        package="paddleocr",
        notes="OCR/layout parser. First real run may download PaddleX model files.",
    ),
    ProviderMetadata(
        name="alphavantage",
        label="Alpha Vantage",
        capabilities=("quote",),
        required_env=("ALPHAVANTAGE_API_KEY",),
        optional_env=("ALPHA_VANTAGE_API_KEY",),
        notes="Realtime-ish quote fallback when an Alpha Vantage key is configured.",
    ),
    ProviderMetadata(
        name="alpaca",
        label="Alpaca Market Data",
        capabilities=("ohlcv",),
        required_env=("ALPACA_API_KEY", "ALPACA_API_SECRET"),
        optional_env=("APCA_API_KEY_ID", "APCA_API_SECRET_KEY", "ALPACA_DATA_FEED"),
        notes="OHLCV provider when Alpaca market-data credentials are configured.",
    ),
)


def list_sources() -> dict[str, Any]:
    """Return provider inventory without making network calls."""
    return {
        "sources": [_source_row(metadata) for metadata in PROVIDERS],
        "count": len(PROVIDERS),
    }


def sources_status() -> dict[str, Any]:
    """Return package/env configuration status without making network calls."""
    rows = [_status_row(metadata) for metadata in PROVIDERS]
    return {
        "sources": rows,
        "count": len(rows),
        "summary": _summary(rows),
    }


def test_source(name: str | None = None, *, symbol: str = "AAPL", timeout: float = 30.0) -> dict[str, Any]:
    """Run small provider connectivity checks."""
    selected = _selected_providers(name)
    results = [_test_one(metadata, symbol=symbol, timeout=timeout).to_dict() for metadata in selected]
    return {
        "symbol": symbol.upper(),
        "results": results,
        "count": len(results),
        "summary": _summary(results),
    }


def _source_row(metadata: ProviderMetadata) -> dict[str, Any]:
    row = metadata.to_dict()
    row["package_installed"] = _package_installed(metadata.package)
    return row


def _status_row(metadata: ProviderMetadata) -> dict[str, Any]:
    required = _env_rows(metadata.required_env)
    optional = _env_rows(metadata.optional_env)
    package_installed = _package_installed(metadata.package)
    configured = all(item["present"] for item in required) and package_installed
    status = "configured" if configured else "missing_config"
    return {
        "name": metadata.name,
        "label": metadata.label,
        "configured": configured,
        "status": status,
        "package": metadata.package,
        "package_installed": package_installed,
        "required_env": required,
        "optional_env": optional,
        "capabilities": list(metadata.capabilities),
        "notes": metadata.notes,
    }


def _test_one(metadata: ProviderMetadata, *, symbol: str, timeout: float) -> ProviderHealth:
    status = _status_row(metadata)
    if not status["configured"]:
        return ProviderHealth(
            name=metadata.name,
            configured=False,
            ok=False,
            status="missing_config",
            error=_missing_message(status),
            required_env=status["required_env"],
            optional_env=status["optional_env"],
            capabilities=metadata.capabilities,
        )
    probe = _probe_for(metadata.name, symbol=symbol, timeout=timeout)
    started = perf_counter()
    try:
        probe()
        return ProviderHealth(
            name=metadata.name,
            configured=True,
            ok=True,
            status="ok",
            latency_ms=round((perf_counter() - started) * 1000, 2),
            required_env=status["required_env"],
            optional_env=status["optional_env"],
            capabilities=metadata.capabilities,
        )
    except Exception as exc:
        return ProviderHealth(
            name=metadata.name,
            configured=True,
            ok=False,
            status="failed",
            latency_ms=round((perf_counter() - started) * 1000, 2),
            error=str(exc),
            required_env=status["required_env"],
            optional_env=status["optional_env"],
            capabilities=metadata.capabilities,
        )


def _probe_for(name: str, *, symbol: str, timeout: float) -> Probe:
    normalized = symbol.upper()
    if name == "yfinance":
        return lambda: YahooFinanceProvider(timeout=int(timeout)).quote(normalized)
    if name == "sec":
        return lambda: SecEdgarProvider(timeout=timeout).get_company(normalized)
    if name == "gdelt":
        return lambda: GdeltNewsProvider(max_records=1, timeout=timeout, min_interval_seconds=0, retry_count=0).search(
            f"{normalized} stock",
            max_records=1,
            timespan="1d",
        )
    if name == "motley_fool":
        return lambda: MotleyFoolTranscriptProvider(timeout=timeout).search(normalized, limit=1)
    if name == "company_ir":
        def probe_company_ir() -> list[dict[str, Any]]:
            quote = YahooFinanceProvider(timeout=int(timeout)).quote(normalized)
            return CompanyIRProvider(timeout=timeout, max_pages=2).list_presentations(
                normalized,
                company_name=quote.get("company_name"),
                website=quote.get("website"),
                ir_website=quote.get("ir_website"),
                limit=1,
            )
        return probe_company_ir
    if name == "fmp":
        return lambda: FMPProvider(timeout=timeout).analyst_estimates(normalized, limit=1)
    if name == "paddleocr":
        def probe_paddleocr() -> str:
            import paddleocr
            return str(getattr(paddleocr, "__version__", "unknown"))
        return probe_paddleocr
    if name == "pymupdf":
        def probe_pymupdf() -> str:
            import fitz
            import rapidfuzz

            return f"PyMuPDF {fitz.version[0]}, rapidfuzz {rapidfuzz.__version__}"
        return probe_pymupdf
    if name == "camelot":
        def probe_camelot() -> str:
            import camelot

            return str(getattr(camelot, "__version__", "unknown"))
        return probe_camelot
    if name == "alphavantage":
        return lambda: AlphaVantageProvider(timeout=timeout).realtime_quote(normalized)
    if name == "alpaca":
        return lambda: AlpacaMarketDataProvider(timeout=timeout).ohlcv(normalized, timeframe="1d", limit=1)
    raise ValueError(f"unknown source: {name}")


def _selected_providers(name: str | None) -> tuple[ProviderMetadata, ...]:
    if not name or name == "all":
        return PROVIDERS
    normalized = name.strip().lower()
    matches = tuple(metadata for metadata in PROVIDERS if metadata.name == normalized)
    if not matches:
        available = ", ".join(metadata.name for metadata in PROVIDERS)
        raise ValueError(f"unknown source: {name}. Available: {available}")
    return matches


def _env_rows(names: tuple[str, ...]) -> list[dict[str, Any]]:
    return [{"name": name, "present": bool(os.getenv(name))} for name in names]


def _package_installed(package: str | None) -> bool:
    if not package:
        return True
    return importlib.util.find_spec(package) is not None


def _missing_message(status: dict[str, Any]) -> str:
    missing_env = [item["name"] for item in status["required_env"] if not item["present"]]
    messages = []
    if status["package"] and not status["package_installed"]:
        messages.append(f"missing package: {status['package']}")
    if missing_env:
        messages.append("missing env: " + ", ".join(missing_env))
    return "; ".join(messages) or "source is not configured"


def _summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    total = len(rows)
    configured = sum(1 for row in rows if row.get("configured"))
    ok = sum(1 for row in rows if row.get("ok") is True)
    failed = sum(1 for row in rows if row.get("ok") is False)
    return {
        "total": total,
        "configured": configured,
        "ok": ok,
        "failed": failed,
        "missing_config": sum(1 for row in rows if row.get("status") == "missing_config"),
    }
