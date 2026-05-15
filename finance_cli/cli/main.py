"""Command-line entry point for finance capabilities."""
from __future__ import annotations

import argparse
import sys

from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.formatting import render_result
from finance_cli.cli.registry import FinanceCommand, get_command, list_commands
from finance_cli.schemas import FinanceCommandResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="finance", description="Finance research helper CLI")
    parser.add_argument("command", nargs="?", help="Command name, for example market.regime")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--output", choices=["json", "text"], default="json")
    parser.add_argument("--list", action="store_true", help="List available commands")
    return parser


def main(argv: list[str] | None = None) -> int:
    register_builtin_commands()
    raw_args = list(sys.argv[1:] if argv is None else argv)
    if raw_args:
        if raw_args[0] == "help":
            if len(raw_args) >= 2:
                return _print_help(raw_args[1])
            _print_command_list()
            print("\nUse `finance NAMESPACE --help` or `finance NAMESPACE.COMMAND --help` for more detail.")
            return 0
        if len(raw_args) >= 2 and raw_args[1] in {"-h", "--help", "help"} and not raw_args[0].startswith("-"):
            return _print_help(raw_args[0])

    parser = build_parser()
    ns = parser.parse_args(raw_args)

    if ns.list or not ns.command:
        _print_command_list()
        return 0

    command = get_command(ns.command)
    if command is None:
        print(render_result(FinanceCommandResult(ok=False, error=f"unknown command: {ns.command}"), ns.output))
        return 2

    try:
        result = command.handler(ns.args)
    except Exception as exc:
        result = FinanceCommandResult(ok=False, error=str(exc))

    print(render_result(result, ns.output))
    return 0 if result.ok else 1


def _print_command_list() -> None:
    for command in list_commands():
        print(f"{command.name}\t{command.summary}")


def _print_command_help(command_name: str) -> int:
    command = get_command(command_name)
    if command is None:
        print(render_result(FinanceCommandResult(ok=False, error=f"unknown command: {command_name}"), "json"))
        return 2
    print(format_command_help(command))
    return 0


def _print_help(name: str) -> int:
    command = get_command(name)
    if command is not None:
        print(format_command_help(command))
        return 0
    matching = _commands_in_namespace(name)
    if matching:
        print(format_namespace_help(name, matching))
        return 0
    print(render_result(FinanceCommandResult(ok=False, error=f"unknown command or namespace: {name}"), "json"))
    return 2


def _commands_in_namespace(namespace: str) -> list[FinanceCommand]:
    prefix = f"{namespace}."
    return [command for command in list_commands() if command.name.startswith(prefix)]


def format_command_help(command: FinanceCommand) -> str:
    lines = [command.name, command.summary]
    if command.usage:
        lines.extend(["", f"Usage: {command.usage}"])
    if command.examples:
        lines.append("")
        lines.append("Examples:")
        lines.extend(f"  {example}" for example in command.examples)
    if command.notes:
        lines.append("")
        lines.append("Details:")
        lines.extend(f"  - {note}" for note in command.notes)
    return "\n".join(lines)


def format_namespace_help(namespace: str, commands: list[FinanceCommand]) -> str:
    lines = [namespace, f"Commands under `{namespace}`:"]
    for command in commands:
        suffix = command.name.split(".", 1)[1]
        lines.append(f"  {suffix:<24} {command.summary}")
    lines.extend(["", f"Use `finance {namespace}.COMMAND --help` for command-specific usage."])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
