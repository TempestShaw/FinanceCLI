"""Structured finance result schemas.

These dataclasses are deliberately plain and serializable so the same results
can be printed by the CLI, returned by LLM tools, or persisted as artifacts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class FinanceMeta:
    source: str
    as_of: str
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketRegime:
    market: str
    timeframe: str
    regime: str
    confidence: float
    signals: list[dict[str, Any]]
    meta: FinanceMeta

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SectorHeat:
    market: str
    group_by: str
    lookback_days: int
    leaders: list[dict[str, Any]]
    laggards: list[dict[str, Any]]
    meta: FinanceMeta

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SymbolSnapshot:
    symbol: str
    company_name: str
    sector: str
    industry: str
    last_price: float | None
    change_pct: float | None
    key_stats: dict[str, Any]
    meta: FinanceMeta

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FinanceCommandResult:
    ok: bool
    data: dict[str, Any] | list[dict[str, Any]] | None = None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    display: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "data": self.data,
            "error": self.error,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class Record:
    """Normalized finance fact record for agent-oriented rendering."""

    entity: str
    kind: str
    period: str | None = None
    timestamp: str | None = None
    fields: dict[str, Any] = field(default_factory=dict)
    source: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self, *, omit_null: bool = True, include_metadata: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "entity": self.entity,
            "kind": self.kind,
            "period": self.period,
            "timestamp": self.timestamp,
            "fields": dict(self.fields),
            "source": self.source,
        }
        if include_metadata:
            payload["metadata"] = dict(self.metadata) if self.metadata is not None else None
        if omit_null:
            return {key: value for key, value in payload.items() if value is not None}
        return payload
