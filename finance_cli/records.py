"""Normalized finance records and generic agent renderers."""
from __future__ import annotations

import json
import re
from io import StringIO
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from rich.console import Console
from rich.table import Table

from finance_cli.schemas import Record


RecordFormat = Literal["json", "compact", "schema", "table"]


@dataclass(frozen=True)
class RecordRenderOptions:
    fields: tuple[str, ...] | None = None
    max_records: int | None = None
    max_chars: int | None = None
    omit_null: bool = True
    include_metadata: bool = False


class RecordAdapter(Protocol):
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        """Normalize a provider or command payload into records."""


class DictRecordAdapter:
    """Best-effort adapter for already record-like dict/list payloads."""

    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        return _records_from_payload(payload, command=command, base_context={})


class MarketQuoteRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        return [
            Record(
                entity=_entity_from_context(payload),
                kind="market_quote",
                fields=_fields_except(payload, {"symbol", "ticker", "source", "provider"}),
                source=_first_text(payload, SOURCE_KEYS),
            )
        ]


class MarketOhlcvRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        if isinstance(payload.get("symbols"), dict):
            records: list[Record] = []
            for symbol, entry in payload["symbols"].items():
                if isinstance(entry, dict):
                    context = {**payload, **entry, "symbol": symbol}
                    records.extend(_market_ohlcv_rows(context))
            return records
        return _market_ohlcv_rows(payload)


class NewsSearchRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        scope = payload.get("scope") if isinstance(payload.get("scope"), dict) else {}
        entity = _entity_from_context({"scope": scope})
        source = _first_text(payload, SOURCE_KEYS)
        records = []
        for article in payload.get("articles") or []:
            if not isinstance(article, dict):
                continue
            records.append(Record(
                entity=entity,
                kind="news_article",
                timestamp=_first_text(article, ("published_at", "seendate", "date", "datetime", "timestamp")),
                fields=dict(article),
                source=source,
                metadata=_adapter_metadata({"published_at": "timestamp", "seendate": "timestamp"}),
            ))
        return records


class FilingsRecentRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        source = _first_text(payload, SOURCE_KEYS)
        records = []
        for filing in payload.get("filings") or []:
            if isinstance(filing, dict):
                records.append(_filing_record(payload, filing, source=source))
        for event in payload.get("events") or []:
            if isinstance(event, dict):
                records.append(_filing_event_record(payload, event, source=source))
        return records


class FilingsStatementRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        filing = payload.get("filing") if isinstance(payload.get("filing"), dict) else {}
        source = _first_text(payload, SOURCE_KEYS)
        entity = _filing_entity(payload, filing)
        records = []
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            fields = {"statement": payload.get("statement"), **_fields_except(filing, set()), **row}
            records.append(Record(
                entity=entity,
                kind="filings_statement_row",
                period=_text_or_none(row.get("period") or filing.get("period_of_report")),
                timestamp=_text_or_none(filing.get("filing_date")),
                fields=fields,
                source=source,
                metadata=_adapter_metadata({"filing_date": "timestamp", "period": "period", "period_of_report": "period"}),
            ))
        return records


class CalendarEarningsRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        source = _first_text(payload, SOURCE_KEYS)
        records = []
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            records.append(Record(
                entity=_entity_from_context(payload),
                kind="earning",
                timestamp=_text_or_none(row.get("earnings_date")),
                fields=dict(row),
                source=source,
                metadata=_adapter_metadata({"earnings_date": "timestamp"}),
            ))
        return records


class TranscriptSearchRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        records = []
        for row in payload.get("transcripts") or []:
            if not isinstance(row, dict):
                continue
            records.append(Record(
                entity=_entity_from_context({**payload, **row}),
                kind="transcript",
                period=_text_or_none(row.get("quarter") or row.get("period")),
                timestamp=_text_or_none(row.get("published_at")),
                fields=dict(row),
                source=_first_text(row, SOURCE_KEYS) or _first_text(payload, SOURCE_KEYS),
                metadata=_adapter_metadata({"quarter": "period", "period": "period", "published_at": "timestamp"}),
            ))
        return records


class TranscriptReadRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        transcript = payload.get("transcript") if isinstance(payload.get("transcript"), dict) else {}
        fields = {**transcript, **_fields_except(payload, {"transcript", "source", "provider"})}
        return [Record(
            entity=_entity_from_context(payload),
            kind="transcript",
            period=_text_or_none(transcript.get("quarter") or payload.get("quarter")),
            timestamp=_text_or_none(transcript.get("published_at") or payload.get("date")),
            fields=fields,
            source=_first_text(payload, SOURCE_KEYS) or _first_text(transcript, SOURCE_KEYS),
            metadata=_adapter_metadata({"quarter": "period", "published_at": "timestamp", "date": "timestamp"}),
        )]


class KpiRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        records: list[Record] = []
        document_lookup = _document_lookup(payload.get("documents"))
        for row in payload.get("kpis") or []:
            if isinstance(row, dict):
                records.append(_kpi_record(payload, row, document_lookup))
        for group in payload.get("history") or []:
            if not isinstance(group, dict):
                continue
            group_lookup = _document_lookup(group.get("documents")) or document_lookup
            for row in group.get("kpis") or []:
                if isinstance(row, dict):
                    records.append(_kpi_record(payload, row, group_lookup))
        return records


class PriceMovesRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        context = _fields_except(payload, {"moves", "count", "notes", "source", "provider"})
        records = []
        for move in payload.get("moves") or []:
            if not isinstance(move, dict):
                continue
            fields = {**context, **move}
            records.append(Record(
                entity=_entity_from_context({**payload, **move}),
                kind="price_move",
                period=_text_or_none(move.get("start_date")),
                timestamp=_text_or_none(move.get("end_date")),
                fields=fields,
                source=_first_text(move, SOURCE_KEYS) or _first_text(payload, SOURCE_KEYS),
                metadata=_adapter_metadata({"start_date": "period", "end_date": "timestamp"}),
            ))
        return records


class PriceContextRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        context = _fields_except(payload, {"timeline", "count", "notes", "warnings"})
        records = []
        for event in payload.get("timeline") or []:
            if not isinstance(event, dict):
                continue
            fields = {**context, **event}
            records.append(Record(
                entity=_entity_from_context(payload),
                kind=f"price_context_{event.get('source_type') or 'event'}",
                timestamp=_text_or_none(event.get("date")),
                fields=fields,
                source=_text_or_none(event.get("source_type")),
                metadata=_adapter_metadata({"date": "timestamp"}),
            ))
        return records


class EstimatesConsensusRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        source = _first_text(payload, SOURCE_KEYS)
        records = []
        for row in payload.get("estimates") or []:
            if not isinstance(row, dict):
                continue
            period = _first_text(row, ("date", "period", "fiscalDateEnding")) or _text_or_none(payload.get("period"))
            records.append(Record(
                entity=_entity_from_context(payload),
                kind="consensus_estimate",
                period=period,
                fields={**_fields_except(payload, {"symbol", "ticker", "estimates", "count", "source", "provider"}), **row},
                source=source,
                metadata=_adapter_metadata({"date": "period", "fiscalDateEnding": "period"}),
            ))
        return records


class ScreenRunRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        context = _fields_except(payload, {"quotes", "count", "total", "source", "provider"})
        source = _first_text(payload, SOURCE_KEYS)
        records = []
        for quote in payload.get("quotes") or []:
            if not isinstance(quote, dict):
                continue
            records.append(Record(
                entity=_entity_from_context(quote),
                kind="screen_quote",
                fields={**context, **quote},
                source=source,
            ))
        return records


class OwnershipHoldersRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        records: list[Record] = []
        source = _first_text(payload, SOURCE_KEYS)
        for section in (
            "major_holders",
            "institutional_holders",
            "mutualfund_holders",
            "insider_transactions",
            "insider_purchases",
            "insider_roster_holders",
        ):
            for row in payload.get(section) or []:
                if not isinstance(row, dict):
                    continue
                records.append(Record(
                    entity=_entity_from_context(payload),
                    kind=section[:-1] if section.endswith("s") else section,
                    timestamp=_first_text(row, ("date_reported", "start_date", "latest_transaction_date")),
                    fields={"section": section, **row},
                    source=source,
                    metadata=_adapter_metadata({
                        "date_reported": "timestamp",
                        "start_date": "timestamp",
                        "latest_transaction_date": "timestamp",
                    }),
                ))
        return records


class FundamentalsGrowthRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        records = []
        source = _first_text(payload, SOURCE_KEYS)
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            kind = {
                "history": "fundamental_history",
                "delta": "fundamental_delta",
            }.get(row.get("kind"), "fundamental_growth")
            records.append(Record(
                entity=_entity_from_context({**payload, **row}),
                kind=kind,
                period=_text_or_none(row.get("period")),
                fields=_fields_except(row, {"kind", "symbol", "ticker", "source", "provider"}),
                source=_first_text(row, SOURCE_KEYS) or source,
            ))
        return records


class PriceRelativeRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        records = []
        source = _first_text(payload, SOURCE_KEYS)
        for row in payload.get("relative_performance") or []:
            if not isinstance(row, dict):
                continue
            records.append(Record(
                entity=_entity_from_context({**payload, **row}),
                kind="relative_price",
                period=_text_or_none(row.get("period")),
                fields=_fields_except(row, {"symbol", "ticker", "period", "source", "provider"}),
                source=_first_text(row, SOURCE_KEYS) or source,
            ))
        return records


class MarketTrendRecordAdapter:
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        if not isinstance(payload, dict):
            return DictRecordAdapter().to_records(payload, command=command)
        records = []
        source = _first_text(payload, SOURCE_KEYS)
        for row in payload.get("trend") or []:
            if not isinstance(row, dict):
                continue
            records.append(Record(
                entity=_entity_from_context(row),
                kind=str(row.get("kind") or "market_trend"),
                fields=_fields_except(row, {"kind", "symbol", "ticker", "source", "provider"}),
                source=_first_text(row, SOURCE_KEYS) or source,
            ))
        return records


ENTITY_KEYS = ("entity", "symbol", "ticker", "market")
PERIOD_KEYS = ("period",)
TIMESTAMP_KEYS = ("timestamp",)
SOURCE_KEYS = ("source", "provider")
COMMAND_RECORD_ADAPTERS: dict[str, RecordAdapter] = {
    "calendar.earnings": CalendarEarningsRecordAdapter(),
    "estimates.consensus": EstimatesConsensusRecordAdapter(),
    "fundamentals.growth": FundamentalsGrowthRecordAdapter(),
    "market.trend": MarketTrendRecordAdapter(),
    "market.quote": MarketQuoteRecordAdapter(),
    "market.ohlcv": MarketOhlcvRecordAdapter(),
    "news.search": NewsSearchRecordAdapter(),
    "ownership.holders": OwnershipHoldersRecordAdapter(),
    "filings.recent": FilingsRecentRecordAdapter(),
    "filings.statement": FilingsStatementRecordAdapter(),
    "kpi.extract": KpiRecordAdapter(),
    "kpi.history": KpiRecordAdapter(),
    "price.context": PriceContextRecordAdapter(),
    "price.moves": PriceMovesRecordAdapter(),
    "price.relative": PriceRelativeRecordAdapter(),
    "screen.run": ScreenRunRecordAdapter(),
    "transcripts.read": TranscriptReadRecordAdapter(),
    "transcripts.search": TranscriptSearchRecordAdapter(),
}
LIST_CONTAINER_KEYS = {
    "records",
    "rows",
    "filings",
    "events",
    "articles",
    "transcripts",
    "estimates",
    "earnings",
    "moves",
    "timeline",
    "matches",
    "reports",
    "sections",
    "presentations",
    "quotes",
    "results",
    "sources",
    "queries",
    "industries",
    "companies",
    "holdings",
    "funds",
    "etfs",
    "qa_pairs",
}
GROUP_CONTAINER_KEYS = {"symbols"}
NESTED_CONTAINER_KEYS = {"payload", "data", "result"}
NON_FIELD_KEYS = {
    "entity",
    "symbol",
    "ticker",
    "kind",
    "period",
    "timestamp",
    "source",
    "provider",
    "metadata",
    "scope",
    "count",
    "total",
    "warnings",
}
DEFAULT_MAX_FIELD_CHARS = 240
FIELD_ALIASES_METADATA_KEY = "field_aliases"


