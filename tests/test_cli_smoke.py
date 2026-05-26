import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import finance_cli
from finance_cli.cli.commands import document as document_commands
from finance_cli.cli.commands import filings as filings_commands
from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.main import main
from finance_cli.cli.registry import clear_commands, list_commands
from finance_cli.providers.camelot_tables import _round_or_none
from scripts.generate_cli_docs import build_command_specs, build_openapi_document, build_tools_document, build_tools_schema_document


def test_package_version_matches_project_metadata():
    metadata = tomllib.loads(Path("pyproject.toml").read_text())

    assert finance_cli.__version__ == metadata["project"]["version"]


def test_finance_cli_formula_command_outputs_json(capsys):
    code = main(["formula.margin", "numerator=10", "denominator=20"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["margin"] == 0.5


def test_finance_cli_lists_commands(capsys):
    code = main(["--list"])
    output = capsys.readouterr().out

    assert code == 0
    assert "formula.margin" in output
    assert "sources.status" in output


def test_generated_agent_schema_covers_registered_commands():
    clear_commands()
    register_builtin_commands()
    commands = sorted(list_commands(), key=lambda command: command.name)
    specs = build_command_specs(commands)
    tools_doc = build_tools_document(specs)
    openapi_doc = build_openapi_document(specs)
    tools_schema = build_tools_schema_document()

    assert len(specs) == len(commands)
    assert len(tools_doc["commands"]) == len(commands)
    assert tools_doc["$schema"] == tools_schema["$id"]
    assert tools_doc["record_schema"]["required"] == ["entity", "kind", "fields"]
    assert tools_doc["output_formats"]["compact"]["record_renderer"] is True
    assert tools_schema["properties"]["record_schema"]["type"] == "object"
    assert "/commands/filings.statement" in openapi_doc["paths"]

    filings_statement = next(spec for spec in specs if spec["name"] == "filings.statement")
    assert filings_statement["side_effects"] == "network_read_only"
    assert filings_statement["args"]["statement"]["enum"] == ["income", "balance", "cashflow"]
    assert filings_statement["args"]["max_rows"]["default"] == 0
    assert "accession_no" in filings_statement["citation_fields"]

    document_scan = next(spec for spec in specs if spec["name"] == "document.scan")
    assert document_scan["side_effects"] == "local_or_network_read"
    assert document_scan["args"]["source"]["required"] is True
    assert document_scan["args"]["match"]["enum"] == ["fuzzy", "all_terms"]

    valuation_dcf = next(spec for spec in specs if spec["name"] == "valuation.dcf")
    assert valuation_dcf["side_effects"] == "pure_calculation"
    assert "investment advice" in valuation_dcf["agent"]["avoid_when"]

    fundamentals_growth = next(spec for spec in specs if spec["name"] == "fundamentals.growth")
    assert "YoY" in fundamentals_growth["agent"]["use_when"]
    assert fundamentals_growth["args"]["metrics"]["default"] == "revenue,eps,operating_margin,net_margin,roe"

    price_relative = next(spec for spec in specs if spec["name"] == "price.relative")
    assert price_relative["args"]["benchmarks"]["default"] == "SPY,QQQ"
    assert "default" not in price_relative["args"]["peers"]
    assert "explicit" in price_relative["agent"]["use_when"]

    market_trend = next(spec for spec in specs if spec["name"] == "market.trend")
    assert "breadth" in market_trend["agent"]["avoid_when"]
    assert market_trend["args"]["symbols"]["default"] == "SPY,QQQ,DIA,IWM,^VIX"


def test_generated_specs_use_package_usage_parser():
    from finance_cli.cli.usage import parse_usage_params

    params = parse_usage_params("price.moves SYMBOL [window=1d|3d|1w|1m limit=20]")

    assert params["window"]["enum"] == ["1d", "3d", "1w", "1m"]
    assert params["limit"]["default"] == 20


def test_completion_command_is_registered():
    clear_commands()
    register_builtin_commands()

    names = {command.name for command in list_commands()}

    assert "completion" in names


def test_filings_report_preserves_lookup_aliases(monkeypatch):
    captured = {}

    def fake_read_filing_report(**kwargs):
        captured.update(kwargs)
        return {"ok": "data"}

    monkeypatch.setattr(filings_commands, "read_filing_report", fake_read_filing_report)

    result = filings_commands._filings_report(
        [
            "symbol=COST",
            "accession_no=0000909832-24-000049",
            "name=Debt",
            "form=10-K",
            "query=lease",
            "max_rows=3",
            "max_chars=900",
        ]
    )

    assert result.ok is True
    assert captured == {
        "symbol": "COST",
        "accession_no": "0000909832-24-000049",
        "url": None,
        "form": "10-K",
        "name": "Debt",
        "query": "lease",
        "max_rows": 3,
        "max_chars": 900,
    }


def test_filings_statement_still_accepts_positional_symbol(monkeypatch):
    captured = {}

    def fake_read_filing_statement(**kwargs):
        captured.update(kwargs)
        return {"rows": []}

    monkeypatch.setattr(filings_commands, "read_filing_statement", fake_read_filing_statement)

    result = filings_commands._filings_statement(["COST", "statement=balance", "max_rows=2"])

    assert result.ok is True
    assert captured["symbol"] == "COST"
    assert captured["accession_no"] is None
    assert captured["url"] is None
    assert captured["statement"] == "balance"
    assert captured["view"] == "standard"
    assert captured["max_rows"] == 2


def test_filings_report_requires_name_even_with_source():
    result = filings_commands._filings_report(["COST"])

    assert result.ok is False
    assert "usage: filings.report" in result.error


def test_document_read_uses_common_result_wrapper(monkeypatch):
    captured = {}

    def fake_read_document(source, **kwargs):
        captured["source"] = source
        captured.update(kwargs)
        return {"text": "hello", "warnings": ["short"]}

    monkeypatch.setattr(document_commands, "read_document", fake_read_document)

    result = document_commands._cmd_document_read(["source=report.pdf", "max_chars=50", "max_pages=2"])

    assert result.ok is True
    assert result.warnings == ["short"]
    assert captured == {
        "source": "report.pdf",
        "max_chars": 50,
        "max_pages": 2,
        "doc_format": None,
    }


def test_document_window_errors_stay_result_shaped():
    result = document_commands._cmd_document_window(["report.pdf"])

    assert result.ok is False
    assert result.error == "start_char= or match_id=char_START_END is required"


def test_round_or_none_only_swallows_numeric_conversion_failures():
    assert _round_or_none(None) is None
    assert _round_or_none("12.345") == 12.35
    assert _round_or_none("not a number") is None
