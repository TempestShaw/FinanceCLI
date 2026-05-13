"""Output formatting for finance CLI commands."""
from __future__ import annotations

import json
from typing import Any

from finance_cli.schemas import FinanceCommandResult


def render_result(result: FinanceCommandResult, output: str = "json") -> str:
    if output == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, default=str, allow_nan=False)
    if output == "text":
        if not result.ok:
            return f"Error: {result.error or 'unknown error'}"
        return _render_text(result.data)
    raise ValueError(f"unknown output format: {output}")


def _render_text(data: Any) -> str:
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    return str(data)
