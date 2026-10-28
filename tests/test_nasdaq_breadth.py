"""Official annual breadth files preserve issue counts, scope and observation dates."""
from datetime import datetime

import httpx
import pytest

from finance_cli.cli.commands.breadth import _market_breadth
from finance_cli.providers import nasdaq_breadth
from finance_cli.providers.base import ProviderError


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 10, 28, tzinfo=tz)


def _serve(monkeypatch, text, status=200):
    def get(url, **kwargs):
        return httpx.Response(status, text=text, request=httpx.Request("GET", url))
    monkeypatch.setattr(nasdaq_breadth.httpx, "get", get)
    monkeypatch.setattr(nasdaq_breadth, "datetime", FixedDateTime)


def test_annual_rows_are_sorted_and_scope_freshness_remain_explicit(monkeypatch):
    _serve(monkeypatch, '"Date","Advances","Declines","Unchanged"\n10/23/2026 0:00:00,1944.00,3004.00,258.00\n10/22/2026 0:00:00,2153,2841,258\n')
    data = nasdaq_breadth.fetch_breadth("nasdaq", year=2026, limit=1)
    assert data["count"] == 1 and data["available_count"] == 2
    assert data["as_of"] == "2026-10-23" and data["age_calendar_days"] == 5
    row = data["rows"][0]
    assert row["net_advances"] == -1060 and row["total_issues"] == 5206
    assert row["advance_decline_ratio"] == pytest.approx(1944 / 3004)
    assert row["period"] == "2026-10-23" and row["source_url"].endswith("daily2026.txt")
    assert any("not live" in warning for warning in data["warnings"])
    assert "Nasdaq-listed" in data["scope"]


def test_zero_decliners_does_not_fabricate_a_ratio(monkeypatch):
    _serve(monkeypatch, "Date,Advances,Declines,Unchanged\n10/27/2026 0:00:00,10,0,1\n")
    data = nasdaq_breadth.fetch_breadth()
    assert data["rows"][0]["advance_decline_ratio"] is None
    assert not any("not live" in warning for warning in data["warnings"])


def test_missing_historical_breadth_is_disclosed_without_dropping_valid_year(monkeypatch):
    _serve(monkeypatch, "Date,Advances,Declines,Unchanged\n3/9/2026 0:00:00,,,\n10/23/2026 0:00:00,10,5,1\n")
    data = nasdaq_breadth.fetch_breadth()
    assert data["count"] == 1 and data["missing_dates"] == ["2026-03-09"]
    assert data["rows"][0]["date"] == "2026-10-23"
    assert any("not zero" in warning for warning in data["warnings"])


def test_keyed_market_is_honored_instead_of_silently_using_nasdaq(monkeypatch):
    _serve(monkeypatch, "Date,Advances,Declines,Unchanged\n10/27/2026 0:00:00,10,5,1\n")
    with pytest.raises(ProviderError, match="NASDAQ only"):
        _market_breadth(["market=NYSE"])
    result = _market_breadth(["market=NASDAQ", "limit=1"])
    assert result.ok and result.data["market"] == "NASDAQ"
    assert result.data["rows"][0]["advances"] == 10


@pytest.mark.parametrize("text", [
    "<html>Access denied</html>",
    "Date,Advances,Declines,Unchanged\n10/27/2026 0:00:00,1.5,2,1\n",
    "Date,Advances,Declines,Unchanged\n10/29/2026 0:00:00,1,2,1\n",
    "Date,Advances,Declines,Unchanged\n",
])
def test_invalid_provider_files_fail_instead_of_becoming_zero_breadth(monkeypatch, text):
    _serve(monkeypatch, text)
    with pytest.raises(ProviderError):
        nasdaq_breadth.fetch_breadth()


@pytest.mark.parametrize("kwargs", [{"market": "US"}, {"year": 2005}, {"limit": 0}, {"limit": 367}])
def test_unsupported_scope_and_bounds_never_fetch(monkeypatch, kwargs):
    monkeypatch.setattr(nasdaq_breadth.httpx, "get", lambda *a, **k: pytest.fail("unexpected fetch"))
    with pytest.raises(ProviderError):
        nasdaq_breadth.fetch_breadth(**kwargs)