def normalize_records(payload: Any, *, command: str | None = None, adapter: RecordAdapter | None = None) -> list[Record]:
    """Normalize a command payload into a list of finance records."""
    normalizer = adapter or (COMMAND_RECORD_ADAPTERS.get(command or "") or DictRecordAdapter())
    return normalizer.to_records(payload, command=command)


def render_records(records: list[Record], output: RecordFormat, options: RecordRenderOptions | None = None) -> str:
    """Render normalized records without API-specific formatting code."""
    opts = options or RecordRenderOptions()
    selected = _select_records(records, opts)
    if output == "json":
        rendered = _render_records_json(selected, opts)
    elif output == "compact":
        rendered = _render_compact(selected, opts)
    elif output == "schema":
        rendered = _render_schema_rows(selected, opts)
    elif output == "table":
        rendered = _render_table(selected, opts)
    else:
        raise ValueError(f"unknown record output format: {output}")
    return _cap_chars(rendered, opts.max_chars)


def _market_ohlcv_rows(payload: dict[str, Any]) -> list[Record]:
    rows = payload.get("rows") or []
    source = _first_text(payload, SOURCE_KEYS)
    records = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        fields = {**_fields_except(payload, {"symbol", "ticker", "symbols", "rows", "count", "source", "provider"}), **row}
        records.append(Record(
            entity=_entity_from_context(payload),
            kind="market_ohlcv_row",
            timestamp=_text_or_none(row.get("date")),
            fields=fields,
            source=source,
            metadata=_adapter_metadata({"date": "timestamp"}),
        ))
    return records


def _filing_record(context: dict[str, Any], filing: dict[str, Any], *, source: str | None) -> Record:
    fields = {**_fields_except(context, {"symbol", "ticker", "filings", "events", "count", "source", "provider"}), **filing}
    return Record(
        entity=_entity_from_context(context),
        kind="filing",
        period=_text_or_none(filing.get("report_date") or filing.get("period_of_report")),
        timestamp=_text_or_none(filing.get("filing_date") or filing.get("filed_at")),
        fields=fields,
        source=source,
        metadata=_adapter_metadata({"report_date": "period", "period_of_report": "period", "filing_date": "timestamp", "filed_at": "timestamp"}),
    )


def _filing_event_record(context: dict[str, Any], event: dict[str, Any], *, source: str | None) -> Record:
    fields = {**_fields_except(context, {"symbol", "ticker", "filings", "events", "count", "source", "provider"}), **event}
    return Record(
        entity=_entity_from_context(context),
        kind=str(event.get("kind") or event.get("event_type") or "filing_event"),
        period=_text_or_none(event.get("report_date") or event.get("period_of_report")),
        timestamp=_text_or_none(event.get("filing_date") or event.get("filed_at") or event.get("date")),
        fields=fields,
        source=source,
        metadata=_adapter_metadata({"report_date": "period", "period_of_report": "period", "filing_date": "timestamp", "filed_at": "timestamp", "date": "timestamp"}),
    )


def _filing_entity(payload: dict[str, Any], filing: dict[str, Any]) -> str:
    symbol = _text_or_none(payload.get("symbol") or filing.get("symbol"))
    if symbol:
        return symbol.upper()
    return _text_or_none(filing.get("company") or filing.get("accession_no")) or "record"


def _document_lookup(documents: Any) -> dict[Any, dict[str, Any]]:
    if not isinstance(documents, list):
        return {}
    lookup = {}
    for document in documents:
        if not isinstance(document, dict):
            continue
        doc_ref = document.get("doc_ref")
        if doc_ref is not None:
            lookup[doc_ref] = document
    return lookup


