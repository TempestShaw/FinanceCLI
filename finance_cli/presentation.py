"""Declarative presentation layer for finance command results.

A :class:`Presentation` is a small, immutable description of *what to show* for a
command result: a one-line ``headline`` (the answer), zero or more ``blocks`` of
supporting detail, and provenance (``source`` / ``as_of``). Renderers turn the
same spec into different surfaces (markdown, plain text) so the human view and
the LLM view never diverge in content -- only in styling.

The spec is intentionally separate from the services that compute results: a
presenter is registered per command (or command namespace) and reads the plain
``data`` dict, mirroring the record-adapter pattern in :mod:`finance_cli.records`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

__all__ = [
    "KeyValue",
    "Block",
    "Presentation",
    "present",
    "register_presenter",
    "scalar_metrics",
    "render_markdown",
    "render_plain",
    "humanize_number",
    "humanize_value",
    "humanize_label",
]


# --------------------------------------------------------------------------- #
# Spec
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class KeyValue:
    label: str
    value: str


@dataclass(frozen=True)
class Block:
    """One section of a presentation: a key/value list, a table, or free text."""

    title: str | None = None
    keyvalues: tuple[KeyValue, ...] = ()
    columns: tuple[str, ...] = ()
    rows: tuple[tuple[str, ...], ...] = ()
    text: str | None = None

    @property
    def is_table(self) -> bool:
        return bool(self.columns)


@dataclass(frozen=True)
class Presentation:
    headline: str
    blocks: tuple[Block, ...] = ()
    source: str | None = None
    as_of: str | None = None
    notes: tuple[str, ...] = ()


Presenter = Callable[[str | None, dict[str, Any]], Presentation | None]


# --------------------------------------------------------------------------- #
# Humanization
# --------------------------------------------------------------------------- #
_SKIP_FIELD_KEYS = {
    "inputs",
    "method",
    "warnings",
    "weights",
    "meta",
    "source",
    "provider",
    "as_of",
    "notes",
    "symbol",
    "ticker",
    "entity",
    "display",
}
# Keys whose value is a 0-1 ratio that humans read as a percentage.
_RATIO_PERCENT_KEYS = {
    "margin",
    "roic",
    "roe",
    "roa",
    "wacc",
    "cagr",
    "cost_of_equity",
    "cost_of_debt",
    "ratio",
    "growth",
    "yield",
    "tax_rate",
    "percent_revenue",
    "risk_free",
    "market_return",
    "beta",  # not a percent; excluded below
}
_NOT_PERCENT = {"beta"}


_ACRONYMS = {
    "wacc", "cagr", "roic", "roe", "roa", "ev", "ebitda", "ebit", "eps",
    "npv", "irr", "capm", "dcf", "fcf", "pe", "ps", "vix", "sma", "ma", "yoy", "ttm",
}


def humanize_label(key: str) -> str:
    words = str(key).replace("_", " ").strip().split()
    return " ".join(word.upper() if word.lower() in _ACRONYMS else word for word in words)


def humanize_number(value: float | int) -> str:
    """Format a number with thousands separators and trimmed decimals.

    Precision is preserved (no lossy ``B``/``M`` compaction) so the same text is
    safe for both a human reader and an LLM parsing the value back out.
    """
    number = float(value)
    if number != number or number in (float("inf"), float("-inf")):  # NaN / inf
        return str(value)
    if number.is_integer() and abs(number) < 1e15:
        return f"{int(number):,}"
    text = f"{number:,.4f}".rstrip("0").rstrip(".")
    return text or "0"


def format_percent(value: float | int) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return str(value)


def humanize_value(value: Any, *, key: str | None = None) -> str:
    """Render a single field value for a human/LLM-readable view."""
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        if key and key.endswith("_pct"):
            return format_percent(value)
        if key and key in _RATIO_PERCENT_KEYS and key not in _NOT_PERCENT:
            return format_percent(float(value) * 100)
        return humanize_number(value)
    if isinstance(value, (list, tuple)):
        return ", ".join(humanize_value(item) for item in value) or "-"
    if isinstance(value, dict):
        return ", ".join(f"{humanize_label(k)} {humanize_value(v, key=k)}" for k, v in value.items()) or "-"
    return str(value)


# --------------------------------------------------------------------------- #
# Default presenter (data-driven, generic across commands)
# --------------------------------------------------------------------------- #
def _entity_prefix(data: dict[str, Any]) -> str:
    for key in ("symbol", "ticker", "entity", "company", "company_name", "market"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().upper() if key in {"symbol", "ticker"} else value.strip()
    return ""


def _scalar_metrics(data: dict[str, Any]) -> list[tuple[str, str]]:
    """Ordered (label, value) for top-level scalar metrics.

    A ``{base}`` / ``{base}_pct`` pair is collapsed into a single percent metric.
    """
    pct_bases = {key[: -len("_pct")] for key in data if key.endswith("_pct")}
    metrics: list[tuple[str, str]] = []
    for key, value in data.items():
        if key in _SKIP_FIELD_KEYS or not _is_scalar(value):
            continue
        if key.endswith("_pct"):
            base = key[: -len("_pct")]
            if base in data:
                continue  # rendered via the base key below
            metrics.append((humanize_label(base), format_percent(value)))
            continue
        if key in pct_bases:
            metrics.append((humanize_label(key), format_percent(data[f"{key}_pct"])))
            continue
        metrics.append((humanize_label(key), humanize_value(value, key=key)))
    return metrics


def default_presentation(command: str | None, data: dict[str, Any]) -> Presentation | None:
    """Build a presentation for a scalar/object result.

    Returns ``None`` for list-shaped payloads (filings, holders, ohlcv, ...),
    which are better served by the existing normalized-record table renderer.
    """
    if not isinstance(data, dict):
        return None
    if _has_record_collection(data):
        return None

    metrics = _scalar_metrics(data)
    if not metrics:
        return None

    prefix = _entity_prefix(data)
    head_label, head_value = metrics[0]
    headline = f"{prefix} {head_label} = {head_value}".strip()

    blocks: list[Block] = []
    if len(metrics) > 1:
        blocks.append(Block(keyvalues=tuple(KeyValue(label, value) for label, value in metrics)))

    inputs = data.get("inputs")
    if isinstance(inputs, dict) and inputs:
        blocks.append(Block(
            title="Inputs",
            keyvalues=tuple(KeyValue(humanize_label(k), humanize_value(v, key=k)) for k, v in inputs.items()),
        ))

    weights = data.get("weights")
    if isinstance(weights, dict) and weights:
        blocks.append(Block(
            title="Weights",
            keyvalues=tuple(KeyValue(humanize_label(k), format_percent(float(v) * 100)) for k, v in weights.items()),
        ))

    notes: list[str] = []
    method = data.get("method")
    if isinstance(method, str) and method.strip():
        notes.append(f"method: {method.strip()}")
    for warning in data.get("warnings") or []:
        notes.append(str(warning))

    return Presentation(
        headline=headline,
        blocks=tuple(blocks),
        source=_first_str(data, ("source", "provider")),
        as_of=_meta_field(data, "as_of"),
        notes=tuple(notes),
    )


# --------------------------------------------------------------------------- #
# Dispatch
# --------------------------------------------------------------------------- #
_EXACT_PRESENTERS: dict[str, Presenter] = {}
_PREFIX_PRESENTERS: dict[str, Presenter] = {}


def register_presenter(command: str, presenter: Presenter, *, prefix: bool = False) -> None:
    """Register a presenter for an exact command name or a namespace prefix."""
    (_PREFIX_PRESENTERS if prefix else _EXACT_PRESENTERS)[command] = presenter


def scalar_metrics(data: Any) -> list[tuple[str, str]]:
    """Public view of a result's top-level scalar metrics as (label, value)."""
    return _scalar_metrics(data) if isinstance(data, dict) else []


