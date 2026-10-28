import httpx
import pytest

from finance_cli.cli.commands.ir_feed import _events, _releases
from finance_cli.providers.base import ProviderError
from finance_cli.providers.ir_feed import IRFeedProvider


RSS = """<?xml version="1.0"?><rss version="2.0"><channel><title>Company Press Releases</title>
<item><title>New product</title><link>https://example.com/news/new</link>
<pubDate>Wed, 28 Oct 2026 10:00:00 -0400</pubDate><description>&lt;p&gt;Product details&lt;/p&gt;</description></item>
<item><title>Undated release</title><link>https://example.com/news/undated</link><pubDate>unknown</pubDate></item>
<item><title>Company blog</title><link>https://example.com/blog/1</link><contentType>blogs</contentType></item>
</channel></rss>"""


def _pages(monkeypatch, pages):
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        content, content_type = pages.get(url, ("not found", "text/plain"))
        return httpx.Response(200 if url in pages else 404, text=content,
                              headers={"content-type": content_type}, request=httpx.Request("GET", url))

    monkeypatch.setattr("finance_cli.providers.ir_feed.httpx.get", get)
    return calls


def test_rss_preserves_evidence_dates_and_missing_dates(monkeypatch):
    url = "https://example.com/releases.xml"
    calls = _pages(monkeypatch, {url: (RSS, "application/rss+xml")})
    result = IRFeedProvider().list_releases("EX", url=url)
    row = result["rows"][0]
    assert calls == [url] and result["count"] == 2
    assert row["timestamp"] == "2026-10-28T10:00:00-04:00" and row["date"] == "2026-10-28"
    assert row["summary"] == "Product details" and row["source_url"] == url
    assert row["date_kind"] == "feed_publication_date"
    assert result["rows"][1]["timestamp"] is None
    assert any("no parseable" in warning for warning in result["warnings"])


def test_atom_events_use_alternate_link_and_do_not_invent_event_time(monkeypatch):
    url = "https://example.com/events.atom"
    atom = """<feed xmlns="http://www.w3.org/2005/Atom"><title>Investor events</title><entry>
    <title>Annual meeting</title><link rel="self" href="/api/entry/1"/><link rel="alternate" href="/events/meeting"/>
    <updated>2026-10-27</updated><summary>Read event details</summary></entry>
    <entry><title>Published event</title><link href="/events/published"/>
    <published>2026-10-26</published><updated>2026-10-28</updated></entry></feed>"""
    _pages(monkeypatch, {url: (atom, "application/atom+xml")})
    result = IRFeedProvider().list_events("EX", url=url)
    assert result["rows"][0]["url"] == "https://example.com/events/meeting"
    assert result["rows"][0]["timestamp"] == "2026-10-27"
    assert result["rows"][0]["date_kind"] == "feed_updated_date"
    assert result["rows"][0]["raw_date_tag"] == "updated"
    assert result["rows"][1]["timestamp"] == "2026-10-26"
    assert result["rows"][1]["date_kind"] == "feed_publication_date"
    assert result["rows"][1]["raw_date_tag"] == "published"
    assert any("not scheduled event times" in warning for warning in result["warnings"])


def test_html_discovery_follows_requested_feed_and_deduplicates(monkeypatch):
    page = "https://investor.example.com/rss"
    feed = "https://news.example.com/releases.xml"
    html = '<html><a href="https://example.com/events.xml">Event RSS Feed</a><a href="https://example.com/presentations.xml">Presentation RSS</a><a href="'+feed+'">Press Release RSS Feed</a><a href="'+feed+'">RSS</a></html>'
    calls = _pages(monkeypatch, {page: (html, "text/html"), feed: (RSS, "application/rss+xml")})
    result = IRFeedProvider().list_releases("EX", url=page, limit=1)
    assert calls == [page, feed] and result["count"] == 1
    assert result["rows"][0]["title"] == "New product"


def test_feed_is_followed_before_html_candidates_fill_requested_limit(monkeypatch):
    page = "https://example.com/investors"
    feed = "https://example.com/releases.xml"
    html = '<html><a href="/press-releases/old">Old release</a><a href="/releases.xml">Press Release RSS</a></html>'
    calls = _pages(monkeypatch, {page: (html, "text/html"), feed: (RSS, "application/rss+xml")})
    result = IRFeedProvider().list_releases("EX", url=page, limit=1)
    assert calls == [page, feed]
    assert result["rows"][0]["title"] == "New product"
    assert result["rows"][0]["source_url"] == feed


def test_html_fallback_warns_when_page_bound_prevents_feed_discovery(monkeypatch):
    page = "https://example.com/investors"
    html = '<html><a href="/press-releases/old">Old release</a><a href="/releases.xml">Press Release RSS</a></html>'
    calls = _pages(monkeypatch, {page: (html, "text/html")})
    result = IRFeedProvider(max_pages=1).list_releases("EX", url=page, limit=1)
    assert calls == [page] and result["rows"][0]["title"] == "Old release"
    assert any("page limit" in warning for warning in result["warnings"])


def test_auto_discovery_uses_company_profile_without_symbol_catalog(monkeypatch):
    home = "https://example.com/"
    feed = "https://example.com/releases.xml"
    monkeypatch.setattr("finance_cli.providers.ir_feed.YahooFinanceProvider.quote",
                        lambda self, symbol: {"website": home, "ir_website": home})
    calls = _pages(monkeypatch, {home: ('<html><link rel="alternate" type="application/rss+xml" href="/releases.xml" title="News"/></html>', "text/html"), feed: (RSS, "application/rss+xml")})
    result = IRFeedProvider().list_releases("ANY", limit=1)
    assert calls == [home, feed] and result["count"] == 1


def test_html_fallback_only_returns_concrete_links_and_marks_missing_dates(monkeypatch):
    page = "https://example.com/investors"
    html = '<html><a href="/press-releases/default.aspx">Press releases</a><a href="/press-releases/product-a">Product A</a></html>'
    _pages(monkeypatch, {page: (html, "text/html")})
    result = IRFeedProvider(max_pages=1).list_releases("EX", url=page)
    assert [row["title"] for row in result["rows"]] == ["Product A"]
    assert result["rows"][0]["timestamp"] is None


def test_empty_discovery_differs_from_fetch_failure(monkeypatch):
    page = "https://example.com/"
    _pages(monkeypatch, {page: ("<html><title>Company</title></html>", "text/html")})
    result = IRFeedProvider().list_releases("EX", url=page)
    assert result["count"] == 0 and any("No matching" in warning for warning in result["warnings"])
    with pytest.raises(ProviderError, match="No company page or feed could be read"):
        IRFeedProvider().list_releases("EX", url="https://example.com/missing")


def test_invalid_url_or_missing_command_symbol_rejected():
    with pytest.raises(ProviderError, match="HTTP or HTTPS"):
        IRFeedProvider().list_releases("EX", url="file:///tmp/data.xml")
    assert not _releases([]).ok and not _events(["url=https://example.com"]).ok