def _kpi_record(payload: dict[str, Any], row: dict[str, Any], document_lookup: dict[Any, dict[str, Any]]) -> Record:
    document = document_lookup.get(row.get("doc_ref"), {})
    value = row.get("value") if isinstance(row.get("value"), dict) else {}
    document_fields = {f"document_{key}": value for key, value in document.items() if key != "doc_ref"}
    fields = {**document_fields, **row}
    if value:
        fields.setdefault("value_raw", value.get("raw"))
        fields.setdefault("value_number", value.get("number"))
        fields.setdefault("currency", value.get("currency"))
    return Record(
        entity=_entity_from_context({**payload, **document}),
        kind="kpi",
        period=_text_or_none(row.get("period") or document.get("period") or document.get("quarter")),
        timestamp=_text_or_none(document.get("published_at")),
        fields=fields,
        source=_first_text(document, SOURCE_KEYS) or _first_text(payload, SOURCE_KEYS),
        metadata=_adapter_metadata({"period": "period", "quarter": "period", "published_at": "timestamp"}),
    )


def _fields_except(mapping: dict[str, Any], excluded: set[str]) -> dict[str, Any]:
    return {key: value for key, value in mapping.items() if key not in excluded}


def _adapter_metadata(field_aliases: dict[str, str]) -> dict[str, Any]:
    return {FIELD_ALIASES_METADATA_KEY: field_aliases}


def _records_from_payload(payload: Any, *, command: str | None, base_context: dict[str, Any]) -> list[Record]:
    if payload is None:
        return []
    if isinstance(payload, Record):
        return [payload]
    if isinstance(payload, list):
        records: list[Record] = []
        for item in payload:
            records.extend(_records_from_payload(item, command=command, base_context=base_context))
        return records
    if isinstance(payload, dict):
        return _records_from_mapping(payload, command=command, base_context=base_context)
    return [Record(entity=_entity_from_context(base_context), kind=_command_kind(command), fields={"value": payload})]


def _records_from_mapping(mapping: dict[str, Any], *, command: str | None, base_context: dict[str, Any]) -> list[Record]:
    if _looks_like_record(mapping):
        return [_record_from_normalized(mapping)]

    records: list[Record] = []
    context = {**base_context, **_context_values(mapping)}

    for key, value in mapping.items():
        if key in GROUP_CONTAINER_KEYS and isinstance(value, dict):
            for group_name, group_payload in value.items():
                group_ctx = dict(context)
                group_ctx["symbol"] = group_ctx.get("symbol", group_name)
                records.extend(_records_from_payload(group_payload, command=command, base_context=group_ctx))

    for key in NESTED_CONTAINER_KEYS:
        value = mapping.get(key)
        if isinstance(value, dict):
            records.extend(_records_from_mapping(value, command=command, base_context=context))

    for key, value in mapping.items():
        if key in GROUP_CONTAINER_KEYS or key in NESTED_CONTAINER_KEYS:
            continue
        if not isinstance(value, list) or not value:
            continue
        if key not in LIST_CONTAINER_KEYS and not all(isinstance(item, dict) for item in value):
            continue
        row_kind = _collection_kind(key, command)
        for item in value:
            if isinstance(item, dict):
                if _looks_like_record(item):
                    records.append(_record_from_normalized(item))
                else:
                    records.append(_record_from_mapping_row(item, command=command, base_context=context, kind=row_kind))

    if records:
        return records
    return [_record_from_mapping_row(mapping, command=command, base_context=base_context, kind=_command_kind(command))]


def _record_from_mapping_row(
    mapping: dict[str, Any],
    *,
    command: str | None,
    base_context: dict[str, Any],
    kind: str,
) -> Record:
    merged = {**base_context, **mapping}
    entity = _entity_from_context(merged)
    record_kind = str(mapping.get("kind") or kind or _command_kind(command))
    period = _first_text(merged, PERIOD_KEYS)
    timestamp = _first_text(merged, TIMESTAMP_KEYS)
    source = _first_text(merged, SOURCE_KEYS)
    fields = {
        key: value
        for key, value in merged.items()
        if key not in NON_FIELD_KEYS and key not in LIST_CONTAINER_KEYS and key not in GROUP_CONTAINER_KEYS and key not in NESTED_CONTAINER_KEYS
    }
    metadata = mapping.get("metadata") if isinstance(mapping.get("metadata"), dict) else None
    if metadata is None and isinstance(merged.get("scope"), dict):
        metadata = {"scope": merged["scope"]}
    return Record(
        entity=entity,
        kind=record_kind,
        period=period,
        timestamp=timestamp,
        fields=fields,
        source=source,
        metadata=metadata,
    )


