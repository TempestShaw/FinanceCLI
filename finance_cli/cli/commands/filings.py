"""SEC filings CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.filings import (
    fetch_filings,
    list_filing_reports,
    list_filing_sections,
    read_filing_report,
    read_filing_section,
    read_filing_statement,
)

def _filings_recent(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: filings.recent SYMBOL [forms=8-K,10-Q limit=20 classify=false]")
    kv = KVArgs(args[1:])
    data = fetch_filings(
        args[0],
        forms=kv.csv("forms") or None,
        limit=kv.int("limit", 20),
        classify=kv.bool("classify"),
    )
    return FinanceCommandResult(ok=True, data=data)


def _split_subject(args: list[str]) -> tuple[str | None, KVArgs]:
    if args and "=" not in args[0]:
        return args[0], KVArgs(args[1:])
    return None, KVArgs(args)


def _filing_lookup(args: list[str]) -> tuple[str | None, str | None, str | None, KVArgs]:
    symbol, kv = _split_subject(args)
    accession_no = kv.str("accession") or kv.str("accession_no")
    return symbol or kv.str("symbol"), accession_no, kv.str("url"), kv


def _missing_filing_source(usage: str) -> FinanceCommandResult:
    return FinanceCommandResult(ok=False, error=f"usage: {usage}")


def _filings_read(args: list[str]) -> FinanceCommandResult:
    symbol, accession_no, url, kv = _filing_lookup(args)
    if not symbol and not accession_no and not url:
        return _missing_filing_source("filings.read [SYMBOL] [accession=...|url=...] [form=10-K section=business max_chars=8000]")
    data = read_filing_section(
        symbol=symbol,
        accession_no=accession_no,
        url=url,
        form=kv.str("form", "10-K"),
        section=kv.str("section", "business"),
        max_chars=kv.int("max_chars", 8000),
    )
    return FinanceCommandResult(ok=True, data=data)


def _filings_sections(args: list[str]) -> FinanceCommandResult:
    symbol, accession_no, url, kv = _filing_lookup(args)
    if not symbol and not accession_no and not url:
        return _missing_filing_source("filings.sections [SYMBOL] [accession=...|url=...] [form=10-K]")
    data = list_filing_sections(
        symbol=symbol,
        accession_no=accession_no,
        url=url,
        form=kv.str("form", "10-K"),
    )
    return FinanceCommandResult(ok=True, data=data)


def _filings_statement(args: list[str]) -> FinanceCommandResult:
    symbol, accession_no, url, kv = _filing_lookup(args)
    if not symbol and not accession_no and not url:
        return _missing_filing_source("filings.statement [SYMBOL] [accession=...|url=...] [form=10-K statement=income|balance|cashflow query=... max_rows=0]")
    data = read_filing_statement(
        symbol=symbol,
        accession_no=accession_no,
        url=url,
        form=kv.str("form", "10-K"),
        statement=kv.str("statement", "income"),
        query=kv.str("query"),
        include_abstract=kv.bool("include_abstract"),
        max_rows=kv.int("max_rows", 0),
    )
    return FinanceCommandResult(ok=True, data=data)


def _filings_reports(args: list[str]) -> FinanceCommandResult:
    symbol, accession_no, url, kv = _filing_lookup(args)
    if not symbol and not accession_no and not url:
        return _missing_filing_source("filings.reports [SYMBOL] [accession=...|url=...] [form=10-K query=lease]")
    data = list_filing_reports(
        symbol=symbol,
        accession_no=accession_no,
        url=url,
        form=kv.str("form", "10-K"),
        query=kv.str("query"),
    )
    return FinanceCommandResult(ok=True, data=data)


def _filings_report(args: list[str]) -> FinanceCommandResult:
    symbol, accession_no, url, kv = _filing_lookup(args)
    name = kv.str("name") or kv.str("report")
    if (not symbol and not accession_no and not url) or not name:
        return _missing_filing_source("filings.report [SYMBOL] [accession=...|url=...] name='Consolidated Balance Sheets (Parenthetical)' [form=10-K query=... max_rows=25 (0=unlimited) max_chars=8000]")
    data = read_filing_report(
        symbol=symbol,
        accession_no=accession_no,
        url=url,
        form=kv.str("form", "10-K"),
        name=name,
        query=kv.str("query"),
        max_rows=kv.int("max_rows", 25),
        max_chars=kv.int("max_chars", 8000),
    )
    return FinanceCommandResult(ok=True, data=data)


def register_filings_commands() -> None:
    register_command(FinanceCommand(
        "filings.recent",
        "Fetch recent SEC filings, optionally classified",
        _filings_recent,
        usage="filings.recent SYMBOL [forms=8-K,10-Q limit=20 classify=false]",
        examples=(
            "finance filings.recent NVDA forms=10-Q,8-K limit=5",
            "finance filings.recent NVDA forms=8-K limit=10 classify=true",
        ),
    ))
    register_command(FinanceCommand(
        "filings.read",
        "Read a canonical 10-K section with edgartools",
        _filings_read,
        usage="filings.read [SYMBOL] [accession=...|url=...] [form=10-K section=business|risk_factors|mda|segments max_chars=8000]",
        examples=(
            "finance filings.read IOT section=business max_chars=3000",
            "finance filings.read accession=0001628280-26-018167 section=risk_factors max_chars=3000",
            "finance filings.read url=https://www.sec.gov/Archives/edgar/data/1642896/000162828026018167/iot-20260131.htm section=mda",
        ),
        notes=("Uses edgartools for filing retrieval, then returns bounded text for CLI/agent consumption.",),
    ))
    register_command(FinanceCommand(
        "filings.sections",
        "List supported and discovered filing sections",
        _filings_sections,
        usage="filings.sections [SYMBOL] [accession=...|url=...] [form=10-K]",
        examples=(
            "finance filings.sections IOT form=10-K",
            "finance filings.sections accession=0001628280-26-018167",
        ),
    ))
    register_command(FinanceCommand(
        "filings.statement",
        "Read structured XBRL statement rows with edgartools",
        _filings_statement,
        usage="filings.statement [SYMBOL] [accession=...|url=...] [form=10-K statement=income|balance|cashflow query=... max_rows=0]",
        examples=(
            "finance filings.statement COST statement=balance query='Common Stock'",
            "finance filings.statement url=https://www.sec.gov/Archives/edgar/data/909832/000090983224000049/cost-20240901.htm statement=income max_rows=20",
        ),
        notes=("Returns raw XBRL values plus reported values scaled by XBRL decimals.",),
    ))
    register_command(FinanceCommand(
        "filings.reports",
        "List edgartools filing summary reports",
        _filings_reports,
        usage="filings.reports [SYMBOL] [accession=...|url=...] [form=10-K query=lease]",
        examples=(
            "finance filings.reports COST form=10-K",
            "finance filings.reports COST form=10-K query=lease",
            "finance filings.reports url=https://www.sec.gov/Archives/edgar/data/909832/000090983224000049/cost-20240901.htm",
        ),
    ))
    register_command(FinanceCommand(
        "filings.report",
        "Read an edgartools filing summary report",
        _filings_report,
        usage="filings.report [SYMBOL] [accession=...|url=...] name='Report Short Name' [form=10-K query=... max_rows=25 (0=unlimited) max_chars=8000]",
        examples=(
            "finance filings.report COST name='Consolidated Balance Sheets (Parenthetical)'",
            "finance filings.report COST name='Leases, Supplemental Balance Sheet Information' query='operating lease liabilities'",
            "finance filings.report url=https://www.sec.gov/Archives/edgar/data/909832/000090983224000049/cost-20240901.htm name='Debt'",
        ),
    ))
