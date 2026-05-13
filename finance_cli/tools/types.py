"""Connector-neutral tool/capability definitions for finance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


FinanceToolHandler = Callable[[dict[str, Any], dict[str, Any]], str]


@dataclass(frozen=True)
class FinanceToolSpec:
    """A finance capability that can be adapted by an external connector."""

    name: str
    schema: dict[str, Any]
    handler: FinanceToolHandler
    read_only: bool = True
    concurrent_safe: bool = True
