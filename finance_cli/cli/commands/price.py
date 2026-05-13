"""Price-move research CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.price import price_context, price_moves


def _price_moves(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(
            ok=False,
            error="usage: price.moves SYMBOL [window=1d|3d|1w|1m years=3 threshold=8|8% limit=20 provider=auto]",
        )
    kv = KVArgs(args[1:])
    data = price_moves(
        args[0],
        window=kv.str("window", "1d") or "1d",
        years=kv.int("years", 3),
        threshold=kv.str("threshold", "8%") or "8%",
        limit=kv.int("limit", 20),
        provider=kv.str("provider", "auto") or "auto",
    )
    return FinanceCommandResult(ok=True, data=data)


def _price_context(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(
            ok=False,
            error="usage: price.context SYMBOL date=YYYY-MM-DD [lookback=3D news_limit=5 filing_limit=80 transcript_limit=12]",
        )
    kv = KVArgs(args[1:])
    target_date = kv.str("date") or kv.str("target_date")
    if not target_date:
        return FinanceCommandResult(
            ok=False,
            error="usage: price.context SYMBOL date=YYYY-MM-DD [lookback=3D news_limit=5 filing_limit=80 transcript_limit=12]",
        )
    data = price_context(
        args[0],
        target_date=target_date,
        lookback=kv.str("lookback", "3D") or "3D",
        news_limit=kv.int("news_limit", 5),
        filing_limit=kv.int("filing_limit", 80),
        transcript_limit=kv.int("transcript_limit", 12),
    )
    return FinanceCommandResult(ok=True, data=data, warnings=data.get("warnings", []))


def register_price_commands() -> None:
    register_command(FinanceCommand(
        "price.moves",
        "Find large deterministic close-to-close stock moves",
        _price_moves,
        usage="price.moves SYMBOL [window=1d|3d|1w|1m years=3 threshold=8|8% limit=20 provider=auto]",
        examples=(
            "finance price.moves IOT years=3 threshold=8% limit=10",
            "finance price.moves NVDA window=3d years=2 threshold=12%",
            "finance price.moves NVDA window=1w years=2 threshold=15 limit=10",
        ),
        notes=(
            "window is a trading-day window: 1d=1 trading day, 1w=5 trading days, 1m=21 trading days.",
            "threshold accepts decimal or percentage-point inputs: 0.08, 8, and 8% all mean 8%.",
            "Uses one OHLCV fetch and deterministic close-to-close math.",
            "Returns move dates and magnitude only; it does not infer causality.",
        ),
    ))
    register_command(FinanceCommand(
        "price.context",
        "Return a source-linked evidence timeline around a date",
        _price_context,
        usage="price.context SYMBOL date=YYYY-MM-DD [lookback=3D news_limit=5 filing_limit=80 transcript_limit=12]",
        examples=(
            "finance price.context IOT date=2026-03-06 lookback=3D",
            "finance price.context NVDA date=2025-01-27 lookback=2D news_limit=5",
            "finance price.context IOT date=2026-03-06 lookback=1W news_limit=5",
        ),
        notes=(
            "lookback is calendar time around date: 3D=3 calendar days before and after, 1W=7 calendar days, 1M=30 calendar days.",
            "Timeline roles are temporal only: before_move, same_day, after_move.",
            "Event/publication dates are explicit to avoid implied causal claims.",
        ),
    ))
