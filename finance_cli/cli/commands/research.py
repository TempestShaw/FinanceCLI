"""Research planning CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.research import research_plan


def _research_plan(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: research.plan SYMBOL [style=fundamental]")
    kv = KVArgs(args[1:])
    return FinanceCommandResult(ok=True, data=research_plan(args[0], style=kv.str("style", "fundamental")))


def register_research_commands() -> None:
    register_command(FinanceCommand(
        "research.plan",
        "Return a deterministic research command checklist",
        _research_plan,
        usage="research.plan SYMBOL [style=fundamental]",
        examples=("finance research.plan IOT style=fundamental",),
        notes=(
            "This returns suggested commands only; it does not execute research or form conclusions.",
            "Use this as a navigation layer for repeatable research workflows.",
        ),
    ))
