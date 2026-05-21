"""Normalized finance records and generic agent renderers."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from finance_cli.schemas import Record


RecordFormat = Literal["json", "compact", "schema"]


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
    """Best-effort adapter for existing dict/list Finance CLI payloads."""

    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        return _records_from_payload(payload, command=command, base_context={})


ENTITY_KEYS = ("entity", "symbol", "ticker", "market")
PERIOD_KEYS = ("period", "fiscal_period", "quarter", "fiscal_year", "year")
TIMESTAMP_KEYS = ("timestamp", "datetime", "published_at", "seendate", "date", "filing_date", "report_date", "earnings_date")
SOURCE_KEYS = ("source", "provider")
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
    "fiscal_period",
    "quarter",
    "fiscal_year",
    "year",
    "timestamp",
    "datetime",
    "published_at",
    "seendate",
    "date",
    "filing_date",
    "report_date",
    "earnings_date",
    "source",
    "provider",
    "metadata",
    "scope",
    "count",
    "total",
    "warnings",
}
DEFAULT_MAX_FIELD_CHARS = 240


def normalize_records(payload: Any, *, command: str | None = None, adapter: RecordAdapter | None = None) -> list[Record]:
    """Normalize a command payload into a list of finance records."""
    normalizer = adapter or DictRecordAdapter()
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
    else:
        raise ValueError(f"unknown record output format: {output}")
    return _cap_chars(rendered, opts.max_chars)


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


def _schema_columns(records: list[Record], options: RecordRenderOptions) -> list[str]:
    structural = ["entity", "kind"]
    structural.extend(key for key in ("period", "timestamp", "source") if any(getattr(record, key) for record in records))
    return structural + list(options.fields or _ordered_field_names(records, options))


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
    return [_value_text(values.get(column)) for column in columns]


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
