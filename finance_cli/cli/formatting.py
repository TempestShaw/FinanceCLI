"""Output formatting for finance CLI commands."""
from __future__ import annotations

import json
import os
import sys
from io import StringIO
from typing import Any

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from finance_cli.presentation import present, render_markdown
from finance_cli.records import RecordRenderOptions, normalize_records, render_records
from finance_cli.schemas import FinanceCommandResult


def render_result(
    result: FinanceCommandResult,
    output: str = "json",
    *,
    command: str | None = None,
    record_options: RecordRenderOptions | None = None,
) -> str:
    if command == "completion" and result.ok and isinstance(result.data, dict) and isinstance(result.data.get("script"), str):
        return result.data["script"].rstrip()
    if output == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, default=str, allow_nan=False)
    if output == "pretty-json":
        return _render_pretty_json(result.to_dict())
    if output == "text":
        if not result.ok:
            return f"Error: {result.error or 'unknown error'}"
        return _render_text(result.data)
    if output == "md":
        if not result.ok:
            return f"**Error:** {result.error or 'unknown error'}"
        if not (record_options and record_options.fields):
            presentation = present(command, result.data)
            if presentation is not None:
                return render_markdown(presentation)
        records = normalize_records(result.data, command=command)
        return render_records(records, "md", record_options)
    if output == "report":
        if not result.ok:
            return f"Error: {result.error or 'unknown error'}"
        return _render_report(result.data, command=command)
    if output in {"compact", "schema", "table"}:
        if not result.ok:
            return f"Error: {result.error or 'unknown error'}"
        if output == "table":
            if result.display is not None and not (record_options and record_options.fields):
                try:
                    return _render_rich_display(result.display)
                except Exception:
                    pass
            rendered = _render_command_table(result.data, command=command, record_options=record_options)
            if rendered is not None:
                return rendered
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
        if _has_text_body(data):
            body = _report_body(data)
        else:
            presentation = present(command, data)
            body = render_markdown(presentation) if presentation is not None else _report_body(data)
    else:
        title = command or "report"
        body = str(data)
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None, width=100)
    console.print(Panel(Markdown(body), title=title, expand=False))
    return buffer.getvalue().rstrip()


def _render_command_table(data: Any, *, command: str | None, record_options: RecordRenderOptions | None) -> str | None:
    if record_options and record_options.fields:
        return None
    if command == "sources.status" and isinstance(data, dict):
        return _render_sources_status_table(data)
    if command == "price.relative" and isinstance(data, dict):
        return _render_price_relative_table(data)
    if command == "fundamentals.growth" and isinstance(data, dict):
        return _render_fundamentals_growth_table(data)
    if command == "fundamentals.statement" and isinstance(data, dict):
        return _render_fundamentals_statement_table(data)
    if command == "market.trend" and isinstance(data, dict):
        return _render_market_trend_table(data)
    if command == "backtest.strategies" and isinstance(data, dict):
        return _render_backtest_strategies_table(data)
    if command == "filings.read" and isinstance(data, dict):
        return _render_filings_read_table(data)
    return None


def _render_sources_status_table(data: dict[str, Any]) -> str:
    table = Table(title="Provider status", show_header=True, header_style="bold")
    table.add_column("Provider", overflow="fold")
    table.add_column("Status", overflow="fold")
    table.add_column("Package", overflow="fold")
    table.add_column("Required env", overflow="fold")
    table.add_column("Capabilities", overflow="fold")

    for row in data.get("sources") or []:
        if not isinstance(row, dict):
            continue
        required_env = row.get("required_env")
        table.add_row(
            str(row.get("name") or ""),
            "OK" if row.get("configured") else "Missing",
            _package_text(row),
            _env_text(required_env),
            ", ".join(str(item) for item in (row.get("capabilities") or [])[:4]),
        )
    return _render_rich_table(table)


