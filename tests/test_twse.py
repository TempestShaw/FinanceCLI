import httpx
import pytest

from finance_cli.cli.commands.twse import _monthly_revenue, _recent_disclosures
from finance_cli.providers.base import ProviderError
from finance_cli.providers.twse import BASE_URL, TWSEProvider


def _snapshot(monkeypatch, rows):
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        return httpx.Response(200, json=rows, request=httpx.Request("GET", url))

    monkeypatch.setattr("finance_cli.providers.twse.httpx.get", get)
    return calls


def test_monthly_revenue_normalizes_roc_period_numbers_and_units(monkeypatch):
    calls = _snapshot(monkeypatch, [{
        "公司代號": "2330", "公司名稱": "台積電", "資料年月": "11509", "出表日期": "1151017",
        "營業收入-當月營收": "1,234,567", "營業收入-上月營收": "1,200,000",
        "營業收入-去年當月營收": "1,000,000", "營業收入-去年同月增減(%)": "23.4567",
        "營業收入-上月比較增減(%)": "0", "累計營業收入-當月累計營收": "9,000,000",
        "累計營業收入-去年累計營收": "--", "備註": "需求增加",
    }, {"公司代號": "2317", "資料年月": "11509"}])
    result = TWSEProvider().monthly_revenue("2330")
    row = result["rows"][0]
    assert result["symbol"] == "2330.TW" and result["count"] == 1
    assert (row["period"], row["date"], row["date_kind"]) == ("2026-09", "2026-10-17", "snapshot_generated_date")
    assert (row["revenue"], row["unit"], row["currency"]) == (1234567, "TWD_thousands", "TWD")
    assert row["yoy_pct"] == 23.4567 and row["mom_pct"] == 0
    assert row["previous_year_ytd_revenue"] is None and row["notes"] == "需求增加"
    assert row["retrieved_at"] == result["retrieved_at"] and row["source_url"] == calls[0]
    assert calls == [f"{BASE_URL}/t187ap05_L"]
    assert any("history" in warning for warning in result["warnings"])


def test_disclosures_filters_sorts_limits_and_retains_publication_time(monkeypatch):
    calls = _snapshot(monkeypatch, [
        {"公司代號": "2330", "發言日期": "115/10/27", "發言時間": "16:00:00", "主旨 ": "舊公告", "說明": "原文"},
        {"公司代號": "2330", "發言日期": "115/10/28", "發言時間": "09:01:02", "事實發生日": "1151027", "主旨 ": "新公告", "說明": "完整內容", "符合條款": "31"},
        {"公司代號": "2317", "發言日期": "115/10/28", "主旨": "另一家公司"},
    ])
    result = TWSEProvider().recent_disclosures("2330.TW", limit=1)
    row = result["rows"][0]
    assert result["count"] == 1 and row["title"] == "新公告"
    assert row["timestamp"] == "2026-10-28T09:01:02+08:00" and row["event_date"] == "2026-10-27"
    assert row["text"] == "完整內容" and row["source_url"] == calls[0]
    assert calls == [f"{BASE_URL}/t187ap04_L"]


def test_empty_snapshot_is_honest_and_source_errors_are_failures(monkeypatch):
    _snapshot(monkeypatch, [])
    result = TWSEProvider().monthly_revenue("2330")
    assert result["count"] == 0 and any("No matching" in warning for warning in result["warnings"])

    def fail(url, **kwargs):
        raise httpx.ReadTimeout("timed out")

    monkeypatch.setattr("finance_cli.providers.twse.httpx.get", fail)
    with pytest.raises(ProviderError, match="TWSE snapshot request failed"):
        TWSEProvider().monthly_revenue("2330")


@pytest.mark.parametrize("symbol", ["TSM", "2330.TWO", "", "../2330"])
def test_non_twse_symbols_rejected(symbol):
    with pytest.raises(ProviderError, match="listed-company code"):
        TWSEProvider().monthly_revenue(symbol)


def test_malformed_snapshot_is_not_silently_normalized(monkeypatch):
    _snapshot(monkeypatch, [{"公司代號": "2330", "資料年月": "bad"}])
    with pytest.raises(ProviderError, match="Invalid TWSE date"):
        TWSEProvider().monthly_revenue("2330")


def test_command_rejects_unsupported_source_or_period_before_fetch():
    assert not _monthly_revenue([]).ok
    assert not _monthly_revenue(["2330", "period=annual"]).ok
    assert not _recent_disclosures(["2330", "source=sec"]).ok
