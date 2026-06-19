"""Side-by-side comparison command: run one command across several symbols."""
from __future__ import annotations

from typing import Any

from finance_cli.cli.registry import FinanceCommand, get_command, register_command
from finance_cli.presentation import (
    Block,
    KeyValue,
    Presentation,
    register_presenter,
)
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.compare import build_comparison

_USAGE = "compare SYMBOL [SYMBOL ...] COMMAND [key=value ...]"


def _compare(args: list[str]) -> FinanceCommandResult:
    symbols, command, extra = _split_args(args)
    if command is None:
        return FinanceCommandResult(
            ok=False,
            error=f"usage: {_USAGE}; provide at least one symbol and a known command, e.g. compare AAPL MSFT market.quote",
        )
    if not symbols:
        return FinanceCommandResult(ok=False, error=f"usage: {_USAGE}; no symbols before command '{command}'")

    def run(name: str, command_args: list[str]) -> FinanceCommandResult:
        target = get_command(name)
        if target is None:
            return FinanceCommandResult(ok=False, error=f"unknown command: {name}")
        try:
            return target.handler(command_args)
        except Exception as exc:  # surface per-symbol failure without aborting the run
            return FinanceCommandResult(ok=False, error=str(exc))

    data = build_comparison(symbols, command, extra, run=run)
    if not data["compared"]:
        joined = "; ".join(f"{symbol}: {message}" for symbol, message in data["errors"].items())
        return FinanceCommandResult(ok=False, error=f"no comparable results ({joined})", data=data)
    return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])


def _split_args(args: list[str]) -> tuple[list[str], str | None, list[str]]:
    for index, token in enumerate(args):
        if "=" in token:
            break
        if get_command(token) is not None:
            return args[:index], token, args[index + 1 :]
    return list(args), None, []


def _compare_presentation(command: str | None, data: dict[str, Any]) -> Presentation | None:
    compared = data.get("compared") or []
    rows = data.get("rows") or []
    if not compared or not rows:
        return None
    sub_command = str(data.get("command") or "")
    columns = ("Metric", *compared)
    table_rows = tuple(
        (str(row.get("metric", "")), *(str(row.get(symbol, "-")) for symbol in compared))
        for row in rows
    )
    headline = f"Compare {sub_command}: " + " vs ".join(compared)
    notes = [f"{symbol}: {message}" for symbol, message in (data.get("errors") or {}).items()]
    return Presentation(
        headline=headline,
        blocks=(Block(columns=columns, rows=table_rows),),
        notes=tuple(notes),
    )


def register_compare_commands() -> None:
    register_presenter("compare", _compare_presentation)
    register_command(FinanceCommand(
        "compare",
        "Run one command across several symbols and align the results",
        _compare,
        usage=_USAGE,
        examples=(
            "finance compare AAPL MSFT GOOG market.quote",
            "finance compare AAPL MSFT valuation.multiples",
        ),
        notes=(
            "The first argument that names a registered command splits symbols from the command.",
            "Comparison aligns the top-level scalar metrics each command returns; list-shaped results are reported per symbol as errors.",
        ),
    ))


# Keep the presenter registered even if the command module is imported without
# the explicit registration call (e.g. via direct import in tests).
register_presenter("compare", _compare_presentation)
