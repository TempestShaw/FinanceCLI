import json

from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.commands.compare import _compare_presentation, _split_args
from finance_cli.cli.main import main
from finance_cli.presentation import present, render_markdown
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.compare import build_comparison


def setup_function() -> None:
    register_builtin_commands()


def test_split_args_separates_symbols_command_and_extra():
    symbols, command, extra = _split_args(["AAPL", "MSFT", "market.quote", "range=1d"])

    assert symbols == ["AAPL", "MSFT"]
    assert command == "market.quote"
    assert extra == ["range=1d"]


def test_split_args_returns_none_command_when_no_registered_command():
    symbols, command, extra = _split_args(["AAPL", "MSFT"])

    assert command is None
    assert symbols == ["AAPL", "MSFT"]
    assert extra == []


def test_build_comparison_aligns_metrics_and_records_errors():
    def fake_run(command: str, args: list[str]) -> FinanceCommandResult:
        table = {
            "AAPL": {"price": 195.0, "pe_ratio": 31.2},
            "MSFT": {"price": 410.0, "pe_ratio": 36.5},
        }
        data = table.get(args[0])
        if data is None:
            return FinanceCommandResult(ok=False, error="symbol not found")
        return FinanceCommandResult(ok=True, data={"symbol": args[0], **data})

    result = build_comparison(["AAPL", "MSFT", "ZZZZ"], "market.quote", [], run=fake_run)

    assert result["compared"] == ["AAPL", "MSFT"]
    assert result["metrics"] == ["price", "PE ratio"]
    assert result["rows"][0] == {"metric": "price", "AAPL": "195", "MSFT": "410"}
    assert result["errors"] == {"ZZZZ": "symbol not found"}


def test_compare_presenter_builds_table_with_symbol_columns():
    data = {
        "command": "market.quote",
        "compared": ["AAPL", "MSFT"],
        "rows": [{"metric": "price", "AAPL": "195", "MSFT": "410"}],
        "errors": {},
    }

    presentation = present("compare", data)
    markdown = render_markdown(presentation)

    assert presentation.headline == "Compare market.quote: AAPL vs MSFT"
    assert "| Metric | AAPL | MSFT |" in markdown
    assert "| price | 195 | 410 |" in markdown


def test_compare_usage_error_when_no_command(capsys):
    code = main(["compare", "AAPL", "MSFT"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 1
    assert payload["ok"] is False
    assert "known command" in payload["error"]
