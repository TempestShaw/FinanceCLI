"""FINRA positions and executed volume retain different dates and coverage."""
from datetime import date

import httpx
import pytest

from finance_cli.providers import finra
from finance_cli.providers.base import ProviderError


def _position(day, current):
    return {"symbolCode": "AAPL", "settlementDate": day,
            "currentShortPositionQuantity": current, "previousShortPositionQuantity": 100,
            "daysToCoverQuantity": 2.5, "issueName": "Apple Inc.", "revisionFlag": "Y"}


def test_positions_filter_one_symbol_sort_locally_and_preserve_settlement_semantics(monkeypatch):
    seen = []
    def post(url, **kwargs):
        seen.append((url, kwargs))
        return httpx.Response(200, json=[_position("2026-09-30", 110), _position("2026-10-15", 125)], request=httpx.Request("POST", url))
    monkeypatch.setattr(finra.httpx, "post", post)
    monkeypatch.setattr(finra, "_today", lambda: date(2026, 10, 28))
    monkeypatch.setenv("FINRA_ACCESS_TOKEN", "test-secret")
    data = finra.fetch_short_interest("aapl", periods=1)
    assert len(seen) == 1 and seen[0][1]["json"]["limit"] == 5000
    assert seen[0][1]["json"]["compareFilters"][0]["fieldValue"] == "AAPL"
    assert seen[0][1]["headers"]["Authorization"] == "Bearer test-secret"
    assert data["as_of"] == "2026-10-15" and data["age_calendar_days"] == 13
    assert data["count"] == 1 and data["available_count"] == 2
    assert data["rows"][0]["short_interest"] == 125
    assert data["rows"][0]["revision_flag"] == "Y"
    assert "published_at" not in data["rows"][0]
    assert any("not publication" in item for item in data["warnings"])


def test_positions_do_not_silently_truncate_before_latest_snapshot(monkeypatch):
    monkeypatch.setattr(finra.httpx, "post", lambda url, **k: httpx.Response(200, json=[_position("2026-10-15", 1)] * 5000, request=httpx.Request("POST", url)))
    with pytest.raises(ProviderError, match="5,000-row bound"):
        finra.fetch_short_interest("AAPL")


def test_auth_failure_is_explicit_and_does_not_expose_token(monkeypatch):
    monkeypatch.setenv("FINRA_ACCESS_TOKEN", "private-secret")
    monkeypatch.setattr(finra.httpx, "post", lambda url, **k: httpx.Response(401, text="private-secret", request=httpx.Request("POST", url)))
    with pytest.raises(ProviderError, match="FINRA_ACCESS_TOKEN") as error:
        finra.fetch_short_interest("AAPL")
    assert "private-secret" not in str(error.value)


def _daily_client(monkeypatch, handler):
    client_class = httpx.Client
    monkeypatch.setattr(finra.httpx, "Client", lambda **kwargs: client_class(transport=httpx.MockTransport(handler), **kwargs))
    monkeypatch.setattr(finra, "_today", lambda: date(2026, 10, 28))


def test_volume_downloads_are_bounded_gaps_explicit_and_fractional_shares_preserved(monkeypatch):
    seen = []
    def handler(request):
        seen.append(str(request.url))
        if "20261027" in str(request.url):
            return httpx.Response(403)
        return httpx.Response(200, text="Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market\n20261026|AAPL|100.5|2|200.5|B,Q,N\n20261026|MSFT|3|0|20|Q\n2\n")
    _daily_client(monkeypatch, handler)
    data = finra.fetch_short_volume("AAPL", days=2)
    assert len(seen) == data["request_count"] == 2
    assert data["queried_dates"] == ["2026-10-27", "2026-10-26"]
    assert data["unavailable_files"][0]["status"] == 403
    assert data["as_of"] == "2026-10-26"
    row = data["rows"][0]
    assert row["short_volume"] == 100.5 and row["short_exempt_volume"] == 2
    assert row["short_volume_pct"] == pytest.approx(100.5 / 200.5 * 100)
    assert any("not outstanding" in warning for warning in data["warnings"])


def test_absent_symbol_is_not_reported_as_zero_volume(monkeypatch):
    _daily_client(monkeypatch, lambda request: httpx.Response(200, text="Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market\n20261027|MSFT|3|0|20|Q\n"))
    data = finra.fetch_short_volume("AAPL", days=1)
    assert data["rows"] == [] and data["as_of"] is None
    assert data["no_symbol_dates"] == ["2026-10-27"]
    assert any("does not establish zero" in warning for warning in data["warnings"])


def test_volume_holidays_do_not_trigger_unbounded_backfilling(monkeypatch):
    seen = []
    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(404)
    _daily_client(monkeypatch, handler)
    with pytest.raises(ProviderError, match="All 3"):
        finra.fetch_short_volume("AAPL", days=3)
    assert len(seen) == 3
    assert seen[-1].endswith("20261023.txt")


def test_invalid_volume_file_cannot_masquerade_as_missing_symbol(monkeypatch):
    _daily_client(monkeypatch, lambda request: httpx.Response(200, text="<html>Unavailable</html>"))
    with pytest.raises(ProviderError, match="invalid columns"):
        finra.fetch_short_volume("AAPL", days=1)


@pytest.mark.parametrize("fn,kwargs", [
    (finra.fetch_short_interest, {"periods": 0}),
    (finra.fetch_short_interest, {"periods": 501}),
    (finra.fetch_short_volume, {"days": 0}),
    (finra.fetch_short_volume, {"days": 61}),
])
def test_request_bounds_are_validated(fn, kwargs):
    with pytest.raises(ProviderError):
        fn("AAPL", **kwargs)
