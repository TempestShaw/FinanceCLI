"""SEC filings services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.sec_edgar import SecEdgarProvider


def list_recent_filings(
    symbol: str,
    *,
    forms: list[str] | None = None,
    limit: int = 20,
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """List recent SEC filings for one symbol."""
    client = provider or SecEdgarProvider()
    filings = client.list_filings(symbol, forms=forms, limit=limit)
    company_name = next((filing.get("company_name") for filing in filings if filing.get("company_name")), None)
    cik = next((filing.get("cik") for filing in filings if filing.get("cik")), None)
    return {
        "symbol": symbol.upper(),
        "company_name": company_name,
        "cik": cik,
        "filings": [_compact_filing_row(filing) for filing in filings],
        "count": len(filings),
        "source": "sec_edgar",
    }


def classify_recent_filings(
    symbol: str,
    *,
    forms: list[str] | None = None,
    limit: int = 20,
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """List canonical filing events for one symbol."""
    client = provider or SecEdgarProvider()
    events = client.filing_events(symbol, forms=forms, limit=limit)
    return {"symbol": symbol.upper(), "events": events, "count": len(events), "source": "sec_edgar"}


def fetch_filings(
    symbol: str,
    *,
    forms: list[str] | None = None,
    limit: int = 20,
    classify: bool = False,
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """Fetch recent filings, optionally classified into event types."""
    if classify:
        return classify_recent_filings(symbol, forms=forms, limit=limit, provider=provider)
    return list_recent_filings(symbol, forms=forms, limit=limit, provider=provider)


def read_filing_section(
    *,
    symbol: str | None = None,
    accession_no: str | None = None,
    url: str | None = None,
    form: str = "10-K",
    section: str = "business",
    max_chars: int = 8000,
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """Read a canonical section from a filing."""
    client = provider or SecEdgarProvider()
    return client.read_filing_section(
        symbol=symbol,
        accession_no=accession_no,
        url=url,
        form=form,
        section=section,
        max_chars=max_chars,
    )


def list_filing_sections(
    *,
    symbol: str | None = None,
    accession_no: str | None = None,
    url: str | None = None,
    form: str = "10-K",
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """List canonical and provider-discovered filing sections."""
    client = provider or SecEdgarProvider()
    return client.filing_sections(symbol=symbol, accession_no=accession_no, url=url, form=form)


def read_filing_statement(
    *,
    symbol: str | None = None,
    accession_no: str | None = None,
    url: str | None = None,
    form: str = "10-K",
    statement: str = "income",
    query: str | None = None,
    include_abstract: bool = False,
    max_rows: int = 0,
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """Read structured XBRL statement rows from a filing."""
    client = provider or SecEdgarProvider()
    return client.filing_statement(
        symbol=symbol,
        accession_no=accession_no,
        url=url,
        form=form,
        statement=statement,
        query=query,
        include_abstract=include_abstract,
        max_rows=max_rows,
    )


def list_filing_reports(
    *,
    symbol: str | None = None,
    accession_no: str | None = None,
    url: str | None = None,
    form: str = "10-K",
    query: str | None = None,
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """List edgartools filing summary reports."""
    client = provider or SecEdgarProvider()
    return client.filing_reports(symbol=symbol, accession_no=accession_no, url=url, form=form, query=query)


def read_filing_report(
    *,
    symbol: str | None = None,
    accession_no: str | None = None,
    url: str | None = None,
    form: str = "10-K",
    name: str,
    query: str | None = None,
    max_rows: int = 25,
    max_chars: int = 8000,
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """Read one edgartools filing summary report."""
    client = provider or SecEdgarProvider()
    return client.read_filing_report(
        symbol=symbol,
        accession_no=accession_no,
        url=url,
        form=form,
        name=name,
        query=query,
        max_rows=max_rows,
        max_chars=max_chars,
    )


def _compact_filing_row(filing: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in filing.items()
        if key not in {"symbol", "company_name", "cik", "primary_document", "primary_doc_description"}
    }