def present(command: str | None, data: Any) -> Presentation | None:
    """Resolve and run the presenter for ``command`` over ``data``."""
    if not isinstance(data, dict):
        return None
    presenter = _EXACT_PRESENTERS.get(command or "")
    if presenter is None and command:
        namespace = command.split(".", 1)[0]
        presenter = _PREFIX_PRESENTERS.get(namespace)
    presenter = presenter or default_presentation
    return presenter(command, data)


# --------------------------------------------------------------------------- #
# Renderers
# --------------------------------------------------------------------------- #
def render_markdown(presentation: Presentation) -> str:
    """GitHub-flavored markdown: ideal for LLMs, docs, and markdown terminals."""
    lines: list[str] = [f"**{presentation.headline}**"]
    for block in presentation.blocks:
        lines.append("")
        if block.title:
            lines.append(f"_{block.title}_")
        if block.is_table:
            lines.extend(_markdown_table(block.columns, block.rows))
        elif block.keyvalues:
            lines.extend(_markdown_table(("Field", "Value"), tuple((kv.label, kv.value) for kv in block.keyvalues)))
        if block.text:
            lines.append(block.text)
    for note in presentation.notes:
        lines.append("")
        lines.append(note)
    footer = _provenance(presentation)
    if footer:
        lines.append("")
        lines.append(f"_{footer}_")
    return "\n".join(lines).rstrip()


