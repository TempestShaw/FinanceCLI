"""Output formatting for finance CLI commands."""
from __future__ import annotations

import json
from typing import Any

from finance_cli.records import RecordRenderOptions, normalize_records, render_records
from finance_cli.schemas import FinanceCommandResult


def render_result(
    result: FinanceCommandResult,
    output: str = "json",
    *,
    command: str | None = None,
    record_options: RecordRenderOptions | None = None,
) -> str:
    if output == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, default=str, allow_nan=False)
    if output == "text":
        if not result.ok:
            return f"Error: {result.error or 'unknown error'}"
        return _render_text(result.data)
    if output in {"compact", "schema"}:
        if not result.ok:
            return f"Error: {result.error or 'unknown error'}"
        records = normalize_records(result.data, command=command)
        return render_records(records, output, record_options)
    raise ValueError(f"unknown output format: {output}")


def _render_text(data: Any) -> str:
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    return str(data)