def _render_price_relative_table(data: dict[str, Any]) -> str:
    symbol = str(data.get("symbol") or "").upper()
    table = Table(title=f"Relative performance: {symbol}" if symbol else "Relative performance", show_header=True, header_style="bold")
    table.add_column("Period", overflow="fold")
    table.add_column("Comparison", overflow="fold")
    table.add_column("Type", overflow="fold")
    table.add_column(f"{symbol or 'Symbol'} return", justify="right")
    table.add_column("Comparison return", justify="right")
    table.add_column("Relative", justify="right")

    for row in data.get("relative_performance") or []:
        if not isinstance(row, dict):
            continue
        table.add_row(
            str(row.get("period") or ""),
            str(row.get("comparison") or ""),
            str(row.get("comparison_type") or ""),
            _pct_text(row.get("symbol_return_pct")),
            _pct_text(row.get("comparison_return_pct")),
            _pct_text(row.get("relative_return_pct")),
        )
    return _render_rich_table(table)


def _render_fundamentals_growth_table(data: dict[str, Any]) -> str:
    symbol = str(data.get("symbol") or "").upper()
    table = Table(title=f"Fundamental growth: {symbol}" if symbol else "Fundamental growth", show_header=True, header_style="bold")
    table.add_column("Period type", overflow="fold")
    table.add_column("Metric", overflow="fold")
    table.add_column("Kind", overflow="fold")
    table.add_column("Period", overflow="fold")
    table.add_column("Comparison", overflow="fold")
    table.add_column("Value", justify="right")

    for row in data.get("rows") or []:
        if not isinstance(row, dict):
            continue
        table.add_row(
            str(row.get("period_type") or ""),
            str(row.get("metric") or ""),
            str(row.get("kind") or ""),
            str(row.get("period") or row.get("current_period") or row.get("end_period") or ""),
            str(row.get("comparison_period") or row.get("start_period") or ""),
            _growth_value_text(row),
        )
    return _render_rich_table(table)


def _render_fundamentals_statement_table(data: dict[str, Any]) -> str:
    symbol = str(data.get("symbol") or "").upper()
    statement = str(data.get("statement") or "statement")
    period = str(data.get("period") or "")
    source = str(data.get("source") or "")
    title = f"{statement.title()} statement"
    if symbol:
        title = f"{title}: {symbol}"
    suffix = " | ".join(part for part in (period, source) if part)
    if suffix:
        title = f"{title} | {suffix}"

    periods = _statement_period_columns(data)
    table = Table(title=title, show_header=True, header_style="bold", box=box.SIMPLE)
    table.add_column("Line item", overflow="fold", ratio=3)
    for column in periods:
        table.add_column(column, justify="right", no_wrap=True)

    for row in data.get("rows") or []:
        if not isinstance(row, dict) or row.get("abstract") is True:
            continue
        table.add_row(
            _statement_label(row),
            *[_statement_value_text(row, period_column) for period_column in periods],
        )
    return _render_rich_table(table)


def _render_market_trend_table(data: dict[str, Any]) -> str:
    market = str(data.get("market") or "").upper()
    state = str(data.get("market_direction_state") or "")
    title = f"Market trend: {market}" if market else "Market trend"
    if state:
        title = f"{title} | State: {state}"
    period_keys = _market_return_periods(data.get("trend") or [])

    table = Table(title=title, show_header=True, header_style="bold", box=box.SIMPLE)
    table.add_column("Symbol", overflow="fold")
    table.add_column("Role", overflow="fold")
    table.add_column("Close", justify="right")
    table.add_column("50D", justify="right")
    table.add_column("200D", justify="right")
    table.add_column("MA", justify="center")
    for period in period_keys:
        table.add_column(period, justify="right")
    table.add_column("VIX", overflow="fold")

    for row in data.get("trend") or []:
        if not isinstance(row, dict):
            continue
        table.add_row(
            str(row.get("symbol") or ""),
            _short_role(row.get("role")),
            _decimal_text(row.get("last_close")),
            _decimal_text(row.get("sma_50")),
            _decimal_text(row.get("sma_200") or row.get("sma_20")),
            _ma_text(row),
            *[_pct_text(row.get(f"return_{period.lower()}_pct")) for period in period_keys],
            _volatility_text(row),
        )
    return _render_rich_table(table)


