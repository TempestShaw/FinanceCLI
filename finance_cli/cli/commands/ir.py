"""IR presentation CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.ir import list_ir_presentations, read_ir_presentation


def _cmd_ir_presentations(args: list[str]) -> FinanceCommandResult:
    symbol: str | None = None
    kv_args = args
    if args and "=" not in args[0]:
        symbol = args[0].strip().upper()
        kv_args = args[1:]
    kv = KVArgs(kv_args)
    if not symbol:
        symbol = kv.str("symbol")
    if not symbol:
        return FinanceCommandResult(ok=False, error="symbol is required")
    limit = kv.int("limit", 20)
    source = kv.str("source", "auto") or "auto"
    try:
        data = list_ir_presentations(symbol, limit=limit, source=source)
        return FinanceCommandResult(ok=True, data=data, warnings=data.get("warnings") or [])
    except Exception as exc:
        return FinanceCommandResult(ok=False, error=str(exc))


def _cmd_ir_read(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    url = kv.str("url")
    if not url:
        return FinanceCommandResult(ok=False, error="url= is required")
    max_chars = kv.int("max_chars", 12000)
    ocr = kv.str("ocr", "off") or "off"
    try:
        data = read_ir_presentation(url, max_chars=max_chars, ocr=ocr)
        return FinanceCommandResult(ok=True, data=data, warnings=data.get("warnings") or [])
    except Exception as exc:
        return FinanceCommandResult(ok=False, error=str(exc))


def register_ir_commands() -> None:
    register_command(FinanceCommand(
        name="ir.presentations",
        summary="Discover IR and investor day presentations from SEC 8-K Exhibit 99 filings",
        handler=_cmd_ir_presentations,
        usage="ir.presentations SYMBOL [limit=20 source=auto|sec|company_ir|all]",
        examples=(
            "finance ir.presentations IOT",
            "finance ir.presentations IOT limit=10 source=all",
            "finance ir.presentations NVDA limit=5 source=sec",
        ),
        notes=(
            "Scans recent 8-K filings for Exhibit 99 files with presentation or slides keywords.",
            "source=auto uses SEC first, then company IR fallback when SEC finds no candidates.",
            "source=all combines SEC and company IR candidates.",
            "Press releases and earnings releases are filtered unless a distinct deck/slides signal is present.",
            "confidence: high = strong presentation signal, medium = weaker or conflicting signal.",
            "kind: investor_day | earnings_presentation | ir_presentation | exhibit_99",
            "Use ir.read url=URL to extract text from a candidate.",
        ),
    ))
    register_command(FinanceCommand(
        name="ir.read",
        summary="Extract text from an IR presentation exhibit URL",
        handler=_cmd_ir_read,
        usage="ir.read url=URL [max_chars=12000 ocr=off|auto|force]",
        examples=(
            "finance ir.read url=https://www.sec.gov/Archives/edgar/data/.../iot_investorday.htm",
            "finance ir.read url=https://www.sec.gov/Archives/edgar/data/.../deck.htm max_chars=20000",
            "finance ir.read url=https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/aapl-20260328.htm ocr=off max_chars=4000",
        ),
        notes=(
            "HTML exhibits/pages are fetched and parsed to plain text.",
            "PDF extraction uses pypdf and returns page-level text when possible.",
            "ocr=auto or ocr=force uses the default PaddleOCR/PP-StructureV3 stack.",
            "Pass the url from ir.presentations output.",
        ),
    ))
