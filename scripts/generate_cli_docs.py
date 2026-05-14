"""Generate human and agent-facing docs from the Finance CLI registry."""
from __future__ import annotations

import json
import re
import shlex
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from finance_cli import __version__
from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.registry import FinanceCommand, clear_commands, list_commands


ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs-site" / "src" / "content" / "docs"
PUBLIC_ROOT = ROOT / "docs-site" / "public"
COMMANDS_OUTPUT = DOCS_ROOT / "commands.md"
ROOT_TOOLS_OUTPUT = ROOT / "tools.json"
ROOT_OPENAPI_OUTPUT = ROOT / "openapi.json"
ROOT_TOOLS_SCHEMA_OUTPUT = ROOT / "schemas" / "finance-cli-tools.schema.json"
PUBLIC_TOOLS_OUTPUT = PUBLIC_ROOT / "tools.json"
PUBLIC_OPENAPI_OUTPUT = PUBLIC_ROOT / "openapi.json"
PUBLIC_TOOLS_SCHEMA_OUTPUT = PUBLIC_ROOT / "schemas" / "finance-cli-tools.schema.json"
ROOT_LLMS_OUTPUT = ROOT / "llms.txt"
ROOT_LLMS_FULL_OUTPUT = ROOT / "llms-full.txt"
PUBLIC_LLMS_OUTPUT = PUBLIC_ROOT / "llms.txt"
PUBLIC_LLMS_FULL_OUTPUT = PUBLIC_ROOT / "llms-full.txt"
SITE_URL = "https://tempestshaw.github.io/FinanceCLI"


RESULT_ENVELOPE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["ok", "data", "error", "warnings"],
    "properties": {
        "ok": {"type": "boolean", "description": "True when the command completed successfully."},
        "data": {"description": "Command-specific payload. Null when ok is false."},
        "error": {"type": ["string", "null"], "description": "Human-readable error when ok is false."},
        "warnings": {"type": "array", "items": {"type": "string"}, "description": "Non-fatal issues."},
    },
}

SIDE_EFFECTS = {
    "pure_calculation": "No network, no filesystem read, no mutation.",
    "local_file_read": "Reads local files supplied by the caller. Does not mutate files.",
    "network_read_only": "Reads remote public/provider data. Does not mutate external state.",
    "local_or_network_read": "Reads a local path or remote URL supplied by the caller. Does not mutate files or external state.",
}

NAMESPACE_DEFAULTS: dict[str, dict[str, Any]] = {
    "backtest": {
        "side_effects": "network_read_only",
        "agent_use": "Use for repeatable strategy checks, payload construction, and VectorBT result summaries.",
        "avoid_when": "Do not present backtests as live trading recommendations.",
        "rate_limit_notes": "Provider data downloads may be rate limited.",
    },
    "calendar": {
        "side_effects": "network_read_only",
        "agent_use": "Use for company calendar fields and earnings-date rows.",
        "rate_limit_notes": "Yahoo Finance responses can vary by symbol and session.",
    },
    "document": {
        "side_effects": "local_or_network_read",
        "agent_use": "Use for PDF/HTML reading, phrase discovery, bounded windows, tables, and OCR fallback.",
        "citation_fields": ["source", "url", "path", "page", "start_char", "end_char", "match_id"],
    },
    "estimates": {
        "side_effects": "pure_calculation",
        "agent_use": "Use for explicit estimate comparison math and structured consensus result shaping.",
    },
    "filings": {
        "side_effects": "network_read_only",
        "agent_use": "Use for SEC filing discovery, canonical section reads, XBRL statement rows, and filing summary reports.",
        "citation_fields": ["symbol", "accession_no", "accession", "url", "form", "report_name", "section"],
        "rate_limit_notes": "SEC/EDGAR availability and provider throttling can affect live calls.",
    },
    "formula": {
        "side_effects": "pure_calculation",
        "agent_use": "Use only when all numeric inputs are explicit in the prompt or already extracted with citations.",
        "avoid_when": "Do not invent missing inputs. Ask for them or extract them first.",
    },
    "fundamentals": {
        "side_effects": "network_read_only",
        "agent_use": "Use for Yahoo financial statement tables outside SEC filing context.",
        "rate_limit_notes": "Yahoo Finance responses can vary by symbol and session.",
    },
    "industry": {
        "side_effects": "network_read_only",
        "agent_use": "Use for Yahoo industry keys, overview data, top companies, and research-report tables.",
        "rate_limit_notes": "Yahoo Finance sector/industry coverage can change.",
    },
    "ir": {
        "side_effects": "network_read_only",
        "agent_use": "Use to discover or read investor presentations from SEC exhibits and company IR pages.",
        "citation_fields": ["symbol", "url", "filing_url", "accession_no", "source"],
    },
    "kpi": {
        "side_effects": "network_read_only",
        "agent_use": "Use to collect KPI evidence from transcripts and filings with source snippets.",
        "citation_fields": ["symbol", "url", "accession_no", "quarter", "metric"],
    },
    "market": {
        "side_effects": "network_read_only",
        "agent_use": "Use for quotes, OHLCV, market status, broad regime, and sector heat context.",
        "rate_limit_notes": "Market data is time-sensitive and provider-specific.",
    },
    "news": {
        "side_effects": "network_read_only",
        "agent_use": "Use for source-attributed news search and GDELT analysis windows.",
        "citation_fields": ["url", "source", "published_at", "seendate"],
        "rate_limit_notes": "News providers can rate limit and can return sparse windows.",
    },
    "price": {
        "side_effects": "network_read_only",
        "agent_use": "Use for price move discovery and evidence timelines around a date.",
        "avoid_when": "Do not infer causality from price.context alone.",
        "citation_fields": ["symbol", "date", "source", "url"],
    },
    "research": {
        "side_effects": "pure_calculation",
        "agent_use": "Use for deterministic research checklists before executing commands.",
    },
    "screen": {
        "side_effects": "network_read_only",
        "agent_use": "Use to list and run Yahoo predefined equity screens.",
        "rate_limit_notes": "Yahoo screen counts and membership can change intraday.",
    },
    "sector": {
        "side_effects": "network_read_only",
        "agent_use": "Use for Yahoo sector keys, industries, overview data, ETFs, mutual funds, and top companies.",
        "rate_limit_notes": "Yahoo Finance sector/industry coverage can change.",
    },
    "sources": {
        "side_effects": "network_read_only",
        "agent_use": "Use to inspect configured data sources and run provider health probes.",
    },
    "symbol": {
        "side_effects": "network_read_only",
        "agent_use": "Use for a public-company profile or compact symbol snapshot.",
        "citation_fields": ["symbol", "source", "provider"],
    },
    "transcripts": {
        "side_effects": "network_read_only",
        "agent_use": "Use for earnings-call transcript search, reading, and Q&A extraction.",
        "citation_fields": ["symbol", "url", "quarter", "speaker", "published_at"],
    },
    "valuation": {
        "side_effects": "pure_calculation",
        "agent_use": "Use for deterministic valuation math once assumptions are explicit.",
        "avoid_when": "Do not present valuation output as investment advice.",
    },
}

