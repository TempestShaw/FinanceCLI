"""Bounded discovery of public company news and event feeds."""
from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import re
from typing import Any
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import httpx
from bs4 import BeautifulSoup

from finance_cli.providers.base import ProviderError
from finance_cli.providers.company_ir import (
    CompanyIRProvider, _candidate_start_urls, _domain_allowed, _normalize_url, _registrable_domain,
)
from finance_cli.providers.yahoo import YahooFinanceProvider


class IRFeedProvider:
    """Follow company-linked RSS/Atom feeds and concrete news/event links."""

    name = "ir_feed"

    def __init__(self, *, timeout: float = 15.0, max_pages: int = 8) -> None:
        self.timeout = timeout
        self.max_pages = max_pages

    def list_releases(self, symbol: str, *, url: str | None = None, limit: int = 20) -> dict[str, Any]:
        return self._list(symbol, kind="release", url=url, limit=limit)

    def list_events(self, symbol: str, *, url: str | None = None, limit: int = 20) -> dict[str, Any]:
        return self._list(symbol, kind="event", url=url, limit=limit)

    def _list(self, symbol: str, *, kind: str, url: str | None, limit: int) -> dict[str, Any]:
        symbol = symbol.strip().upper()
        if not symbol or limit < 1:
            raise ProviderError("symbol is required and limit must be positive")
        warnings: list[str] = []
        if url:
            if not re.match(r"^https?://", url, re.IGNORECASE):
                raise ProviderError("url must be an HTTP or HTTPS company page or feed")
            starts = [_normalize_url(url)]
        else:
            try:
                profile = YahooFinanceProvider().quote(symbol)
            except Exception as exc:
                raise ProviderError(f"Company profile unavailable; pass url=PAGE_OR_FEED: {exc}") from exc
            starts = _candidate_start_urls(website=profile.get("website"), ir_website=profile.get("ir_website"))
            website = _normalize_url(str(profile.get("website") or ""))
            if website:
                starts.insert(1 if profile.get("ir_website") else 0, website)
            if not starts:
                raise ProviderError("Company profile has no website; pass url=PAGE_OR_FEED")

        queue = deque(dict.fromkeys(starts))
        domains = {_registrable_domain(start) for start in starts}
        visited: set[str] = set()
        rows: list[dict[str, Any]] = []
        html_rows: list[dict[str, Any]] = []
        retrieved_at = datetime.now(timezone.utc).isoformat()
        successful_pages = 0
        while queue and len(visited) < self.max_pages and len(rows) < limit:
            page_url = queue.popleft()
            if not page_url or page_url in visited:
                continue
            visited.add(page_url)
            try:
                response = httpx.get(page_url, headers={"User-Agent": CompanyIRProvider.USER_AGENT},
                                     timeout=self.timeout, follow_redirects=True)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                warnings.append(f"Could not fetch {page_url}: {exc}")
                continue
            actual_url = str(response.url)
            try:
                root = ElementTree.fromstring(response.content)
            except ElementTree.ParseError:
                root = None
            if root is not None and _tag(root) in {"rss", "feed", "RDF"}:
                successful_pages += 1
                feed_title = _child_text(root.find("channel") if _tag(root) == "rss" else root, "title")
                feed_kind = _kind(f"{feed_title} {actual_url}")
                if feed_kind and feed_kind != kind:
                    warnings.append(f"Skipped a {feed_kind} feed for requested {kind} items: {actual_url}")
                    continue
                if not feed_kind:
                    warnings.append("Feed category is unspecified; entries are returned under the requested kind.")
                rows.extend(_feed_rows(root, actual_url, symbol, kind, retrieved_at))
                continue
            if "xml" in response.headers.get("content-type", "").lower():
                warnings.append(f"Could not parse RSS/Atom feed: {actual_url}")
                continue
            if "html" not in response.headers.get("content-type", "").lower() and "<html" not in response.text.lower():
                warnings.append(f"Not an RSS/Atom feed or HTML page: {actual_url}")
                continue
            successful_pages += 1
            soup = BeautifulSoup(response.text, "html.parser")
            feeds, navigation = [], []
            for link in soup.find_all(["a", "link"]):
                href = str(link.get("href") or "").strip()
                absolute = _normalize_url(urljoin(actual_url, href)) if href else ""
                if not absolute or absolute in visited:
                    continue
                label = link.get_text(" ", strip=True) or str(link.get("title") or "")
                combined = f"{label} {absolute}"
                link_kind = _kind(combined)
                if link_kind and link_kind != kind:
                    continue
                is_feed = bool(re.search(r"rss|atom|\.xml(?:$|\?)", combined, re.IGNORECASE)) or "xml" in str(link.get("type") or "")
                if link.name == "link" and not is_feed:
                    continue
                if is_feed:
                    feeds.append(absolute)
                elif _domain_allowed(absolute, domains):
                    if _item_link(absolute, kind) and label:
                        html_rows.append({"symbol": symbol, "kind": kind, "title": label, "url": absolute,
                                     "date": None, "timestamp": None, "source_url": actual_url,
                                     "source": self.name, "retrieved_at": retrieved_at})
                    elif re.search(r"investor|\bir\b|news|release|event|rss", f"{label} {urlparse(absolute).path}", re.IGNORECASE):
                        navigation.append(absolute)
            feeds.sort(key=lambda target: bool(re.search(r"press[\s_/-]*release" if kind == "release" else r"event", target, re.IGNORECASE)), reverse=True)
            queue.extendleft(reversed(feeds + navigation))
        if not successful_pages:
            raise ProviderError("No company page or feed could be read. " + "; ".join(warnings))
        if len(visited) >= self.max_pages and any(target not in visited for target in queue):
            warnings.append("Discovery reached the page limit; additional company pages or feeds may contain more items.")
        rows = rows or html_rows
        unique = {row["url"]: row for row in reversed(rows)}
        rows = sorted(unique.values(), key=lambda row: row.get("timestamp") or "", reverse=True)[:limit]
        if any(row.get("timestamp") is None for row in rows):
            warnings.append("Some items have no parseable publication/event date; no date was inferred.")
        if not rows:
            warnings.append("No matching items discovered within the page limit; this does not establish that none exist. Try url=PAGE_OR_FEED.")
        if kind == "event":
            warnings.append("Feed dates may be publication or update dates, not scheduled event times; inspect the linked event page.")
        return {"symbol": symbol, "source": self.name, "source_url": rows[0]["source_url"] if rows else starts[0], "kind": kind,
                "rows": rows, "count": len(rows), "retrieved_at": retrieved_at,
                "pages_visited": len(visited), "warnings": list(dict.fromkeys(warnings))}


