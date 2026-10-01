"""filings.recent must find filings that sit outside SEC's recent-submissions window."""
from __future__ import annotations

import pytest

from finance_cli.providers.base import ProviderError
from finance_cli.providers.sec_edgar import SecEdgarProvider

CIK = "0001326801"
MAIN_URL = f"https://data.sec.gov/submissions/CIK{CIK}.json"
PAGE_1 = f"CIK{CIK}-submissions-001.json"
PAGE_2 = f"CIK{CIK}-submissions-002.json"


def _columns(rows: list[tuple[str, str, str]]) -> dict[str, list[str]]:
    """Build SEC's columnar filing layout from (form, filing date, accession) rows."""
    return {
        "form": [r[0] for r in rows],
        "filingDate": [r[1] for r in rows],
        "reportDate": [r[1] for r in rows],
        "accessionNumber": [r[2] for r in rows],
        "primaryDocument": [f"doc-{r[2]}.htm" for r in rows],
        "primaryDocDescription": [r[0] for r in rows],
        "items": ["" for _ in rows],
    }


RECENT = _columns([
    ("4", "2026-02-01", "0000000000-26-000100"),
    ("10-K", "2026-01-29", "0001628280-26-003942"),
    ("4", "2025-06-01", "0000000000-25-000200"),
    ("10-K", "2025-01-30", "0001326801-25-000017"),
])
OLDER = _columns([
    ("4", "2024-05-01", "0000000000-24-000300"),
    ("10-K", "2024-02-02", "0001326801-24-000012"),
    ("10-K", "2023-02-02", "0001326801-23-000013"),
])
OLDEST = _columns([("10-K", "2022-02-03", "0001326801-22-000018")])


@pytest.fixture
def requests(monkeypatch):
    """Serve fake SEC JSON and record every URL requested."""
    seen: list[str] = []
    pages = {
        MAIN_URL: {"filings": {"recent": RECENT, "files": [
            {"name": PAGE_1, "filingCount": 3, "filingFrom": "2023-01-01", "filingTo": "2024-12-31"},
            {"name": PAGE_2, "filingCount": 1, "filingFrom": "2020-01-01", "filingTo": "2022-12-31"},
        ]}},
        f"https://data.sec.gov/submissions/{PAGE_1}": OLDER,
        f"https://data.sec.gov/submissions/{PAGE_2}": OLDEST,
    }

    def fake_get_json(self, url):
        seen.append(url)
        if url not in pages:
            raise ProviderError(f"SEC request failed: 404 for {url}")
        return pages[url]

    monkeypatch.setattr(SecEdgarProvider, "_get_json", fake_get_json)
    monkeypatch.setattr(SecEdgarProvider, "get_company", lambda self, symbol: {"cik_str": "1326801", "title": "Meta Platforms, Inc."})
    return seen, pages


def test_older_annual_reports_come_from_paginated_submission_files(requests):
    seen, _ = requests
    filings = SecEdgarProvider().list_filings("META", forms=["10-K"], limit=4)

    assert [f["accession_no"] for f in filings] == [
        "0001628280-26-003942", "0001326801-25-000017", "0001326801-24-000012", "0001326801-23-000013",
    ]
    assert [f["filed_at"] for f in filings] == ["2026-01-29", "2025-01-30", "2024-02-02", "2023-02-02"]
    assert filings[2]["url"] == "https://www.sec.gov/Archives/edgar/data/1326801/000132680124000012/doc-0001326801-24-000012.htm"
    # The limit was reached on the first older page, so the oldest page is never requested.
    assert seen == [MAIN_URL, f"https://data.sec.gov/submissions/{PAGE_1}"]


def test_all_pages_are_read_until_the_limit_is_met(requests):
    seen, _ = requests
    filings = SecEdgarProvider().list_filings("META", forms=["10-K"], limit=10)

    assert [f["filed_at"][:4] for f in filings] == ["2026", "2025", "2024", "2023", "2022"]
    assert len(seen) == 3


def test_recent_window_alone_is_used_when_it_satisfies_the_limit(requests):
    seen, _ = requests
    filings = SecEdgarProvider().list_filings("META", forms=["10-K"], limit=2)

    assert len(filings) == 2
    assert seen == [MAIN_URL]


def test_failed_older_page_is_reported_not_silently_dropped(requests):
    _, pages = requests
    del pages[f"https://data.sec.gov/submissions/{PAGE_1}"]

    with pytest.raises(ProviderError, match=PAGE_1):
        SecEdgarProvider().list_filings("META", forms=["10-K"], limit=4)


def test_companies_without_paginated_files_are_unchanged(monkeypatch):
    monkeypatch.setattr(SecEdgarProvider, "_get_json", lambda self, url: {"filings": {"recent": RECENT}})
    monkeypatch.setattr(SecEdgarProvider, "get_company", lambda self, symbol: {"cik_str": "1326801", "title": "Meta"})

    filings = SecEdgarProvider().list_filings("META", forms=["10-K"], limit=6)

    assert [f["accession_no"] for f in filings] == ["0001628280-26-003942", "0001326801-25-000017"]