COMMAND_OVERRIDES: dict[str, dict[str, Any]] = {
    "backtest.run": {
        "side_effects": "network_read_only",
        "agent_use": "Use when the user asks to run a named strategy over explicit symbols and dates.",
        "avoid_when": "Do not use as proof a strategy will work live.",
    },
    "document.read": {
        "agent_use": "Use for first-pass text extraction from a known PDF or SEC HTML URL.",
        "next_steps": ["document.scan", "document.window", "document.tables", "document.ocr"],
    },
    "document.scan": {
        "agent_use": "Use when the user needs phrase, table, or topic discovery inside a filing or document.",
        "next_steps": ["document.window", "formula.*"],
    },
    "document.window": {
        "agent_use": "Use after document.scan to read around a stable char offset or match_id without re-scanning the full document.",
    },
    "document.tables": {
        "agent_use": "Use for table previews in text-based PDFs when text windows are not enough.",
    },
    "document.ocr": {
        "agent_use": "Use as fallback for scanned or image-heavy PDFs after document.read/scan cannot extract text.",
    },
    "filings.recent": {
        "agent_use": "Use first when the user names a ticker but not a filing URL or accession.",
        "next_steps": ["filings.sections", "filings.statement", "filings.report", "document.scan"],
    },
    "filings.statement": {
        "agent_use": "Use when the user asks for structured XBRL financial statement rows such as income, balance, or cashflow items.",
        "avoid_when": "Do not use for narrative section text or non-XBRL table discovery.",
        "next_steps": ["filings.report", "document.scan", "formula.*"],
    },
    "filings.read": {
        "agent_use": "Use when the user asks for a canonical 10-K section such as business, risk factors, MD&A, or segments.",
        "next_steps": ["document.scan", "document.window"],
    },
    "filings.report": {
        "agent_use": "Use when the user already knows or discovered an edgartools report name and wants rows from that report.",
    },
    "formula.margin": {
        "agent_use": "Use for explicit numerator/denominator ratio math after cited inputs are known.",
    },
    "market.quote": {
        "agent_use": "Use for a current provider quote or compact company market snapshot.",
        "citation_fields": ["symbol", "source", "provider", "timestamp"],
    },
    "market.ohlcv": {
        "agent_use": "Use for historical bars needed by backtests, event windows, and price context.",
        "citation_fields": ["symbol", "date", "source", "provider"],
    },
    "market.status": {
        "agent_use": "Use to check current market open/close state and major-index summary.",
    },
    "price.context": {
        "agent_use": "Use when the user asks what filings, news, or transcripts were near a dated price move.",
        "avoid_when": "Do not claim causality unless the evidence explicitly supports it.",
    },
    "research.plan": {
        "agent_use": "Use before executing a complex public-company research workflow.",
    },
    "screen.run": {
        "agent_use": "Use after screen.predefined when the user asks for Yahoo predefined screen results.",
    },
    "sources.status": {
        "agent_use": "Use to report which providers are configured locally without making provider-specific claims.",
    },
    "sources.test": {
        "agent_use": "Use for provider connectivity checks when debugging setup.",
    },
    "valuation.dcf": {
        "agent_use": "Use only for deterministic DCF math from explicit cash flows and discount assumptions.",
        "avoid_when": "Do not use as investment advice or infer assumptions silently.",
    },
}

