"""Earnings-call transcript CLI commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.transcripts import read_transcript, search_transcripts, transcript_qa


def _split_subject(args: list[str]) -> tuple[str | None, KVArgs]:
    if args and "=" not in args[0]:
        return args[0], KVArgs(args[1:])
    return None, KVArgs(args)


def _transcripts_search(args: list[str]) -> FinanceCommandResult:
    if not args:
        return FinanceCommandResult(ok=False, error="usage: transcripts.search SYMBOL [limit=4 debug=false]")
    kv = KVArgs(args[1:])
    data = search_transcripts(args[0], limit=kv.int("limit", 4), debug=kv.bool("debug"))
    return FinanceCommandResult(ok=True, data=data)


def _transcripts_read(args: list[str]) -> FinanceCommandResult:
    symbol, kv = _split_subject(args)
    url = kv.str("url")
    if not symbol and not url:
        return FinanceCommandResult(ok=False, error="usage: transcripts.read [SYMBOL] [url=URL] [quarter=latest max_chars=12000]")
    data = read_transcript(
        symbol,
        url=url,
        quarter=kv.str("quarter", "latest"),
        max_chars=kv.int("max_chars", 12000),
        include_turns=kv.bool("include_turns"),
    )
    return FinanceCommandResult(ok=True, data=data)


def _transcripts_qa(args: list[str]) -> FinanceCommandResult:
    symbol, kv = _split_subject(args)
    url = kv.str("url")
    if not symbol and not url:
        return FinanceCommandResult(ok=False, error="usage: transcripts.qa [SYMBOL] [url=URL] [quarter=latest limit=10]")
    data = transcript_qa(
        symbol,
        url=url,
        quarter=kv.str("quarter", "latest"),
        limit=kv.int("limit", 10),
    )
    return FinanceCommandResult(ok=True, data=data)


def register_transcript_commands() -> None:
    register_command(FinanceCommand(
        "transcripts.search",
        "Search public earnings-call transcripts",
        _transcripts_search,
        usage="transcripts.search SYMBOL [limit=4 debug=false]",
        examples=("finance transcripts.search IOT limit=4", "finance transcripts.search IOT debug=true"),
        notes=("Uses public Motley Fool transcript pages when available.",),
    ))
    register_command(FinanceCommand(
        "transcripts.read",
        "Read a transcript and split prepared remarks / Q&A",
        _transcripts_read,
        usage="transcripts.read [SYMBOL] [url=URL] [quarter=latest max_chars=12000 include_turns=false]",
        examples=(
            "finance transcripts.read IOT quarter=latest max_chars=4000",
            "finance transcripts.read IOT include_turns=true max_chars=2000",
            "finance transcripts.read url=https://www.fool.com/earnings/call-transcripts/2026/03/05/samsara-iot-q4-2026-earnings-call-transcript/",
        ),
    ))
    register_command(FinanceCommand(
        "transcripts.qa",
        "Extract analyst Q&A pairs from a transcript",
        _transcripts_qa,
        usage="transcripts.qa [SYMBOL] [url=URL] [quarter=latest limit=10]",
        examples=("finance transcripts.qa IOT quarter=latest limit=5",),
    ))
