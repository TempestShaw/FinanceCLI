"""Yahoo screener CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.screen import list_predefined_screens, run_predefined_screen


def _screen_predefined(_args: list[str]) -> FinanceCommandResult:
    return FinanceCommandResult(ok=True, data=list_predefined_screens())


def _screen_run(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: screen.run QUERY [count=25 offset=0 sort_field=FIELD sort_asc=false]")
    kv = KVArgs(args[1:])
    offset = kv.str("offset")
    sort_asc = kv.str("sort_asc")
    data = run_predefined_screen(
        args[0],
        count=kv.int("count", 25),
        offset=int(offset) if offset is not None else None,
        sort_field=kv.str("sort_field"),
        sort_asc=kv.bool("sort_asc") if sort_asc is not None else None,
    )
    return FinanceCommandResult(ok=True, data=data)


def register_screen_commands() -> None:
    register_command(FinanceCommand(
        "screen.predefined",
        "List predefined Yahoo equity screens",
        _screen_predefined,
        usage="screen.predefined",
        examples=("finance screen.predefined",),
    ))
    register_command(FinanceCommand(
        "screen.run",
        "Run a predefined Yahoo equity screen",
        _screen_run,
        usage="screen.run QUERY [count=25 offset=0 sort_field=FIELD sort_asc=false]",
        examples=("finance screen.run day_gainers count=10",),
        notes=("Use screen.predefined to list available query keys.", "count is the maximum number of quotes requested."),
    ))