PARAM_OVERRIDES: dict[str, dict[str, dict[str, Any]]] = {
    "filings.statement": {
        "symbol": {"type": "string", "required": False, "description": "Ticker used to locate a recent filing."},
        "accession": {"type": "string", "required": False, "aliases": ["accession_no"], "description": "SEC accession number."},
        "url": {"type": "string", "required": False, "format": "uri", "description": "Direct SEC filing URL."},
        "form": {"type": "string", "required": False, "default": "10-K", "description": "SEC form used when resolving by symbol."},
        "statement": {"type": "string", "required": False, "default": "income", "enum": ["income", "balance", "cashflow"], "description": "Statement family."},
        "query": {"type": "string", "required": False, "description": "Optional row label search."},
        "include_abstract": {"type": "boolean", "required": False, "default": False, "description": "Include abstract rows when true."},
        "max_rows": {"type": "integer", "required": False, "default": 0, "description": "Maximum rows; 0 means unlimited."},
    },
    "document.scan": {
        "source": {"type": "string", "required": True, "aliases": ["path", "url"], "description": "Local path or URL."},
        "query": {"type": "string", "required": False, "description": "Literal phrase or table text to find."},
        "topics": {"type": "array", "items": {"type": "string"}, "required": False, "description": "Known topic names or literal queries."},
        "format": {"type": "string", "required": False, "enum": ["pdf", "html"], "description": "Document format override."},
        "match": {"type": "string", "required": False, "default": "fuzzy", "enum": ["fuzzy", "all_terms"], "description": "Match mode."},
        "threshold": {"type": "number", "required": False, "default": 80.0, "description": "Fuzzy score threshold."},
        "max_chars": {"type": "integer", "required": False, "default": 12000, "description": "Maximum text chars to read; 0 means unbounded in current readers."},
        "max_pages": {"type": "integer", "required": False, "default": 5, "description": "Maximum pages for PDFs; 0 means all pages."},
        "limit": {"type": "integer", "required": False, "default": 50, "description": "Maximum matches."},
        "window": {"type": "integer", "required": False, "default": 0, "description": "Optional context chars per match."},
        "start_char": {"type": "integer", "required": False, "description": "Start offset for a bounded scan."},
        "end_char": {"type": "integer", "required": False, "description": "End offset for a bounded scan."},
    },
    "document.window": {
        "source": {"type": "string", "required": True, "aliases": ["path", "url"], "description": "Local path or URL."},
        "format": {"type": "string", "required": False, "enum": ["pdf", "html"], "description": "Document format override."},
        "start_char": {"type": "integer", "required": False, "description": "Character offset."},
        "match_id": {"type": "string", "required": False, "description": "Match id returned by document.scan."},
        "chars": {"type": "integer", "required": False, "default": 4000, "description": "Window size in characters."},
        "direction": {"type": "string", "required": False, "default": "around", "enum": ["around", "next", "previous"], "description": "Window direction."},
    },
    "market.ohlcv": {
        "symbols": {"type": "string", "required": True, "description": "One ticker or comma-separated tickers."},
        "timeframe": {"type": "string", "required": False, "default": "1d", "description": "Bar interval."},
        "start_date": {"type": "string", "required": False, "format": "date", "description": "Start date."},
        "end_date": {"type": "string", "required": False, "format": "date", "description": "End date."},
        "limit": {"type": "integer", "required": False, "default": 200, "description": "Maximum bars when date bounds are not enough."},
        "provider": {"type": "string", "required": False, "default": "auto", "description": "Provider selection."},
        "include_attempts": {"type": "boolean", "required": False, "default": False, "description": "Include provider-attempt diagnostics."},
    },
    "news.search": {
        "query": {"type": "string", "required": False, "description": "Free-text news query."},
        "symbol": {"type": "string", "required": False, "description": "Ticker query."},
        "sector": {"type": "string", "required": False, "description": "Sector query."},
    },
    "news.analyze": {
        "analysis": {"type": "string", "required": True, "enum": ["timeline", "tone", "context", "geo", "doc"], "description": "Analysis mode."},
    },
    "formula.adjusted_ebitda": {
        "addbacks": {"type": "array", "items": {"type": "number"}, "required": False, "default": [], "description": "Optional addback values."},
    },
    "formula.enterprise_value": {
        "debt": {"type": "number", "required": False, "default": 0, "description": "Debt value."},
        "cash": {"type": "number", "required": False, "default": 0, "description": "Cash value."},
        "operating_cash": {"type": "number", "required": False, "default": 0, "description": "Cash treated as operating rather than excess."},
    },
    "formula.wacc": {
        "tax_rate": {"type": "number", "required": False, "default": 0, "description": "Tax rate; CLI accepts decimal or percent."},
        "debt_tax": {"type": "string", "required": False, "default": "after_tax", "enum": ["pretax", "after_tax"], "description": "Whether cost_of_debt is pretax or already after tax."},
    },
    "valuation.wacc": {
        "tax_rate": {"type": "number", "required": False, "default": 0, "description": "Tax rate; CLI accepts decimal or percent."},
    },
    "valuation.dcf": {
        "cashflows": {"type": "array", "items": {"type": "number"}, "required": True, "description": "Forecast cash flows. CLI accepts K/M/B suffixes."},
        "discount_rate": {"type": "number", "required": True, "description": "Discount rate; CLI accepts decimal or percent."},
        "terminal_growth": {"type": "number", "required": False, "description": "Perpetuity growth rate."},
        "exit_multiple": {"type": "number", "required": False, "description": "Exit multiple alternative to terminal growth."},
    },
}

