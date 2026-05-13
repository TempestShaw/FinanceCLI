"""Document OCR CLI commands."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.documents import extract_document_tables, ocr_document, read_document, scan_document, window_document

SOURCE_REQUIRED_ERROR = "source=, path=, url=, or positional document path/URL is required"


def _source_and_kv(args: list[str]) -> tuple[str | None, KVArgs]:
    source = args[0] if args and "=" not in args[0] else None
    kv_args = args[1:] if source else args
    kv = KVArgs(kv_args)
    source = source or kv.str("source") or kv.str("path") or kv.str("url")
    return source, kv


def _document_result(
    args: list[str],
    call: Callable[[str, KVArgs], dict[str, Any]],
) -> FinanceCommandResult:
    source, kv = _source_and_kv(args)
    if not source:
        return FinanceCommandResult(ok=False, error=SOURCE_REQUIRED_ERROR)
    try:
        data = call(source, kv)
        return FinanceCommandResult(ok=True, data=data, warnings=data.get("warnings") or [])
    except Exception as exc:
        return FinanceCommandResult(ok=False, error=str(exc))


def _cmd_document_read(args: list[str]) -> FinanceCommandResult:
    return _document_result(
        args,
        lambda source, kv: read_document(
            source,
            max_chars=kv.int("max_chars", 12000),
            max_pages=kv.int("max_pages", 0) or None,
            doc_format=kv.str("format"),
        ),
    )


def _cmd_document_scan(args: list[str]) -> FinanceCommandResult:
    def call(source: str, kv: KVArgs) -> dict[str, Any]:
        query = kv.str("query")
        topics = ([query] if query else None) or kv.csv("topics") or kv.csv("topic") or []
        return scan_document(
            source,
            topics=topics or None,
            threshold=kv.float("threshold", 80.0),
            max_chars=kv.int("max_chars", 12000),
            max_pages=kv.int("max_pages", 0) or None,
            limit=kv.int("limit", 50),
            window_chars=kv.int("window", 0),
            match_mode=kv.str("match", "fuzzy") or "fuzzy",
            start_char=kv.int("start_char", 0) if kv.str("start_char") is not None else None,
            end_char=kv.int("end_char", 0) if kv.str("end_char") is not None else None,
            doc_format=kv.str("format"),
        )

    return _document_result(args, call)


def _cmd_document_window(args: list[str]) -> FinanceCommandResult:
    def call(source: str, kv: KVArgs) -> dict[str, Any]:
        raw_start = kv.str("start_char") or kv.str("start")
        return window_document(
            source,
            start_char=int(raw_start) if raw_start is not None else None,
            match_id=kv.str("match_id"),
            chars=kv.int("chars", 4000),
            direction=kv.str("direction", "around") or "around",
            doc_format=kv.str("format"),
        )

    return _document_result(args, call)


def _cmd_document_ocr(args: list[str]) -> FinanceCommandResult:
    return _document_result(
        args,
        lambda source, kv: ocr_document(
            source,
            max_chars=kv.int("max_chars", 12000),
            max_pages=kv.int("max_pages", 0) or None,
        ),
    )


def _cmd_document_tables(args: list[str]) -> FinanceCommandResult:
    return _document_result(
        args,
        lambda source, kv: extract_document_tables(
            source,
            pages=kv.str("pages", "1-end") or "1-end",
            flavor=kv.str("flavor", "stream") or "stream",
            max_tables=kv.int("max_tables", 20),
            max_rows=kv.int("max_rows", 25),
        ),
    )


def register_document_commands() -> None:
    register_command(FinanceCommand(
        name="document.read",
        summary="Extract native PDF or HTML text and layout/search blocks",
        handler=_cmd_document_read,
        usage="document.read SOURCE|source=PATH_OR_URL [format=pdf|html max_chars=12000 max_pages=5]",
        examples=(
            "finance document.read ./deck.pdf max_pages=3",
            "finance document.read url=https://example.com/deck.pdf max_chars=4000",
            "finance document.read url=https://www.sec.gov/.../filing.htm format=html max_chars=4000",
        ),
        notes=(
            "Lightweight first-pass parser for text-based PDFs and HTML filings; does not run OCR.",
            "Returns page text plus positioned or offset-bearing blocks for downstream matching or agent analysis.",
        ),
    ))
    register_command(FinanceCommand(
        name="document.scan",
        summary="Scan document text/layout for configured topics or literal queries with RapidFuzz",
        handler=_cmd_document_scan,
        usage="document.scan SOURCE|source=PATH_OR_URL [query=... topics=risk,disclosure format=pdf|html match=fuzzy|all_terms threshold=80 max_chars=12000 max_pages=5 limit=50 window=0 start_char=0 end_char=0]",
        examples=(
            "finance document.scan ./report.pdf topics=risk,financial_reporting",
            "finance document.scan ./deck.pdf topics=guidance threshold=75 max_pages=10",
            "finance document.scan url=https://www.sec.gov/.../filing.htm format=html query='Operating lease costs' max_chars=0 window=1200",
            "finance document.scan url=https://www.sec.gov/.../filing.htm format=html match=all_terms threshold=100 query='Receivables net Total current assets' max_chars=0",
            "finance document.scan url=https://www.sec.gov/.../filing.htm format=html start_char=122000 query='Accounts payable'",
        ),
        notes=(
            "Uses PyMuPDF for native PDF layout, BeautifulSoup for HTML text, and RapidFuzz for deterministic fuzzy matching.",
            "Known topics include disclosure, risk, financial_reporting, portfolio, and guidance.",
            "Unknown topics are treated as literal fuzzy queries.",
            "Use match=all_terms threshold=100 for table-style queries where every meaningful query word should appear.",
            "Use start_char/end_char to restrict a follow-up scan to a known section or window.",
            "HTML matches include char offsets and match IDs that can be passed to document.window.",
        ),
    ))
    register_command(FinanceCommand(
        name="document.window",
        summary="Read a bounded text window around a document offset or scan match ID",
        handler=_cmd_document_window,
        usage="document.window SOURCE|source=PATH_OR_URL [format=pdf|html start_char=0|match_id=char_START_END chars=4000 direction=around|next|previous]",
        examples=(
            "finance document.window url=https://www.sec.gov/.../filing.htm format=html start_char=52000 chars=4000",
            "finance document.window url=https://www.sec.gov/.../filing.htm format=html match_id=char_52000_52200 direction=next chars=4000",
        ),
        notes=(
            "Designed for agentic continuation reading after document.scan.",
            "Use direction=next or direction=previous to move through a table or section without re-scanning.",
        ),
    ))
    register_command(FinanceCommand(
        name="document.tables",
        summary="Extract compact table previews from text-based PDFs with Camelot",
        handler=_cmd_document_tables,
        usage="document.tables SOURCE|source=PATH_OR_URL [pages=1-end flavor=stream|lattice max_tables=20 max_rows=25]",
        examples=(
            "finance document.tables ./report.pdf pages=10-12 flavor=stream",
            "finance document.tables ./filing.pdf pages=all max_tables=5 max_rows=10",
        ),
        notes=(
            "Uses the default Finance CLI table extraction stack.",
            "Use flavor=stream for whitespace-separated tables and flavor=lattice for ruled-line tables.",
            "Returns compact row previews with page, shape, accuracy, and truncation metadata.",
        ),
    ))
    register_command(FinanceCommand(
        name="document.ocr",
        summary="Run PaddleOCR/PP-StructureV3 OCR fallback on a local or remote document",
        handler=_cmd_document_ocr,
        usage="document.ocr SOURCE|source=PATH_OR_URL [max_chars=12000 max_pages=5]",
        examples=(
            "finance document.ocr ./deck.pdf max_pages=3",
            "finance document.ocr url=https://example.com/deck.pdf max_chars=4000",
        ),
        notes=(
            "Prefer document.read or document.scan for text-based PDFs.",
            "Uses the default Finance CLI OCR stack.",
            "Use as fallback for scanned or image-heavy documents.",
        ),
    ))
