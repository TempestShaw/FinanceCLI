"""Walk SEC company submissions across the recent window and older pages.

``data.sec.gov/submissions/CIK##########.json`` holds roughly the latest 1,000
filings under ``filings.recent``. Older filings live in paginated files listed
under ``filings.files``. Companies with many insider (Form 3/4/5) filings push
their older 10-Ks out of the recent window, so a form-filtered lookup has to
read those pages too.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from finance_cli.providers.base import ProviderError
from finance_cli.providers.sec_edgar.events import _zip_recent_filings

PAGE_URL = "https://data.sec.gov/submissions/{name}"


def matching_filing_rows(
    payload: dict[str, Any],
    *,
    wanted_forms: set[str],
    limit: int,
    fetch_json: Callable[[str], dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return up to ``limit`` filing rows of the wanted forms, newest first.

    Older pages are fetched only while the limit is still unmet, newest page
    first. A failed page raises ``ProviderError`` rather than returning a
    silently incomplete list.
    """
    filings = payload.get("filings", {})
    matches = _filter(_zip_recent_filings(filings.get("recent", {})), wanted_forms)
    for page in _pages_newest_first(filings.get("files")):
        if len(matches) >= limit:
            break
        name = page["name"]
        try:
            columns = fetch_json(PAGE_URL.format(name=name))
        except ProviderError as exc:
            raise ProviderError(f"SEC submissions page {name} could not be read: {exc}") from exc
        matches = [*matches, *_filter(_zip_recent_filings(columns), wanted_forms)]
    return sorted(matches, key=lambda row: str(row.get("filingDate") or ""), reverse=True)[:limit]


def _filter(rows: list[dict[str, Any]], wanted_forms: set[str]) -> list[dict[str, Any]]:
    return [row for row in rows if str(row.get("form", "")).upper() in wanted_forms]


def _pages_newest_first(files: Any) -> list[dict[str, Any]]:
    if not isinstance(files, list):
        return []
    pages = [page for page in files if isinstance(page, dict) and page.get("name")]
    return sorted(pages, key=lambda page: str(page.get("filingTo") or ""), reverse=True)
