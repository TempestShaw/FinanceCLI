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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