PARAM_REMOVALS: dict[str, set[str]] = {
    "market.ohlcv": {"symbol"},
}

COMMON_PARAM_OVERRIDES: dict[str, dict[str, Any]] = {
    "symbol": {"type": "string", "description": "Ticker symbol."},
    "symbols": {"type": "string", "description": "Ticker symbol or comma-separated ticker list."},
    "market": {"type": "string", "description": "Market code.", "default": "US"},
    "timeframe": {"type": "string", "description": "Provider-supported timeframe or research horizon."},
    "limit": {"type": "integer", "description": "Maximum records to return."},
    "max_records": {"type": "integer", "description": "Maximum records to return."},
    "max_rows": {"type": "integer", "description": "Maximum rows to return."},
    "max_chars": {"type": "integer", "description": "Maximum text characters to return."},
    "max_pages": {"type": "integer", "description": "Maximum PDF pages to read."},
    "query": {"type": "string", "description": "Search query."},
    "url": {"type": "string", "format": "uri", "description": "Remote URL."},
    "source": {"type": "string", "description": "Source key, path, or URL depending on command."},
    "path": {"type": "string", "description": "Local file path."},
    "form": {"type": "string", "description": "SEC form type."},
    "statement": {"type": "string", "enum": ["income", "balance", "cashflow"], "description": "Financial statement family."},
    "section": {"type": "string", "description": "Filing section key."},
    "accession": {"type": "string", "description": "SEC accession number."},
    "accession_no": {"type": "string", "description": "SEC accession number."},
    "include_attempts": {"type": "boolean", "description": "Include provider-attempt diagnostics."},
    "classify": {"type": "boolean", "description": "Classify filing events when supported."},
    "debug": {"type": "boolean", "description": "Include debug details."},
    "include_turns": {"type": "boolean", "description": "Include transcript speaker turns."},
    "count": {"type": "integer", "description": "Maximum records requested."},
    "offset": {"type": "integer", "description": "Result offset."},
    "sort_asc": {"type": "boolean", "description": "Sort ascending when set."},
    "start_date": {"type": "string", "format": "date", "description": "Start date."},
    "end_date": {"type": "string", "format": "date", "description": "End date."},
    "date": {"type": "string", "format": "date", "description": "Date."},
    "cashflows": {"type": "array", "items": {"type": "number"}, "description": "Cash-flow series. CLI accepts comma-separated K/M/B suffixed values."},
    "discount_rate": {"type": "number", "description": "Discount rate. CLI accepts decimal or percent."},
}

COMMAND_DATA_SCHEMAS: dict[str, dict[str, Any]] = {
    "filings.statement": {
        "type": "object",
        "properties": {
            "symbol": {"type": ["string", "null"]},
            "accession_no": {"type": ["string", "null"]},
            "url": {"type": ["string", "null"]},
            "statement": {"type": "string"},
            "rows": {"type": "array", "items": {"type": "object"}},
            "count": {"type": "integer"},
            "source": {"type": "string"},
        },
        "additionalProperties": True,
    },
    "document.scan": {
        "type": "object",
        "properties": {
            "source": {"type": "string"},
            "matches": {"type": "array", "items": {"type": "object"}},
            "count": {"type": "integer"},
            "char_count": {"type": "integer"},
            "warnings": {"type": "array", "items": {"type": "string"}},
        },
        "additionalProperties": True,
    },
}

NAMESPACE_DATA_SCHEMAS: dict[str, dict[str, Any]] = {
    "backtest": {"type": "object", "description": "Backtest metrics, trades, plots, or payload metadata.", "additionalProperties": True},
    "calendar": {"type": "object", "description": "Company calendar or earnings-date rows.", "additionalProperties": True},
    "document": {"type": "object", "description": "Document text, blocks, matches, tables, OCR, or window metadata.", "additionalProperties": True},
    "estimates": {"type": "object", "description": "Consensus estimate or comparison result.", "additionalProperties": True},
    "filings": {"type": "object", "description": "SEC filing metadata, section text, reports, or XBRL rows.", "additionalProperties": True},
    "formula": {"type": "object", "description": "Deterministic calculation with inputs and method.", "additionalProperties": True},
    "fundamentals": {"type": "object", "description": "Statement rows from Yahoo Finance.", "additionalProperties": True},
    "industry": {"type": "object", "description": "Yahoo industry key, overview, or table result.", "additionalProperties": True},
    "ir": {"type": "object", "description": "Investor-presentation discovery or text extraction result.", "additionalProperties": True},
    "kpi": {"type": "object", "description": "KPI evidence snippets and history rows.", "additionalProperties": True},
    "market": {"type": "object", "description": "Quote, bars, market status, regime, or sector heat data.", "additionalProperties": True},
    "news": {"type": "object", "description": "News records or analysis result.", "additionalProperties": True},
    "price": {"type": "object", "description": "Price moves or dated evidence timeline.", "additionalProperties": True},
    "research": {"type": "object", "description": "Research checklist.", "additionalProperties": True},
    "screen": {"type": "object", "description": "Yahoo predefined screen metadata or quote rows.", "additionalProperties": True},
    "sector": {"type": "object", "description": "Yahoo sector key, overview, industries, or table result.", "additionalProperties": True},
    "sources": {"type": "object", "description": "Provider status, capability list, or test result.", "additionalProperties": True},
    "symbol": {"type": "object", "description": "Symbol profile or snapshot.", "additionalProperties": True},
    "transcripts": {"type": "object", "description": "Transcript search, read, or Q&A result.", "additionalProperties": True},
    "valuation": {"type": "object", "description": "Valuation calculation result and assumptions.", "additionalProperties": True},
}