def _looks_like_record(mapping: dict[str, Any]) -> bool:
    return isinstance(mapping.get("fields"), dict) and "entity" in mapping and "kind" in mapping


def _record_from_normalized(mapping: dict[str, Any]) -> Record:
    return Record(
        entity=str(mapping["entity"]),
        kind=str(mapping["kind"]),
        period=_text_or_none(mapping.get("period")),
        timestamp=_text_or_none(mapping.get("timestamp")),
        fields=dict(mapping.get("fields") or {}),
        source=_text_or_none(mapping.get("source")),
        metadata=dict(mapping["metadata"]) if isinstance(mapping.get("metadata"), dict) else None,
    )


def _context_values(mapping: dict[str, Any]) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for key, value in mapping.items():
        if key in LIST_CONTAINER_KEYS or key in GROUP_CONTAINER_KEYS or key in NESTED_CONTAINER_KEYS:
            continue
        if _is_simple(value) or key == "scope":
            context[key] = value
    return context


def _entity_from_context(ctx: dict[str, Any]) -> str:
    for key in ENTITY_KEYS:
        value = _text_or_none(ctx.get(key))
        if value:
            return value.upper() if key in {"symbol", "ticker"} else value
    scope = ctx.get("scope")
    if isinstance(scope, dict):
        value = _text_or_none(scope.get("value"))
        if value:
            return value.upper() if scope.get("type") == "symbol" else value
    return "record"


