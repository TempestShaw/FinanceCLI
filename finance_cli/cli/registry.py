"""Small command registry for the finance CLI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from finance_cli.schemas import FinanceCommandResult


CommandHandler = Callable[[list[str]], FinanceCommandResult]


@dataclass(frozen=True)
class FinanceCommand:
    name: str
    summary: str
    handler: CommandHandler
    usage: str = ""
    examples: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


_COMMANDS: dict[str, FinanceCommand] = {}


def register_command(command: FinanceCommand) -> None:
    _COMMANDS[command.name] = command


def get_command(name: str) -> FinanceCommand | None:
    return _COMMANDS.get(name)


def list_commands() -> list[FinanceCommand]:
    return list(_COMMANDS.values())


def clear_commands() -> None:
    _COMMANDS.clear()
