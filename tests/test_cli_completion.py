from finance_cli.cli.usage import parse_usage_params


def test_parse_usage_params_extracts_keys_required_flags_and_enums():
    params = parse_usage_params(
        "document.scan SOURCE|source=PATH_OR_URL "
        "[query=TEXT format=pdf|html match=fuzzy|all_terms max_chars=12000]"
    )

    assert params["source"]["required"] is True
    assert params["source"]["aliases"] == ["SOURCE"]
    assert params["format"]["enum"] == ["pdf", "html"]
    assert params["match"]["enum"] == ["fuzzy", "all_terms"]
    assert params["max_chars"]["default"] == 12000


from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.completion import complete
from finance_cli.cli.main import main
from finance_cli.cli.registry import FinanceCommand, clear_commands, register_command
from finance_cli.schemas import FinanceCommandResult


def registered_completions(line: str) -> list[str]:
    clear_commands()
    register_builtin_commands()
    return complete(line, len(line))


def test_completion_suggests_namespaces_and_commands():
    assert "sources." in registered_completions("finance sou")
    assert "sources.status" in registered_completions("finance sources.sta")
    assert {"sources.list", "sources.status", "sources.test"}.issubset(
        set(registered_completions("finance sources."))
    )


def test_completion_suggests_global_options_anywhere():
    assert "--output" in registered_completions("finance --outp")
    assert "--output" in registered_completions("finance market.quote AAPL --outp")


def test_completion_suggests_output_values_after_output_option():
    suggestions = registered_completions("finance market.quote AAPL --output ")

    assert {"json", "compact", "schema"}.issubset(set(suggestions))


def test_completion_suggests_key_value_arguments_and_enum_values():
    assert "format=" in registered_completions("finance document.scan sample.pdf for")

    suggestions = registered_completions("finance document.scan sample.pdf format=")

    assert "format=pdf" in suggestions
    assert "format=html" in suggestions


def test_completion_does_not_execute_command_handlers():
    clear_commands()

    def fail_if_called(_args: list[str]) -> FinanceCommandResult:
        raise AssertionError("completion must not run command handlers")

    register_command(FinanceCommand("custom.status", "Custom status", fail_if_called, usage="custom.status [mode=fast|full]"))

    assert complete("finance custom.status mode=", len("finance custom.status mode=")) == ["mode=fast", "mode=full"]


def test_hidden_complete_entrypoint_prints_suggestions(capsys, monkeypatch):
    monkeypatch.setenv("COMP_LINE", "finance sources.sta")
    monkeypatch.setenv("COMP_POINT", str(len("finance sources.sta")))

    code = main(["__complete", "bash"])
    output = capsys.readouterr().out.strip().splitlines()

    assert code == 0
    assert "sources.status" in output


def test_hidden_complete_entrypoint_rejects_unknown_shell(capsys, monkeypatch):
    monkeypatch.setenv("COMP_LINE", "finance sources.")
    monkeypatch.setenv("COMP_POINT", str(len("finance sources.")))

    code = main(["__complete", "powershell"])
    output = capsys.readouterr().out

    assert code == 2
    assert "unknown completion shell" in output
