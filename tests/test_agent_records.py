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


def test_filings_statement_adapter_normalizes_sec_statement_rows():
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

    assert records[0].entity == "AAPL"
    assert records[0].kind == "filings_statement_row"
    assert records[0].period == "2024"
    assert records[0].fields == {
        "statement": "income",
        "label": "Net sales",
        "period": "2024",
        "value": 391035000000,
        "unit": "USD",
        "accession_no": "0000320193-24-000123",
    }
    assert records[0].source == "sec_edgar"


def test_market_ohlcv_adapter_normalizes_grouped_symbol_rows():
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
    assert records[0].fields == {"timeframe": "1d", "date": "2026-05-20", "close": 190.1, "volume": 1000}
    assert records[0].source == "test"


def test_filings_recent_adapter_treats_report_date_as_period_and_filing_date_as_timestamp():
    payload = {
        "symbol": "AAPL",
        "filings": [
            {
                "form": "10-K",
                "accession_no": "0000320193-25-000079",
                "filing_date": "2025-10-31",
                "report_date": "2025-09-27",
                "url": "https://www.sec.gov/example",
            }
        ],
        "source": "sec_edgar",
    }

    records = normalize_records(payload, command="filings.recent")

    assert records[0].entity == "AAPL"
    assert records[0].kind == "filing"
    assert records[0].period == "2025-09-27"
    assert records[0].timestamp == "2025-10-31"
    assert records[0].fields == {
        "form": "10-K",
        "accession_no": "0000320193-25-000079",
        "filing_date": "2025-10-31",
        "report_date": "2025-09-27",
        "url": "https://www.sec.gov/example",
    }
    assert records[0].source == "sec_edgar"


def test_agent_adapters_cover_earnings_transcripts_kpis_and_price_moves():
    earnings = normalize_records(
        {
            "symbol": "AAPL",
            "rows": [{"earnings_date": "2026-07-30", "eps_estimate": 1.9}],
            "source": "yfinance",
        },
        command="calendar.earnings",
    )
    transcripts = normalize_records(
        {
            "symbol": "IOT",
            "transcripts": [{"title": "Q4 call", "quarter": "Q4 2026", "published_at": "2026-03-05", "url": "https://example.com", "source": "motley_fool"}],
            "source": "motley_fool",
        },
        command="transcripts.search",
    )
    kpis = normalize_records(
        {
            "symbol": "IOT",
            "source": "transcripts",
            "documents": [{"doc_ref": 0, "quarter": "Q4 2026", "published_at": "2026-03-05", "source": "motley_fool"}],
            "kpis": [{"doc_ref": 0, "metric": "arr", "period": "Q4 2026", "value": {"raw": "$1.9B", "number": 1900000000, "currency": "USD"}}],
        },
        command="kpi.extract",
    )
    moves = normalize_records(
        {
            "symbol": "IOT",
            "moves": [{"start_date": "2026-03-05", "end_date": "2026-03-06", "return_pct": 19.54, "source": "yfinance"}],
            "source": "yfinance",
        },
        command="price.moves",
    )

    assert (earnings[0].kind, earnings[0].timestamp, earnings[0].source) == ("earning", "2026-07-30", "yfinance")
    assert (transcripts[0].kind, transcripts[0].period, transcripts[0].timestamp) == ("transcript", "Q4 2026", "2026-03-05")
    assert kpis[0].fields["value_number"] == 1900000000
    assert kpis[0].source == "motley_fool"
    assert (moves[0].kind, moves[0].period, moves[0].timestamp) == ("price_move", "2026-03-05", "2026-03-06")


def test_screen_and_price_context_adapters_keep_source_context():
    screen = normalize_records(
        {
            "query": "day_gainers",
            "title": "Day Gainers",
            "quotes": [{"symbol": "NVDA", "price": 215.33, "change_pct": 5.1}],
            "source": "yfinance",
        },
        command="screen.run",
    )
    context = normalize_records(
        {
            "symbol": "IOT",
            "target_date": "2026-03-06",
            "timeline": [{"date": "2026-03-05", "source_type": "filing", "title": "8-K filed"}],
        },
        command="price.context",
    )

    assert screen[0].entity == "NVDA"
    assert screen[0].kind == "screen_quote"
    assert screen[0].fields["query"] == "day_gainers"
    assert context[0].kind == "price_context_filing"
    assert context[0].timestamp == "2026-03-05"


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

    code = main(["market.ohlcv", "aapl", "--output", "schema", "--fields", "date,close", "--max-records", "1"])
    output = capsys.readouterr().out.strip().splitlines()

    assert code == 0
    assert output == [
        "schema|entity|kind|source|date|close",
        "row|AAPL|market_ohlcv_row|test_provider|2026-05-20|190.12",
    ]


def test_schema_selected_structural_aliases_are_filled_without_duplicate_columns():
    records = normalize_records(
        {
            "symbol": "AAPL",
            "filings": [
                {
                    "form": "10-K",
                    "accession_no": "0000320193-25-000079",
                    "filing_date": "2025-10-31",
                    "report_date": "2025-09-27",
                }
            ],
            "source": "sec_edgar",
        },
        command="filings.recent",
    )
    options = RecordRenderOptions(fields=("filing_date", "report_date", "form", "source"))

    assert render_records(records, "schema", options).splitlines() == [
        "schema|entity|kind|filing_date|report_date|form|source",
        "row|AAPL|filing|2025-10-31|2025-09-27|10-K|sec_edgar",
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
