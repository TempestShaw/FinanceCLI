"""Live CLI contract diagnostics.

These tests intentionally call the real CLI without monkeypatching providers.
They are skipped by default because many commands depend on network providers,
local OCR/table tooling, or third-party rate limits.

Run:
    FINANCECLI_LIVE=1 python -m pytest tests/test_live_cli_contracts.py -s

Artifacts:
    .pytest_cache/finance_cli_live/<command>.json
    .pytest_cache/finance_cli_live/summary.json
    Each artifact includes json.duration_seconds and json.attempts for CLI subprocess calls.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.registry import clear_commands, list_commands


pytestmark = pytest.mark.skipif(os.getenv("FINANCECLI_LIVE") != "1", reason="set FINANCECLI_LIVE=1 to run live CLI diagnostics")

LIVE_TIMEOUT_SECONDS = int(os.getenv("FINANCECLI_LIVE_TIMEOUT", "90"))
LIVE_MAX_ATTEMPTS = int(os.getenv("FINANCECLI_LIVE_ATTEMPTS", "3"))
LIVE_RETRY_DELAY_SECONDS = float(os.getenv("FINANCECLI_LIVE_RETRY_DELAY", "60"))
STRICT_LIVE = os.getenv("FINANCECLI_LIVE_STRICT") == "1"
ARTIFACT_DIR = Path(".pytest_cache/finance_cli_live")
SUMMARY_PATH = ARTIFACT_DIR / "summary.json"
SAMPLE_DOC = ARTIFACT_DIR / "sample.html"
SAMPLE_TABLE_PDF_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
SENSITIVE_ENV_NAMES = (
    "FMP_API_KEY",
    "ALPHAVANTAGE_API_KEY",
    "ALPHA_VANTAGE_API_KEY",
    "ALPACA_API_KEY",
    "ALPACA_API_SECRET",
    "FINANCE_API_KEY",
    "NEWS_API_KEY",
)


LIVE_COMMAND_CASES: dict[str, list[str]] = {
    "backtest.describe": ["sma_cross"],
    "backtest.factor.payload": ["rsi_14", "AAPL,MSFT", "2024-01-01", "2024-02-01", "top_pct=0.5", "bottom_pct=0.5"],
    "backtest.factor.weights": ["rsi_14", 'scores={"AAPL":1.1,"MSFT":0.3}', "top_pct=0.5", "bottom_pct=0.5"],
    "backtest.run": ["sma_cross", "AAPL", "2024-01-01", "2024-02-01", "fast=5", "slow=10"],
    "backtest.strategies": [],
    "backtest.strategy.payload": ["mean_reversion", "2024-01-01", "2024-02-01"],
    "backtest.tune": ["sma_cross", "AAPL", "2024-01-01", "2024-02-01", 'grid={"fast":[5],"slow":[10]}', "max_runs=1"],
    "calendar.company": ["AAPL"],
    "calendar.earnings": ["AAPL", "limit=3"],
    "document.ocr": [str(SAMPLE_DOC), "max_chars=500", "max_pages=1"],
    "document.read": [str(SAMPLE_DOC), "format=html", "max_chars=500"],
    "document.scan": [str(SAMPLE_DOC), "format=html", "query=revenue", "limit=3", "max_chars=500"],
    "document.tables": [SAMPLE_TABLE_PDF_URL, "pages=1", "flavor=stream", "max_tables=1", "max_rows=3"],
    "document.window": [str(SAMPLE_DOC), "format=html", "start_char=0", "chars=120"],
    "estimates.compare": ["IOT", "revenue=2.2B", "consensus_revenue=2.0B", "eps=0.50", "consensus_eps=0.45", "fiscal_year=2027"],
    "estimates.consensus": ["IOT", "period=annual", "limit=2"],
    "filings.read": ["AAPL", "form=10-K", "section=business", "max_chars=500"],
    "filings.recent": ["AAPL", "forms=10-K,10-Q", "limit=2"],
    "filings.report": ["COST", "form=10-K", "name=Consolidated Balance Sheets (Parenthetical)", "max_rows=2", "max_chars=500"],
    "filings.reports": ["COST", "form=10-K", "query=lease"],
    "filings.sections": ["AAPL", "form=10-K"],
    "filings.statement": ["COST", "statement=balance", "view=standard", "query=Common Stock", "max_rows=2"],
    "formula.adjusted_ebitda": ["ebit=9285", "d_and_a=2237", "addbacks=284,163"],
    "formula.cagr": ["start=100", "end=150", "periods=3"],
    "formula.capm": ["risk_free=4.617%", "beta=0.79", "market_return=11%"],
    "formula.days": ["current=2721", "prior=2285", "denominator=254453"],
    "formula.ebitda": ["ebit=9285", "d_and_a=2237"],
    "formula.enterprise_value": ["market_equity=418856", "debt=11415", "cash=11144", "operating_cash=5089"],
    "formula.lease_equivalent": ["base_liability=2554", "variable_cost=163", "operating_cost=284"],
    "formula.margin": ["numerator=11969", "denominator=254453"],
    "formula.net_debt": ["debt=11415", "cash=11144", "operating_cash=5089"],
    "formula.operating_cash": ["revenue=254453", "cash_like_assets=11144", "percent_revenue=2%"],
    "formula.operating_current_assets": ["current_assets=34246", "cash_like_assets=11144", "operating_cash=5089"],
    "formula.operating_current_liabilities": ["current_liabilities=35464", "interest_bearing_current_debt=103"],
    "formula.roic": ["nopat=7113", "invested_capital=28077"],
    "formula.turnover": ["numerator=222358", "current=18647", "prior=16651"],
    "formula.wacc": ["equity_value=418856", "debt_value=11415", "cost_of_equity=9.66%", "cost_of_debt=6%", "tax_rate=24%", "debt_tax=pretax"],
    "formula.working_capital": ["operating_current_assets=28191", "operating_current_liabilities=35035"],
    "fundamentals.metrics": ["NVDA", "period=quarterly", "metrics=revenue,eps,net_income,operating_income"],
    "fundamentals.statement": ["NVDA", "statement=income", "period=quarterly", "provider=sec"],
    "industry.keys": ["sector=technology"],
    "industry.overview": ["software-infrastructure"],
    "industry.table": ["software-infrastructure", "table=top_companies", "limit=3"],
    "ir.presentations": ["IOT", "limit=3", "source=sec"],
    "ir.read": ["url=https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/aapl-20260328.htm", "max_chars=500", "ocr=off"],
    "market.ohlcv": ["AAPL", "timeframe=1d", "limit=3"],
    "market.quote": ["AAPL"],
    "market.regime": ["US", "swing"],
    "market.sector_heat": ["US", "5", "sector"],
    "market.status": ["US"],
    "news.analyze": ["symbol=NVDA", "analysis=timeline", "timespan=1d", "max_records=3"],
    "news.search": ["symbol=NVDA", "timespan=1d", "max_records=3"],
    "ownership.holders": ["NVDA", "limit=2"],
    "price.context": ["IOT", "date=2026-03-06", "lookback=3D", "news_limit=2", "filing_limit=5", "transcript_limit=2"],
    "price.moves": ["IOT", "years=1", "threshold=8%", "limit=3"],
    "price.performance": ["NVDA", "benchmark=SPY", "periods=1M,3M"],
    "research.plan": ["IOT", "style=fundamental"],
    "screen.predefined": [],
    "screen.run": ["day_gainers", "count=3"],
    "sector.industries": ["technology"],
    "sector.keys": [],
    "sector.overview": ["technology"],
    "sector.table": ["technology", "table=top_companies", "limit=3"],
    "sources.list": [],
    "sources.status": [],
    "sources.test": ["yfinance", "symbol=AAPL", "timeout=10"],
    "symbol.profile": ["IOT"],
    "symbol.snapshot": ["NVDA"],
    "transcripts.qa": ["IOT", "quarter=latest", "limit=3"],
    "transcripts.read": ["IOT", "quarter=latest", "max_chars=500"],
    "transcripts.search": ["IOT", "limit=2"],
    "valuation.dcf": ["cashflows=100M,120M,140M", "discount_rate=10%", "terminal_growth=3%"],
    "valuation.irr": ["cashflows=-100M,30M,40M,50M"],
    "valuation.multiples": ["IOT"],
    "valuation.npv": ["cashflows=-100M,30M,40M,50M", "discount_rate=10%"],
    "valuation.scenario": ["IOT", "revenue=2.2B", "bear_multiple=7", "base_multiple=10", "bull_multiple=13", "shares=580M"],
    "valuation.wacc": ["equity_value=10B", "debt_value=1B", "cost_of_equity=10%", "cost_of_debt=5%", "tax_rate=21%"],
}

LIVE_COMMAND_VARIANTS: dict[str, tuple[str, list[str]]] = {
    "filings.statement.raw": ("filings.statement", ["COST", "statement=balance", "view=raw", "query=Common Stock", "max_rows=2"]),
}

def test_live_cases_cover_every_registered_command() -> None:
    assert set(LIVE_COMMAND_CASES) == set(_registered_command_names())


@pytest.fixture(scope="session", autouse=True)
def _live_summary_writer() -> Any:
    yield
    if os.getenv("FINANCECLI_LIVE") == "1":
        _write_live_summary()


@pytest.mark.parametrize("command", sorted(LIVE_COMMAND_CASES))
def test_live_command_json_contract(command: str) -> None:
    _ensure_sample_doc()
    args = LIVE_COMMAND_CASES[command]
    json_run, payload, attempts = _run_cli_json_with_retries([command, *args, "--output", "json"])
    json_summary = _summarize_run(json_run, payload)
    json_summary["attempt_count"] = len(attempts)
    json_summary["max_attempts"] = LIVE_MAX_ATTEMPTS
    json_summary["retry_delay_seconds"] = LIVE_RETRY_DELAY_SECONDS
    json_summary["total_call_duration_seconds"] = round(sum(attempt["duration_seconds"] for attempt in attempts), 3)
    json_summary["attempts"] = attempts
    artifact: dict[str, Any] = {
        "command": command,
        "namespace": command.split(".", 1)[0],
        "args": args,
        "json": json_summary,
    }

    _write_artifact(command, artifact)
    print(json.dumps(artifact, ensure_ascii=False, sort_keys=True))

    assert json_run.returncode in {0, 1, 124}
    assert set(payload) >= {"ok", "data", "error", "warnings"}
    if STRICT_LIVE:
        assert json_run.returncode == 0
        assert payload["ok"] is True


@pytest.mark.parametrize("case_id", sorted(LIVE_COMMAND_VARIANTS))
def test_live_command_json_contract_variants(case_id: str) -> None:
    command, args = LIVE_COMMAND_VARIANTS[case_id]
    json_run, payload, attempts = _run_cli_json_with_retries([command, *args, "--output", "json"])
    json_summary = _summarize_run(json_run, payload)
    json_summary["attempt_count"] = len(attempts)
    json_summary["max_attempts"] = LIVE_MAX_ATTEMPTS
    json_summary["retry_delay_seconds"] = LIVE_RETRY_DELAY_SECONDS
    json_summary["total_call_duration_seconds"] = round(sum(attempt["duration_seconds"] for attempt in attempts), 3)
    json_summary["attempts"] = attempts
    artifact: dict[str, Any] = {
        "command": command,
        "case_id": case_id,
        "namespace": command.split(".", 1)[0],
        "args": args,
        "json": json_summary,
    }

    _write_artifact(case_id, artifact)
    print(json.dumps(artifact, ensure_ascii=False, sort_keys=True))

    assert json_run.returncode in {0, 1, 124}
    assert set(payload) >= {"ok", "data", "error", "warnings"}
    if STRICT_LIVE:
        assert json_run.returncode == 0
        assert payload["ok"] is True


def _registered_command_names() -> list[str]:
    clear_commands()
    register_builtin_commands()
    return sorted(command.name for command in list_commands())


def _run_cli_json_with_retries(args: list[str]) -> tuple[subprocess.CompletedProcess[str], dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    for attempt in range(1, LIVE_MAX_ATTEMPTS + 1):
        run = _run_cli(args)
        payload = _parse_json_payload(run)
        summary = _summarize_run(run, payload)
        summary["attempt"] = attempt
        attempts.append(summary)
        if not _should_retry_live_run(run, payload) or attempt == LIVE_MAX_ATTEMPTS:
            return run, payload, attempts
        time.sleep(LIVE_RETRY_DELAY_SECONDS)
    raise AssertionError("unreachable live retry state")


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "-m", "finance_cli.cli", *args]
    start = time.perf_counter()
    try:
        run = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            timeout=LIVE_TIMEOUT_SECONDS,
            check=False,
        )
        run.duration_seconds = time.perf_counter() - start
        return run
    except subprocess.TimeoutExpired as exc:
        duration_seconds = time.perf_counter() - start
        payload = {
            "ok": False,
            "data": None,
            "error": f"CLI command timed out after {LIVE_TIMEOUT_SECONDS} seconds",
            "warnings": [],
        }
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        run = subprocess.CompletedProcess(command, 124, stdout=json.dumps(payload), stderr=stderr)
        run.duration_seconds = duration_seconds
        return run


def _should_retry_live_run(run: subprocess.CompletedProcess[str], payload: dict[str, Any]) -> bool:
    if payload.get("ok") is True and run.returncode == 0:
        return False
    error = str(payload.get("error") or "").lower()
    transient_markers = (
        "429",
        "rate limit",
        "too many",
        "timed out",
        "timeout",
        "temporarily unavailable",
        "connection reset",
    )
    return run.returncode == 124 or any(marker in error for marker in transient_markers)


def _parse_json_payload(run: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        payload = json.loads(run.stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(f"CLI returned non-JSON output\nexit={run.returncode}\nstdout={run.stdout[:1000]}\nstderr={run.stderr[:1000]}\nerror={exc}")
    if not isinstance(payload, dict):
        pytest.fail(f"CLI JSON output was not an object: {type(payload).__name__}")
    return payload


def _summarize_run(run: subprocess.CompletedProcess[str], payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    ok = payload.get("ok") is True and run.returncode == 0
    return {
        "exit_code": run.returncode,
        "duration_seconds": round(getattr(run, "duration_seconds", 0.0), 3),
        "ok": payload.get("ok"),
        "error": _redact_text(payload.get("error")),
        "warnings": payload.get("warnings") or [],
        "failure_payload": _redacted_payload(payload) if not ok else None,
        "data_shape": _shape(data),
        "data_counts": _counts(data),
        "stdout_preview": _preview(_redact_text(run.stdout)),
        "stderr_preview": _preview(_redact_text(run.stderr)),
    }


def _shape(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _shape(value[key]) for key in sorted(value)[:20]}
    if isinstance(value, list):
        return {"type": "list", "len": len(value), "item": _shape(value[0]) if value else None}
    return type(value).__name__


def _counts(value: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, list):
                counts[key] = len(item)
            elif isinstance(item, dict):
                nested = _counts(item)
                for nested_key, nested_count in nested.items():
                    counts[f"{key}.{nested_key}"] = nested_count
    return counts


def _preview(text: str, *, limit: int = 800) -> str:
    cleaned = " ".join(text.split())
    return cleaned[:limit]


def _redact_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    for name in SENSITIVE_ENV_NAMES:
        secret = os.getenv(name)
        if secret:
            text = text.replace(secret, "<redacted>")
    return re.sub(r"(?i)((?:api[-_]?key|apikey|access_token|token|client_secret|secret)=)[^&\\s\"']+", r"\1<redacted>", text)


def _write_artifact(command: str, artifact: dict[str, Any]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / f"{command.replace('.', '__')}.json"
    path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def _write_live_summary() -> None:
    artifacts = []
    for path in sorted(ARTIFACT_DIR.glob("*.json")):
        if path.name == SUMMARY_PATH.name:
            continue
        try:
            artifact = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(artifact, dict) and isinstance(artifact.get("json"), dict):
            artifacts.append(artifact)

    commands = [_summary_command_row(artifact) for artifact in artifacts]
    failed = [row for row in commands if not row["ok"]]
    retried = [row for row in commands if row["attempt_count"] > 1]
    slowest = sorted(commands, key=lambda row: row["total_call_duration_seconds"], reverse=True)[:15]
    completed_commands = {str(row["command"]) for row in commands}
    expected_commands = set(LIVE_COMMAND_CASES)

    summary = {
        "expected_command_count": len(expected_commands),
        "command_count": len(commands),
        "missing_commands": sorted(expected_commands - completed_commands),
        "ok_count": len([row for row in commands if row["ok"]]),
        "failed_count": len(failed),
        "retried_count": len(retried),
        "slowest": slowest,
        "failed": failed,
        "retried": retried,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def _summary_command_row(artifact: dict[str, Any]) -> dict[str, Any]:
    result = artifact["json"]
    return {
        "command": artifact.get("command"),
        "namespace": artifact.get("namespace"),
        "ok": result.get("ok") is True,
        "exit_code": result.get("exit_code"),
        "duration_seconds": result.get("duration_seconds") or 0,
        "total_call_duration_seconds": result.get("total_call_duration_seconds") or result.get("duration_seconds") or 0,
        "attempt_count": result.get("attempt_count") or 1,
        "error": result.get("error"),
        "failure_payload": result.get("failure_payload"),
    }


def _redacted_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(_redact_text(json.dumps(payload, ensure_ascii=False, default=str)) or "{}")


def _ensure_sample_doc() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if not SAMPLE_DOC.exists():
        SAMPLE_DOC.write_text(
            """
            <html>
              <body>
                <h1>Sample Filing</h1>
                <p>Revenue increased while risk factors remained focused on demand, supply, and liquidity.</p>
                <table><tr><th>metric</th><th>value</th></tr><tr><td>revenue</td><td>100</td></tr></table>
              </body>
            </html>
            """,
            encoding="utf-8",
        )