def _render_backtest_strategies_table(data: dict[str, Any]) -> str:
    engine = str(data.get("engine") or "")
    title = f"Backtest strategies: {engine}" if engine else "Backtest strategies"
    table = Table(title=title, show_header=True, header_style="bold", box=box.SIMPLE)
    table.add_column("Name", style="bold", overflow="fold")
    table.add_column("Summary", overflow="fold")
    table.add_column("Parameters", overflow="fold")

    for strategy in data.get("strategies") or []:
        if not isinstance(strategy, dict):
            continue
        table.add_row(
            str(strategy.get("name") or ""),
            str(strategy.get("summary") or ""),
            _strategy_parameters_text(strategy.get("parameters")),
        )
    return _render_rich_table(table)


def _render_filings_read_table(data: dict[str, Any]) -> str:
    text = str(data.get("text") or "").strip()
    if not text:
        return _render_rich_table(Table(title="Filing section"))
    filing = data.get("filing") if isinstance(data.get("filing"), dict) else {}
    section = data.get("section") if isinstance(data.get("section"), dict) else {}
    title_parts = [
        str(filing.get("company") or filing.get("company_name") or "").strip(),
        str(filing.get("form") or "").strip(),
        str(section.get("title") or section.get("key") or "").strip(),
    ]
    title = " | ".join(part for part in title_parts if part) or "Filing section"
    subtitle_parts = []
    accession = filing.get("accession_no")
    if accession:
        subtitle_parts.append(str(accession))
    if data.get("truncated"):
        subtitle_parts.append(f"truncated to {data.get('returned_chars')} chars")
    panel = Panel(Text(text), title=title, subtitle=" | ".join(subtitle_parts), expand=False)
    return _render_rich_display(panel)


def _render_rich_table(table: Table) -> str:
    return _render_rich_display(table)


def _render_rich_display(display: Any) -> str:
    if callable(display):
        display = display()
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None, width=120)
    console.print(display)
    return buffer.getvalue().rstrip()


def _package_text(row: dict[str, Any]) -> str:
    package = row.get("package")
    if not package:
        return "-"
    return f"{package} OK" if row.get("package_installed") else f"{package} missing"


def _env_text(value: Any) -> str:
    if not value:
        return "-"
    if not isinstance(value, list):
        return str(value)
    missing = [str(item.get("name")) for item in value if isinstance(item, dict) and not item.get("present")]
    if missing:
        return "missing " + ", ".join(missing)
    names = [str(item.get("name")) for item in value if isinstance(item, dict) and item.get("name")]
    return "OK" if names else "-"


def _pct_text(value: Any) -> str:
    number = _number(value)
    if number is None:
        return "-"
    return f"{number:+.2f}%"


def _decimal_text(value: Any) -> str:
    number = _number(value)
    if number is None:
        return "-"
    return f"{number:.2f}"


def _short_role(value: Any) -> str:
    aliases = {
        "primary": "main",
        "growth": "growth",
        "dow": "dow",
        "small_caps": "small",
        "volatility": "vol",
        "comparison": "comp",
    }
    text = str(value or "")
    return aliases.get(text, text.replace("_", " "))


def _ma_text(row: dict[str, Any]) -> str:
    above_50 = row.get("above_sma_50")
    above_200 = row.get("above_sma_200")
    if above_50 is None and above_200 is None:
        return "-"
    return f"{_bool_letter(above_50)}/{_bool_letter(above_200)}"


def _bool_letter(value: Any) -> str:
    if value is True:
        return "Y"
    if value is False:
        return "N"
    return "-"


def _volatility_text(row: dict[str, Any]) -> str:
    trend = _short_volatility_trend(row.get("volatility_trend"))
    state = _short_volatility_state(row.get("volatility_state"))
    return " ".join(part for part in (trend, state) if part) or "-"


