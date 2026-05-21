import json

from finance_cli.cli.main import main
from finance_cli.records import RecordRenderOptions, normalize_records, render_records
from finance_cli.schemas import Record


def test_record_renderers_share_normalized_schema():
    record = Record(
        entity="AAPL",
        kind="financial_metric",
        period="2024Q4",
        fields={"revenue": "119.6B USD", "net_income": "36.3B USD"},
        source="10-K",
    )
    options = RecordRenderOptions(fields=("revenue", "net_income"))

    assert render_records([record], "compact", options) == "AAPL|financial_metric|2024Q4|revenue=119.6B USD|net_income=36.3B USD|src=10-K"
    assert render_records([record], "schema", options).splitlines()[0] == "schema|entity|kind|period|source|revenue|net_income"

    normalized_json = json.loads(render_records([record], "json", options))
    assert normalized_json == [
        {
            "entity": "AAPL",
            "kind": "financial_metric",
            "period": "2024Q4",
            "fields": {"revenue": "119.6B USD", "net_income": "36.3B USD"},
            "source": "10-K",
        }
    ]


def test_dict_adapter_normalizes_sec_statement_rows():
    payload = {
        "symbol": "aapl",
        "statement": "income",
        "rows": [
            {
                "label": "Net sales",
                "period": "2024",
                "value": 391035000000,
                "unit": "USD",
                "accession_no": "0000320193-24-000123",
            }
        ],
        "count": 1,
        "source": "sec_edgar",
    }

    records = normalize_records(payload, command="filings.statement")

    assert records == [
        Record(
            entity="AAPL",
            kind="filings_statement_row",
            period="2024",
            fields={
                "statement": "income",
                "label": "Net sales",
                "value": 391035000000,
                "unit": "USD",
                "accession_no": "0000320193-24-000123",
            },
            source="sec_edgar",
        )
    ]


def test_dict_adapter_normalizes_grouped_symbol_rows():
    payload = {
        "timeframe": "1d",
        "symbols": {
            "AAPL": {
                "symbol": "AAPL",
                "rows": [{"date": "2026-05-20", "close": 190.1, "volume": 1000}],
                "count": 1,
                "source": "test",
            }
        },
        "count": 1,
    }

    records = normalize_records(payload, command="market.ohlcv")

    assert records[0].entity == "AAPL"
    assert records[0].kind == "market_ohlcv_row"
    assert records[0].timestamp == "2026-05-20"
    assert records[0].fields == {"timeframe": "1d", "close": 190.1, "volume": 1000}
    assert records[0].source == "test"


def test_cli_compact_output_uses_generic_record_renderer(capsys, monkeypatch):
    def fake_quote(symbol):
        return {
            "symbol": symbol.upper(),
            "last_price": 190.12,
            "market_cap": 2960000000000,
            "currency": "USD",
            "source": "test_provider",
            "long_text": "x" * 500,
        }

    monkeypatch.setattr("finance_cli.cli.commands.market_data.fetch_realtime_quote", fake_quote)

    code = main(["market.quote", "aapl", "--output", "compact", "--fields", "last_price,market_cap,currency"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert output == "AAPL|market_quote|last_price=190.12|market_cap=2960000000000|currency=USD|src=test_provider"


def test_cli_json_output_keeps_existing_envelope(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.market_data.fetch_realtime_quote",
        lambda symbol: {"symbol": symbol.upper(), "last_price": 190.12, "source": "test_provider"},
    )

    code = main(["market.quote", "aapl", "--output", "json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload == {
        "ok": True,
        "data": {"symbol": "AAPL", "last_price": 190.12, "source": "test_provider"},
        "error": None,
        "warnings": [],
    }


def test_cli_schema_output_uses_data_driven_columns(capsys, monkeypatch):
    def fake_ohlcv(symbol, **kwargs):
        return {
            "symbol": symbol.upper(),
            "rows": [
                {"date": "2026-05-20", "close": 190.12},
                {"date": "2026-05-21", "close": 191.25},
            ],
            "count": 2,
            "source": "test_provider",
        }

    monkeypatch.setattr("finance_cli.cli.commands.market_data.fetch_ohlcv", fake_ohlcv)

    code = main(["market.ohlcv", "aapl", "--output", "schema", "--max-records", "1"])
    output = capsys.readouterr().out.strip().splitlines()

    assert code == 0
    assert output == [
        "schema|entity|kind|timestamp|source|close",
        "row|AAPL|market_ohlcv_row|2026-05-20|test_provider|190.12",
    ]


def test_cli_record_max_chars_is_wired(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.market_data.fetch_realtime_quote",
        lambda symbol: {"symbol": symbol.upper(), "summary": "x" * 120, "source": "test_provider"},
    )

    code = main(["market.quote", "aapl", "--output", "compact", "--fields", "summary", "--max-chars", "60"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert len(output) <= 60
    assert output.endswith("...truncated")


def test_record_render_controls_bound_output():
    records = [
        Record(entity="AAPL", kind="news_article", fields={"title": "first"}),
        Record(entity="AAPL", kind="news_article", fields={"title": "second"}),
    ]
    options = RecordRenderOptions(fields=("title",), max_records=1, max_chars=80)

    output = render_records(records, "compact", options)

    assert "first" in output
    assert "second" not in output
    assert len(output) <= 80
