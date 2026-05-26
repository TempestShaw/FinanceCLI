"""Shell completion CLI command."""
from __future__ import annotations

from finance_cli.cli.completion import completion_script
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult


def _completion(args: list[str]) -> FinanceCommandResult:
    shell = args[0] if args else "bash"
    try:
        script = completion_script(shell)
    except ValueError as exc:
        return FinanceCommandResult(ok=False, error=str(exc))
    return FinanceCommandResult(ok=True, data={"shell": shell, "script": script})


def register_completion_commands() -> None:
    register_command(FinanceCommand(
        "completion",
        "Print shell completion setup for bash, zsh, or fish",
        _completion,
        usage="completion SHELL",
        examples=(
            "finance completion bash > ~/.local/share/bash-completion/completions/finance",
            "finance completion zsh > ~/.zfunc/_finance",
            "finance completion fish > ~/.config/fish/completions/finance.fish",
        ),
        notes=(
            "Prints shell code only; it does not modify shell startup files.",
            "Completion candidates are generated from the live command registry and usage metadata.",
        ),
    ))
