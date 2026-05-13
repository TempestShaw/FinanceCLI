import json
from pathlib import Path

from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.main import main
from finance_cli.cli.registry import clear_commands, get_command, list_commands
from finance_cli.core.market import get_market_regime, get_sector_heat
from finance_cli.core.symbols import get_symbol_snapshot
from finance_cli.backtesting.portfolio import build_quantile_weights
from finance_cli.backtesting.result_shaping import shape_backtest_result
from finance_cli.providers.alpaca import AlpacaMarketDataProvider
from finance_cli.providers.company_ir import CompanyIRProvider
from finance_cli.providers.company_ir import _extract_date as _extract_company_ir_date
from finance_cli.providers.company_ir import _registrable_domain as _company_ir_registrable_domain
from finance_cli.providers.config import PRESENTATION_RULES
from finance_cli.providers.camelot_tables import CamelotTableProvider
from finance_cli.providers.fmp import FMPProvider
from finance_cli.providers.gdelt import GdeltNewsProvider
from finance_cli.providers.historical import HistoricalMarketDataService
from finance_cli.providers.html_document import HTMLDocumentProvider, _text_blocks
from finance_cli.providers.native_pdf import NativePDFProvider, reconstruct_reading_order
from finance_cli.providers.paddle_ocr import PaddleOCRProvider
from finance_cli.providers.sec_edgar import SecEdgarProvider
from finance_cli.providers.sec_edgar.events import classify_filing_event
from finance_cli.providers.transcripts import MotleyFoolTranscriptProvider
from finance_cli.providers.yahoo import YahooFinanceProvider
from finance_cli.services.backtest import (
    available_backtest_strategies,
    build_factor_backtest_payload,
    run_backtest,
    tune_backtest,
    preview_factor_rebalance,
)
from finance_cli.services.documents import extract_document_tables, ocr_document, read_document, scan_document, window_document
from finance_cli.services.estimates import compare_estimates, consensus_estimates
from finance_cli.services.formulas import (
    formula_cagr,
    formula_days,
    formula_lease_equivalent,
    formula_net_debt,
    formula_operating_cash,
    formula_operating_current_assets,
    formula_operating_current_liabilities,
    formula_wacc,
    formula_working_capital,
)
from finance_cli.services.kpi import extract_kpi_evidence
from finance_cli.services.market_data import fetch_ohlcv
from finance_cli.services.news import news_geo, normalize_news_timespan
from finance_cli.services.price import detect_price_moves, price_context
from finance_cli.services.research import research_plan
from finance_cli.services.sources import list_sources, sources_status
from finance_cli.services.valuation import valuation_dcf, valuation_irr, valuation_multiples, valuation_npv, valuation_scenario, valuation_wacc
from finance_cli.tools import FINANCE_TOOL_SPECS


def setup_function():
    clear_commands()


def test_default_install_includes_full_research_stack_without_vectorbt_full():
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    text = pyproject.read_text()
    dependencies = text.split("dependencies = [", 1)[1].split("]\n\n[project.optional-dependencies]", 1)[0]

    for package in ("camelot-py", "edgartools", "paddleocr", "paddlepaddle", "pypdf", "PyMuPDF", "yfinance", "vectorbt"):
        assert package in dependencies

    for package in ("vectorbt[full]",):
        assert package not in dependencies

    optional_dependencies = text.split("[project.optional-dependencies]", 1)[1].split("[project.scripts]", 1)[0]
    assert "dev =" in optional_dependencies
    assert "ocr =" not in optional_dependencies
    assert "tables =" not in optional_dependencies


def test_core_market_and_symbol_capabilities_return_structured_results(monkeypatch):
    class MarketDataService:
        def load_ohlcv_batch(self, symbols, **kwargs):
            return {
                symbol: (_fake_market_rows(100, 110), None, [])
                for symbol in symbols
            }

    monkeypatch.setattr(
        "finance_cli.core.symbols.fetch_symbol_profile",
        lambda symbol: {
            "symbol": symbol,
            "company_name": "NVIDIA Corporation",
            "sector": "Technology",
            "industry": "Semiconductors",
            "last_price": 111.4,
            "market_cap": 1_000_000_000,
            "currency": "USD",
            "cik": "0001045810",
            "sources": ["test"],
        },
    )

    regime = get_market_regime("US", "swing", service=MarketDataService())
    heat = get_sector_heat("US", 20, "sector", service=MarketDataService())
    snapshot = get_symbol_snapshot("nvda")

    assert regime.market == "US"
    assert regime.signals
    assert regime.meta.source == "historical_market_data"
    assert heat.leaders
    assert heat.meta.source == "historical_market_data"
    assert snapshot.symbol == "NVDA"
    assert snapshot.company_name == "NVIDIA Corporation"


def _fake_market_rows(start: float, end: float, *, count: int = 260) -> list[dict]:
    step = (end - start) / max(count - 1, 1)
    return [
        {"date": f"2026-01-{(index % 28) + 1:02d}", "close": start + step * index, "source": "test"}
        for index in range(count)
    ]


def test_cli_registry_registers_builtin_commands():
    register_builtin_commands()
    names = {command.name for command in list_commands()}

    assert "market.regime" in names
    assert "sources.list" in names
    assert "sources.status" in names
    assert "sources.test" in names
    assert "market.sector_heat" in names
    assert "symbol.snapshot" in names
    assert "symbol.profile" in names
    assert "news.search" in names
    assert "news.analyze" in names
    assert "filings.recent" in names
    assert "filings.read" in names
    assert "filings.sections" in names
    assert "filings.statement" in names
    assert "filings.reports" in names
    assert "filings.report" in names
    assert "transcripts.search" in names
    assert "transcripts.read" in names
    assert "transcripts.qa" in names
    assert "fundamentals.statement" in names
    assert "kpi.extract" in names
    assert "kpi.history" in names
    assert "valuation.multiples" in names
    assert "valuation.scenario" in names
    assert "valuation.npv" in names
    assert "valuation.irr" in names
    assert "valuation.wacc" in names
    assert "valuation.dcf" in names
    assert "formula.ebitda" in names
    assert "formula.adjusted_ebitda" in names
    assert "formula.margin" in names
    assert "formula.days" in names
    assert "formula.turnover" in names
    assert "formula.operating_cash" in names
    assert "formula.lease_equivalent" in names
    assert "formula.capm" in names
    assert "formula.wacc" in names
    assert "formula.enterprise_value" in names
    assert "formula.roic" in names
    assert "formula.cagr" in names
    assert "formula.net_debt" in names
    assert "formula.operating_current_assets" in names
    assert "formula.operating_current_liabilities" in names
    assert "formula.working_capital" in names
    assert "estimates.consensus" in names
    assert "estimates.compare" in names
    assert "price.moves" in names
    assert "price.context" in names
    assert "research.plan" in names
    assert "market.quote" in names
    assert "market.ohlcv" in names
    assert "backtest.strategy.payload" in names
    assert "backtest.factor.payload" in names
    assert "backtest.factor.weights" in names
    assert "document.read" in names
    assert "document.scan" in names
    assert "document.window" in names
    assert "document.tables" in names
    assert "document.ocr" in names
    assert get_command("symbol.snapshot") is not None


