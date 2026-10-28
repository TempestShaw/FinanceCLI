import httpx
import pytest

from finance_cli.cli.commands.energy import _energy_electricity, _energy_inventory
from finance_cli.providers.base import ProviderError
from finance_cli.providers.eia import EIAProvider


@pytest.mark.parametrize("product,route,series,region,units", [
    ("crude", "petroleum/stoc/wstk", "WCESTUS1", "US", "MBBL"),
    ("gasoline", "petroleum/stoc/wstk", "WGTSTUS1", "US", "MBBL"),
    ("distillate", "petroleum/stoc/wstk", "WDISTUS1", "US", "MBBL"),
    ("natural_gas", "natural-gas/stor/wkly", "NW2_EPG0_SWO_R48_BCF", "Lower 48 States", "BCF"),
])
def test_eia_inventory_uses_exact_series_and_preserves_source_units(monkeypatch, product, route, series, region, units):
    def get(url, *, params, timeout):
        assert url.endswith(f"/{route}/data/")
        assert params["facets[series][]"] == series
        assert params["frequency"] == "weekly" and params["data[0]"] == "value"
        assert params["offset"] == 0 and params["length"] == 1
        assert params["sort[0][direction]"] == "desc"
        return httpx.Response(200, request=httpx.Request("GET", "https://example.test"), json={"response": {"total": "50", "data": [{"period": "2026-10-16", "series": series, "value": "123.5", "units": units}]}})

    monkeypatch.setattr(httpx, "get", get)
    data = EIAProvider(api_key="test").inventory(product=product, limit=1)
    assert data["rows"][0]["value"] == 123.5
    assert data["rows"][0]["units"] == units
    assert data["region"] == region and data["series_id"] == series
    assert data["truncated"] and data["total_available"] == 50
    if product == "crude":
        assert "excluding" in data["description"]


def test_eia_electricity_filters_all_sector_state_and_keeps_metric_units(monkeypatch):
    def get(url, *, params, timeout):
        assert url.endswith("/electricity/retail-sales/data/")
        assert params["facets[stateid][]"] == "TX" and params["facets[sectorid][]"] == "ALL"
        assert params["frequency"] == "monthly"
        return httpx.Response(200, request=httpx.Request("GET", "https://example.test"), json={"response": {"total": "1", "data": [{
            "period": "2026-07", "stateid": "TX", "stateDescription": "Texas", "sectorid": "ALL", "sectorName": "all sectors",
            "sales": "1234", "sales-units": "million kilowatthours", "price": "10.5", "price-units": "cents per kilowatthour",
        }]}})

    monkeypatch.setattr(httpx, "get", get)
    data = EIAProvider(api_key="test").electricity(region="tx", limit=1)
    row = data["rows"][0]
    assert row["period"] == "2026-07" and row["sales"] == 1234
    assert row["sales_units"] == "million kilowatthours" and row["price_units"] == "cents per kilowatthour"
    assert not data["truncated"]


def test_eia_missing_key_is_actionable_in_both_cli_commands(monkeypatch):
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    assert "EIA_API_KEY" in _energy_inventory([]).error
    assert "EIA_API_KEY" in _energy_electricity([]).error


def test_eia_http_errors_do_not_disclose_key(monkeypatch):
    def get(url, *, params, timeout):
        return httpx.Response(403, request=httpx.Request("GET", url, params=params))

    monkeypatch.setattr(httpx, "get", get)
    with pytest.raises(ProviderError, match="HTTP 403") as error:
        EIAProvider(api_key="private-key").inventory()
    assert "private-key" not in str(error.value) and "api_key" not in str(error.value)


@pytest.mark.parametrize("kwargs", [{"limit": 0}, {"limit": 5001}, {"country": "CA"}, {"product": "unknown"}])
def test_eia_rejects_bad_inventory_bounds(kwargs):
    with pytest.raises(ProviderError):
        EIAProvider(api_key="test").inventory(**kwargs)


@pytest.mark.parametrize("kind,fault", [("inventory", "empty"), ("electricity", "empty"),
    ("inventory", "identity"), ("electricity", "identity"), ("electricity", "sector"),
    ("inventory", "date"), ("electricity", "date"), ("inventory", "missing_value"),
    ("electricity", "missing_value"), ("inventory", "units"), ("electricity", "units"),
    ("inventory", "nonfinite"), ("electricity", "nonfinite")])
def test_eia_rejects_malformed_evidence(monkeypatch, kind, fault):
    row = ({"period": "2026-10-16", "series": "WCESTUS1", "value": "123", "units": "MBBL"}
           if kind == "inventory" else {"period": "2026-08", "stateid": "TX", "sectorid": "ALL",
               "sales": "123", "price": "10", "sales-units": "million kilowatt hours", "price-units": "cents per kilowatt-hour"})
    if fault == "empty":
        row = {}
    elif fault == "identity":
        row["series" if kind == "inventory" else "stateid"] = "WRONG"
    elif fault == "sector":
        row["sectorid"] = "RES"
    elif fault == "date":
        row["period"] = "2026-02-30" if kind == "inventory" else "2026-13"
    elif fault == "missing_value":
        del row["value" if kind == "inventory" else "sales"]
    elif fault == "units":
        del row["units" if kind == "inventory" else "price-units"]
    else:
        row["value" if kind == "inventory" else "price"] = "NaN"
    monkeypatch.setattr(EIAProvider, "_request", lambda *args, **kwargs: ({"total": "1"}, [row], []))
    with pytest.raises(ProviderError):
        getattr(EIAProvider(api_key="test"), kind)()


@pytest.mark.parametrize("missing", [None, "W", "NA"])
def test_eia_explicit_missing_values_remain_null(monkeypatch, missing):
    row = {"period": "2026-10-16", "series": "WCESTUS1", "value": missing, "units": "MBBL"}
    monkeypatch.setattr(EIAProvider, "_request", lambda *args, **kwargs: ({"total": "1"}, [row], []))
    assert EIAProvider(api_key="test").inventory()["rows"][0]["value"] is None