def render_plain(presentation: Presentation) -> str:
    """Aligned plain text for non-markdown terminals."""
    lines: list[str] = [presentation.headline]
    for block in presentation.blocks:
        lines.append("")
        if block.title:
            lines.append(f"{block.title}:")
        if block.is_table:
            lines.extend(_aligned_rows([block.columns, *block.rows]))
        elif block.keyvalues:
            lines.extend(_aligned_rows([(kv.label, kv.value) for kv in block.keyvalues]))
        if block.text:
            lines.append(block.text)
    for note in presentation.notes:
        lines.append("")
        lines.append(note)
    footer = _provenance(presentation)
    if footer:
        lines.append("")
        lines.append(footer)
    return "\n".join(lines).rstrip()


def _provenance(presentation: Presentation) -> str:
    parts = []
    if presentation.source:
        parts.append(f"Source: {presentation.source}")
    if presentation.as_of:
        parts.append(f"as of {presentation.as_of}")
    return " · ".join(parts)


def _markdown_table(columns: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> list[str]:
    header = "| " + " | ".join(_md_cell(col) for col in columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(_md_cell(cell) for cell in row) + " |" for row in rows]
    return [header, divider, *body]


def _md_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _aligned_rows(rows: list[tuple[str, ...]] | list[list[str]]) -> list[str]:
    if not rows:
        return []
    width = max(len(str(row[0])) for row in rows if row)
    out: list[str] = []
    for row in rows:
        cells = list(row)
        if len(cells) == 1:
            out.append(f"  {cells[0]}")
        else:
            out.append(f"  {str(cells[0]).ljust(width)}  {'  '.join(str(c) for c in cells[1:])}")
    return out


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _has_record_collection(data: dict[str, Any]) -> bool:
    from finance_cli.records import GROUP_CONTAINER_KEYS, LIST_CONTAINER_KEYS

    for key, value in data.items():
        if key in LIST_CONTAINER_KEYS and isinstance(value, list) and value:
            return True
        if key in GROUP_CONTAINER_KEYS and isinstance(value, dict) and value:
            return True
    return False


def _first_str(data: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _meta_field(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    meta = data.get("meta")
    if isinstance(meta, dict):
        inner = meta.get(key)
        if isinstance(inner, str) and inner.strip():
            return inner.strip()
    return None
