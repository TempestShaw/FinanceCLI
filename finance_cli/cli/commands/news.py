"""News CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.news import analyze_news, search_news


def _news_search(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    data = search_news(
        query=kv.str("query"),
        symbol=kv.str("symbol"),
        sector=kv.str("sector"),
        max_records=kv.int("max_records", 50),
        timespan=kv.str("timespan"),
        date=kv.str("date"),
        start_date=kv.str("start_date"),
        end_date=kv.str("end_date"),
        start_datetime=kv.str("start_datetime"),
        end_datetime=kv.str("end_datetime"),
    )
    return FinanceCommandResult(ok=True, data=data)


def _news_analyze(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    data = analyze_news(
        analysis=kv.str("analysis", kv.str("type", "timeline")) or "timeline",
        query=kv.str("query"),
        symbol=kv.str("symbol"),
        sector=kv.str("sector"),
        mode=kv.str("mode"),
        max_records=kv.int("max_records", 50),
        timespan=kv.str("timespan"),
        date=kv.str("date"),
        start_date=kv.str("start_date"),
        end_date=kv.str("end_date"),
        start_datetime=kv.str("start_datetime"),
        end_datetime=kv.str("end_datetime"),
    )
    return FinanceCommandResult(ok=True, data=data)


def register_news_commands() -> None:
    register_command(FinanceCommand(
        "news.search",
        "Search finance news through GDELT",
        _news_search,
        usage="news.search [query=TEXT | symbol=SYMBOL | sector=SECTOR] [max_records=50 timespan=30D|1W|1M|24H date=YYYY-MM-DD start_date=YYYY-MM-DD end_date=YYYY-MM-DD start_datetime=YYYYMMDDHHMMSS end_datetime=YYYYMMDDHHMMSS]",
        examples=(
            "finance news.search symbol=NVDA max_records=5",
            "finance news.search symbol=NVDA timespan=30D max_records=10",
            "finance news.search symbol=NVDA timespan=1W max_records=10",
            "finance news.search query='NVIDIA export controls' timespan=24h",
            "finance news.search symbol=IOT date=2026-03-06 max_records=5",
            "finance news.search symbol=IOT start_date=2026-03-03 end_date=2026-03-09 max_records=5",
        ),
        notes=(
            "Use date for one full day, or start_date/end_date for a full-day range.",
            "Use timespan for relative lookback from now, such as 30D, 1W, 1M, 24H, or 90min.",
            "Use start_datetime/end_datetime only when you need second-level precision.",
            "Use either timespan or fixed date/date-time inputs, not both.",
        ),
    ))
    register_command(FinanceCommand(
        "news.analyze",
        "Analyze news volume, tone, context, or geography",
        _news_analyze,
        usage="news.analyze analysis=timeline|tone|context|geo|doc [query=TEXT | symbol=SYMBOL | sector=SECTOR] [mode=MODE max_records=50 timespan=30D|1W|1M|24H date=YYYY-MM-DD start_date=YYYY-MM-DD end_date=YYYY-MM-DD start_datetime=YYYYMMDDHHMMSS end_datetime=YYYYMMDDHHMMSS]",
        examples=(
            "finance news.analyze symbol=NVDA analysis=timeline timespan=1d",
            "finance news.analyze symbol=NVDA analysis=timeline timespan=1M",
            "finance news.analyze query='NVIDIA export controls' analysis=context max_records=5 timespan=24h",
            "finance news.analyze symbol=IOT analysis=timeline start_date=2026-03-03 end_date=2026-03-09",
            "finance news.analyze query=FOOD_SECURITY analysis=geo max_records=3 timespan=1h",
        ),
        notes=(
            "Use this only when you need trend, tone, context, geo, or raw DOC analysis.",
            "Use timespan for relative lookback from now, such as 30D, 1W, 1M, 24H, or 90min.",
            "date/start_date/end_date are preferred for humans and agents; datetime inputs are optional precision controls.",
        ),
    ))