PLAYBOOKS: list[dict[str, Any]] = [
    {
        "task": "extract_metric_from_10k",
        "when": "The user asks for a metric or table value from a company's latest 10-K.",
        "steps": ["filings.recent", "filings.statement", "document.scan", "document.window", "formula.*"],
        "failure_modes": [
            "If no XBRL row matches, fall back to filings.reports then document.scan.",
            "If document.scan finds multiple matches, use document.window around each candidate and cite offsets.",
        ],
    },
    {
        "task": "explain_price_move",
        "when": "The user asks what happened around a dated price move.",
        "steps": ["price.moves", "price.context", "news.search", "filings.recent", "transcripts.search"],
        "failure_modes": [
            "If no dated evidence appears, say the CLI found no direct evidence rather than inferring causality.",
            "Always cite provider, date, and URL/accession when available.",
        ],
    },
    {
        "task": "screen_and_contextualize_equities",
        "when": "The user asks for market ideas from predefined Yahoo screens.",
        "steps": ["screen.predefined", "screen.run", "symbol.snapshot", "market.quote", "filings.recent"],
        "failure_modes": [
            "If a screen returns fewer rows than requested, keep the returned count and source.",
            "Do not describe screen membership as a recommendation.",
        ],
    },
    {
        "task": "run_reproducible_backtest",
        "when": "The user asks to test a strategy over explicit symbols and dates.",
        "steps": ["backtest.strategies", "backtest.describe", "backtest.run", "backtest.tune"],
        "failure_modes": [
            "If provider data is unavailable, fail clearly with the provider error.",
            "Preserve strategy name, symbols, dates, params, and JSON output.",
        ],
    },
]


def main() -> None:
    commands = _registered_commands()
    specs = build_command_specs(commands)

    _write_text(COMMANDS_OUTPUT, build_commands_markdown(commands))
    tools_doc = build_tools_document(specs)
    openapi_doc = build_openapi_document(specs)
    tools_schema_doc = build_tools_schema_document()
    _write_json(ROOT_TOOLS_OUTPUT, tools_doc)
    _write_json(PUBLIC_TOOLS_OUTPUT, tools_doc)
    _write_json(ROOT_OPENAPI_OUTPUT, openapi_doc)
    _write_json(PUBLIC_OPENAPI_OUTPUT, openapi_doc)
    _write_json(ROOT_TOOLS_SCHEMA_OUTPUT, tools_schema_doc)
    _write_json(PUBLIC_TOOLS_SCHEMA_OUTPUT, tools_schema_doc)

    llms_txt = build_llms_txt()
    llms_full_txt = build_llms_full_txt(specs)
    _write_text(ROOT_LLMS_OUTPUT, llms_txt)
    _write_text(PUBLIC_LLMS_OUTPUT, llms_txt)
    _write_text(ROOT_LLMS_FULL_OUTPUT, llms_full_txt)
    _write_text(PUBLIC_LLMS_FULL_OUTPUT, llms_full_txt)


def _registered_commands() -> list[FinanceCommand]:
    clear_commands()
    register_builtin_commands()
    return sorted(list_commands(), key=lambda command: command.name)


def build_commands_markdown(commands: list[FinanceCommand]) -> str:
    by_namespace: dict[str, list[FinanceCommand]] = defaultdict(list)
    for command in commands:
        namespace = command.name.split(".", 1)[0]
        by_namespace[namespace].append(command)

    lines = [
        "---",
        "title: Commands",
        "description: Generated command reference for Finance CLI.",
        "---",
        "",
        "# Commands",
        "",
        "This page is generated from the Finance CLI command registry.",
        "",
        "Run `python scripts/generate_cli_docs.py` after changing command metadata.",
        "",
        "Agent-facing schemas are available as [`tools.json`](/FinanceCLI/tools.json) and [`openapi.json`](/FinanceCLI/openapi.json).",
        "",
    ]
    for namespace in sorted(by_namespace):
        lines.extend([f"## `{namespace}.*`", ""])
        for command in by_namespace[namespace]:
            lines.extend([f"### `{command.name}`", "", command.summary, ""])
            if command.usage:
                lines.extend(["**Usage**", "", "```bash", f"finance {command.usage}", "```", ""])
            if command.examples:
                lines.extend(["**Examples**", "", "```bash"])
                lines.extend(command.examples)
                lines.extend(["```", ""])
            if command.notes:
                lines.append("**Notes**")
                lines.append("")
                lines.extend(f"- {note}" for note in command.notes)
                lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_command_specs(commands: list[FinanceCommand]) -> list[dict[str, Any]]:
    return [build_command_spec(command) for command in commands]


