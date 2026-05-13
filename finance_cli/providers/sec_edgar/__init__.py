"""SEC EDGAR provider and filing-event classifier.

This module keeps the public import path stable while implementation helpers
live in smaller, reviewable modules.
"""
from __future__ import annotations

import os
from io import BytesIO
from typing import Any

import httpx

from finance_cli.providers.base import ProviderError, quiet_call, require_dependency
from finance_cli.providers.native_pdf import NativePDFProvider
from finance_cli.providers.sec_edgar import common as _common
from finance_cli.providers.sec_edgar import events as _events
from finance_cli.providers.sec_edgar import exhibits as _exhibits
from finance_cli.providers.sec_edgar import reports as _reports
from finance_cli.providers.sec_edgar import sections as _sections
from finance_cli.providers.sec_edgar import statements as _statements

class SecEdgarProvider:
    """Direct SEC JSON API client for filings and event classification."""

    TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
    SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"

    def __init__(self, *, user_agent: str | None = None, timeout: float = 30.0) -> None:
        self.user_agent = user_agent or os.getenv(
            "FINANCE_SEC_USER_AGENT",
            "FinanceCLI/0.1 contact@example.com",
        )
        self.timeout = timeout
        self._ticker_cache: dict[str, dict[str, Any]] | None = None
        self._edgar_identity_set = False

    def list_filings(
        self,
        symbol: str,
        *,
        forms: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Fetch recent filings for a ticker from SEC company submissions JSON."""
        symbol = symbol.strip().upper()
        if not symbol:
            raise ProviderError("symbol is required")
        company = self.get_company(symbol)
        cik = f"{int(company['cik_str']):010d}"
        payload = self._get_json(self.SUBMISSIONS_URL.format(cik=cik))
        recent = payload.get("filings", {}).get("recent", {})
        rows = _events._zip_recent_filings(recent)
        wanted = {form.upper() for form in forms} if forms else set(_events.SUPPORTED_FORMS)
        filtered = [row for row in rows if str(row.get("form", "")).upper() in wanted]
        result = []
        for row in filtered[:limit]:
            accession = str(row.get("accessionNumber") or "")
            primary_doc = str(row.get("primaryDocument") or "")
            accession_path = accession.replace("-", "")
            filing_url = (
                f"https://www.sec.gov/Archives/edgar/data/{int(company['cik_str'])}/"
                f"{accession_path}/{primary_doc}"
                if accession and primary_doc
                else None
            )
            result.append(
                {
                    "symbol": symbol,
                    "company_name": company.get("title"),
                    "cik": cik,
                    "form": row.get("form"),
                    "accession_no": accession,
                    "filed_at": row.get("filingDate"),
                    "report_date": row.get("reportDate"),
                    "acceptance_datetime": row.get("acceptanceDateTime"),
                    "items": _events._split_items(row.get("items")),
                    "primary_document": primary_doc,
                    "primary_doc_description": row.get("primaryDocDescription"),
                    "url": filing_url,
                }
            )
        return result

    def filing_events(
        self,
        symbol: str,
        *,
        forms: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Classify recent filings into canonical event records."""
        events: list[dict[str, Any]] = []
        for filing in self.list_filings(symbol, forms=forms, limit=limit):
            events.extend(event.to_dict() for event in _events.classify_filing_event(filing))
        return events

    def read_filing_section(
        self,
        *,
        symbol: str | None = None,
        accession_no: str | None = None,
        url: str | None = None,
        form: str = "10-K",
        section: str = "business",
        max_chars: int = 8000,
    ) -> dict[str, Any]:
        """Read a canonical filing section using edgartools."""
        filing = self._get_filing(symbol=symbol, accession_no=accession_no, url=url, form=form)
        spec = _sections._normalize_section(section)
        text = self._extract_section_text(filing, spec)
        truncated_text = _common._truncate_text(text, max_chars=max_chars)
        return {
            "filing": _common._filing_metadata(filing),
            "section": {
                "key": spec.key,
                "title": spec.title,
                "edgar_section": spec.edgar_section,
            },
            "text": truncated_text,
            "char_count": len(text),
            "returned_chars": len(truncated_text),
            "truncated": len(truncated_text) < len(text),
            "source": "edgartools",
        }

    def filing_sections(
        self,
        *,
        symbol: str | None = None,
        accession_no: str | None = None,
        url: str | None = None,
        form: str = "10-K",
    ) -> dict[str, Any]:
        """List supported canonical sections and edgartools-discovered sections."""
        filing = self._get_filing(symbol=symbol, accession_no=accession_no, url=url, form=form)
        doc = quiet_call(filing.parse)
        available = _sections._available_sections(doc)
        supported = []
        for spec in _sections.FILING_SECTION_SPECS.values():
            try:
                text = self._extract_section_text(filing, spec)
            except Exception:
                text = ""
            supported.append({
                "key": spec.key,
                "title": spec.title,
                "edgar_section": spec.edgar_section,
                "available": bool(text.strip()),
                "char_count": len(text),
            })
        return {
            "filing": _common._filing_metadata(filing),
            "supported_sections": supported,
            "edgartools_sections": available,
            "source": "edgartools",
        }

    def filing_statement(
        self,
        *,
        symbol: str | None = None,
        accession_no: str | None = None,
        url: str | None = None,
        form: str = "10-K",
        statement: str = "income",
        query: str | None = None,
        include_abstract: bool = False,
        max_rows: int = 0,
    ) -> dict[str, Any]:
        """Return structured XBRL statement rows from an annual/quarterly filing."""
        filing = self._get_filing(symbol=symbol, accession_no=accession_no, url=url, form=form)
        statement_key, statement_obj = _statements._get_statement_object(filing, statement)
        raw_rows = quiet_call(statement_obj.get_raw_data)
        rows = _statements._shape_statement_rows(
            raw_rows,
            query=query,
            include_abstract=include_abstract,
            max_rows=max_rows,
        )
        return {
            "filing": _common._filing_metadata(filing),
            "statement": statement_key,
            "periods": _statements._statement_periods(raw_rows),
            "rows": rows,
            "count": len(rows),
            "truncated": max_rows > 0 and len(rows) >= max_rows,
            "source": "edgartools",
        }

    def filing_reports(
        self,
        *,
        symbol: str | None = None,
        accession_no: str | None = None,
        url: str | None = None,
        form: str = "10-K",
        query: str | None = None,
    ) -> dict[str, Any]:
        """List edgartools filing summary reports for a filing."""
        filing = self._get_filing(symbol=symbol, accession_no=accession_no, url=url, form=form)
        reports = _reports._get_filing_reports(filing)
        shaped_reports = _reports._shape_report_list(reports, query=query)
        return {
            "filing": _common._filing_metadata(filing),
            "reports": shaped_reports,
            "count": len(shaped_reports),
            "query": query,
            "source": "edgartools",
        }

    def read_filing_report(
        self,
        *,
        symbol: str | None = None,
        accession_no: str | None = None,
        url: str | None = None,
        form: str = "10-K",
        name: str,
        query: str | None = None,
        max_rows: int = 25,
        max_chars: int = 8000,
    ) -> dict[str, Any]:
        """Read one edgartools filing summary report by short name."""
        filing = self._get_filing(symbol=symbol, accession_no=accession_no, url=url, form=form)
        reports = _reports._get_filing_reports(filing)
        report = _reports._find_report(reports, name)
        text = _reports._report_text(report)
        rows = _reports._report_rows(report, query=query, max_rows=max_rows)
        truncated_text = _common._truncate_text(text, max_chars=max_chars)
        return {
            "filing": _common._filing_metadata(filing),
            "report": _reports._shape_report(report),
            "text": truncated_text,
            "rows": rows,
            "row_count": len(rows),
            "row_query": query,
            "rows_truncated": max_rows > 0 and len(rows) >= max_rows,
            "char_count": len(text),
            "returned_chars": len(truncated_text),
            "truncated": len(truncated_text) < len(text),
            "source": "edgartools",
        }

    def list_exhibit_candidates(
        self,
        symbol: str,
        *,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Scan recent 8-K filings for Exhibit 99 presentation candidates."""
        company = self.get_company(symbol)
        cik_int = int(company["cik_str"])
        filings = self.list_filings(symbol, forms=["8-K"], limit=limit)
        candidates = []
        for filing in filings:
            accession_no = filing.get("accession_no") or ""
            if not accession_no:
                continue
            exhibits = self._fetch_filing_index(cik_int=cik_int, accession_no=accession_no)
            for exhibit in exhibits:
                score = _exhibits._score_exhibit_candidate(exhibit)
                if score is None:
                    continue
                description = str(exhibit.get("description") or "")
                filename = str(exhibit.get("document") or "")
                if not filename:
                    continue
                accession_path = accession_no.replace("-", "")
                exhibit_url = (
                    f"https://www.sec.gov/Archives/edgar/data/{cik_int}"
                    f"/{accession_path}/{filename}"
                )
                candidates.append({
                    "title": _exhibits._exhibit_display_title(description, filename),
                    "date": filing.get("filed_at"),
                    "report_date": filing.get("report_date"),
                    "kind": _exhibits._classify_exhibit_kind(description, filename),
                    "source": "sec_edgar",
                    "url": exhibit_url,
                    "filing_url": filing.get("url"),
                    "filing_accession": accession_no,
                    "filing_items": filing.get("items") or [],
                    "exhibit": exhibit.get("type"),
                    "document": filename,
                    "size": exhibit.get("size"),
                    "confidence": score["confidence"],
                    "why_matched": score["reason"],
                    "warnings": score.get("warnings", []),
                })
        return sorted(candidates, key=_exhibits._candidate_sort_key)

    def _fetch_filing_index(self, *, cik_int: int, accession_no: str) -> list[dict[str, Any]]:
        """Fetch the per-filing exhibit list by parsing the EDGAR HTML filing index."""
        accession_path = accession_no.replace("-", "")
        url = (
            f"https://www.sec.gov/Archives/edgar/data/{cik_int}"
            f"/{accession_path}/{accession_no}-index.html"
        )
        try:
            response = httpx.get(
                url, headers={"User-Agent": self.user_agent}, timeout=self.timeout
            )
            response.raise_for_status()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            return _exhibits._parse_filing_index_html(soup)
        except Exception:
            return []

    def read_exhibit_text(self, url: str, *, max_chars: int = 12000) -> dict[str, Any]:
        """Fetch an exhibit URL and extract plain text from HTML or PDF."""
        if url.lower().endswith(".pdf"):
            return self._read_pdf_text(url, max_chars=max_chars)
        try:
            response = httpx.get(
                url, headers={"User-Agent": self.user_agent}, timeout=self.timeout
            )
            response.raise_for_status()
            raw = response.text
        except Exception as exc:
            raise ProviderError(f"exhibit fetch failed: {exc}") from exc

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(["script", "style", "meta", "link"]):
            tag.decompose()
        text = _common._clean_text(soup.get_text(separator="\n"))
        pages = _common._shape_text_pages([text], max_chars=max_chars)
        truncated_text = "\n\n".join(page["text"] for page in pages)
        warnings = []
        if len(text) < 500:
            warnings.append(
                "Extracted text is very short; this exhibit may be image-based, a wrapper, or not a full deck."
            )
        return {
            "url": url,
            "text": truncated_text,
            "char_count": len(text),
            "returned_chars": len(truncated_text),
            "truncated": len(truncated_text) < len(text),
            "format": "html",
            "pages": pages,
            "warnings": warnings,
        }

    def _read_pdf_text(self, url: str, *, max_chars: int) -> dict[str, Any]:
        warnings = []
        try:
            response = httpx.get(
                url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout,
                follow_redirects=True,
            )
            response.raise_for_status()
            raw = response.content
        except Exception as exc:
            return _common._empty_pdf_result(url, f"PDF fetch failed: {exc}")

        try:
            return NativePDFProvider(timeout=self.timeout).read_bytes(url, raw, max_chars=max_chars)
        except Exception:
            pass

        try:
            pypdf = require_dependency(
                "pypdf",
                "Install or repair Finance CLI with: python -m pip install -U finance-cli",
            )
            reader = pypdf.PdfReader(BytesIO(raw))
            raw_pages = [_common._clean_text(page.extract_text() or "") for page in reader.pages]
        except Exception as exc:
            return _common._empty_pdf_result(url, f"PDF text extraction failed: {exc}")

        char_count = sum(len(page) for page in raw_pages)
        if char_count == 0:
            warnings.append("PDF text extraction returned no text; the deck may be scanned or image-based.")
        elif char_count < 500:
            warnings.append("Extracted PDF text is very short; the deck may be image-heavy or text extraction may be incomplete.")
        pages = _common._shape_text_pages(raw_pages, max_chars=max_chars)
        text = "\n\n".join(page["text"] for page in pages)
        return {
            "url": url,
            "text": text or None,
            "char_count": char_count,
            "returned_chars": len(text),
            "truncated": len(text) < char_count,
            "format": "pdf",
            "pages": pages,
            "warnings": warnings,
        }

    def get_company(self, symbol: str) -> dict[str, Any]:
        """Resolve a ticker to SEC company metadata."""
        symbol = symbol.strip().upper()
        if self._ticker_cache is None:
            records = self._get_json(self.TICKERS_URL)
            self._ticker_cache = {
                str(record.get("ticker", "")).upper(): record
                for record in records.values()
                if isinstance(record, dict)
            }
        company = self._ticker_cache.get(symbol)
        if not company:
            raise ProviderError(f"SEC ticker not found: {symbol}")
        return company

    def _get_filing(
        self,
        *,
        symbol: str | None,
        accession_no: str | None,
        url: str | None,
        form: str,
    ) -> Any:
        edgar = self._edgar()
        accession = _sections._normalize_accession(accession_no) or _sections._accession_from_url(url)
        try:
            if accession:
                return quiet_call(edgar.get_by_accession_number, accession)
            if not symbol:
                raise ProviderError("symbol, accession_no, or url is required")
            company = quiet_call(edgar.Company, symbol.strip().upper())
            filings = quiet_call(company.get_filings, form=form)
            return quiet_call(filings.latest)
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"edgartools filing request failed: {exc}") from exc

    def _extract_section_text(self, filing: Any, spec: _sections.FilingSectionSpec) -> str:
        if spec.key == "segments":
            return _sections._extract_segments_text(filing)

        try:
            obj = quiet_call(filing.obj)
            if spec.tenk_attr and hasattr(obj, spec.tenk_attr):
                value = getattr(obj, spec.tenk_attr)
                if isinstance(value, str) and value.strip():
                    return _common._clean_text(value)
        except Exception:
            pass

        doc = quiet_call(filing.parse)
        if spec.edgar_section and hasattr(doc, "get_sec_section"):
            value = doc.get_sec_section(spec.edgar_section)
            if isinstance(value, str) and value.strip():
                return _common._clean_text(value)
        raise ProviderError(f"section not available: {spec.key}")

    def _edgar(self) -> Any:
        edgar = quiet_call(
            require_dependency,
            "edgar",
            "Install or repair Finance CLI with: python -m pip install -U finance-cli",
        )
        if not self._edgar_identity_set and hasattr(edgar, "set_identity"):
            quiet_call(edgar.set_identity, self.user_agent)
            self._edgar_identity_set = True
        return edgar

    def _get_json(self, url: str) -> dict[str, Any]:
        headers = {"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"}
        try:
            response = httpx.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ProviderError(f"SEC request failed: {exc}") from exc
        if not isinstance(payload, dict):
            raise ProviderError("SEC response was not a JSON object")
        return payload
