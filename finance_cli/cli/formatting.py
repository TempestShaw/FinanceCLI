"""Output formatting for finance CLI commands."""
from __future__ import annotations

import json
import os
import sys
from io import StringIO
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

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
    if output == "pretty-json":
        return _render_pretty_json(result.to_dict())
    if output == "text":
        if not result.ok:
            return f"Error: {result.error or 'unknown error'}"
        return _render_text(result.data)
    if output == "report":
        if not result.ok:
            return f"Error: {result.error or 'unknown error'}"
        return _render_report(result.data, command=command)
    if output in {"compact", "schema", "table"}:
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


def _render_pretty_json(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, indent=2, ensure_ascii=False, default=str, allow_nan=False)
    if not (sys.stdout.isatty() or os.getenv("FORCE_COLOR") in {"1", "true", "TRUE"}):
        return text
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, color_system="truecolor", width=100)
    console.print(Syntax(text, "json", theme="default", word_wrap=True))
    return buffer.getvalue().rstrip()


def _render_report(data: Any, *, command: str | None) -> str:
    if isinstance(data, dict):
        title = command or str(data.get("title") or data.get("source") or "report")
        body = _report_body(data)
    else:
        title = command or "report"
        body = str(data)
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None, width=100)
    console.print(Panel(Markdown(body), title=title, expand=False))
    return buffer.getvalue().rstrip()


def _report_body(data: dict[str, Any]) -> str:
    text = data.get("text") or data.get("content") or data.get("summary")
    lines: list[str] = []
    metadata = []
    for key in ("source", "url", "title", "form", "period", "format", "pages"):
        value = data.get(key)
        if value is not None:
            metadata.append(f"**{key.replace('_', ' ').title()}:** {value}")
    if metadata:
        lines.extend(metadata)
        lines.append("")
    if text is not None:
        lines.append(str(text))
    else:
        lines.append("```json")
        lines.append(json.dumps(data, indent=2, ensure_ascii=False, default=str, allow_nan=False))
        lines.append("```")
    return "\n".join(lines)