def build_command_spec(command: FinanceCommand) -> dict[str, Any]:
    namespace = command.name.split(".", 1)[0]
    defaults = deepcopy(NAMESPACE_DEFAULTS.get(namespace, {}))
    overrides = deepcopy(COMMAND_OVERRIDES.get(command.name, {}))
    params = _parse_usage_params(command.usage)
    params = _apply_common_param_metadata(params)
    for param_name in PARAM_REMOVALS.get(command.name, set()):
        params.pop(param_name, None)
    params.update(deepcopy(PARAM_OVERRIDES.get(command.name, {})))

    if namespace == "formula":
        params = _mark_numeric_formula_params(params)
    if namespace == "valuation":
        params = _mark_valuation_params(params)

    input_schema = _input_schema(params)
    data_schema = deepcopy(COMMAND_DATA_SCHEMAS.get(command.name) or NAMESPACE_DATA_SCHEMAS.get(namespace) or {"type": "object"})
    output_schema = deepcopy(RESULT_ENVELOPE_SCHEMA)
    output_schema["properties"]["data"] = {"anyOf": [data_schema, {"type": "null"}]}

    side_effects = overrides.get("side_effects") or defaults.get("side_effects") or "network_read_only"
    auth_required = _auth_required(namespace, command.name)
    command_spec = {
        "name": command.name,
        "namespace": namespace,
        "description": command.summary,
        "usage": f"finance {command.usage}" if command.usage else "finance " + command.name,
        "examples": list(command.examples),
        "notes": list(command.notes),
        "args": params,
        "input_schema": input_schema,
        "output_schema": output_schema,
        "side_effects": side_effects,
        "side_effects_description": SIDE_EFFECTS[side_effects],
        "auth_required": auth_required,
        "rate_limit_notes": overrides.get("rate_limit_notes") or defaults.get("rate_limit_notes"),
        "citation_fields": overrides.get("citation_fields") or defaults.get("citation_fields", []),
        "agent": {
            "use_when": overrides.get("agent_use") or defaults.get("agent_use") or f"Use for {namespace} workflows.",
            "avoid_when": overrides.get("avoid_when") or defaults.get("avoid_when"),
            "next_steps": overrides.get("next_steps", []),
        },
    }
    return command_spec


def build_tools_document(specs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "$schema": "https://tempestshaw.github.io/FinanceCLI/schemas/finance-cli-tools.schema.json",
        "name": "finresearch-cli",
        "version": __version__,
        "description": "Machine-readable Finance CLI command metadata for LLM agents, MCP adapters, and plugin wrappers.",
        "canonical_docs": SITE_URL + "/",
        "result_envelope": RESULT_ENVELOPE_SCHEMA,
        "side_effect_levels": SIDE_EFFECTS,
        "trust_policy": {
            "cite_when_available": ["accession", "accession_no", "url", "report_name", "section", "page", "start_char", "end_char", "source", "provider", "timestamp"],
            "market_data": "Never claim live market data without provider/source and timestamp/date fields when available.",
            "source_truth": "Treat Yahoo, FMP, SEC, GDELT, transcripts, and company IR as source-specific records, not ground truth.",
            "credentials": "API keys are read from environment variables at runtime and are not written by the CLI.",
        },
        "playbooks": PLAYBOOKS,
        "commands": specs,
    }


def build_openapi_document(specs: list[dict[str, Any]]) -> dict[str, Any]:
    paths: dict[str, Any] = {}
    for spec in specs:
        operation_id = "finance_" + re.sub(r"[^a-zA-Z0-9_]", "_", spec["name"])
        paths[f"/commands/{spec['name']}"] = {
            "post": {
                "operationId": operation_id,
                "summary": spec["description"],
                "description": spec["agent"]["use_when"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": spec["input_schema"],
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Finance CLI result envelope.",
                        "content": {
                            "application/json": {
                                "schema": spec["output_schema"],
                            }
                        },
                    }
                },
                "x-finance-cli": {
                    "command": spec["name"],
                    "usage": spec["usage"],
                    "side_effects": spec["side_effects"],
                    "auth_required": spec["auth_required"],
                    "citation_fields": spec["citation_fields"],
                },
            }
        }
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Finance CLI command adapter contract",
            "version": __version__,
            "description": "OpenAPI-style schema for adapters that expose Finance CLI commands over HTTP, MCP, or tool runtimes. The CLI itself is local.",
        },
        "servers": [{"url": "local://finance-cli", "description": "Adapter-defined local execution endpoint."}],
        "paths": paths,
    }


def build_tools_schema_document() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://tempestshaw.github.io/FinanceCLI/schemas/finance-cli-tools.schema.json",
        "title": "Finance CLI tools schema",
        "type": "object",
        "required": ["name", "version", "result_envelope", "side_effect_levels", "commands"],
        "properties": {
            "$schema": {"type": "string"},
            "name": {"type": "string"},
            "version": {"type": "string"},
            "description": {"type": "string"},
            "canonical_docs": {"type": "string"},
            "result_envelope": {"type": "object"},
            "side_effect_levels": {"type": "object"},
            "trust_policy": {"type": "object"},
            "playbooks": {"type": "array", "items": {"type": "object"}},
            "commands": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "name",
                        "namespace",
                        "description",
                        "usage",
                        "args",
                        "input_schema",
                        "output_schema",
                        "side_effects",
                        "auth_required",
                        "agent",
                    ],
                    "properties": {
                        "name": {"type": "string"},
                        "namespace": {"type": "string"},
                        "description": {"type": "string"},
                        "usage": {"type": "string"},
                        "examples": {"type": "array", "items": {"type": "string"}},
                        "notes": {"type": "array", "items": {"type": "string"}},
                        "args": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "object",
                                "required": ["type", "required", "description"],
                                "properties": {
                                    "type": {},
                                    "required": {"type": "boolean"},
                                    "description": {"type": "string"},
                                    "default": {},
                                    "enum": {"type": "array"},
                                    "format": {"type": "string"},
                                    "items": {"type": "object"},
                                    "aliases": {"type": "array", "items": {"type": "string"}},
                                },
                                "additionalProperties": True,
                            },
                        },
                        "input_schema": {"type": "object"},
                        "output_schema": {"type": "object"},
                        "side_effects": {"enum": sorted(SIDE_EFFECTS)},
                        "side_effects_description": {"type": "string"},
                        "auth_required": {"type": "string"},
                        "rate_limit_notes": {"type": ["string", "null"]},
                        "citation_fields": {"type": "array", "items": {"type": "string"}},
                        "agent": {
                            "type": "object",
                            "required": ["use_when", "next_steps"],
                            "properties": {
                                "use_when": {"type": "string"},
                                "avoid_when": {"type": ["string", "null"]},
                                "next_steps": {"type": "array", "items": {"type": "string"}},
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": True,
                },
            },
        },
        "additionalProperties": True,
    }


