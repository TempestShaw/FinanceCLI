"""Earnings-call transcript services."""
from __future__ import annotations

from typing import Any

from finance_cli.providers.transcripts import MotleyFoolTranscriptProvider


def search_transcripts(
    symbol: str,
    *,
    limit: int = 4,
    debug: bool = False,
    provider: MotleyFoolTranscriptProvider | None = None,
) -> dict[str, Any]:
    """Search public earnings-call transcripts for a symbol."""
    client = provider or MotleyFoolTranscriptProvider()
    return client.search(symbol, limit=limit, debug=debug)


def read_transcript(
    symbol: str | None = None,
    *,
    url: str | None = None,
    quarter: str = "latest",
    max_chars: int = 12000,
    include_turns: bool = False,
    provider: MotleyFoolTranscriptProvider | None = None,
) -> dict[str, Any]:
    """Read a transcript by symbol or URL."""
    client = provider or MotleyFoolTranscriptProvider()
    return client.read(symbol, url=url, quarter=quarter, max_chars=max_chars, include_turns=include_turns)


def transcript_qa(
    symbol: str | None = None,
    *,
    url: str | None = None,
    quarter: str = "latest",
    limit: int = 10,
    provider: MotleyFoolTranscriptProvider | None = None,
) -> dict[str, Any]:
    """Extract analyst Q&A pairs from a transcript."""
    client = provider or MotleyFoolTranscriptProvider()
    return client.qa(symbol, url=url, quarter=quarter, limit=limit)