def _first_text(mapping: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = _text_or_none(mapping.get(key))
        if value:
            return value
    return None


def _text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _is_simple(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _command_kind(command: str | None) -> str:
    return (command or "record").replace(".", "_")


def _collection_kind(key: str, command: str | None) -> str:
    if key == "rows" and command:
        return f"{_command_kind(command)}_row"
    if key == "articles":
        return "news_article"
    if key == "qa_pairs":
        return "transcript_qa"
    if key.endswith("ies"):
        return key[:-3] + "y"
    if key.endswith("s") and len(key) > 1:
        return key[:-1]
    return key


def _select_records(records: list[Record], options: RecordRenderOptions) -> list[Record]:
    if options.max_records is not None and options.max_records >= 0:
        return records[: options.max_records]
    return records


def _render_records_json(records: list[Record], options: RecordRenderOptions) -> str:
    payload = [_record_dict(record, options) for record in records]
    return json.dumps(payload, ensure_ascii=False, default=str, allow_nan=False, separators=(",", ":"))


def _record_dict(record: Record, options: RecordRenderOptions) -> dict[str, Any]:
    payload = record.to_dict(omit_null=options.omit_null, include_metadata=options.include_metadata)
    payload["fields"] = dict(_field_pairs(record, options, include_large=bool(options.fields)))
    return payload


def _render_compact(records: list[Record], options: RecordRenderOptions) -> str:
    if not records:
        return ""
    lines = []
    for record in records:
        parts = [_clean_text(record.entity), _clean_text(record.kind)]
        if record.period:
            parts.append(_clean_text(record.period))
        if record.timestamp:
            parts.append(_clean_text(record.timestamp))
        parts.extend(f"{key}={_value_text(value)}" for key, value in _field_pairs(record, options))
        if record.source:
            parts.append(f"src={_clean_text(record.source)}")
        if options.include_metadata and record.metadata:
            parts.append(f"meta={_value_text(record.metadata)}")
        lines.append("|".join(part for part in parts if part != ""))
    return "\n".join(lines)


def _render_schema_rows(records: list[Record], options: RecordRenderOptions) -> str:
    if not records:
        return ""
    columns = _schema_columns(records, options)
    lines = ["schema|" + "|".join(columns)]
    for record in records:
        lines.append("row|" + "|".join(_record_schema_row(record, columns, options)))
    return "\n".join(lines)


def _render_table(records: list[Record], options: RecordRenderOptions) -> str:
    if not records:
        return ""
    columns = _schema_columns(records, options)
    table = Table(show_header=True, header_style="bold")
    for column in columns:
        table.add_column(_title_column(column), overflow="fold")
    for record in records:
        table.add_row(*_record_schema_row(record, columns, options))
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None, width=120)
    console.print(table)
    return buffer.getvalue().rstrip()


def _schema_columns(records: list[Record], options: RecordRenderOptions) -> list[str]:
    selected_structural = _selected_structural_fields(records, options)
    structural = ["entity", "kind"]
    structural.extend(
        key
        for key in ("period", "timestamp", "source")
        if key not in selected_structural and any(getattr(record, key) for record in records)
    )
    return _dedupe_columns(structural + list(options.fields or _ordered_field_names(records, options)))


def _title_column(column: str) -> str:
    return column.replace("_", " ").title()


def _record_schema_row(record: Record, columns: list[str], options: RecordRenderOptions) -> list[str]:
    fields = dict(_field_pairs(record, options, include_large=bool(options.fields)))
    values = {
        "entity": record.entity,
        "kind": record.kind,
        "period": record.period,
        "timestamp": record.timestamp,
        "source": record.source,
        **fields,
    }
    return [_value_text(_schema_value(record, values, column)) for column in columns]


def _schema_value(record: Record, values: dict[str, Any], column: str) -> Any:
    value = values.get(column)
    if value is not None:
        return value
    structural_key = _field_aliases(record).get(column)
    if structural_key:
        return getattr(record, structural_key)
    return None


def _selected_structural_fields(records: list[Record], options: RecordRenderOptions) -> set[str]:
    selected: set[str] = set()
    for field in options.fields or ():
        if field in {"period", "timestamp", "source"}:
            selected.add(field)
        for record in records:
            target = _field_aliases(record).get(field)
            if target in {"period", "timestamp", "source"}:
                selected.add(target)
    return selected


def _field_aliases(record: Record) -> dict[str, str]:
    if not isinstance(record.metadata, dict):
        return {}
    aliases = record.metadata.get(FIELD_ALIASES_METADATA_KEY)
    if not isinstance(aliases, dict):
        return {}
    return {str(key): str(value) for key, value in aliases.items()}


def _dedupe_columns(columns: list[str]) -> list[str]:
    deduped: list[str] = []
    for column in columns:
        if column not in deduped:
            deduped.append(column)
    return deduped


def _ordered_field_names(records: list[Record], options: RecordRenderOptions) -> tuple[str, ...]:
    names: list[str] = []
    for record in records:
        for key, _value in _field_pairs(record, options):
            if key not in names:
                names.append(key)
    return tuple(names)


def _field_pairs(record: Record, options: RecordRenderOptions, *, include_large: bool = False) -> tuple[tuple[str, Any], ...]:
    selected = set(options.fields or ())
    pairs: list[tuple[str, Any]] = []
    for key, value in record.fields.items():
        if selected and key not in selected:
            continue
        if options.omit_null and value is None:
            continue
        if not include_large and _is_large_value(value):
            continue
        pairs.append((key, value))
    return tuple(pairs)


def _is_large_value(value: Any) -> bool:
    return len(_value_text(value)) > DEFAULT_MAX_FIELD_CHARS


def _value_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, default=str, allow_nan=False, separators=(",", ":"))
    else:
        text = str(value)
    return _clean_text(text)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip().replace("|", "\\|")


def _cap_chars(text: str, max_chars: int | None) -> str:
    if max_chars is None or max_chars < 0 or len(text) <= max_chars:
        return text
    suffix = "\n...truncated"
    if max_chars <= len(suffix):
        return text[:max_chars]
    return text[: max_chars - len(suffix)].rstrip() + suffix