def build_llms_txt() -> str:
    return "\n".join([
        "# Finance CLI",
        "",
        "> Public-company research CLI for SEC filings, documents, market data, finance math, and backtests. Commands return JSON envelopes: ok, data, error, warnings.",
        "",
        "## Agent Entry Points",
        "",
        f"- Quick start: {SITE_URL}/quickstart/",
        f"- Agent guide: {SITE_URL}/agents/",
        f"- Agent playbooks: {SITE_URL}/workflows/",
        f"- Trust and citation policy: {SITE_URL}/trust/",
        f"- Human command reference: {SITE_URL}/commands/",
        "",
        "## Machine-Readable Schemas",
        "",
        f"- Tools schema: {SITE_URL}/tools.json",
        f"- OpenAPI-style adapter contract: {SITE_URL}/openapi.json",
        f"- Full LLM context: {SITE_URL}/llms-full.txt",
        f"- MCP/plugin notes: {SITE_URL}/mcp/",
        "",
        "## Routing Rules",
        "",
        "- Use filings.* for SEC filing discovery, sections, XBRL statement rows, and filing reports.",
        "- Use document.* for PDF/HTML text extraction, phrase/table discovery, char windows, tables, and OCR fallback.",
        "- Use formula.* only when numeric inputs are explicit and cited.",
        "- Use valuation.* only for deterministic math with explicit assumptions; do not present it as investment advice.",
        "- Use market.*, sector.*, industry.*, screen.*, and calendar.* for provider-attributed market context.",
        "- Preserve source fields, accessions, URLs, report names, page numbers, offsets, providers, and warnings.",
    ]) + "\n"