def _tag(element: ElementTree.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _child_text(element: ElementTree.Element | None, name: str) -> str:
    if element is None:
        return ""
    return next(("".join(child.itertext()).strip() for child in element if _tag(child) == name), "")


def _kind(text: str) -> str | None:
    text = text.lower()
    if re.search(r"sec[\s_/-]*filing", text):
        return "filing"
    if re.search(r"event|webcast|conference", text):
        return "event"
    if "presentation" in text:
        return "presentation"
    if re.search(r"news|press[\s_/-]*release", text):
        return "release"
    return None


def _item_link(url: str, kind: str) -> bool:
    pattern = r"/(?:news-details|press-releases?)/(?!default\.|index\.|$).+" if kind == "release" else r"/event-details?/(?!default\.|index\.|$).+"
    return bool(re.search(pattern, url, re.IGNORECASE))


def _feed_rows(root: ElementTree.Element, url: str, symbol: str, kind: str, retrieved_at: str) -> list[dict[str, Any]]:
    rows = []
    for item in root.iter():
        if _tag(item) not in {"item", "entry"}:
            continue
        title = _child_text(item, "title")
        content_type = _child_text(item, "contentType")
        if kind == "release" and content_type.lower() in {"blog", "blogs"}:
            continue
        link = _child_text(item, "link")
        if not link:
            link = next((child.get("href", "") for child in item if _tag(child) == "link" and child.get("rel", "alternate") == "alternate"), "")
        if not title or not link:
            continue
        date_fields = ((tag, _child_text(item, tag)) for tag in ("pubDate", "published", "updated", "date"))
        date_tag, raw_date = next(((tag, value) for tag, value in date_fields if value), (None, ""))
        date_kind = {"pubDate": "feed_publication_date", "published": "feed_publication_date",
                     "updated": "feed_updated_date", "date": "feed_date"}.get(date_tag)
        timestamp = _timestamp(raw_date)
        summary = _child_text(item, "description") or _child_text(item, "summary")
        if "<" in summary:
            summary = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)
        rows.append({"symbol": symbol, "kind": kind, "title": title, "url": urljoin(url, link),
                     "date": timestamp[:10] if timestamp else None, "timestamp": timestamp,
                     "date_kind": date_kind, "raw_date": raw_date or None, "raw_date_tag": date_tag,
                     "content_type": content_type or None,
                     "summary": summary[:2000],
                     "source": "ir_feed", "source_url": url, "retrieved_at": retrieved_at})
    return rows


def _timestamp(text: str) -> str | None:
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(text)
        except (ValueError, TypeError):
            return None
    # Preserve a date-only/naive value without inventing its timezone.
    return parsed.date().isoformat() if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) else parsed.isoformat()
