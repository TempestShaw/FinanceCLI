"""Conservative company investor-relations page discovery."""
from __future__ import annotations

import re
import os
from collections import deque
from datetime import date
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

from finance_cli.providers.base import ProviderError
from finance_cli.providers.config import PRESENTATION_RULES
from finance_cli.providers.fuzzy_terms import best_fuzzy_term, has_fuzzy_term
from finance_cli.providers.sec_edgar.exhibits import _classify_exhibit_kind


class CompanyIRProvider:
    """Best-effort public company IR website crawler with tight guardrails."""

    name = "company_ir"
    USER_AGENT = os.getenv("FINANCE_USER_AGENT", "FinanceCLI/0.1 contact@example.com")

    def __init__(self, *, timeout: float = 15.0, max_pages: int = 12) -> None:
        self.timeout = timeout
        self.max_pages = max_pages

    def list_presentations(
        self,
        symbol: str,
        *,
        company_name: str | None = None,
        website: str | None = None,
        ir_website: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Discover presentation-like links from company IR pages."""
        start_urls = _candidate_start_urls(website=website, ir_website=ir_website)
        if not start_urls:
            return []

        allowed_domains = {_registrable_domain(url) for url in start_urls if _registrable_domain(url)}
        visited: set[str] = set()
        queue: deque[str] = deque(start_urls)
        candidates: list[dict[str, Any]] = []

        while queue and len(visited) < self.max_pages and len(candidates) < limit * 3:
            page_url = queue.popleft()
            normalized_page = _normalize_url(page_url)
            if not normalized_page or normalized_page in visited:
                continue
            if not _domain_allowed(normalized_page, allowed_domains):
                continue
            visited.add(normalized_page)
            try:
                html = self._fetch_html(normalized_page)
            except ProviderError:
                continue

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            page_title = _clean_text(soup.title.get_text(" ", strip=True) if soup.title else "")
            for link in soup.find_all("a"):
                href = str(link.get("href") or "").strip()
                absolute = _normalize_url(urljoin(normalized_page, href))
                if not absolute:
                    continue
                label = _clean_text(link.get_text(" ", strip=True))
                score = _score_ir_link(label=label, url=absolute)
                allowed_domain = _domain_allowed(absolute, allowed_domains)
                if score and (allowed_domain or _looks_like_document_url(absolute)):
                    candidates.append(
                        {
                            "title": label or _title_from_url(absolute),
                            "date": _extract_date(f"{label} {absolute}"),
                            "kind": _classify_exhibit_kind(label, absolute),
                            "source": "company_ir",
                            "url": absolute,
                            "page_url": normalized_page,
                            "page_title": page_title,
                            "company_name": company_name,
                            "symbol": symbol.strip().upper(),
                            "confidence": score["confidence"],
                            "why_matched": score["reason"],
                            "warnings": [] if allowed_domain else ["document is hosted on an external CDN linked from the IR page"],
                        }
                    )
                    continue
                if allowed_domain and _looks_like_ir_nav(label, absolute) and absolute not in visited:
                    queue.append(absolute)

        return _dedupe_candidates(candidates)[:limit]

    def _fetch_html(self, url: str) -> str:
        try:
            response = httpx.get(
                url,
                headers={"User-Agent": self.USER_AGENT},
                timeout=self.timeout,
                follow_redirects=True,
            )
            response.raise_for_status()
        except Exception as exc:
            raise ProviderError(f"company IR fetch failed: {exc}") from exc
        content_type = response.headers.get("content-type", "")
        if "html" not in content_type.lower() and not response.text.lstrip().lower().startswith("<!doctype"):
            raise ProviderError(f"company IR URL is not HTML: {url}")
        return response.text


def _candidate_start_urls(*, website: str | None, ir_website: str | None) -> list[str]:
    candidates: list[str] = []
    if ir_website:
        candidates.append(ir_website)
    if website:
        parsed = urlparse(_with_scheme(website))
        host = parsed.netloc
        base = f"{parsed.scheme}://{host}"
        if host.startswith("www."):
            bare = host[4:]
            candidates.extend([f"{parsed.scheme}://investors.{bare}", f"{parsed.scheme}://ir.{bare}"])
        candidates.extend(
            [
                f"{base}/investors",
                f"{base}/overview",
                f"{base}/investor-relations",
                f"{base}/ir",
                f"{base}/company/investor",
                f"{base}/company/investors",
                f"{base}/events-and-presentations/presentations/default.aspx",
                f"{base}/financials/quarterly-results/default.aspx",
            ]
        )
    return _dedupe_urls(candidates)


def _score_ir_link(*, label: str, url: str) -> dict[str, str] | None:
    combined = _match_text(f"{label} {url}")
    if has_fuzzy_term(combined, PRESENTATION_RULES.exclude_terms, threshold=PRESENTATION_RULES.exclude_threshold):
        return None
    if _is_navigation_link(label, url):
        return None
    high = best_fuzzy_term(combined, PRESENTATION_RULES.high_terms)
    if high.score >= PRESENTATION_RULES.match_threshold:
        return {"confidence": "high", "reason": f"IR page link fuzzy-matches '{high.term}'"}
    medium = best_fuzzy_term(combined, PRESENTATION_RULES.medium_terms)
    if medium.score >= PRESENTATION_RULES.match_threshold and _looks_like_document_url(url):
        return {"confidence": "medium", "reason": f"IR page link fuzzy-matches '{medium.term}'"}
    return None


def _looks_like_ir_nav(label: str, url: str) -> bool:
    text = _match_text(f"{label} {url}")
    if has_fuzzy_term(text, PRESENTATION_RULES.exclude_terms, threshold=PRESENTATION_RULES.exclude_threshold):
        return False
    return has_fuzzy_term(text, PRESENTATION_RULES.ir_page_hints, threshold=PRESENTATION_RULES.match_threshold)


def _is_navigation_link(label: str, url: str) -> bool:
    normalized_label = _match_text(label)
    if normalized_label in PRESENTATION_RULES.navigation_labels:
        return True
    path = urlparse(url).path.lower().rstrip("/")
    return path.endswith("/default.aspx") and normalized_label in {"events", "presentations", "financials"}


def _looks_like_document_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    if path.endswith("/default.aspx"):
        return False
    return bool(re.search(r"\.(pdf|html?|aspx)(?:$|\?)", url, re.IGNORECASE))


def _domain_allowed(url: str, allowed_domains: set[str]) -> bool:
    domain = _registrable_domain(url)
    return bool(domain and any(domain == allowed or domain.endswith(f".{allowed}") for allowed in allowed_domains))


def _registrable_domain(url: str) -> str:
    host = urlparse(url).netloc.lower().split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if len(parts) < 2:
        return host
    multipart_suffixes = {
        "ac.uk",
        "co.uk",
        "gov.uk",
        "com.au",
        "com.br",
        "com.cn",
        "com.hk",
        "com.mx",
        "com.sg",
        "co.in",
        "co.jp",
        "co.kr",
    }
    suffix = ".".join(parts[-2:])
    if suffix in multipart_suffixes and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _normalize_url(url: str) -> str:
    if not url or url.startswith(("mailto:", "tel:", "javascript:")):
        return ""
    parsed = urlparse(_with_scheme(url))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    path = parsed.path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{parsed.scheme}://{parsed.netloc}{path}{query}"


def _with_scheme(url: str) -> str:
    return url if re.match(r"^https?://", url, re.IGNORECASE) else f"https://{url}"


def _dedupe_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        normalized = _normalize_url(url)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _dedupe_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for candidate in candidates:
        url = str(candidate.get("url") or "")
        key = _candidate_key(candidate)
        if not url or key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    return result


def _candidate_key(candidate: dict[str, Any]) -> str:
    url = str(candidate.get("url") or "")
    parsed = urlparse(url)
    filename = parsed.path.rstrip("/").split("/")[-1].lower()
    title = _match_text(str(candidate.get("title") or ""))
    return f"{filename}|{title}" if filename else url


def _extract_date(text: str) -> str | None:
    match = re.search(r"(20\d{2})[-_/](0?[1-9]|1[0-2])[-_/](0?[1-9]|[12]\d|3[01])", text)
    if match:
        year, month, day = match.groups()
        if not _reasonable_year(year):
            return None
        return f"{year}-{int(month):02d}-{int(day):02d}"
    match = re.search(r"\b(20\d{2})\b", text)
    if match and _reasonable_year(match.group(1)):
        return match.group(1)
    match = re.search(r"\bfy\s*'?(\d{2})\b", text, re.IGNORECASE)
    if match:
        year = f"20{match.group(1)}"
        return year if _reasonable_year(year) else None
    return None


def _reasonable_year(year: str) -> bool:
    numeric = int(year)
    return 2000 <= numeric <= date.today().year + 1


def _title_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/").split("/")[-1]
    return re.sub(r"[-_]+", " ", path) or url


def _match_text(text: str) -> str:
    return re.sub(r"[\s_\-.]+", " ", str(text or "").lower())


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
