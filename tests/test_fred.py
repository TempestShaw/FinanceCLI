import httpx
import pytest

from finance_cli.cli.commands.macro import _macro_search, _macro_series
from finance_cli.providers.base import ProviderError
from finance_cli.providers.fred import FREDProvider


def test_fred_vintage_pins_metadata_and_observations_and_preserves_missing(monkeypatch):
    calls = []

    def get(url, *, params, timeout):
        calls.append((url, params.copy()))
        data = {"seriess": [{"id": "GDP", "title": "GDP", "units": "Billions of Dollars", "frequency": "Quarterly"}]}
        if url.endswith("observations"):
            data = {"count": 8, "realtime_start": "2024-01-01", "realtime_end": "2024-01-01",
                    "observations": [{"date": "2023-10-01", "value": ".", "realtime_start": "2024-01-01"},
                                     {"date": "2023-07-01", "value": "27000.5", "realtime_start": "2024-01-01"}]}
        return httpx.Response(200, json=data, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", get)
    result = FREDProvider(api_key="test-secret").series("gdp", start="2023-01-01", end="2023-12-31", as_of="2024-01-01", limit=2)
    assert len(calls) == 2
    for _, params in calls:
        assert params["realtime_start"] == params["realtime_end"] == "2024-01-01"
        assert params["api_key"] == "test-secret"
    assert calls[1][1]["observation_start"] == "2023-01-01"
    assert calls[1][1]["observation_end"] == "2023-12-31"
    assert calls[1][1]["limit"] == 2 and calls[1][1]["sort_order"] == "desc"
    assert [row["value"] for row in result["rows"]] == [27000.5, None]
    assert result["rows"][0]["units"] == "Billions of Dollars"
    assert result["metadata"]["frequency"] == "Quarterly"
    assert result["truncated"] and result["total_available"] == 8
    assert "test-secret" not in str(result)


def test_fred_search_uses_query_and_returns_metadata(monkeypatch):
    def get(url, *, params, timeout):
        assert url.endswith("series/search")
        assert params["search_text"] == "consumer price index" and params["limit"] == 3
        return httpx.Response(200, request=httpx.Request("GET", url), json={"count": 1, "seriess": [{"id": "CPIAUCSL", "units": "Index", "frequency": "Monthly"}]})

    monkeypatch.setattr(httpx, "get", get)
    result = FREDProvider(api_key="test").search("consumer price index", limit=3)
    assert result["rows"][0]["series_id"] == "CPIAUCSL"
    assert result["rows"][0]["source_url"] == "https://fred.stlouisfed.org/series/CPIAUCSL"


def test_fred_missing_key_and_cli_errors(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="FRED_API_KEY"):
        FREDProvider().search("GDP")
    assert not _macro_series(["GDP"]).ok
    assert "FRED_API_KEY" in _macro_search(["query=GDP"]).error


def test_fred_http_error_does_not_disclose_key(monkeypatch):
    def get(url, *, params, timeout):
        return httpx.Response(403, request=httpx.Request("GET", url, params=params))

    monkeypatch.setattr(httpx, "get", get)
    with pytest.raises(ProviderError, match="HTTP 403") as error:
        FREDProvider(api_key="private-key").search("GDP")
    assert "private-key" not in str(error.value)
    assert "api_key" not in str(error.value)


@pytest.mark.parametrize("kwargs", [{"limit": 0}, {"limit": 100001}, {"as_of": "2024-02-30"},
                                     {"start": "2025-01-01", "end": "2024-01-01"}])
def test_fred_rejects_bad_bounds_before_network(kwargs):
    with pytest.raises(ProviderError):
        FREDProvider(api_key="test").series("GDP", **kwargs)


@pytest.mark.parametrize("row", [{}, {"date": "2024-02-30", "value": "1"},
                                {"date": "2024-01-01"}, {"date": "2024-01-01", "value": "NaN"}])
def test_fred_malformed_observations_are_errors(monkeypatch, row):
    def request(self, endpoint, params):
        return ({"seriess": [{"id": "GDP", "units": "Dollars", "frequency": "Quarterly"}]}
                if endpoint == "series" else {"observations": [row]})
    monkeypatch.setattr(FREDProvider, "_request", request)
    with pytest.raises(ProviderError, match="observation"):
        FREDProvider(api_key="test").series("GDP")


@pytest.mark.parametrize("metadata", [{}, {"id": "UNRATE", "units": "Percent", "frequency": "Monthly"}])
def test_fred_metadata_identity_must_match_request(monkeypatch, metadata):
    monkeypatch.setattr(FREDProvider, "_request", lambda *args: {"seriess": [metadata]})
    with pytest.raises(ProviderError, match="metadata"):
        FREDProvider(api_key="test").series("GDP")


def test_fred_explicit_null_value_is_preserved(monkeypatch):
    def request(self, endpoint, params):
        return ({"seriess": [{"id": "GDP", "units": "Dollars", "frequency": "Quarterly"}]}
                if endpoint == "series" else {"observations": [{"date": "2024-01-01", "value": None}]})
    monkeypatch.setattr(FREDProvider, "_request", request)
    assert FREDProvider(api_key="test").series("GDP")["rows"][0]["value"] is None