def _strategy_parameters_text(value: Any) -> str:
    if not isinstance(value, dict) or not value:
        return "-"
    parts: list[str] = []
    for name, meta in value.items():
        if isinstance(meta, dict):
            text = str(name)
            if "default" in meta:
                text += f"={meta['default']}"
            if meta.get("allowed"):
                text += f" ({'/'.join(str(item) for item in meta['allowed'])})"
            parts.append(text)
        else:
            parts.append(str(name))
    return ", ".join(parts)


def _short_volatility_trend(value: Any) -> str:
    text = str(value or "")
    aliases = {
        "falling_or_flat": "flat/down",
        "rising": "rising",
    }
    return aliases.get(text, text.replace("_", " "))


def _short_volatility_state(value: Any) -> str:
    aliases = {
        "contained": "ok",
        "elevated": "elev",
        "stressed": "stress",
        "unknown": "",
    }
    text = str(value or "")
    return aliases.get(text, text.replace("_", " "))


def _market_return_periods(rows: Any) -> list[str]:
    if not isinstance(rows, list):
        return []
    periods: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in row:
            if key.startswith("return_") and key.endswith("_pct"):
                period = key[len("return_") : -len("_pct")].upper()
                if period not in periods:
                    periods.append(period)
    order = {"1D": 1, "5D": 2, "1M": 3, "3M": 4, "6M": 5, "YTD": 6, "1Y": 7, "3Y": 8, "5Y": 9}
    return sorted(periods, key=lambda period: (order.get(period, 100), period))


def _growth_value_text(row: dict[str, Any]) -> str:
    kind = row.get("kind")
    if kind == "growth":
        return _pct_text(row.get("growth_pct"))
    if kind == "delta":
        value = _number(row.get("delta"))
        return "-" if value is None else _signed_number_text(value)
    value = _number(row.get("value"))
    return "-" if value is None else _plain_number_text(value)


def _statement_period_columns(data: dict[str, Any]) -> list[str]:
    periods = data.get("periods")
    if isinstance(periods, list):
        return [str(period) for period in periods if str(period).strip()][:6]

    columns: list[str] = []
    metadata = {"abstract", "concept", "label", "level", "source", "statement", "unit", "view"}
    for row in data.get("rows") or []:
        if not isinstance(row, dict):
            continue
        for key, value in row.items():
            if key in metadata or _number(value) is None:
                continue
            text = str(key)
            if any(char.isdigit() for char in text) and text not in columns:
                columns.append(text)
    return columns[:6]


def _statement_label(row: dict[str, Any]) -> str:
    label = str(row.get("label") or row.get("concept") or "")
    level = _int(row.get("level"))
    if level is None:
        return label
    return ("  " * min(max(level - 1, 0), 3)) + label


def _statement_value_text(row: dict[str, Any], period: str) -> str:
    value = row.get(period)
    if isinstance(value, dict):
        value = value.get("reported", value.get("raw"))
    number = _number(value)
    if number is None:
        return "-"
    if _statement_row_is_per_share(row):
        return _plain_number_text(number)
    return _compact_number_text(number)


def _statement_row_is_per_share(row: dict[str, Any]) -> bool:
    text = " ".join(str(row.get(key) or "") for key in ("concept", "label")).lower()
    return "earningspershare" in text.replace("_", "") or "per share" in text


def _compact_number_text(value: float) -> str:
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    for divisor, suffix in (
        (1_000_000_000_000, "T"),
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "K"),
    ):
        if magnitude >= divisor:
            return f"{sign}{_plain_number_text(magnitude / divisor, places=2)}{suffix}"
    return f"{sign}{_plain_number_text(magnitude)}"


def _number(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except Exception:
        return None


def _plain_number_text(value: float, *, places: int = 4) -> str:
    rounded = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return rounded or "0"


def _signed_number_text(value: float) -> str:
    rounded = _plain_number_text(abs(value))
    sign = "+" if value >= 0 else "-"
    return f"{sign}{rounded}"


def _has_text_body(data: dict[str, Any]) -> bool:
    return any(isinstance(data.get(key), str) and data.get(key) for key in ("text", "content", "summary"))


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
