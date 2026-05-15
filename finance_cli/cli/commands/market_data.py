"""Market-data CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs, parse_csv
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.market_data import fetch_ohlcv, fetch_ohlcv_batch, fetch_realtime_quote


def _market_quote(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: market.quote SYMBOL")
    return FinanceCommandResult(ok=True, data=fetch_realtime_quote(args[0]))


def _market_ohlcv(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: market.ohlcv SYMBOL[,SYMBOL...] [timeframe=1d start_date=YYYY-MM-DD end_date=YYYY-MM-DD limit=200 provider=auto include_attempts=false]")
    kv = KVArgs(args[1:])
    symbols = parse_csv(args[0])
    common_kwargs = dict(
        timeframe=kv.str("timeframe", "1d"),
        start_date=kv.str("start_date"),
        end_date=kv.str("end_date"),
        limit=kv.int("limit", 200),
        provider=kv.str("provider", "auto"),
        include_attempts=kv.bool("include_attempts"),
    )
    data = fetch_ohlcv_batch(symbols, **common_kwargs) if len(symbols) > 1 else fetch_ohlcv(symbols[0], **common_kwargs)
    return FinanceCommandResult(ok=True, data=data)


def register_market_data_commands() -> None:
    register_command(FinanceCommand(
        "market.quote",
        "Fetch quote via the best available provider",
        _market_quote,
        usage="market.quote SYMBOL",
        examples=("finance market.quote NVDA",),
        notes=("Uses Alpha Vantage when configured, with Yahoo fallback.",),
    ))
    register_command(FinanceCommand(
        "market.ohlcv",
        "Fetch normalized OHLCV records for one or more symbols",
        _market_ohlcv,
        usage="market.ohlcv SYMBOL[,SYMBOL...] [timeframe=1d start_date=YYYY-MM-DD end_date=YYYY-MM-DD limit=200 provider=auto include_attempts=false]",
        examples=(
            "finance market.ohlcv NVDA timeframe=1d limit=20",
            "finance market.ohlcv AAPL,MSFT,NVDA timeframe=1d limit=5 provider=auto",
        ),
        notes=("Arguments use key=value syntax for script-friendly CLI calls.",),
    ))
