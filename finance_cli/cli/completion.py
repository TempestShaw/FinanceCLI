"""FinanceCLI shell completion engine."""
from __future__ import annotations

import shlex
from dataclasses import dataclass
from importlib import resources

from finance_cli.cli.options import GLOBAL_OPTIONS
from finance_cli.cli.registry import FinanceCommand, list_commands
from finance_cli.cli.usage import parse_usage_params


SUPPORTED_SHELLS = {"bash", "zsh", "fish"}
SCRIPT_FILES = {
    "bash": "finance.bash",
    "zsh": "finance.zsh",
    "fish": "finance.fish",
}


@dataclass(frozen=True)
class CompletionContext:
    words: tuple[str, ...]
    current: str


def complete(line: str, point: int | None = None) -> list[str]:
    state = _context(line, point)
    command = _selected_command(state.words)
    if _previous_word(state.words) == "--output":
        return _prefix_filter(GLOBAL_OPTIONS["--output"], state.current)
    if state.current.startswith("--"):
        return _prefix_filter(list(GLOBAL_OPTIONS), state.current)
    if "=" in state.current and command is not None:
        return _complete_key_value(command, state.current)
    if command is not None:
        command_args = _command_arg_suggestions(command, state.current)
        if command_args:
            return command_args
        return _prefix_filter(list(GLOBAL_OPTIONS), state.current)
    return _complete_command_or_namespace(state.current)


def complete_from_env(shell: str, env: dict[str, str]) -> tuple[int, str]:
    if shell not in SUPPORTED_SHELLS:
        return 2, f"unknown completion shell: {shell}"
    line = env.get("COMP_LINE", "")
    try:
        point = int(env.get("COMP_POINT", str(len(line))))
    except ValueError:
        point = len(line)
    suggestions = complete(line, point)
    return 0, "\n".join(_format_suggestion(shell, suggestion) for suggestion in suggestions)


def completion_script(shell: str) -> str:
    filename = SCRIPT_FILES.get(shell)
    if filename is None:
        raise ValueError(f"unknown completion shell: {shell}")
    return (resources.files("finance_cli.cli.completions") / filename).read_text(encoding="utf-8")


def _format_suggestion(shell: str, suggestion: str) -> str:
    if shell == "fish":
        return suggestion.replace("\t", " ")
    return suggestion


def _context(line: str, point: int | None) -> CompletionContext:
    left = line[: point if point is not None else len(line)]
    ends_with_space = left.endswith((" ", "\t"))
    words = tuple(_safe_split(left))
    if not words:
        return CompletionContext(words=(), current="")
    if ends_with_space:
        return CompletionContext(words=words, current="")
    return CompletionContext(words=words[:-1], current=words[-1])


def _safe_split(text: str) -> list[str]:
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()


def _previous_word(words: tuple[str, ...]) -> str | None:
    return words[-1] if words else None


def _selected_command(words: tuple[str, ...]) -> FinanceCommand | None:
    commands = {command.name: command for command in list_commands()}
    for word in words:
        if word in commands:
            return commands[word]
    return None


def _complete_command_or_namespace(prefix: str) -> list[str]:
    names = sorted(command.name for command in list_commands())
    namespaces = sorted({name.split(".", 1)[0] + "." for name in names if "." in name})
    if "." not in prefix:
        return _prefix_filter(namespaces + names, prefix)
    return _prefix_filter(names, prefix)


def _command_arg_suggestions(command: FinanceCommand, prefix: str) -> list[str]:
    params = parse_usage_params(command.usage)
    keys = sorted(f"{name}=" for name in params if not name.isupper())
    return _prefix_filter(keys, prefix)


def _complete_key_value(command: FinanceCommand, current: str) -> list[str]:
    key, value_prefix = current.split("=", 1)
    params = parse_usage_params(command.usage)
    meta = params.get(key)
    if not meta:
        return []
    values = [f"{key}={value}" for value in meta.get("enum", [])]
    return _prefix_filter(values, f"{key}={value_prefix}")


def _prefix_filter(values: list[str], prefix: str) -> list[str]:
    return [value for value in values if value.startswith(prefix)]
