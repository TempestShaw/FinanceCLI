import httpx
import pytest

from finance_cli.providers.base import ProviderError
from finance_cli.providers.cftc import CFTCProvider


@pytest.mark.parametrize("report,dataset,category,long_field,short_field,spread_field", [
    ("disaggregated", "72hh-3qpy", "managed_money", "m_money_positions_long_all", "m_money_positions_short_all", "m_money_positions_spread"),
    ("tff", "gpe5-46if", "leveraged_money", "lev_money_positions_long", "lev_money_positions_short", "lev_money_positions_spread"),
    ("legacy", "6dca-aqww", "noncommercial", "noncomm_positions_long_all", "noncomm_positions_short_all", "noncomm_postions_spread_all"),
])
def test_cot_selects_report_specific_categories_and_position_date(monkeypatch, report, dataset, category, long_field, short_field, spread_field):
    def get(url, *, params, timeout):
        assert url.endswith(f"/{dataset}.json")
        assert params["cftc_contract_market_code"] == "088691"
        assert params["$limit"] == 2 and "$where" not in params
        return httpx.Response(200, request=httpx.Request("GET", "https://example.test"), json=[{
            **dict.fromkeys(params["$select"].split(",")),
            "cftc_contract_market_code": "088691", "market_and_exchange_names": "GOLD - COMMODITY EXCHANGE INC.",
            "report_date_as_yyyy_mm_dd": "2026-10-20T00:00:00.000", "open_interest_all": "400000",
            "contract_units": "100 TROY OUNCES", long_field: "100", short_field: "40", spread_field: "5",
        }])

    monkeypatch.setattr(httpx, "get", get)
    data = CFTCProvider().cot("gold", report=report, weeks=2)
    row = next(row for row in data["rows"] if row["category"] == category)
    assert (row["long"], row["short"], row["net"], row["spreading"]) == (100, 40, 60, 5)
    assert row["as_of_date"] == row["period"] == "2026-10-20"
    assert "published_at" not in row and row["units"] == "contracts"
    assert row["report"] == report and row["futures_only"]
    assert data["weeks_returned"] == 1


@pytest.mark.parametrize("market,report,weeks", [("gold' OR 1=1", "legacy", 2), ("gold", "unknown", 2), ("gold", "legacy", 0), ("gold", "legacy", 1001)])
def test_cot_validates_filters_before_request(monkeypatch, market, report, weeks):
    def unexpected(*args, **kwargs):
        pytest.fail("invalid filters reached the network")
    monkeypatch.setattr(httpx, "get", unexpected)
    with pytest.raises(ProviderError):
        CFTCProvider().cot(market, report=report, weeks=weeks)


def test_cot_empty_report_is_explicit(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: httpx.Response(200, request=httpx.Request("GET", "https://example.test"), json=[]))
    data = CFTCProvider().cot("gold", report="tff", weeks=1)
    assert data["count"] == 0 and data["warnings"]


@pytest.mark.parametrize("fault", ["empty", "identity", "date", "missing_field", "nonfinite"])
def test_cot_malformed_evidence_is_rejected(monkeypatch, fault):
    def get(url, *, params, timeout):
        row = dict.fromkeys(params["$select"].split(","))
        row.update(cftc_contract_market_code="088691", market_and_exchange_names="GOLD",
                   report_date_as_yyyy_mm_dd="2026-10-20T00:00:00.000")
        if fault == "empty":
            row = {}
        elif fault == "identity":
            row["cftc_contract_market_code"] = "13874A"
        elif fault == "date":
            row["report_date_as_yyyy_mm_dd"] = "2026-02-30T00:00:00.000"
        elif fault == "missing_field":
            del row["m_money_positions_short_all"]
        else:
            row["m_money_positions_long_all"] = "Infinity"
        return httpx.Response(200, request=httpx.Request("GET", url), json=[row])

    monkeypatch.setattr(httpx, "get", get)
    with pytest.raises(ProviderError):
        CFTCProvider().cot("gold", weeks=1)
