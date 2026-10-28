"""Public source commands share discovery, health, and output contracts."""
import json

import pytest

from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.main import main
from finance_cli.cli.registry import get_command
from finance_cli.providers.base import ProviderError, ProviderMetadata
from finance_cli.providers.twse import TWSEProvider
from finance_cli.services import sources
from scripts.generate_cli_docs import PUBLIC_DATA_COMMANDS, build_command_spec


def test_public_sources_are_discoverable_without_network():
    register_builtin_commands()
    for name in PUBLIC_DATA_COMMANDS:
        command = get_command(name)
        assert command is not None
        spec = build_command_spec(command)
        assert spec["side_effects"] == "network_read_only"
        assert "rows" in spec["output_schema"]["properties"]["data"]["anyOf"][0]["required"]
        assert "source_url" in spec["citation_fields"]
    names = {row["name"] for row in sources.list_sources()["sources"]}
    assert {"ir_feed", "fred", "twse", "nasdaq_breadth", "finra", "cftc", "eia"} <= names


@pytest.mark.parametrize("payload,status,ok", [
    ([], "empty", False),
    ({"count": 0, "rows": []}, "empty", False),
    ({"count": 1, "rows": [{"value": 1}], "warnings": ["One requested file was unavailable"]}, "partial", True),
    ({"count": 1, "rows": [{"value": 1}]}, "ok", True),
])
def test_health_checks_retrieved_data_not_only_exceptions(monkeypatch, payload, status, ok):
    monkeypatch.setattr(sources, "_probe_for", lambda *args, **kwargs: lambda: payload)
    health = sources._test_one(ProviderMetadata("test", "Test", ("rows",)), symbol="AAPL", timeout=1)
    assert health.status == status
    assert health.ok is ok


def test_failed_health_check_keeps_the_source_error(monkeypatch):
    def fail():
        raise ProviderError("upstream HTTP 503")
    monkeypatch.setattr(sources, "_probe_for", lambda *args, **kwargs: fail)
    health = sources._test_one(ProviderMetadata("test", "Test", ("rows",)), symbol="AAPL", timeout=1)
    assert health.status == "failed"
    assert health.ok is False
    assert health.error == "upstream HTTP 503"


@pytest.mark.parametrize("command,key", [("macro.series", "FRED_API_KEY"), ("energy.inventory", "EIA_API_KEY")])
def test_unconfigured_keyed_commands_fail_actionably_without_network(monkeypatch, capsys, command, key):
    monkeypatch.delenv(key, raising=False)
    args = [command, "CPIAUCSL"] if command == "macro.series" else [command]
    assert main([*args, "--output", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert key in payload["error"]


@pytest.mark.parametrize("output", ["json", "compact", "schema", "md"])
def test_new_rows_keep_period_unit_and_provenance_in_existing_renderers(monkeypatch, capsys, output):
    monkeypatch.setattr(TWSEProvider, "monthly_revenue", lambda self, symbol: {
        "symbol": "2330.TW", "source": "twse", "source_url": "https://openapi.twse.com.tw/v1/opendata/t187ap05_L",
        "retrieved_at": "2026-10-28T00:00:00+00:00", "warnings": [], "count": 1,
        "rows": [{"period": "2026-09", "revenue": 1000, "unit": "TWD_thousands"}],
    })
    assert main(["fundamentals.revenue", "2330.TW", "--output", output]) == 0
    text = capsys.readouterr().out
    for expected in ("2330.TW", "2026-09", "TWD_thousands", "openapi.twse.com.tw"):
        assert expected in text


def test_compact_source_warnings_stay_visible_without_polluting_records(monkeypatch, capsys):
    monkeypatch.setattr(TWSEProvider, "monthly_revenue", lambda self, symbol: {
        "symbol": symbol, "source": "twse", "count": 1,
        "rows": [{"period": "2026-09", "revenue": 1000}],
        "warnings": ["Latest snapshot only"],
    })
    assert main(["fundamentals.revenue", "2330.TW", "--output", "compact"]) == 0
    captured = capsys.readouterr()
    assert "Latest snapshot only" in captured.err
    assert "Latest snapshot only" not in captured.out
