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


def test_table_renderer_outputs_human_readable_columns():
    record = Record(
        entity="AAPL",
        kind="financial_metric",
        period="2024Q4",
        fields={"revenue": "119.6B USD", "net_income": "36.3B USD"},
        source="10-K",
    )
    options = RecordRenderOptions(fields=("revenue", "net_income"))

    output = render_records([record], "table", options)

    assert "Entity" in output
    assert "Kind" in output
    assert "Revenue" in output
    assert "AAPL" in output
    assert "119.6B USD" in output


def test_human_record_renderers_cap_float_precision():
    record = Record(
        entity="AAPL",
        kind="metric",
        fields={
            "margin": 0.04703815635893466,
            "return_pct": 28.3565,
            "nested": {"ratio": 1.23456789},
        },
    )

    compact = render_records([record], "compact")
    schema = render_records([record], "schema")
    table = render_records([record], "table")
    json_output = render_records([record], "json")

    for output in (compact, schema, table):
        assert "0.047" in output
        assert "28.3565" in output
        assert "1.2346" in output
        assert "0.047038" not in output
        assert "1.234567" not in output
    assert "0.04703815635893466" in json_output


def test_pretty_json_output_is_indented_and_parseable(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.market_data.fetch_realtime_quote",
        lambda symbol: {"symbol": symbol.upper(), "last_price": 190.12, "source": "test_provider"},
    )
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)

    code = main(["market.quote", "aapl", "--output", "pretty-json"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert '\n  "ok": true' in output
    assert payload["data"]["symbol"] == "AAPL"


def test_pretty_json_interactive_output_uses_rich_highlighting(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.market_data.fetch_realtime_quote",
        lambda symbol: {"symbol": symbol.upper(), "last_price": 190.12, "source": "test_provider"},
    )
    monkeypatch.setenv("FORCE_COLOR", "1")

    code = main(["market.quote", "aapl", "--output", "pretty-json"])
    output = capsys.readouterr().out

    assert code == 0
    assert "\x1b[" in output
    assert '"AAPL"' in output


def test_report_output_renders_document_text_as_paragraphs(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.document.read_document",
        lambda source, **_kwargs: {
            "source": source,
            "format": "pdf",
            "pages": 1,
            "text": "Revenue increased year over year.\n\nMargins improved.",
        },
    )
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)

    code = main(["document.read", "sample.pdf", "--output", "report"])
    output = capsys.readouterr().out

    assert code == 0
    assert "document.read" in output
    assert "sample.pdf" in output
    assert "Revenue increased year over year." in output
    assert "Margins improved." in output


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


def test_agent_adapters_cover_earnings_transcripts_and_price_moves():
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


def test_cli_compact_output_renders_ownership_holders(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.ownership.fetch_holders",
        lambda symbol, limit=10: {
            "symbol": symbol.upper(),
            "major_holders": [{"breakdown": "institutionsPercentHeld", "value": 0.7}],
            "institutional_holders": [{"holder": "Blackrock Inc.", "shares": 1000, "pct_held": 0.08}],
            "source": "test_provider",
        },
    )

    code = main(["ownership.holders", "nvda", "--output", "compact", "--fields", "section,holder,shares,breakdown,value"])
    output = capsys.readouterr().out.strip().splitlines()

    assert code == 0
    assert output == [
        "NVDA|major_holder|section=major_holders|breakdown=institutionsPercentHeld|value=0.7|src=test_provider",
        "NVDA|institutional_holder|section=institutional_holders|holder=Blackrock Inc.|shares=1000|src=test_provider",
    ]


def test_cli_compact_output_renders_price_performance(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.price.price_performance",
        lambda symbol, **_kwargs: {
            "symbol": symbol.upper(),
            "benchmark": "SPY",
            "performance": [{"period": "1M", "symbol_return_pct": 12.5, "benchmark_return_pct": 5.0, "relative_return_pct": 7.5}],
            "source": "test_provider",
        },
    )

    code = main(["price.performance", "nvda", "--output", "compact", "--fields", "period,symbol_return_pct,benchmark_return_pct,relative_return_pct"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert output == "NVDA|performance|1M|symbol_return_pct=12.5|benchmark_return_pct=5.0|relative_return_pct=7.5|src=test_provider"


def test_cli_compact_output_renders_price_relative(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.price.relative_price_performance",
        lambda *args, **_kwargs: {
            "symbol": "NVDA",
            "relative_performance": [
                {
                    "symbol": "NVDA",
                    "period": "1M",
                    "comparison": "SPY",
                    "comparison_type": "benchmark",
                    "symbol_return_pct": 30.0,
                    "comparison_return_pct": 10.0,
                    "relative_return_pct": 20.0,
                    "source": "test_provider",
                }
            ],
            "source": "test_provider",
        },
    )

    code = main(["price.relative", "nvda", "--output", "compact", "--fields", "period,comparison,comparison_type,relative_return_pct"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert output == "NVDA|relative_price|1M|comparison=SPY|comparison_type=benchmark|relative_return_pct=20.0|src=test_provider"


def test_cli_table_output_renders_price_relative_table(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.price.relative_price_performance",
        lambda *args, **_kwargs: {
            "symbol": "NVDA",
            "relative_performance": [
                {
                    "symbol": "NVDA",
                    "period": "1M",
                    "comparison": "SPY",
                    "comparison_type": "benchmark",
                    "symbol_return_pct": 30.0,
                    "comparison_return_pct": 10.0,
                    "relative_return_pct": 20.0,
                    "source": "test_provider",
                }
            ],
            "source": "test_provider",
        },
    )

    code = main(["price.relative", "nvda", "--output", "table"])
    output = capsys.readouterr().out

    assert code == 0
    assert not output.lstrip().startswith("{")
    assert "Relative performance: NVDA" in output
    assert "SPY" in output
    assert "+20.00%" in output


def test_cli_configured_default_output_uses_table(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(
        "finance_cli.cli.commands.price.relative_price_performance",
        lambda *args, **_kwargs: {
            "symbol": "NVDA",
            "relative_performance": [
                {
                    "symbol": "NVDA",
                    "period": "1M",
                    "comparison": "SPY",
                    "comparison_type": "benchmark",
                    "symbol_return_pct": 30.0,
                    "comparison_return_pct": 10.0,
                    "relative_return_pct": 20.0,
                    "source": "test_provider",
                }
            ],
            "source": "test_provider",
        },
    )
    config_path = tmp_path / "config.toml"
    config_path.write_text('[output]\ndefault = "table"\n', encoding="utf-8")
    monkeypatch.setenv("FINANCECLI_CONFIG", str(config_path))

    code = main(["price.relative", "nvda"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Relative performance: NVDA" in output
    assert not output.lstrip().startswith("{")


def test_cli_compact_output_renders_market_trend(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.market.market_trend",
        lambda *args, **_kwargs: {
            "market": "US",
            "trend": [
                {
                    "kind": "market_trend",
                    "symbol": "SPY",
                    "role": "primary",
                    "last_close": 500.0,
                    "sma_50": 480.0,
                    "sma_200": 450.0,
                    "above_sma_50": True,
                    "above_sma_200": True,
                    "source": "test_provider",
                }
            ],
            "market_direction_state": "uptrend",
            "source": "historical_market_data",
        },
    )

    code = main(["market.trend", "US", "--output", "compact", "--fields", "role,last_close,sma_50,sma_200,above_sma_50"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert output == "SPY|market_trend|role=primary|last_close=500.0|sma_50=480.0|sma_200=450.0|above_sma_50=true|src=test_provider"


def test_cli_table_output_renders_market_trend_readably(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.market.market_trend",
        lambda *args, **_kwargs: {
            "market": "US",
            "market_direction_state": "uptrend",
            "trend": [
                {
                    "kind": "market_trend",
                    "symbol": "SPY",
                    "role": "primary",
                    "last_close": 750.18,
                    "sma_50": 698.288,
                    "sma_200": 676.8651,
                    "above_sma_50": True,
                    "above_sma_200": True,
                    "return_1m_pct": 5.0761,
                    "return_3m_pct": 9.439,
                    "return_6m_pct": 15.6194,
                    "return_1y_pct": 28.3565,
                    "source": "test_provider",
                },
                {
                    "kind": "market_volatility",
                    "symbol": "^VIX",
                    "role": "volatility",
                    "last_close": 16.96,
                    "sma_20": 17.514,
                    "sma_50": 20.4342,
                    "volatility_trend": "falling_or_flat",
                    "volatility_state": "contained",
                    "source": "test_provider",
                },
            ],
            "source": "historical_market_data",
        },
    )

    code = main(["market.trend", "US", "--output", "table"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Market trend: US" in output
    assert "State: uptrend" in output
    assert "SPY" in output
    assert "+5.08%" in output
    assert "flat/down" in output
    assert "Entity" not in output
    assert "Last Close" not in output


def test_cli_table_output_renders_backtest_strategies_readably(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.backtest.available_backtest_strategies",
        lambda: {
            "engine": "vectorbt",
            "strategies": [
                {
                    "name": "buy_hold",
                    "summary": "Equal-weight buy and hold across all symbols.",
                    "parameters": {},
                },
                {
                    "name": "sma_cross",
                    "summary": "Long when fast moving average crosses above slow.",
                    "parameters": {
                        "fast": {"default": 20, "type": "integer"},
                        "slow": {"default": 100, "type": "integer"},
                    },
                },
            ],
        },
    )

    code = main(["backtest.strategies", "--output", "table"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Backtest strategies: vectorbt" in output
    assert "buy_hold" in output
    assert "sma_cross" in output
    assert "fast=20" in output
    assert "slow=100" in output
    assert '{"fast"' not in output
    assert "Entity" not in output
    assert "Kind" not in output


def test_cli_table_output_renders_fundamental_growth_without_fixed_zero_decimals(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.fundamentals.fundamentals_growth",
        lambda *args, **_kwargs: {
            "symbol": "NVDA",
            "rows": [
                {
                    "kind": "history",
                    "symbol": "NVDA",
                    "metric": "revenue",
                    "period_type": "annual",
                    "period": "2026",
                    "value": 215938000000.0,
                    "method": "statement",
                    "source": "test_provider",
                },
                {
                    "kind": "delta",
                    "symbol": "NVDA",
                    "metric": "net_margin",
                    "period_type": "annual",
                    "current_period": "2026",
                    "comparison_period": "2025",
                    "delta": -0.00245789,
                    "source": "test_provider",
                },
            ],
            "source": "test_provider",
        },
    )

    code = main(["fundamentals.growth", "NVDA", "--output", "table"])
    output = capsys.readouterr().out

    assert code == 0
    assert "215938000000.0000" not in output
    assert "215938000000" in output
    assert "-0.0025" in output


def test_cli_compact_output_renders_fundamental_metrics(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.fundamentals.fetch_financial_metrics",
        lambda symbol, **_kwargs: {
            "symbol": symbol.upper(),
            "period": "quarterly",
            "metrics": [{"metric": "revenue", "value": 100.0}, {"metric": "eps", "value": 2.5}],
            "source": "test_provider",
        },
    )

    code = main(["fundamentals.metrics", "nvda", "--output", "compact", "--fields", "metric,value"])
    output = capsys.readouterr().out.strip().splitlines()

    assert code == 0
    assert output == [
        "NVDA|metric|quarterly|metric=revenue|value=100.0|src=test_provider",
        "NVDA|metric|quarterly|metric=eps|value=2.5|src=test_provider",
    ]


def test_cli_compact_output_renders_fundamentals_growth(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.fundamentals.fundamentals_growth",
        lambda *args, **_kwargs: {
            "symbol": "NVDA",
            "rows": [
                {
                    "kind": "growth",
                    "metric": "revenue",
                    "period_type": "quarterly",
                    "current_period": "2025Q1",
                    "comparison_period": "2024Q1",
                    "current_value": 75.0,
                    "comparison_value": 50.0,
                    "growth_type": "yoy",
                    "growth_pct": 50.0,
                    "source": "test_provider",
                }
            ],
            "source": "test_provider",
        },
    )

    code = main(["fundamentals.growth", "nvda", "--output", "compact", "--fields", "metric,growth_type,growth_pct"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert output == "NVDA|fundamental_growth|metric=revenue|growth_type=yoy|growth_pct=50.0|src=test_provider"


def test_cli_compact_output_renders_fundamental_delta(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.fundamentals.fundamentals_growth",
        lambda *args, **_kwargs: {
            "symbol": "NVDA",
            "rows": [
                {
                    "kind": "delta",
                    "metric": "net_margin",
                    "period_type": "annual",
                    "current_period": "2025",
                    "comparison_period": "2024",
                    "current_value": 0.2,
                    "comparison_value": 0.1,
                    "delta": 0.1,
                    "source": "test_provider",
                }
            ],
            "source": "test_provider",
        },
    )

    code = main(["fundamentals.growth", "nvda", "--output", "compact", "--fields", "metric,current_period,comparison_period,delta"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert output == "NVDA|fundamental_delta|metric=net_margin|current_period=2025|comparison_period=2024|delta=0.1|src=test_provider"


def test_cli_table_output_renders_fundamentals_statement_as_financial_table(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.fundamentals.fetch_financial_statement_with_display",
        lambda symbol, **_kwargs: ({
            "symbol": symbol.upper(),
            "statement": "income",
            "period": "annual",
            "periods": ["2025-09-27", "2024-09-28", "2023-09-30"],
            "rows": [
                {
                    "concept": "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax",
                    "label": "Net sales",
                    "level": 4,
                    "abstract": False,
                    "2025-09-27": 416_161_000_000,
                    "2024-09-28": 391_035_000_000,
                    "2023-09-30": 383_285_000_000,
                },
                {
                    "concept": "us-gaap_EarningsPerShareDiluted",
                    "label": "Diluted (in dollars per share)",
                    "level": 4,
                    "abstract": False,
                    "2025-09-27": 7.46,
                    "2024-09-28": 6.08,
                    "2023-09-30": 6.13,
                },
            ],
            "source": "edgartools",
        }, None),
    )

    code = main(["fundamentals.statement", "AAPL", "--output", "table"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Income statement: AAPL | annual | edgartools" in output
    assert "Line item" in output
    assert "Net sales" in output
    assert "416.16B" in output
    assert "Diluted (in dollars per share)" in output
    assert "7.46" in output
    assert "Entity" not in output
    assert "Kind" not in output
    assert "Concept" not in output


def test_cli_table_output_prefers_native_statement_display(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.fundamentals.fetch_financial_statement_with_display",
        lambda symbol, **_kwargs: ({
            "symbol": symbol.upper(),
            "statement": "income",
            "period": "annual",
            "rows": [{"label": "Net sales", "2025": 100}],
            "source": "edgartools",
        }, "NATIVE EDGARTOOLS RICH"),
    )

    code = main(["fundamentals.statement", "AAPL", "--output", "table"])
    output = capsys.readouterr().out

    assert code == 0
    assert output.strip() == "NATIVE EDGARTOOLS RICH"


def test_cli_json_output_omits_native_statement_display(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.fundamentals.fetch_financial_statement_with_display",
        lambda symbol, **_kwargs: ({
            "symbol": symbol.upper(),
            "statement": "income",
            "period": "annual",
            "rows": [{"label": "Net sales", "2025": 100}],
            "source": "edgartools",
        }, "NATIVE EDGARTOOLS RICH"),
    )

    code = main(["fundamentals.statement", "AAPL", "--output", "json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["data"]["rows"][0]["label"] == "Net sales"
    assert "display" not in payload
    assert "NATIVE EDGARTOOLS RICH" not in json.dumps(payload)


def test_cli_schema_output_renders_standard_filing_statement_rows(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.filings.read_filing_statement_with_display",
        lambda **_kwargs: ({
            "filing": {"company": "Costco", "filing_date": "2024-10-09", "period_of_report": "2024-09-01"},
            "statement": "balance",
            "view": "standard",
            "rows": [{"concept": "us-gaap_CommonStockValue", "label": "Common Stock", "level": 4, "abstract": False, "2024-09-01": 2}],
            "source": "edgartools",
        }, None),
    )

    code = main(["filings.statement", "COST", "statement=balance", "--output", "schema", "--fields", "concept,label,2024-09-01"])
    output = capsys.readouterr().out.strip().splitlines()

    assert code == 0
    assert output == [
        "schema|entity|kind|period|timestamp|source|concept|label|2024-09-01",
        "row|Costco|filings_statement_row|2024-09-01|2024-10-09|edgartools|us-gaap_CommonStockValue|Common Stock|2",
    ]


def test_cli_compact_output_renders_raw_filing_statement_rows(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.filings.read_filing_statement_with_display",
        lambda **_kwargs: ({
            "filing": {"company": "Costco", "filing_date": "2024-10-09", "period_of_report": "2024-09-01"},
            "statement": "balance",
            "view": "raw",
            "rows": [{"label": "Common Stock", "values": {"2024-09-01": {"raw": 2000000, "reported": 2, "unit": "usd"}}}],
            "source": "edgartools",
        }, None),
    )

    code = main(["filings.statement", "COST", "statement=balance", "view=raw", "--output", "compact", "--fields", "label,values"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert output == 'Costco|filings_statement_row|2024-09-01|2024-10-09|label=Common Stock|values={"2024-09-01":{"raw":2000000,"reported":2,"unit":"usd"}}|src=edgartools'


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