def test_cli_main_runs_symbol_snapshot(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.symbol.fetch_symbol_profile",
        lambda symbol: {"symbol": symbol.upper(), "company_name": "NVIDIA Corporation"},
    )

    code = main(["symbol.snapshot", "NVDA"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["symbol"] == "NVDA"


def test_cli_main_shows_command_help(capsys):
    code = main(["news.analyze", "--help"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Usage: news.analyze" in output
    assert "analysis=timeline|tone|context|geo|doc" in output
    assert "timespan=30D|1W|1M|24H" in output
    assert "date=YYYY-MM-DD" in output
    assert "start_date=YYYY-MM-DD" in output
    assert "Examples:" in output


def test_news_timespan_accepts_human_friendly_lookbacks():
    assert normalize_news_timespan("30D") == "30d"
    assert normalize_news_timespan("1W") == "1w"
    assert normalize_news_timespan("1M") == "1m"
    assert normalize_news_timespan("24H") == "24h"
    assert normalize_news_timespan("90min") == "90min"
    assert normalize_news_timespan("2 weeks") == "2w"


def test_provider_presentation_rules_are_configured_once():
    assert "investor day" in PRESENTATION_RULES.high_terms
    assert "press release" in PRESENTATION_RULES.exclude_terms
    assert "presentation" in PRESENTATION_RULES.override_terms


def test_cli_command_accepts_help_flag(capsys):
    code = main(["market.ohlcv", "--help"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Usage: market.ohlcv" in output
    assert "SYMBOL[,SYMBOL...]" in output


def test_cli_sources_help_and_status(capsys):
    code = main(["sources", "--help"])
    output = capsys.readouterr().out

    assert code == 0
    assert "list" in output
    assert "status" in output
    assert "test" in output

    code = main(["sources.status"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert any(row["name"] == "yfinance" for row in payload["data"]["sources"])


def test_cli_namespace_help_lists_child_commands(capsys):
    code = main(["market", "--help"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Commands under `market`" in output
    assert "quote" in output
    assert "ohlcv" in output
    assert "finance market.COMMAND --help" in output


def test_cli_valuation_help_documents_new_commands(capsys):
    code = main(["valuation", "--help"])
    output = capsys.readouterr().out

    assert code == 0
    assert "multiples" in output
    assert "scenario" in output
    assert "npv" in output
    assert "irr" in output
    assert "wacc" in output
    assert "dcf" in output

    code = main(["valuation.dcf", "--help"])
    output = capsys.readouterr().out

    assert code == 0
    assert "terminal_growth=3%" in output
    assert "do not include an initial t=0 investment cash flow" in output
    assert "Use either terminal_growth or exit_multiple" in output


def test_cli_price_help_documents_temporal_evidence(capsys):
    register_builtin_commands()

    code = main(["price", "--help"])
    output = capsys.readouterr().out

    assert code == 0
    assert "moves" in output
    assert "context" in output

    code = main(["price.context", "--help"])
    output = capsys.readouterr().out

    assert code == 0
    assert "date=YYYY-MM-DD" in output
    assert "lookback=3D" in output
    assert "temporal only" in output

    code = main(["price.moves", "--help"])
    output = capsys.readouterr().out

    assert code == 0
    assert "1w=5 trading days" in output
    assert "0.08, 8, and 8%" in output
    assert "window is a trading-day window" in output


def test_sources_inventory_and_status_are_non_network_diagnostics():
    inventory = list_sources()
    status = sources_status()

    assert inventory["count"] >= 4
    assert any(row["name"] == "sec" for row in inventory["sources"])
    assert any(row["name"] == "fmp" for row in inventory["sources"])
    assert any(row["name"] == "gdelt" for row in status["sources"])
    assert "summary" in status


def test_detect_price_moves_is_deterministic_and_close_to_close():
    rows = [
        {"date": "2026-01-01", "close": 100, "volume": 100, "source": "test"},
        {"date": "2026-01-02", "close": 103, "volume": 100, "source": "test"},
        {"date": "2026-01-03", "close": 90, "volume": 300, "source": "test"},
        {"date": "2026-01-04", "close": 99, "volume": 200, "source": "test"},
    ]

    moves = detect_price_moves(rows, symbol="IOT", threshold="8%", limit=10)

    assert [move["end_date"] for move in moves] == ["2026-01-03", "2026-01-04"]
    assert moves[0]["direction"] == "down"
    assert moves[0]["return_pct"] == -12.62
    assert "evidence_role" not in moves[0]


def test_price_move_window_and_threshold_are_explicit():
    rows = [
        {"date": "2026-01-01", "close": 100, "volume": 100, "source": "test"},
        {"date": "2026-01-02", "close": 101, "volume": 100, "source": "test"},
        {"date": "2026-01-05", "close": 102, "volume": 100, "source": "test"},
        {"date": "2026-01-06", "close": 103, "volume": 100, "source": "test"},
        {"date": "2026-01-07", "close": 104, "volume": 100, "source": "test"},
        {"date": "2026-01-08", "close": 110, "volume": 100, "source": "test"},
    ]

    weekly_moves = detect_price_moves(rows, symbol="IOT", window="1w", threshold="9%", limit=10)
    decimal_threshold_moves = detect_price_moves(rows, symbol="IOT", window="1d", threshold=0.08, limit=10)
    explicit_tiny_threshold_moves = detect_price_moves(rows, symbol="IOT", window="1d", threshold="0.08%", limit=10)

    assert weekly_moves[0]["window"] == "5 trading days"
    assert weekly_moves[0]["return_pct"] == 10.0
    assert decimal_threshold_moves == []
    assert explicit_tiny_threshold_moves


def test_price_context_returns_temporal_timeline_without_causality(monkeypatch):
    monkeypatch.setattr(
        "finance_cli.services.price.list_recent_filings",
        lambda *args, **kwargs: {
            "filings": [
                {
                    "form": "8-K",
                    "filed_at": "2026-01-03",
                    "report_date": "2026-01-02",
                    "accession_no": "0000000000-26-000001",
                    "items": ["2.02"],
                    "url": "https://sec.example/filing",
                }
            ]
        },
    )
    monkeypatch.setattr(
        "finance_cli.services.price._news_rows",
        lambda *args, **kwargs: [
            {
                "title": "Company reports results",
                "url": "https://news.example/story",
                "seendate": "20260102T120000Z",
                "domain": "news.example",
                "language": "English",
            }
        ],
    )
    monkeypatch.setattr(
        "finance_cli.services.price.search_transcripts",
        lambda *args, **kwargs: {
            "transcripts": [
                {
                    "title": "IOT earnings call",
                    "url": "https://transcript.example/iot",
                    "quarter": "Q4",
                    "published_at": "2026-01-04T01:00:00+00:00",
                    "source": "test",
                }
            ]
        },
    )

    result = price_context("IOT", target_date="2026-01-03", lookback="1D")

    assert result["count"] == 3
    roles = {row["source_type"]: row["evidence_role"] for row in result["timeline"]}
    assert roles == {"news": "before_move", "filing": "same_day", "transcript": "after_move"}
    assert "caused_by" not in json.dumps(result)


def test_price_context_accepts_calendar_window_strings(monkeypatch):
    monkeypatch.setattr("finance_cli.services.price.list_recent_filings", lambda *args, **kwargs: {"filings": []})
    monkeypatch.setattr("finance_cli.services.price._news_rows", lambda *args, **kwargs: [])
    monkeypatch.setattr("finance_cli.services.price.search_transcripts", lambda *args, **kwargs: {"transcripts": []})

    result = price_context("IOT", target_date="2026-01-03", lookback="1W")

    assert result["lookback_days"] == 7
    assert result["start_date"] == "2025-12-27"
    assert result["end_date"] == "2026-01-10"


def test_finance_capabilities_are_connector_neutral():
    finance_py_files = [
        path for path in Path("finance_cli").rglob("*.py")
        if "__pycache__" not in path.parts
    ]
    forbidden_imports = (
        "memory.",
        "context.",
        "checkpoint.",
        "task.",
        "src.",
    )

    offenders = []
    for path in finance_py_files:
        text = path.read_text(encoding="utf-8")
        for forbidden in forbidden_imports:
            if forbidden in text:
                offenders.append(f"{path}:{forbidden}")

    assert offenders == []


def test_sec_filing_classifier_maps_8k_earnings_event():
    events = classify_filing_event(
        {
            "symbol": "MSFT",
            "cik": "0000789019",
            "form": "8-K",
            "accession_no": "0000789019-26-000001",
            "filed_at": "2026-01-30",
            "items": ["Item 2.02"],
        }
    )

    assert len(events) == 1
    assert events[0].event_type == "earnings_release"
    assert events[0].importance == 9


def test_cli_filings_read_passes_accession_and_section(capsys, monkeypatch):
    def fake_read_filing_section(**kwargs):
        return {
            "filing": {"accession_no": kwargs["accession_no"]},
            "section": {"key": kwargs["section"]},
            "text": "Business text",
        }

    monkeypatch.setattr("finance_cli.cli.commands.filings.read_filing_section", fake_read_filing_section)
    code = main(["filings.read", "accession=0001628280-26-018167", "section=business", "max_chars=100"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["filing"]["accession_no"] == "0001628280-26-018167"
    assert payload["data"]["section"]["key"] == "business"


def test_cli_filings_sections_passes_symbol(capsys, monkeypatch):
    def fake_list_filing_sections(**kwargs):
        return {
            "filing": {"company": "Samsara Inc."},
            "supported_sections": [{"key": "business", "available": True}],
            "symbol": kwargs["symbol"],
        }

    monkeypatch.setattr("finance_cli.cli.commands.filings.list_filing_sections", fake_list_filing_sections)
    code = main(["filings.sections", "IOT", "form=10-K"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["symbol"] == "IOT"
    assert payload["data"]["supported_sections"][0]["available"] is True


def test_cli_filings_statement_passes_url_and_query(capsys, monkeypatch):
    def fake_read_filing_statement(**kwargs):
        return {
            "filing": {"accession_no": "0000909832-24-000049"},
            "statement": kwargs["statement"],
            "query": kwargs["query"],
            "max_rows": kwargs["max_rows"],
            "url": kwargs["url"],
        }

    monkeypatch.setattr("finance_cli.cli.commands.filings.read_filing_statement", fake_read_filing_statement)
    code = main([
        "filings.statement",
        "url=https://www.sec.gov/Archives/edgar/data/909832/000090983224000049/cost-20240901.htm",
        "statement=balance",
        "query=Common Stock",
    ])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["statement"] == "balance"
    assert payload["data"]["query"] == "Common Stock"
    assert payload["data"]["max_rows"] == 0
    assert payload["data"]["url"].endswith("cost-20240901.htm")


def test_cli_filings_report_passes_report_name(capsys, monkeypatch):
    def fake_read_filing_report(**kwargs):
        return {
            "report": {"short_name": kwargs["name"]},
            "query": kwargs["query"],
            "max_rows": kwargs["max_rows"],
            "max_chars": kwargs["max_chars"],
        }

    monkeypatch.setattr("finance_cli.cli.commands.filings.read_filing_report", fake_read_filing_report)
    code = main([
        "filings.report",
        "COST",
        "name=Consolidated Balance Sheets (Parenthetical)",
        "query=shares issued",
        "max_rows=3",
        "max_chars=2000",
    ])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["report"]["short_name"] == "Consolidated Balance Sheets (Parenthetical)"
    assert payload["data"]["query"] == "shares issued"
    assert payload["data"]["max_rows"] == 3
    assert payload["data"]["max_chars"] == 2000


def test_cli_filings_reports_passes_query(capsys, monkeypatch):
    def fake_list_filing_reports(**kwargs):
        return {
            "reports": [{"short_name": "Leases"}],
            "query": kwargs["query"],
        }

    monkeypatch.setattr("finance_cli.cli.commands.filings.list_filing_reports", fake_list_filing_reports)
    code = main(["filings.reports", "COST", "query=lease"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["query"] == "lease"


def test_sec_edgar_filing_statement_scales_reported_values(monkeypatch):
    class Statement:
        def get_raw_data(self):
            return [
                {
                    "concept": "us-gaap_CommonStockValue",
                    "label": "Common Stock $.005 par value; 443,126,000 shares issued and outstanding",
                    "values": {"instant_2024-09-01": 2_000_000.0, "instant_2023-09-03": 2_000_000.0},
                    "decimals": {"instant_2024-09-01": -6, "instant_2023-09-03": -6},
                    "units": {"instant_2024-09-01": "usd", "instant_2023-09-03": "usd"},
                    "period_types": {"instant_2024-09-01": "instant", "instant_2023-09-03": "instant"},
                    "preferred_signs": {"instant_2024-09-01": 1, "instant_2023-09-03": 1},
                    "level": 4,
                    "is_abstract": False,
                    "balance": "credit",
                    "parent": "us-gaap_StockholdersEquityAbstract",
                    "calculation_parent": "us-gaap_StockholdersEquity",
                }
            ]

    class FilingObject:
        balance_sheet = Statement()

    class Filing:
        company = "Costco"
        cik = "909832"
        form = "10-K"
        filing_date = "2024-10-09"
        period_of_report = "2024-09-01"
        accession_no = "0000909832-24-000049"
        filing_url = "https://sec.example/cost.htm"
        homepage_url = "https://sec.example/index.htm"
        text_url = "https://sec.example/cost.txt"

        def obj(self):
            return FilingObject()

    provider = SecEdgarProvider()
    monkeypatch.setattr(provider, "_get_filing", lambda **kwargs: Filing())

    data = provider.filing_statement(url="https://sec.example/cost.htm", statement="balance", query="Common Stock")

    assert data["periods"] == ["2024-09-01", "2023-09-03"]
    assert data["rows"][0]["values"]["2024-09-01"]["raw"] == 2_000_000
    assert data["rows"][0]["values"]["2024-09-01"]["reported"] == 2


def test_sec_edgar_report_reads_parenthetical_report(monkeypatch):
    class Report:
        short_name = "Consolidated Balance Sheets (Parenthetical)"
        long_name = "Consolidated Balance Sheets (Parenthetical)"
        menu_category = "Statements"
        html_file_name = "R6.htm"
        content = """
        <table class="report">
          <tr>
            <th><div>Consolidated Balance Sheets (Parenthetical)</div></th>
            <th><div>Sep. 01, 2024</div></th>
            <th><div>Sep. 03, 2023</div></th>
          </tr>
          <tr>
            <td><a onclick="Show.showAR(this, 'defref_cost_CommonSharesIssuedAndOutstanding', window);">Common stock, shares issued and outstanding</a></td>
            <td>443,126,000</td>
            <td>442,793,000</td>
          </tr>
        </table>
        """

        def text(self):
            return "Common stock, shares issued 443,126,000 442,793,000"

    class Reports:
        short_names = ["Consolidated Balance Sheets", "Consolidated Balance Sheets (Parenthetical)"]

        def get_by_short_name(self, name):
            return Report()

    class FilingObject:
        reports = Reports()

    class Filing:
        company = "Costco"
        cik = "909832"
        form = "10-K"
        filing_date = "2024-10-09"
        period_of_report = "2024-09-01"
        accession_no = "0000909832-24-000049"
        filing_url = "https://sec.example/cost.htm"
        homepage_url = "https://sec.example/index.htm"
        text_url = "https://sec.example/cost.txt"

        def obj(self):
            return FilingObject()

    provider = SecEdgarProvider()
    monkeypatch.setattr(provider, "_get_filing", lambda **kwargs: Filing())

    data = provider.read_filing_report(
        url="https://sec.example/cost.htm",
        name="Parenthetical",
        query="shares issued",
        max_chars=200,
    )

    assert data["report"]["short_name"] == "Consolidated Balance Sheets (Parenthetical)"
    assert "shares issued" in data["text"]
    assert data["rows"][0]["label"] == "Common stock, shares issued and outstanding"
    assert data["rows"][0]["values"][0]["number"] == 443126000
    assert data["rows"][0]["concept"] == "cost_CommonSharesIssuedAndOutstanding"


def test_sec_edgar_reports_can_filter_by_query(monkeypatch):
    class Report:
        def __init__(self, short_name):
            self.short_name = short_name
            self.long_name = short_name
            self.menu_category = "Details"
            self.html_file_name = f"{short_name}.htm"

    class Reports:
        short_names = ["Debt", "Leases", "Segment Reporting"]

        def get_by_short_name(self, name):
            return Report(name)

    class FilingObject:
        reports = Reports()

    class Filing:
        company = "Costco"
        cik = "909832"
        form = "10-K"
        filing_date = "2024-10-09"
        period_of_report = "2024-09-01"
        accession_no = "0000909832-24-000049"
        filing_url = "https://sec.example/cost.htm"
        homepage_url = "https://sec.example/index.htm"
        text_url = "https://sec.example/cost.txt"

        def obj(self):
            return FilingObject()

    provider = SecEdgarProvider()
    monkeypatch.setattr(provider, "_get_filing", lambda **kwargs: Filing())

    data = provider.filing_reports(url="https://sec.example/cost.htm", query="lease")

    assert data["count"] == 1
    assert data["reports"][0]["short_name"] == "Leases"

    file_name_query = provider.filing_reports(url="https://sec.example/cost.htm", query="r2")
    assert file_name_query["count"] == 0


def test_sec_edgar_report_rows_include_context_for_repeated_labels(monkeypatch):
    class Report:
        short_name = "Segment Reporting Information by Segment"
        long_name = short_name
        menu_category = "Details"
        html_file_name = "R68.htm"
        content = """
        <table class="report">
          <tr><th>Segment Reporting</th><th>Sep. 01, 2024</th></tr>
          <tr><td><a onclick="Show.showAR(this, 'defref_srt_ConsolidationItemsAxis=us-gaap_OperatingSegmentsMember', window);">Operating Segments | United States Operations</a></td><td></td></tr>
          <tr><td><a onclick="Show.showAR(this, 'defref_us-gaap_Revenues', window);">Total revenue</a></td><td>184,143</td></tr>
          <tr><td><a onclick="Show.showAR(this, 'defref_srt_ConsolidationItemsAxis=us-gaap_OperatingSegmentsMember', window);">Operating Segments | Canadian Operations</a></td><td></td></tr>
          <tr><td><a onclick="Show.showAR(this, 'defref_us-gaap_Revenues', window);">Total revenue</a></td><td>34,874</td></tr>
        </table>
        """

        def text(self):
            return "Total revenue 184,143 34,874"

    class Reports:
        short_names = ["Segment Reporting Information by Segment"]

        def get_by_short_name(self, name):
            return Report()

    class FilingObject:
        reports = Reports()

    class Filing:
        company = "Costco"
        cik = "909832"
        form = "10-K"
        filing_date = "2024-10-09"
        period_of_report = "2024-09-01"
        accession_no = "0000909832-24-000049"
        filing_url = "https://sec.example/cost.htm"
        homepage_url = "https://sec.example/index.htm"
        text_url = "https://sec.example/cost.txt"

        def obj(self):
            return FilingObject()

    provider = SecEdgarProvider()
    monkeypatch.setattr(provider, "_get_filing", lambda **kwargs: Filing())

    data = provider.read_filing_report(
        url="https://sec.example/cost.htm",
        name="Segment",
        query="Canadian total revenue",
    )

    assert data["row_count"] == 1
    assert data["rows"][0]["context"] == ["Operating Segments | Canadian Operations"]
    assert data["rows"][0]["values"][0]["number"] == 34874


def test_sec_edgar_report_rows_respect_max_rows_and_parse_numbers(monkeypatch):
    class Report:
        short_name = "Tax"
        long_name = short_name
        menu_category = "Details"
        html_file_name = "R1.htm"
        content = """
        <table class="report">
          <tr><th>Tax</th><th>2024</th></tr>
          <tr><td>Federal tax</td><td>(1,234)</td></tr>
          <tr><td>State rate</td><td>12.5%</td></tr>
          <tr><td>Other tax</td><td>$ 45</td></tr>
        </table>
        """

        def text(self):
            return "Federal tax (1,234) State rate 12.5% Other tax $45"

    class Reports:
        short_names = ["Tax"]

        def get_by_short_name(self, name):
            return Report()

    class FilingObject:
        reports = Reports()

    class Filing:
        company = "Costco"
        cik = "909832"
        form = "10-K"
        filing_date = "2024-10-09"
        period_of_report = "2024-09-01"
        accession_no = "0000909832-24-000049"
        filing_url = "https://sec.example/cost.htm"
        homepage_url = "https://sec.example/index.htm"
        text_url = "https://sec.example/cost.txt"

        def obj(self):
            return FilingObject()

    provider = SecEdgarProvider()
    monkeypatch.setattr(provider, "_get_filing", lambda **kwargs: Filing())

    data = provider.read_filing_report(url="https://sec.example/cost.htm", name="Tax", max_rows=2)

    assert data["row_count"] == 2
    assert data["rows_truncated"] is True
    assert data["rows"][0]["values"][0]["number"] == -1234
    assert data["rows"][1]["values"][0]["number"] == 0.125


def test_cli_transcripts_search_passes_symbol(capsys, monkeypatch):
    def fake_search_transcripts(symbol, *, limit, debug):
        return {"symbol": symbol, "count": limit, "debug": debug, "transcripts": []}

    monkeypatch.setattr("finance_cli.cli.commands.transcripts.search_transcripts", fake_search_transcripts)
    code = main(["transcripts.search", "IOT", "limit=2"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["symbol"] == "IOT"
    assert payload["data"]["count"] == 2
    assert payload["data"]["debug"] is False


def test_motley_fool_transcript_parser_extracts_qa_pairs():
    html = """
    <html>
      <head>
        <script type="application/ld+json">
        {"headline":"Samsara (IOT) Q4 2026 Earnings Call Transcript","datePublished":"2026-03-05T23:27:39.000Z"}
        </script>
      </head>
      <body>
        <div id="article-body-transcript">
          <h2>Date</h2>
          <p>Thursday, March 5, 2026 at 5 p.m. ET</p>
          <h2>Summary</h2>
          <p>Summary text.</p>
          <h2>Full Conference Call Transcript</h2>
          <p>Sanjit Biswas: Prepared remarks.</p>
          <p>Dominic Phillips: Financial remarks.</p>
          <p>Mike Chang: We will now open the line up for questions.</p>
          <p>Matt Hedberg: Can you talk about large customer growth?</p>
          <p>Sanjit Biswas: Large customers are adopting more products.</p>
          <p>Mike Chang: The next question comes from Keith Weiss.</p>
          <p>Keith Weiss: What is driving emerging products?</p>
          <p>Dominic Phillips: Emerging products are contributing more net new ACV.</p>
        </div>
      </body>
    </html>
    """

    class FakeProvider(MotleyFoolTranscriptProvider):
        def _get_text(self, _url):
            return html

    data = FakeProvider().read("IOT", url="https://example.test/transcript", max_chars=200, include_turns=True)

    assert data["transcript"]["quarter"] == "Q4 2026"
    assert data["date"] == "Thursday, March 5, 2026 at 5 p.m. ET"
    assert data["summary"] == "Summary text."
    assert len(data["prepared_remarks"]) == 2
    assert len(data["qa_pairs"]) == 2
    assert data["qa_pairs"][0]["questioner"] == "Matt Hedberg"
    assert data["qa_pairs"][0]["answers"][0]["speaker"] == "Sanjit Biswas"


def test_transcript_parser_uses_fuzzy_qa_markers():
    html = """
    <html><body>
      <div id="article-body-transcript">
        <h2>Full Conference Call Transcript</h2>
        <p>CEO Person: Prepared remarks.</p>
        <p>IR Person: We will now open the call up for questions.</p>
        <p>Analyst One: What changed in demand?</p>
        <p>CEO Person: Demand improved.</p>
        <p>IR Person: Your next question is from Analyst Two.</p>
        <p>Analyst Two: How should we think about margins?</p>
        <p>CEO Person: Margins expanded.</p>
      </div>
    </body></html>
    """

    class FakeProvider(MotleyFoolTranscriptProvider):
        def _get_text(self, _url):
            return html

    data = FakeProvider().read("IOT", url="https://example.test/transcript", include_turns=True)

    assert len(data["prepared_remarks"]) == 1
    assert len(data["qa_pairs"]) == 2
    assert data["qa_pairs"][1]["questioner"] == "Analyst Two"


def test_kpi_evidence_extractor_finds_saas_metrics():
    text = (
        "We ended the year with $1.9 billion in ARR, growing 30% year over year. "
        "Our $432 million of net new ARR drove this performance. "
        "We added 204 new $100K+ ARR customers and achieved net retention of approximately 115%. "
        "Emerging products contributed 23% of net new ACV in Q4."
    )
    rows = extract_kpi_evidence(
        text,
        metrics=["arr", "net_new_arr", "large_customers", "nrr", "emerging_products"],
        source_document={"kind": "transcript", "quarter": "Q4 2026"},
    )

    metrics = {row["metric"] for row in rows}
    assert {"arr", "net_new_arr", "large_customers", "nrr", "emerging_products"}.issubset(metrics)
    arr = next(row for row in rows if row["metric"] == "arr")
    assert arr["value"]["raw"] == "$1.9 billion"
    assert arr["period"] == "Q4 2026"
    assert arr["match_method"] == "exact"
    assert arr["match_score"] == 100.0


def test_kpi_evidence_extractor_uses_high_confidence_fuzzy_terms():
    text = (
        "Annual recurring rev reached $2.0 billion in Q4 FY2026. "
        "Large custmers reached 204. "
        "Free cashflow margin was 25%."
    )
    rows = extract_kpi_evidence(
        text,
        metrics=["arr", "large_customers", "fcf_margin"],
        source_document={"kind": "transcript", "quarter": "Q4 2026"},
    )

    by_metric = {row["metric"]: row for row in rows}
    assert by_metric["arr"]["value"]["raw"] == "$2.0 billion"
    assert by_metric["arr"]["match_method"].startswith("fuzzy:")
    assert by_metric["arr"]["match_score"] >= 90
    assert by_metric["large_customers"]["value"]["raw"] == "204"
    assert by_metric["large_customers"]["match_method"].startswith("fuzzy:")
    assert by_metric["fcf_margin"]["value"]["raw"] == "25%"


def test_kpi_evidence_extractor_does_not_match_low_confidence_noise():
    text = "The company discussed retention hiring and recurring meetings with 115 employees."
    rows = extract_kpi_evidence(text, metrics=["nrr", "arr"])

    assert rows == []


def test_kpi_evidence_extractor_preserves_financial_abbreviations():
    text = (
        "U.S. enterprise customers expanded vs. last year as we ended FY 2026 "
        "with $1.9 billion in ARR, growing 30% year over year."
    )
    rows = extract_kpi_evidence(
        text,
        metrics=["arr"],
        source_document={"kind": "transcript", "quarter": "Q4 2026"},
    )

    assert len(rows) == 1
    assert rows[0]["value"]["raw"] == "$1.9 billion"
    assert rows[0]["evidence"].startswith("U.S. enterprise customers expanded vs. last year")


def test_valuation_multiples_calculates_sales_multiples(monkeypatch):
    monkeypatch.setattr(
        "finance_cli.services.valuation.fetch_realtime_quote",
        lambda symbol: {
            "symbol": symbol,
            "price": 30.0,
            "market_cap": 18_000_000_000,
            "enterprise_value": 17_000_000_000,
            "currency": "USD",
        },
    )
    monkeypatch.setattr(
        "finance_cli.services.valuation.fetch_financial_statement",
        lambda *_args, **_kwargs: {
            "rows": [{"field": "Total Revenue", "2026-01-31": 1_800_000_000}],
        },
    )

    data = valuation_multiples("IOT")

    assert data["multiples"]["price_to_sales"] == 10.0
    assert data["multiples"]["ev_to_sales"] == 17_000_000_000 / 1_800_000_000


def test_valuation_scenario_calculates_implied_prices(monkeypatch):
    monkeypatch.setattr(
        "finance_cli.services.valuation.fetch_realtime_quote",
        lambda _symbol: {
            "price": 30.0,
            "market_cap": 18_000_000_000,
            "shares_outstanding": 600_000_000,
            "currency": "USD",
        },
    )

    data = valuation_scenario(
        "IOT",
        revenue=2_000_000_000,
        bear_multiple=6,
        base_multiple=9,
        bull_multiple=12,
    )

    base = next(row for row in data["cases"] if row["case"] == "base")
    assert base["implied_market_cap"] == 18_000_000_000
    assert base["implied_price"] == 30.0
    assert base["upside_pct"] == 0.0
    assert data["shares_source"]["source"] == "yfinance.sharesOutstanding"


def test_valuation_scenario_rejects_zero_user_shares(monkeypatch):
    monkeypatch.setattr(
        "finance_cli.services.valuation.fetch_realtime_quote",
        lambda _symbol: {"price": 30.0, "market_cap": 18_000_000_000, "currency": "USD"},
    )

    try:
        valuation_scenario(
            "IOT",
            revenue="2.2B",
            bear_multiple=6,
            base_multiple=9,
            bull_multiple=12,
            shares=0,
        )
    except ValueError as exc:
        assert "shares must be greater than 0" in str(exc)
    else:
        raise AssertionError("expected ValueError for zero shares")


def test_valuation_math_primitives_are_deterministic():
    npv = valuation_npv(cashflows=["-100M", "60M", "60M"], discount_rate="10%")
    assert round(npv["npv"], 2) == 4_132_231.40

    irr = valuation_irr(cashflows=["-100M", "60M", "60M"])
    assert round(irr["irr"], 6) == round(0.1306623862918075, 6)

    wacc = valuation_wacc(
        equity_value="10B",
        debt_value="2B",
        cost_of_equity="10%",
        cost_of_debt="5%",
        tax_rate="21%",
    )
    assert round(wacc["wacc"], 6) == round((10 / 12) * 0.10 + (2 / 12) * 0.05 * (1 - 0.21), 6)

    dcf = valuation_dcf(cashflows=["100M", "120M"], discount_rate="10%", terminal_growth="3%")
    terminal_value = 120_000_000 * 1.03 / (0.10 - 0.03)
    expected = 100_000_000 / 1.1 + 120_000_000 / (1.1 ** 2) + terminal_value / (1.1 ** 2)
    assert round(dcf["enterprise_value"], 2) == round(expected, 2)


def test_formula_financeqa_primitives_are_deterministic():
    days = formula_days(current=2721, prior=2285, denominator=254453)
    assert round(days["days"], 2) == 3.59

    operating_cash = formula_operating_cash(revenue=254453, cash_like_assets=11144, percent_revenue="2%")
    assert round(operating_cash["operating_cash"], 2) == 5089.06

    lease_equivalent = formula_lease_equivalent(base_liability=2554, variable_cost=163, operating_cost=284)
    assert round(lease_equivalent["lease_equivalent"], 2) == 1465.85

    pretax_wacc = formula_wacc(
        equity_value=100,
        debt_value=25,
        cost_of_equity="10%",
        cost_of_debt="6%",
        tax_rate="24%",
        debt_tax="pretax",
    )
    after_tax_wacc = formula_wacc(
        equity_value=100,
        debt_value=25,
        cost_of_equity="10%",
        cost_of_debt="6%",
        tax_rate="24%",
        debt_tax="after_tax",
    )
    assert pretax_wacc["wacc"] > after_tax_wacc["wacc"]

    cagr = formula_cagr(start=100, end=150, periods=3)
    assert round(cagr["cagr_pct"], 2) == 14.47

    net_debt = formula_net_debt(debt=11415, cash=11144, operating_cash=5089)
    assert net_debt["net_debt"] == 5360

    operating_assets = formula_operating_current_assets(
        current_assets=34246,
        cash_like_assets=11144,
        operating_cash=5089,
    )
    assert operating_assets["operating_current_assets"] == 28191

    operating_liabilities = formula_operating_current_liabilities(
        current_liabilities=35464,
        interest_bearing_current_debt=103,
    )
    assert operating_liabilities["operating_current_liabilities"] == 35361

    working_capital = formula_working_capital(
        operating_current_assets=28191,
        operating_current_liabilities=35361,
    )
    assert working_capital["working_capital"] == -7170


def test_estimates_compare_is_local_and_deterministic():
    result = compare_estimates(
        "IOT",
        fiscal_year="2027",
        revenue="2.2B",
        consensus_revenue="2.0B",
        eps="0.50",
        consensus_eps="0.40",
    )

    assert result["symbol"] == "IOT"
    assert result["count"] == 2
    assert result["comparisons"][0]["metric"] == "revenue"
    assert result["comparisons"][0]["absolute_gap"] == 200_000_000
    assert result["comparisons"][1]["valuation_input_hint"] == "above_consensus"


def test_fmp_consensus_provider_normalizes_rows():
    class Provider:
        def analyst_estimates(self, symbol, **kwargs):
            assert symbol == "IOT"
            assert kwargs["period"] == "annual"
            return [
                {
                    "symbol": "IOT",
                    "date": "2027-01-31",
                    "period": "annual",
                    "revenue": {"avg": 2_000_000_000, "low": 1_900_000_000, "high": 2_100_000_000},
                    "eps": {"avg": 0.4, "low": 0.3, "high": 0.5},
                    "provider": "fmp",
                }
            ]

    result = consensus_estimates("iot", provider=Provider())

    assert result["symbol"] == "IOT"
    assert result["provider"] == "fmp"
    assert result["estimates"][0]["revenue"]["avg"] == 2_000_000_000


def test_fmp_provider_maps_analyst_estimate_payload(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return [
                {
                    "symbol": "IOT",
                    "date": "2027-01-31",
                    "revenueAvg": 2_000_000_000,
                    "revenueLow": 1_900_000_000,
                    "revenueHigh": 2_100_000_000,
                    "epsAvg": 0.4,
                    "numAnalystsRevenue": 20,
                }
            ]

    monkeypatch.setattr("finance_cli.providers.fmp.httpx.get", lambda *args, **kwargs: Response())

    rows = FMPProvider(api_key="test").analyst_estimates("iot", limit=1)

    assert rows[0]["symbol"] == "IOT"
    assert rows[0]["revenue"] == {"avg": 2_000_000_000, "low": 1_900_000_000, "high": 2_100_000_000}
    assert rows[0]["eps"]["avg"] == 0.4
    assert rows[0]["analyst_count"]["revenue"] == 20


def test_cli_formula_command_returns_json(capsys):
    code = main(["formula.operating_cash", "revenue=254453", "cash_like_assets=11144", "percent_revenue=2%"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert round(payload["data"]["operating_cash"], 2) == 5089.06

    code = main(["formula.cagr", "start=100", "end=150", "periods=3"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert round(payload["data"]["cagr_pct"], 2) == 14.47


def test_cli_formula_missing_arg_returns_usage(capsys):
    code = main(["formula.ebitda"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 1
    assert payload["ok"] is False
    assert "usage: formula.ebitda" in payload["error"]
    assert "ebit is required" in payload["error"]


def test_cli_estimates_compare_returns_json(capsys):
    code = main([
        "estimates.compare",
        "IOT",
        "revenue=2.2B",
        "consensus_revenue=2.0B",
        "eps=0.50",
        "consensus_eps=0.40",
        "fiscal_year=2027",
    ])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["count"] == 2
    assert payload["data"]["comparisons"][0]["percent_gap_pct"] == 10.0


def test_cli_estimates_consensus_missing_key_is_fast_error(capsys, monkeypatch):
    monkeypatch.delenv("FMP_API_KEY", raising=False)

    code = main(["estimates.consensus", "IOT", "limit=1"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 1
    assert payload["ok"] is False
    assert "FMP_API_KEY" in payload["error"]


def test_research_plan_returns_supported_fundamental_checklist():
    plan = research_plan("iot", style="fundamental")

    assert plan["symbol"] == "IOT"
    assert plan["plan_type"] == "deterministic_cli_checklist"
    assert any(step["id"] == "filings" for step in plan["steps"])
    assert any("finance valuation.multiples IOT" in step["commands"] for step in plan["steps"] if step["id"] == "valuation")


def test_backtest_payload_builder_matches_migrated_contract():
    payload = build_factor_backtest_payload(
        factor_name="rsi_14",
        symbols=["aapl", "MSFT"],
        start_date="2024-01-01",
        end_date="2024-12-31",
        initial_cash=250000,
    )

    assert payload["factor_name"] == "rsi_14"
    assert payload["symbols"] == ["AAPL", "MSFT"]
    assert payload["direction"] == "long_short"
    assert payload["initial_cash"] == 250000.0


def test_backtesting_primitives_preview_factor_rebalance():
    weights = build_quantile_weights(
        {"AAPL": 1.0, "MSFT": 0.5, "NVDA": 2.0, "TSLA": -1.0},
        top_pct=0.25,
        bottom_pct=0.25,
    )

    assert weights["NVDA"] == 0.5
    assert weights["TSLA"] == -0.5
    assert sum(weights.values()) == 0.0

    preview = preview_factor_rebalance(
        factor_name="demo_factor",
        scores={"AAPL": 1.0, "MSFT": 0.5, "NVDA": 2.0, "TSLA": -1.0},
        timestamp="2026-01-01",
        top_pct=0.25,
        bottom_pct=0.25,
    )

    assert preview["run_type"] == "factor_rebalance_preview"
    assert preview["gross_exposure"] == 1.0
    assert preview["rebalance_snapshot"]["long"][0]["symbol"] == "NVDA"


def _fake_backtest_ohlcv(symbols, **kwargs):
    from datetime import date, timedelta

    class Attempt:
        provider = "test"

    start_date = date.fromisoformat(kwargs["start_date"]) if kwargs.get("start_date") else None
    end_date = date.fromisoformat(kwargs["end_date"]) if kwargs.get("end_date") else None
    payload = {}
    for offset, symbol in enumerate(symbols):
        rows = []
        for index in range(180):
            day = date(2024, 1, 1) + timedelta(days=index)
            if start_date and day < start_date:
                continue
            if end_date and day > end_date:
                continue
            close = 100 + offset * 10 + index * (0.25 + offset * 0.05)
            rows.append({
                "symbol": symbol,
                "date": day.isoformat(),
                "open": close - 0.2,
                "high": close + 0.5,
                "low": close - 0.5,
                "close": close,
                "volume": 1000 + index,
                "source": "test",
            })
        payload[symbol] = {"symbol": symbol, "rows": rows, "count": len(rows), "source": Attempt.provider}
    return {"timeframe": "1d", "symbols": payload, "count": sum(entry["count"] for entry in payload.values())}


def _flat_backtest_ohlcv(symbols, **_kwargs):
    from datetime import date, timedelta

    payload = {}
    for symbol in symbols:
        rows = []
        for index in range(40):
            day = date(2024, 1, 1) + timedelta(days=index)
            rows.append({
                "symbol": symbol,
                "date": day.isoformat(),
                "open": 100,
                "high": 100,
                "low": 100,
                "close": 100,
                "volume": 1000,
                "source": "test",
            })
        payload[symbol] = {"symbol": symbol, "rows": rows, "count": len(rows), "source": "test"}
    return {"timeframe": "1d", "symbols": payload, "count": sum(entry["count"] for entry in payload.values())}


def test_vectorbt_backtest_lists_and_runs_builtin_strategy(monkeypatch):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _fake_backtest_ohlcv)

    strategies = available_backtest_strategies()
    assert strategies["engine"] == "vectorbt"
    assert any(strategy["name"] == "buy_hold" for strategy in strategies["strategies"])

    result = run_backtest(
        strategy="buy_hold",
        symbols=["AAPL", "MSFT"],
        start_date="2024-01-01",
        end_date="2024-06-30",
        initial_cash=10_000,
        fees=0,
    )

    assert result["engine"] == "vectorbt"
    assert result["config"]["strategy"] == "buy_hold"
    assert result["data"]["symbols"] == ["AAPL", "MSFT"]
    assert result["metrics"]["end_value"] > 10_000
    assert result["target_weights"][0]["weights"] == {"AAPL": 0.5, "MSFT": 0.5}


def test_vectorbt_backtest_result_is_strict_json_with_nonfinite_metrics(monkeypatch):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _flat_backtest_ohlcv)

    result = run_backtest(
        strategy="buy_hold",
        symbols=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-02-15",
        fees=0,
    )

    assert result["metrics"]["sharpe_ratio"] is None
    assert "total_return_decimal" in result["metrics"]
    json.dumps(result, allow_nan=False)


def test_vectorbt_backtest_uses_requested_window_without_strategy_warmup(monkeypatch):
    calls = []

    def fake_fetch(symbols, **kwargs):
        calls.append(kwargs)
        return _fake_backtest_ohlcv(symbols, **kwargs)

    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", fake_fetch)

    result = run_backtest(
        strategy="sma_cross",
        symbols=["AAPL"],
        start_date="2024-04-01",
        end_date="2024-06-30",
        params={"fast": 5, "slow": 60},
        fees=0,
    )

    assert calls[0]["start_date"] == "2024-04-01"
    assert "warmup_bars" not in result["config"]
    assert "warmup_start_date" not in result["config"]
    assert result["data"]["start"].startswith("2024-04-01")


def test_vectorbt_backtest_tunes_sma_cross(monkeypatch):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _fake_backtest_ohlcv)

    result = tune_backtest(
        strategy="sma_cross",
        symbols=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-06-30",
        grid={"fast": [5, 10], "slow": [30, 60]},
        metric="total_return_pct",
        fees=0,
    )

    assert result["engine"] == "vectorbt"
    assert result["runs"] == 4
    assert result["best"]["params"]["fast"] in {5, 10}
    assert result["results"][0]["metrics"]["total_return_pct"] is not None


def test_vectorbt_backtest_loads_custom_strategy_file(monkeypatch, tmp_path):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _fake_backtest_ohlcv)
    strategy_file = tmp_path / "rule.py"
    strategy_file.write_text(
        "def generate_weights(close, params, ohlcv=None):\n"
        "    weights = close.copy() * 0.0\n"
        "    weights.iloc[0, :] = 1.0 / len(close.columns)\n"
        "    return weights\n"
    )

    result = run_backtest(
        strategy="custom",
        symbols=["AAPL", "MSFT"],
        start_date="2024-01-01",
        end_date="2024-06-30",
        strategy_file=strategy_file.as_posix(),
        plot_path=(tmp_path / "plot.html").as_posix(),
        fees=0,
    )

    assert result["config"]["strategy"] == "custom"
    assert result["config"]["strategy_file"] == strategy_file.as_posix()
    assert Path(result["plot_path"]).exists()
    assert result["target_weights"][0]["weights"] == {"AAPL": 0.5, "MSFT": 0.5}


def test_vectorbt_backtest_loads_custom_signal_file(monkeypatch, tmp_path):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _fake_backtest_ohlcv)
    strategy_file = tmp_path / "signals.py"
    strategy_file.write_text(
        "def generate_signals(close, params, ohlcv=None):\n"
        "    entries = close.copy() == close.copy()\n"
        "    exits = close.copy() != close.copy()\n"
        "    entries.iloc[1:, :] = False\n"
        "    return entries, exits\n"
    )

    result = run_backtest(
        strategy="custom",
        symbols=["AAPL", "MSFT"],
        start_date="2024-01-01",
        end_date="2024-06-30",
        strategy_file=strategy_file.as_posix(),
        fees=0,
    )

    assert result["config"]["strategy"] == "custom"
    assert result["target_weights"][0]["weights"] == {"AAPL": 0.5, "MSFT": 0.5}


def test_vectorbt_backtest_rejects_unknown_and_invalid_strategies(monkeypatch, tmp_path):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _fake_backtest_ohlcv)

    try:
        run_backtest(
            strategy="not_real",
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-06-30",
        )
    except ValueError as exc:
        assert "unknown strategy" in str(exc)
    else:
        raise AssertionError("unknown strategy should fail")

    try:
        run_backtest(
            strategy="sma_cross",
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-06-30",
            params={"fast": 50, "slow": 20},
        )
    except ValueError as exc:
        assert "fast must be below slow" in str(exc)
    else:
        raise AssertionError("invalid sma params should fail")

    missing = tmp_path / "missing.py"
    try:
        run_backtest(
            strategy="custom",
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-06-30",
            strategy_file=missing.as_posix(),
        )
    except ValueError as exc:
        assert "strategy_file not found" in str(exc)
    else:
        raise AssertionError("missing custom strategy should fail")


def test_vectorbt_backtest_rejects_oversized_tune_grid(monkeypatch):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _fake_backtest_ohlcv)

    try:
        tune_backtest(
            strategy="sma_cross",
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-06-30",
            grid={"fast": [5, 10, 15], "slow": [20, 30]},
            max_runs=5,
        )
    except ValueError as exc:
        assert "above max_runs=5" in str(exc)
    else:
        raise AssertionError("oversized grid should fail")


def test_shape_backtest_result_normalizes_events():
    result = shape_backtest_result(
        run_type="unit",
        config={"x": 1},
        metrics={"total_return": 0.1},
        events=[{"event_time": "2026-01-01T00:00:00Z", "event_type": "trade", "payload": {"a": 1}}],
    )

    assert result["events"][0]["event_time"] == "2026-01-01T00:00:00+00:00"
    assert result["total_return"] == 0.1


class _FailingProvider:
    name = "failing"

    def ohlcv(self, *_args, **_kwargs):
        raise RuntimeError("boom")


class _WorkingProvider:
    name = "working"

    def ohlcv(self, symbol, **_kwargs):
        return [
            {
                "symbol": symbol,
                "date": "2026-01-01",
                "open": 1,
                "high": 2,
                "low": 1,
                "close": 2,
                "volume": 100,
                "adjusted_close": 2,
                "source": "working",
            }
        ]


def test_market_data_service_uses_sync_provider_fallback():
    service = HistoricalMarketDataService(providers=[_FailingProvider(), _WorkingProvider()])
    result = fetch_ohlcv("AAPL", service=service, include_attempts=True)

    assert result["source"] == "working"
    assert result["count"] == 1
    assert result["attempts"][0]["provider"] == "failing"
    assert result["attempts"][0]["success"] is False
    assert result["attempts"][1]["provider"] == "working"
    assert result["attempts"][1]["success"] is True


def test_alpaca_provider_normalizes_bars(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "bars": {
                    "AAPL": [
                        {
                            "t": "2026-01-02T14:30:00Z",
                            "o": 10,
                            "h": 11,
                            "l": 9,
                            "c": 10.5,
                            "v": 1234,
                        }
                    ]
                }
            }

    calls = []

    def fake_get(url, params, headers, timeout, **kwargs):
        calls.append({"url": url, "params": params, "headers": headers, "timeout": timeout, **kwargs})
        return Response()

    monkeypatch.setattr("finance_cli.providers.alpaca.httpx.get", fake_get)
    provider = AlpacaMarketDataProvider(api_key="key", api_secret="secret", base_url="https://example.test")
    rows = provider.ohlcv("AAPL", timeframe="5m", start_date="2026-01-01", end_date="2026-01-02", limit=10)

    assert calls[0]["url"] == "https://example.test/v2/stocks/bars"
    assert calls[0]["params"]["timeframe"] == "5Min"
    assert calls[0]["params"]["feed"] == "iex"
    assert calls[0]["params"]["sort"] == "desc"
    assert rows[0]["symbol"] == "AAPL"
    assert rows[0]["close"] == 10.5
    assert rows[0]["source"] == "alpaca"


def test_yahoo_provider_suppresses_noisy_stdout(monkeypatch, capsys):
    class FakeTicker:
        def __init__(self, symbol):
            print(f"constructing {symbol}")

        @property
        def info(self):
            print("loading info")
            return {
                "longName": "Samsara Inc.",
                "sector": "Technology",
                "industry": "Software - Infrastructure",
                "regularMarketPrice": 29.96,
                "marketCap": 17398259712,
                "currency": "USD",
            }

    class FakeYFinance:
        Ticker = FakeTicker

    monkeypatch.setattr(
        "finance_cli.providers.yahoo.require_dependency",
        lambda *_args, **_kwargs: FakeYFinance,
    )

    quote = YahooFinanceProvider().quote("IOT")
    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""
    assert quote["company_name"] == "Samsara Inc."


def test_gdelt_news_provider_uses_doc_api_without_lang_query(monkeypatch):
    class Response:
        status_code = 200
        text = '{"articles":[]}'

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "articles": [
                    {"title": "NVIDIA news", "language": "English"},
                    {"title": "Other language", "language": "Spanish"},
                ]
            }

    calls = []

    def fake_get(url, params, headers, timeout, **kwargs):
        calls.append({"url": url, "params": params, "headers": headers, "timeout": timeout, **kwargs})
        return Response()

    monkeypatch.setattr("finance_cli.providers.gdelt.httpx.get", fake_get)
    rows = GdeltNewsProvider(min_interval_seconds=0, retry_count=0).symbol_news("NVDA", max_records=2)

    assert calls[0]["url"] == "https://api.gdeltproject.org/api/v2/doc/doc"
    assert calls[0]["params"]["query"] == '"NVDA" stock sourcelang:english'
    assert calls[0]["params"]["mode"] == "artlist"
    assert calls[0]["params"]["format"] == "json"
    assert calls[0]["params"]["timespan"] == "1d"
    assert calls[0]["trust_env"] is False
    assert "lang:english" not in calls[0]["params"]["query"].split()
    assert "sourcelang:english" in calls[0]["params"]["query"]
    assert len(rows) == 1
    assert rows[0]["title"] == "NVIDIA news"


def test_gdelt_news_provider_retries_rate_limit_text(monkeypatch):
    class RateLimitedResponse:
        status_code = 200
        text = "Rate limit exceeded. Please slow down."

        def raise_for_status(self):
            return None

        def json(self):
            return {}

    class SuccessResponse:
        status_code = 200
        text = '{"articles":[{"title":"NVIDIA rebound","language":"English"}]}'

        def raise_for_status(self):
            return None

        def json(self):
            return {"articles": [{"title": "NVIDIA rebound", "language": "English"}]}

    calls = []

    def fake_get(url, params, headers, timeout, **kwargs):
        calls.append({"url": url, "params": params, "headers": headers, "timeout": timeout, **kwargs})
        return RateLimitedResponse() if len(calls) == 1 else SuccessResponse()

    monkeypatch.setattr("finance_cli.providers.gdelt.httpx.get", fake_get)
    monkeypatch.setattr("finance_cli.providers.gdelt.time.sleep", lambda _: None)

    rows = GdeltNewsProvider(min_interval_seconds=0, retry_count=1, retry_delay_seconds=0).search("NVIDIA")

    assert len(calls) == 2
    assert rows == [{"title": "NVIDIA rebound", "language": "English"}]


def test_gdelt_doc_timeline_uses_supported_doc_mode(monkeypatch):
    class Response:
        status_code = 200
        text = '{"timeline":[{"date":"20260425","value":2}]}'

        def raise_for_status(self):
            return None

        def json(self):
            return {"timeline": [{"date": "20260425", "value": 2}]}

    calls = []

    def fake_get(url, params, headers, timeout, **kwargs):
        calls.append({"url": url, "params": params, "headers": headers, "timeout": timeout, **kwargs})
        return Response()

    monkeypatch.setattr("finance_cli.providers.gdelt.httpx.get", fake_get)

    payload = GdeltNewsProvider(min_interval_seconds=0, retry_count=0).timeline(
        "NVIDIA",
        mode="timeline_vol_raw",
        timespan="2d",
        timeline_smooth=3,
    )

    assert calls[0]["url"] == "https://api.gdeltproject.org/api/v2/doc/doc"
    assert calls[0]["params"]["mode"] == "timelinevolraw"
    assert calls[0]["params"]["query"] == "NVIDIA sourcelang:english"
    assert calls[0]["params"]["timespan"] == "2d"
    assert calls[0]["params"]["timelinesmooth"] == 3
    assert payload["timeline"][0]["value"] == 2


def test_gdelt_context_uses_context_endpoint_without_source_language(monkeypatch):
    class Response:
        status_code = 200
        text = '{"articles":[{"title":"NVIDIA", "context":"AI chip sentence"}]}'

        def raise_for_status(self):
            return None

        def json(self):
            return {"articles": [{"title": "NVIDIA", "context": "AI chip sentence"}]}

    calls = []

    def fake_get(url, params, headers, timeout, **kwargs):
        calls.append({"url": url, "params": params, "headers": headers, "timeout": timeout, **kwargs})
        return Response()

    monkeypatch.setattr("finance_cli.providers.gdelt.httpx.get", fake_get)

    payload = GdeltNewsProvider(min_interval_seconds=0, retry_count=0).context(
        "NVIDIA export controls",
        max_records=5,
        timespan="24h",
        is_quote=True,
    )

    assert calls[0]["url"] == "https://api.gdeltproject.org/api/v2/context/context"
    assert calls[0]["params"]["mode"] == "artlist"
    assert calls[0]["params"]["format"] == "json"
    assert calls[0]["params"]["query"] == "NVIDIA export controls"
    assert calls[0]["params"]["isquote"] == 1
    assert payload["articles"][0]["context"] == "AI chip sentence"


def test_gdelt_geo_uses_gkg_geojson_endpoint(monkeypatch):
    class Response:
        status_code = 200
        text = '{"type":"FeatureCollection","features":[{"type":"Feature"}]}'

        def raise_for_status(self):
            return None

        def json(self):
            return {"type": "FeatureCollection", "features": [{"type": "Feature"}]}

    calls = []

    def fake_get(url, params, headers, timeout, **kwargs):
        calls.append({"url": url, "params": params, "headers": headers, "timeout": timeout, **kwargs})
        return Response()

    monkeypatch.setattr("finance_cli.providers.gdelt.httpx.get", fake_get)

    payload = GdeltNewsProvider(min_interval_seconds=0, retry_count=0).geo(
        "NVIDIA",
        mode="pointdata",
        max_points=10,
    )

    assert calls[0]["url"] == "https://api.gdeltproject.org/api/v1/gkg_geojson"
    assert calls[0]["params"]["QUERY"] == "NVIDIA"
    assert calls[0]["params"]["TIMESPAN"] == 1440
    assert calls[0]["params"]["OUTPUTTYPE"] == 1
    assert calls[0]["params"]["MAXROWS"] == 10
    assert payload["type"] == "FeatureCollection"


def test_gdelt_geo_timespan_accepts_human_friendly_values():
    assert GdeltNewsProvider._timespan_to_minutes("90min") == 90
    assert GdeltNewsProvider._timespan_to_minutes("2 hours") == 120
    assert GdeltNewsProvider._timespan_to_minutes("30D") == 1440


def test_news_geo_returns_empty_geojson_without_enrichment():
    class Provider:
        SECTOR_QUERY_EXPANSIONS = {}

        def geo(self, query, mode, timespan, max_points):
            return {"type": "FeatureCollection", "features": []}

    result = news_geo(symbol="NVDA", max_points=3, provider=Provider())

    assert result["count"] == 0
    assert result["payload"] == {"type": "FeatureCollection", "features": []}
    assert "enrichment" not in result


def test_cli_main_builds_factor_backtest_payload(capsys):
    code = main([
        "backtest.factor.payload",
        "rsi_14",
        "AAPL,MSFT",
        "2024-01-01",
        "2024-12-31",
        "top_pct=0.1",
    ])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["symbols"] == ["AAPL", "MSFT"]
    assert payload["data"]["top_pct"] == 0.1


def test_cli_main_builds_factor_weights_preview(capsys):
    code = main([
        "backtest.factor.weights",
        "rsi_14",
        'scores={"AAPL":1,"MSFT":0.5,"NVDA":2,"TSLA":-1}',
        "top_pct=0.25",
        "bottom_pct=0.25",
    ])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["weights"]["NVDA"] == 0.5


def test_cli_main_runs_vectorbt_backtest(monkeypatch, capsys):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _fake_backtest_ohlcv)

    code = main([
        "backtest.run",
        "buy_hold",
        "AAPL,MSFT",
        "2024-01-01",
        "2024-06-30",
        "fees=0",
    ])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["engine"] == "vectorbt"
    assert payload["data"]["metrics"]["end_value"] > 100000


def test_cli_main_tunes_vectorbt_backtest(monkeypatch, capsys):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _fake_backtest_ohlcv)

    code = main([
        "backtest.tune",
        "sma_cross",
        "AAPL",
        "2024-01-01",
        "2024-06-30",
        'grid={"fast":[5,10],"slow":[30]}',
        "metric=total_return_pct",
        "fees=0",
    ])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["runs"] == 2
    assert payload["data"]["best"]["params"]["slow"] == 30


def test_cli_main_reports_vectorbt_backtest_errors(monkeypatch, capsys):
    monkeypatch.setattr("finance_cli.services.market_data.fetch_ohlcv_batch", _fake_backtest_ohlcv)

    code = main([
        "backtest.run",
        "sma_cross",
        "AAPL",
        "2024-01-01",
        "2024-06-30",
        "fast=60",
        "slow=20",
    ])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 1
    assert payload["ok"] is False
    assert "fast must be below slow" in payload["error"]

    code = main([
        "backtest.tune",
        "sma_cross",
        "AAPL",
        "2024-01-01",
        "2024-06-30",
        'grid={"fast":[5,10,15],"slow":[20,30]}',
        "max_runs=5",
    ])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 1
    assert payload["ok"] is False
    assert "above max_runs=5" in payload["error"]


from finance_cli.providers.sec_edgar.exhibits import (
    _score_exhibit_candidate,
    _classify_exhibit_kind,
)


def test_score_exhibit_candidate_returns_high_for_presentation_description():
    exhibit = {
        "type": "EX-99.1",
        "document": "iot20260305_ex99-1.htm",
        "description": "INVESTOR DAY PRESENTATION",
        "size": "500000",
    }
    score = _score_exhibit_candidate(exhibit)
    assert score is not None
    assert score["confidence"] == "high"
    assert "investor day" in score["reason"].lower()


def test_score_exhibit_candidate_returns_medium_for_filename_keyword():
    exhibit = {
        "type": "EX-99.1",
        "document": "iot-slides-2026.htm",
        "description": "EXHIBIT 99.1",
        "size": "300000",
    }
    score = _score_exhibit_candidate(exhibit)
    assert score is not None
    assert score["confidence"] == "medium"


def test_score_exhibit_candidate_returns_none_for_earnings_release():
    exhibit = {
        "type": "EX-99.1",
        "document": "iot20260305_pressrelease.htm",
        "description": "PRESS RELEASE",
        "size": "50000",
    }
    score = _score_exhibit_candidate(exhibit)
    assert score is None


def test_score_exhibit_candidate_downgrades_conflicting_press_release_description():
    exhibit = {
        "type": "EX-99.1",
        "document": "iot-q4-results-and-investorday.htm",
        "description": "PRESS RELEASE AND INVESTOR DAY PRESENTATION",
        "size": "900000",
    }
    score = _score_exhibit_candidate(exhibit)
    assert score is not None
    assert score["confidence"] == "medium"
    assert score["warnings"]


def test_score_exhibit_candidate_excludes_investor_day_press_release_filename():
    exhibit = {
        "type": "EX-99.1",
        "document": "ex991-investordaypressrele.htm",
        "description": "EX-99.1",
        "size": "120000",
    }
    score = _score_exhibit_candidate(exhibit)
    assert score is None


def test_classify_exhibit_kind_maps_investor_day():
    assert _classify_exhibit_kind("Investor Day Presentation", "iot-investorday.htm") == "investor_day"
    assert _classify_exhibit_kind("EX-99.2", "investorday2025.htm") == "investor_day"
    assert _classify_exhibit_kind("Analyst Day Slides", "slides.htm") == "investor_day"
    assert _classify_exhibit_kind("Q4 2026 Earnings Results Presentation", "ex99.htm") == "earnings_presentation"
    assert _classify_exhibit_kind("IR Deck 2026", "deck.htm") == "ir_presentation"
    assert _classify_exhibit_kind("EXHIBIT 99.1", "ex99-1.htm") == "exhibit_99"


def test_sec_edgar_provider_builds_exhibit_candidate_url(monkeypatch):
    from bs4 import BeautifulSoup

    index_html = """
    <html><body>
    <table class="tableFile">
      <tr><th>Seq</th><th>Description</th><th>Document</th><th>Type</th><th>Size</th></tr>
      <tr>
        <td>1</td><td>FORM 8-K</td>
        <td><a href="/Archives/edgar/data/1648802/000164880226000011/iot_8k.htm">iot_8k.htm</a></td>
        <td>8-K</td><td>10000</td>
      </tr>
      <tr>
        <td>2</td><td>INVESTOR DAY PRESENTATION</td>
        <td><a href="/Archives/edgar/data/1648802/000164880226000011/iot_investorday.htm">iot_investorday.htm</a></td>
        <td>EX-99.1</td><td>800000</td>
      </tr>
    </table>
    </body></html>
    """

    class FakeIndexResponse:
        text = index_html
        status_code = 200

        def raise_for_status(self):
            return None

    def fake_get_json(self, url):
        return {
            "filings": {
                "recent": {
                    "form": ["8-K"],
                    "filingDate": ["2026-03-05"],
                    "reportDate": ["2026-03-05"],
                    "accessionNumber": ["0001648802-26-000011"],
                    "primaryDocument": ["iot_8k.htm"],
                    "primaryDocDescription": ["FORM 8-K"],
                    "items": ["7.01"],
                }
            }
        }

    def fake_httpx_get(url, headers, timeout):
        return FakeIndexResponse()

    def fake_get_company(self, symbol):
        return {"cik_str": "1648802", "title": "Samsara Inc."}

    monkeypatch.setattr("finance_cli.providers.sec_edgar.SecEdgarProvider._get_json", fake_get_json)
    monkeypatch.setattr("finance_cli.providers.sec_edgar.SecEdgarProvider.get_company", fake_get_company)
    monkeypatch.setattr("finance_cli.providers.sec_edgar.httpx.get", fake_httpx_get)

    candidates = SecEdgarProvider().list_exhibit_candidates("IOT", limit=5)

    assert len(candidates) == 1
    assert candidates[0]["kind"] == "investor_day"
    assert candidates[0]["confidence"] == "high"
    assert candidates[0]["filing_accession"] == "0001648802-26-000011"
    assert "iot_investorday.htm" in candidates[0]["url"]
    assert candidates[0]["source"] == "sec_edgar"
    assert candidates[0]["filing_url"].endswith("/iot_8k.htm")
    assert candidates[0]["document"] == "iot_investorday.htm"
    assert candidates[0]["warnings"] == []


def test_read_exhibit_text_returns_warning_when_pdf_fetch_fails(monkeypatch):
    def fake_get(*args, **kwargs):
        raise RuntimeError("network error")

    monkeypatch.setattr("finance_cli.providers.sec_edgar.httpx.get", fake_get)

    result = SecEdgarProvider().read_exhibit_text("https://sec.example/deck.pdf")
    assert result["format"] == "pdf"
    assert result["text"] is None
    assert result["warnings"]
    assert result["pages"] == []
    assert result["truncated"] is False


def test_read_exhibit_text_extracts_pdf_pages(monkeypatch):
    class Response:
        content = b"%PDF fake"

        def raise_for_status(self):
            return None

    class Page:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakePdfReader:
        def __init__(self, _stream):
            self.pages = [Page("Slide 1 revenue growth"), Page("Slide 2 margin expansion")]

    class FakePypdf:
        PdfReader = FakePdfReader

    monkeypatch.setattr("finance_cli.providers.sec_edgar.httpx.get", lambda *args, **kwargs: Response())
    monkeypatch.setattr("finance_cli.providers.sec_edgar.require_dependency", lambda *args, **kwargs: FakePypdf)

    result = SecEdgarProvider().read_exhibit_text("https://sec.example/deck.pdf", max_chars=1000)

    assert result["format"] == "pdf"
    assert result["text"].startswith("Slide 1")
    assert len(result["pages"]) == 2
    assert result["warnings"]


def test_read_exhibit_text_warns_when_html_text_is_too_short(monkeypatch):
    class Response:
        text = "<html><body><document>EX-99.2</document></body></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr("finance_cli.providers.sec_edgar.httpx.get", lambda *args, **kwargs: Response())

    result = SecEdgarProvider().read_exhibit_text("https://sec.example/deck.htm")

    assert result["format"] == "html"
    assert result["pages"]
    assert result["warnings"]
    assert "very short" in result["warnings"][0]


def test_paddle_ocr_provider_shapes_markdown_pages(tmp_path):
    class FakePipeline:
        def predict(self, input):
            return [
                {"page_index": 0, "markdown": "# Slide 1\nRevenue growth", "blocks": [{"type": "title", "text": "Slide 1"}]},
                {"page_index": 1, "markdown": "# Slide 2\nMargin expansion"},
            ]

    path = tmp_path / "deck.pdf"
    path.write_bytes(b"fake pdf")

    result = PaddleOCRProvider(pipeline=FakePipeline()).read_document(str(path), max_chars=1000)

    assert result["engine"] == "paddleocr_pp_structure_v3"
    assert result["format"] == "pdf"
    assert result["pages"][0]["page"] == 1
    assert result["pages"][0]["blocks"][0]["type"] == "title"
    assert "Revenue growth" in result["markdown"]


def test_native_pdf_reconstructs_columns_left_to_right():
    blocks = [
        {"index": 2, "text": "right top", "bbox": [320, 10, 500, 20]},
        {"index": 1, "text": "left bottom", "bbox": [20, 50, 200, 60]},
        {"index": 0, "text": "left top", "bbox": [20, 10, 200, 20]},
    ]

    ordered = reconstruct_reading_order(blocks)

    assert [block["text"] for block in ordered] == ["left top", "left bottom", "right top"]


def test_native_pdf_provider_extracts_positioned_blocks(monkeypatch, tmp_path):
    class Page:
        def get_text(self, mode):
            assert mode == "blocks"
            return [
                (300, 10, 500, 20, "Right column", 1, 0),
                (20, 10, 200, 20, "Left column", 0, 0),
            ]

    class Document:
        def __len__(self):
            return 1

        def __getitem__(self, index):
            assert index == 0
            return Page()

    class Fitz:
        @staticmethod
        def open(path):
            return Document()

    path = tmp_path / "deck.pdf"
    path.write_bytes(b"%PDF")
    monkeypatch.setattr("finance_cli.providers.native_pdf.require_dependency", lambda *args, **kwargs: Fitz)

    result = NativePDFProvider().read_document(str(path), max_chars=1000)

    assert result["engine"] == "pymupdf"
    assert result["format"] == "pdf"
    assert result["pages"][0]["blocks"][0]["text"] == "Left column"
    assert "Left column" in result["text"]


def test_document_read_service_uses_injected_provider():
    class Provider:
        def read_document(self, source, max_chars, max_pages):
            return {"source": source, "max_chars": max_chars, "max_pages": max_pages, "pages": [], "warnings": []}

    result = read_document("deck.pdf", max_chars=500, max_pages=2, provider=Provider())

    assert result["source"] == "deck.pdf"
    assert result["max_chars"] == 500
    assert result["max_pages"] == 2


def test_document_scan_uses_rapidfuzz_topic_matching():
    class Provider:
        def read_document(self, source, max_chars, max_pages):
            return {
                "source": source,
                "engine": "test",
                "format": "pdf",
                "pages": [
                    {
                        "page": 12,
                        "text": "Risk Factors include customer concentration risk.",
                        "char_count": 51,
                        "blocks": [
                            {
                                "index": 0,
                                "text": "Risk Factors include customer concentration risk.",
                                "bbox": [0, 0, 100, 20],
                            }
                        ],
                    }
                ],
                "char_count": 51,
                "warnings": [],
            }

    result = scan_document("report.pdf", topics=["risk"], threshold=70, provider=Provider())

    assert result["count"] == 1
    assert result["matches"][0]["topic"] == "risk"
    assert result["matches"][0]["page"] == 12


def test_html_document_provider_returns_offset_blocks(tmp_path):
    path = tmp_path / "filing.htm"
    path.write_text(
        """
        <html><body>
          <ix:header>
            <ix:hidden>cost:FoodandSundriesMember 2023-09-04 2024-09-01</ix:hidden>
          </ix:header>
          <div style="display:none">Hidden XBRL metadata</div>
          <h1>Note 5-Leases</h1>
          <table>
            <tr><th>Metric</th><th>2024</th></tr>
            <tr><td>Operating lease costs</td><td>$284</td></tr>
          </table>
        </body></html>
        """,
        encoding="utf-8",
    )

    result = HTMLDocumentProvider().read_document(str(path), max_chars=0)

    assert result["format"] == "html"
    assert "Operating lease costs" in result["text"]
    assert "FoodandSundriesMember" not in result["text"]
    assert "Hidden XBRL metadata" not in result["text"]
    assert result["pages"][0]["blocks"][0]["start_char"] == 0
    assert result["pages"][0]["blocks"][0]["end_char"] > 0


def test_document_scan_html_provider_returns_offsets_and_window():
    text = (
        "Note 5-Leases\n"
        "The components of lease expense were as follows:\n"
        "Operating lease costs $284 $309 $297\n"
        "Variable lease costs $163 $160 $157\n"
    )

    class Provider:
        def read_document(self, source, max_chars, max_pages):
            return {
                "source": source,
                "engine": "test-html",
                "format": "html",
                "text": text,
                "pages": [
                    {
                        "page": 1,
                        "text": text,
                        "char_count": len(text),
                        "blocks": [
                            {
                                "index": 0,
                                "text": text,
                                "start_char": 0,
                                "end_char": len(text),
                                "bbox": None,
                            }
                        ],
                    }
                ],
                "char_count": len(text),
                "warnings": [],
            }

    result = scan_document(
        "filing.htm",
        topics=["Operating lease costs"],
        threshold=70,
        max_chars=0,
        window_chars=40,
        provider=Provider(),
    )

    match = result["matches"][0]
    assert match["match_id"] == f"char_0_{len(text)}"
    assert match["start_char"] == 0
    assert "Operating lease costs" in match["snippet"]


def test_document_scan_all_terms_filters_fuzzy_false_positive():
    text = "Cover page current report language.\n\nReceivables net merchandise inventories total current assets."

    class Provider:
        def read_document(self, source, max_chars, max_pages):
            return {
                "source": source,
                "engine": "test-html",
                "format": "html",
                "text": text,
                "pages": [
                    {
                        "page": 1,
                        "text": text,
                        "char_count": len(text),
                        "blocks": [
                            {
                                "index": 0,
                                "text": "Cover page current report language.",
                                "start_char": 0,
                                "end_char": 35,
                                "bbox": None,
                            },
                            {
                                "index": 1,
                                "text": "Receivables net merchandise inventories total current assets.",
                                "start_char": 37,
                                "end_char": len(text),
                                "bbox": None,
                            },
                        ],
                    }
                ],
                "char_count": len(text),
                "warnings": [],
            }

    result = scan_document(
        "filing.htm",
        topics=["Receivables net merchandise inventories total current assets"],
        threshold=80,
        match_mode="all_terms",
        provider=Provider(),
    )

    assert result["count"] == 1
    assert result["matches"][0]["block_index"] == 1
    assert result["matches"][0]["match_mode"] == "all_terms"


def test_document_scan_all_terms_uses_word_tokens_and_threshold():
    text = "Internet receivable current assets."

    class Provider:
        def read_document(self, source, max_chars, max_pages):
            return {
                "source": source,
                "engine": "test-html",
                "format": "html",
                "text": text,
                "pages": [
                    {
                        "page": 1,
                        "text": text,
                        "char_count": len(text),
                        "blocks": [
                            {
                                "index": 0,
                                "text": text,
                                "start_char": 0,
                                "end_char": len(text),
                                "bbox": None,
                            }
                        ],
                    }
                ],
                "char_count": len(text),
                "warnings": [],
            }

    result = scan_document(
        "filing.htm",
        topics=["net current assets"],
        threshold=100,
        match_mode="all_terms",
        provider=Provider(),
    )

    assert result["count"] == 0


def test_document_scan_can_restrict_html_offsets():
    text = "Risk factor merchandise inventories.\n\nBalance sheet merchandise inventories."

    class Provider:
        def read_document(self, source, max_chars, max_pages):
            return {
                "source": source,
                "engine": "test-html",
                "format": "html",
                "text": text,
                "pages": [
                    {
                        "page": 1,
                        "text": text,
                        "char_count": len(text),
                        "blocks": [
                            {
                                "index": 0,
                                "text": "Risk factor merchandise inventories.",
                                "start_char": 0,
                                "end_char": 34,
                                "bbox": None,
                            },
                            {
                                "index": 1,
                                "text": "Balance sheet merchandise inventories.",
                                "start_char": 36,
                                "end_char": len(text),
                                "bbox": None,
                            },
                        ],
                    }
                ],
                "char_count": len(text),
                "warnings": [],
            }

    result = scan_document(
        "filing.htm",
        topics=["merchandise inventories"],
        threshold=80,
        start_char=36,
        provider=Provider(),
    )

    assert result["count"] == 1
    assert result["matches"][0]["block_index"] == 1


def test_document_scan_offset_filter_clips_blocks():
    text = "before target phrase after"

    class Provider:
        def read_document(self, source, max_chars, max_pages):
            return {
                "source": source,
                "engine": "test-html",
                "format": "html",
                "text": text,
                "pages": [
                    {
                        "page": 1,
                        "text": text,
                        "char_count": len(text),
                        "blocks": [
                            {
                                "index": 0,
                                "text": text,
                                "start_char": 0,
                                "end_char": len(text),
                                "bbox": None,
                            }
                        ],
                    }
                ],
                "char_count": len(text),
                "warnings": [],
            }

    result = scan_document(
        "filing.htm",
        topics=["before"],
        threshold=100,
        start_char=7,
        end_char=19,
        provider=Provider(),
    )

    assert result["count"] == 0


def test_html_text_blocks_preserve_offsets_after_overflow_split():
    text = "a" * 10 + "\n" + "b" * 10

    blocks = _text_blocks(text, max_block_chars=11, max_block_lines=3)

    assert blocks[0]["text"] == "a" * 10
    assert blocks[0]["start_char"] == 0
    assert blocks[0]["end_char"] == 10
    assert blocks[1]["text"] == "b" * 10
    assert blocks[1]["start_char"] == 11
    assert blocks[1]["end_char"] == 21


def test_document_window_reads_from_match_id():
    text = "Revenue table\nOperating income $9,285\nDepreciation and amortization $2,237\n"

    class Provider:
        def read_document(self, source, max_chars, max_pages):
            return {
                "source": source,
                "engine": "test-html",
                "format": "html",
                "text": text,
                "pages": [],
                "char_count": len(text),
                "warnings": [],
            }

    result = window_document(
        "filing.htm",
        match_id="char_14_37",
        direction="next",
        chars=60,
        provider=Provider(),
    )

    assert result["start_char"] == 37
    assert "Depreciation and amortization" in result["text"]


def test_camelot_table_provider_returns_compact_rows(monkeypatch, tmp_path):
    class Values:
        def __init__(self, rows):
            self._rows = rows

        def tolist(self):
            return self._rows

    class Frame:
        shape = (3, 2)

        def head(self, count):
            self._count = count
            return self

        def fillna(self, value):
            return self

        def astype(self, kind):
            return self

        @property
        def values(self):
            return Values([["Metric", "Value"], ["Revenue", "$100"]])

    class Table:
        page = "5"
        df = Frame()
        parsing_report = {"accuracy": 98.765, "whitespace": 12.345}

    class Camelot:
        @staticmethod
        def read_pdf(path, pages, flavor):
            assert pages == "5"
            assert flavor == "stream"
            return [Table()]

    path = tmp_path / "report.pdf"
    path.write_bytes(b"%PDF")
    monkeypatch.setattr("finance_cli.providers.camelot_tables.require_dependency", lambda *args, **kwargs: Camelot)

    result = CamelotTableProvider().extract_tables(str(path), pages="5", flavor="stream", max_rows=2)

    assert result["engine"] == "camelot"
    assert result["count"] == 1
    assert result["tables"][0]["page"] == "5"
    assert result["tables"][0]["accuracy"] == 98.77
    assert result["tables"][0]["rows"][1] == ["Revenue", "$100"]
    assert result["tables"][0]["truncated"] is True


def test_document_tables_service_uses_injected_provider():
    class Provider:
        def extract_tables(self, source, pages, flavor, max_tables, max_rows):
            return {
                "source": source,
                "pages": pages,
                "flavor": flavor,
                "max_tables": max_tables,
                "max_rows": max_rows,
                "tables": [],
                "warnings": [],
            }

    result = extract_document_tables("report.pdf", pages="2", flavor="lattice", max_tables=3, max_rows=4, provider=Provider())

    assert result["source"] == "report.pdf"
    assert result["pages"] == "2"
    assert result["flavor"] == "lattice"
    assert result["max_tables"] == 3
    assert result["max_rows"] == 4


def test_document_ocr_service_uses_injected_provider():
    class Provider:
        def read_document(self, source, max_chars, max_pages):
            return {"source": source, "max_chars": max_chars, "max_pages": max_pages, "pages": [], "warnings": []}

    result = ocr_document("deck.pdf", max_chars=500, max_pages=2, provider=Provider())

    assert result["source"] == "deck.pdf"
    assert result["max_chars"] == 500
    assert result["max_pages"] == 2


def test_fetch_filing_index_returns_empty_on_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise RuntimeError("network error")

    monkeypatch.setattr("finance_cli.providers.sec_edgar.httpx.get", fake_get)
    result = SecEdgarProvider()._fetch_filing_index(cik_int=1648802, accession_no="0001648802-26-000011")
    assert result == []


from finance_cli.services.ir import list_ir_presentations, read_ir_presentation


def test_company_ir_provider_discovers_presentation_links(monkeypatch):
    html = """
    <html><head><title>Investor Relations</title></head><body>
      <a href="/news/press-release">Press Release</a>
      <a href="/events/investor-day-2026-presentation.pdf">Investor Day 2026 Presentation</a>
      <a href="/events/q4-2026-earnings-slides.htm">Q4 2026 Earnings Slides</a>
    </body></html>
    """

    class Response:
        text = html
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            return None

    monkeypatch.setattr("finance_cli.providers.company_ir.httpx.get", lambda *args, **kwargs: Response())

    rows = CompanyIRProvider().list_presentations(
        "IOT",
        company_name="Samsara Inc.",
        website="https://www.samsara.com",
        ir_website="https://investors.samsara.com",
    )

    assert len(rows) == 2
    assert rows[0]["source"] == "company_ir"
    assert rows[0]["confidence"] == "high"
    assert "press" not in {row["title"].lower() for row in rows}


def test_company_ir_domain_parsing_handles_multipart_tlds():
    assert _company_ir_registrable_domain("https://investors.example.co.uk/events") == "example.co.uk"
    assert _company_ir_registrable_domain("https://ir.example.com/presentations") == "example.com"


def test_company_ir_date_extraction_rejects_unreasonable_future_year():
    assert _extract_company_ir_date("Q4 FY26 Investor Presentation") == "2026"
    assert _extract_company_ir_date("Strategy 2030 presentation") is None


def test_list_ir_presentations_auto_uses_company_ir_fallback(monkeypatch):
    monkeypatch.setattr(
        "finance_cli.services.ir.SecEdgarProvider.list_exhibit_candidates",
        lambda self, symbol, limit: [],
    )
    monkeypatch.setattr(
        "finance_cli.services.ir.YahooFinanceProvider.quote",
        lambda self, symbol: {
            "symbol": symbol,
            "company_name": "Samsara Inc.",
            "website": "https://www.samsara.com",
            "ir_website": "https://investors.samsara.com",
        },
    )
    monkeypatch.setattr(
        "finance_cli.services.ir.CompanyIRProvider.list_presentations",
        lambda self, symbol, company_name, website, ir_website, limit: [
            {
                "title": "Investor Day 2026 Presentation",
                "kind": "investor_day",
                "source": "company_ir",
                "url": "https://investors.samsara.com/deck.pdf",
                "confidence": "high",
                "warnings": [],
            }
        ],
    )

    result = list_ir_presentations("IOT", limit=5)

    assert result["source"] == "auto"
    assert result["sources_used"] == ["sec_edgar", "company_ir"]
    assert result["count"] == 1
    assert result["presentations"][0]["source"] == "company_ir"


def test_list_ir_presentations_returns_candidate_rows(monkeypatch):
    monkeypatch.setattr(
        "finance_cli.services.ir.SecEdgarProvider.list_exhibit_candidates",
        lambda self, symbol, limit: [
            {
                "title": "Investor Day 2026",
                "date": "2026-03-05",
                "kind": "investor_day",
                "source": "sec_edgar",
                "url": "https://sec.example/iot_investorday.htm",
                "filing_accession": "0001648802-26-000011",
                "exhibit": "EX-99.1",
                "confidence": "high",
                "why_matched": "description contains 'investor day'",
            }
        ],
    )

    result = list_ir_presentations("IOT", limit=5)

    assert result["symbol"] == "IOT"
    assert result["count"] == 1
    assert result["presentations"][0]["kind"] == "investor_day"
    assert result["presentations"][0]["confidence"] == "high"
    assert result["source"] == "auto"
    assert result["sources_used"] == ["sec_edgar"]


def test_read_ir_presentation_html(monkeypatch):
    monkeypatch.setattr(
        "finance_cli.services.ir.SecEdgarProvider.read_exhibit_text",
        lambda self, url, max_chars: {
            "url": url,
            "text": "Samsara Investor Day 2026 content here.",
            "char_count": 40,
            "returned_chars": 40,
            "truncated": False,
            "format": "html",
            "warnings": [],
        },
    )

    result = read_ir_presentation("https://sec.example/iot_investorday.htm", max_chars=1000)

    assert result["text"] == "Samsara Investor Day 2026 content here."
    assert result["format"] == "html"
    assert result["warnings"] == []


def test_read_ir_presentation_auto_ocr_fallback(monkeypatch):
    monkeypatch.setattr(
        "finance_cli.services.ir.SecEdgarProvider.read_exhibit_text",
        lambda self, url, max_chars: {
            "url": url,
            "text": "",
            "char_count": 0,
            "returned_chars": 0,
            "truncated": False,
            "format": "pdf",
            "warnings": ["PDF text extraction returned no text."],
        },
    )
    monkeypatch.setattr(
        "finance_cli.services.ir.ocr_document",
        lambda source, max_chars, provider=None: {
            "source": source,
            "engine": "paddleocr_pp_structure_v3",
            "text": "OCR investor presentation text",
            "markdown": "# OCR investor presentation text",
            "pages": [{"page": 1, "text": "OCR investor presentation text"}],
            "warnings": [],
        },
    )

    result = read_ir_presentation("https://sec.example/deck.pdf", max_chars=1000, ocr="auto")

    assert result["ocr"]["ok"] is True
    assert result["text"] == "OCR investor presentation text"
    assert result["native_extraction"]["format"] == "pdf"


def test_read_ir_presentation_pdf_warns(monkeypatch):
    monkeypatch.setattr(
        "finance_cli.services.ir.SecEdgarProvider.read_exhibit_text",
        lambda self, url, max_chars: {
            "url": url,
            "text": None,
            "char_count": 0,
            "returned_chars": 0,
            "truncated": False,
            "format": "pdf",
            "warnings": ["PDF text extraction is not yet supported."],
        },
    )

    result = read_ir_presentation("https://sec.example/deck.pdf", max_chars=1000)

    assert result["text"] is None
    assert result["format"] == "pdf"
    assert result["warnings"]


def test_cli_ir_commands_registered():
    register_builtin_commands()
    names = {command.name for command in list_commands()}
    assert "ir.presentations" in names
    assert "ir.read" in names


def test_cli_ir_presentations_returns_candidates(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.ir.list_ir_presentations",
        lambda symbol, limit, source="auto": {
            "symbol": symbol,
            "presentations": [{"title": "Investor Day 2026", "kind": "investor_day", "confidence": "high"}],
            "count": 1,
            "source": source,
            "notes": [],
            "warnings": [],
        },
    )

    code = main(["ir.presentations", "IOT", "limit=3"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["count"] == 1
    assert payload["data"]["presentations"][0]["kind"] == "investor_day"


def test_cli_ir_read_returns_text(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.ir.read_ir_presentation",
        lambda url, max_chars, ocr="off": {
            "url": url,
            "text": "Investor Day content.",
            "char_count": 21,
            "returned_chars": 21,
            "truncated": False,
            "format": "html",
            "warnings": [],
        },
    )

    code = main(["ir.read", "url=https://sec.example/deck.htm", "max_chars=500"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["text"] == "Investor Day content."
    assert payload["data"]["format"] == "html"


def test_cli_ir_presentations_help(capsys):
    code = main(["ir.presentations", "--help"])
    output = capsys.readouterr().out
    assert code == 0
    assert "ir.presentations" in output
    assert "limit=" in output
    assert "source=" in output


def test_cli_ir_read_help(capsys):
    code = main(["ir.read", "--help"])
    output = capsys.readouterr().out
    assert code == 0
    assert "url=" in output
    assert "max_chars=" in output
    assert "ocr=" in output
    assert "PDF" in output


def test_cli_document_help_documents_native_and_ocr_paths(capsys):
    register_builtin_commands()

    code = main(["document", "--help"])
    output = capsys.readouterr().out
    assert code == 0
    assert "read" in output
    assert "scan" in output
    assert "tables" in output
    assert "ocr" in output

    code = main(["document.scan", "--help"])
    output = capsys.readouterr().out
    assert code == 0
    assert "topics=" in output
    assert "threshold=" in output
    assert "RapidFuzz" in output

    code = main(["document.tables", "--help"])
    output = capsys.readouterr().out
    assert code == 0
    assert "pages=" in output
    assert "flavor=" in output
    assert "Camelot" in output