def build_llms_full_txt(specs: list[dict[str, Any]]) -> str:
    lines = [
        "# Finance CLI Full Agent Context",
        "",
        "Finance CLI is a local command-line tool for repeatable public-company research. Prefer the machine-readable schema over scraping prose docs.",
        "",
        "## Canonical Files",
        "",
        f"- `tools.json`: {SITE_URL}/tools.json",
        f"- `openapi.json`: {SITE_URL}/openapi.json",
        f"- Human docs: {SITE_URL}/",
        "",
        "## Result Envelope",
        "",
        "Every command returns JSON shaped like:",
        "",
        "```json",
        json.dumps({"ok": True, "data": {}, "error": None, "warnings": []}, indent=2),
        "```",
        "",
        "## Trust Rules",
        "",
        "- Cite accession, URL, report_name, section, page, start_char/end_char, source, provider, and timestamp when available.",
        "- Never claim live market data without provider/source and timestamp/date fields when available.",
        "- Treat Yahoo, FMP, SEC, GDELT, transcripts, and company IR as source-specific records, not ground truth.",
        "- Formula and valuation commands are deterministic calculators, not investment advice.",
        "- If `ok=false`, surface the error clearly and do not fabricate data.",
        "",
        "## Agent Playbooks",
        "",
    ]
    for playbook in PLAYBOOKS:
        lines.extend([
            f"### {playbook['task']}",
            f"Use when: {playbook['when']}",
            "Steps:",
        ])
        lines.extend(f"- {step}" for step in playbook["steps"])
        lines.append("Failure modes:")
        lines.extend(f"- {mode}" for mode in playbook["failure_modes"])
        lines.append("")

    lines.extend(["## Command Routing", ""])
    for spec in specs:
        args = ", ".join(
            f"{name}:{meta.get('type', 'string')}{' required' if meta.get('required') else ''}"
            for name, meta in spec["args"].items()
        ) or "none"
        lines.extend([
            f"### {spec['name']}",
            f"Use when: {spec['agent']['use_when']}",
            f"Avoid when: {spec['agent']['avoid_when'] or 'No command-specific restriction beyond trust rules.'}",
            f"Side effects: {spec['side_effects']}",
            f"Args: {args}",
            f"Usage: `{spec['usage']}`",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def _parse_usage_params(usage: str) -> dict[str, dict[str, Any]]:
    if not usage:
        return {}
    parts = _split_usage(usage)
    tokens = parts[1:]
    params: dict[str, dict[str, Any]] = {}
    for token, optional in tokens:
        for raw_part in _expand_token(token):
            parsed = _parse_token(raw_part, optional=optional)
            if parsed is None:
                continue
            name, meta = parsed
            if name in params:
                params[name] = {**params[name], **meta}
                params[name]["required"] = params[name].get("required", False) or meta.get("required", False)
            else:
                params[name] = meta
    return params


def _split_usage(usage: str) -> list[tuple[str, bool]]:
    tokens: list[tuple[str, bool]] = []
    current: list[str] = []
    optional = False
    for char in usage:
        if char == "[":
            if current:
                tokens.extend((part, optional) for part in _shell_split("".join(current)))
                current = []
            optional = True
            continue
        if char == "]":
            if current:
                tokens.extend((part, True) for part in _shell_split("".join(current)))
                current = []
            optional = False
            continue
        current.append(char)
    if current:
        tokens.extend((part, optional) for part in _shell_split("".join(current)))
    return tokens


def _shell_split(text: str) -> list[str]:
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()


def _expand_token(token: str) -> list[str]:
    token = token.strip(",")
    if not token or token.startswith("(") or token.endswith(")"):
        return []
    if "|" not in token:
        return [token]
    parts = [part for part in token.split("|") if part]
    if all("=" in part for part in parts):
        return parts
    if any("=" in part for part in parts) and "=" not in parts[0]:
        return [part for part in parts if "=" in part]
    return [token]


def _parse_token(token: str, *, optional: bool) -> tuple[str, dict[str, Any]] | None:
    token = token.strip()
    if not token or token.startswith("-"):
        return None
    if "=" in token:
        name, raw_value = token.split("=", 1)
        name = _normalize_param_name(name)
        if not name:
            return None
        meta = _infer_schema_from_value(raw_value)
        meta["required"] = not optional
        if not optional:
            meta.pop("default", None)
        if optional and raw_value not in {"...", "TEXT", "URL", "FIELD"} and "default" not in meta and "|" not in raw_value:
            meta["default"] = _coerce_default(raw_value)
        return name, meta
    name = _normalize_param_name(token)
    if not name:
        return None
    return name, {"type": "string", "required": not optional}


def _normalize_param_name(name: str) -> str:
    name = name.strip("<>[]'\"")
    if not name:
        return ""
    if name == "SYMBOL[,SYMBOL...]":
        return "symbols"
    if name == "SOURCE|source":
        return "source"
    name = name.replace("PATH_OR_URL", "source")
    name = re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_")
    return name.lower()


def _infer_schema_from_value(raw_value: str) -> dict[str, Any]:
    value = raw_value.strip("'\"")
    if "|" in value and not value.startswith("{"):
        enum = [_coerce_default(part) for part in value.split("|") if part and part != "..."]
        return {"type": _common_type_for_enum(enum), "enum": enum}
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return {"type": "boolean", "default": lowered == "true"}
    if re.fullmatch(r"-?\d+", value):
        return {"type": "integer", "default": int(value)}
    if re.fullmatch(r"-?\d+\.\d+", value):
        return {"type": "number", "default": float(value)}
    if value == "YYYY-MM-DD":
        return {"type": "string", "format": "date"}
    if value in {"{}", "'{}'"}:
        return {"type": "object"}
    return {"type": "string"}


def _coerce_default(value: str) -> Any:
    value = value.strip("'\"")
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def _common_type_for_enum(enum: list[Any]) -> str:
    if enum and all(isinstance(item, bool) for item in enum):
        return "boolean"
    if enum and all(isinstance(item, int) for item in enum):
        return "integer"
    if enum and all(isinstance(item, (int, float)) for item in enum):
        return "number"
    return "string"


def _apply_common_param_metadata(params: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    enriched: dict[str, dict[str, Any]] = {}
    for name, meta in params.items():
        common = deepcopy(COMMON_PARAM_OVERRIDES.get(name, {}))
        common.update(meta)
        if "description" not in common:
            common["description"] = f"{name.replace('_', ' ').title()} parameter."
        enriched[name] = common
    return enriched


def _mark_numeric_formula_params(params: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    for name, meta in params.items():
        if name in {"debt_tax"}:
            continue
        if name == "addbacks":
            meta.update({"type": "array", "items": {"type": "number"}, "description": "Comma-separated addback values."})
            continue
        meta.setdefault("description", f"Explicit numeric input for {name}.")
        meta["type"] = "number"
    return params


def _mark_valuation_params(params: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    for name, meta in params.items():
        if name in {"symbol"}:
            continue
        if name in {"cashflows"}:
            meta.update({"type": "array", "items": {"type": "number"}})
            continue
        if any(word in name for word in ("rate", "value", "revenue", "multiple", "shares", "growth")):
            meta["type"] = "number"
    return params


def _input_schema(params: dict[str, dict[str, Any]]) -> dict[str, Any]:
    properties = {}
    required = []
    for name, meta in params.items():
        prop = {key: value for key, value in meta.items() if key not in {"required", "aliases"}}
        properties[name] = prop
        if meta.get("required"):
            required.append(name)
    schema = {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }
    return schema


def _auth_required(namespace: str, command_name: str) -> str:
    if command_name.startswith("sources."):
        return "optional_environment"
    if namespace in {"news", "market", "price", "symbol", "fundamentals", "calendar", "sector", "industry", "screen", "filings", "transcripts", "ir", "kpi"}:
        return "optional_environment_or_public_provider"
    return "none"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


if __name__ == "__main__":
    main()
