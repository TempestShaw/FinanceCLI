"""Company press-release and event feed commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.providers.ir_feed import IRFeedProvider
from finance_cli.schemas import FinanceCommandResult


def _items(args: list[str], *, kind: str) -> FinanceCommandResult:
    if not args or "=" in args[0]:
        return FinanceCommandResult(ok=False, error=f"usage: ir.{kind} SYMBOL [url=PAGE_OR_FEED limit=20]")
    kv = KVArgs(args[1:])
    provider = IRFeedProvider()
    fetch = provider.list_releases if kind == "releases" else provider.list_events
    data = fetch(args[0], url=kv.str("url"), limit=kv.int("limit", 20))
    return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])


def _releases(args: list[str]) -> FinanceCommandResult:
    return _items(args, kind="releases")


def _events(args: list[str]) -> FinanceCommandResult:
    return _items(args, kind="events")


def register_ir_feed_commands() -> None:
    for name, handler in (("releases", _releases), ("events", _events)):
        register_command(FinanceCommand(
            f"ir.{name}", f"Discover company {name} from public RSS/Atom feeds and IR pages", handler,
            usage=f"ir.{name} SYMBOL [url=PAGE_OR_FEED limit=20]",
            examples=(f"finance ir.{name} NVDA url=https://investor.nvidia.com/investor-resources/rss/default.aspx limit=5",),
            notes=("Best-effort discovery from the company's website; pass an explicit page/feed URL when auto-discovery is incomplete.",
                   "Returns source links and feed dates; event feed publication dates may differ from scheduled event times."),
        ))
