"""Research workflow planning helpers.

The planner returns deterministic command checklists. It does not execute
research steps or generate investment conclusions.
"""
from __future__ import annotations

from typing import Any


def research_plan(symbol: str, *, style: str = "fundamental") -> dict[str, Any]:
    """Return a CLI research checklist for a symbol."""
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("symbol is required")
    style_key = style.strip().lower()
    if style_key not in {"fundamental"}:
        raise ValueError("style must be one of: fundamental")
    steps = _fundamental_steps(normalized)
    return {
        "symbol": normalized,
        "style": style_key,
        "plan_type": "deterministic_cli_checklist",
        "steps": steps,
        "count": len(steps),
        "notes": [
            "This is a navigation checklist, not an investment conclusion.",
            "Read returned evidence and choose assumptions before valuation.",
        ],
    }


def _fundamental_steps(symbol: str) -> list[dict[str, Any]]:
    return [
        _step(
            "profile",
            "Establish company identity, quote, market cap, and SEC CIK.",
            [
                f"finance symbol.profile {symbol}",
                f"finance market.quote {symbol}",
            ],
        ),
        _step(
            "filings",
            "Read core 10-K sections for business model, risk, MD&A, and financial statement detail.",
            [
                f"finance filings.recent {symbol} forms=10-K,10-Q,8-K limit=8",
                f"finance filings.sections {symbol} form=10-K",
                f"finance filings.read {symbol} form=10-K section=business max_chars=12000",
                f"finance filings.read {symbol} form=10-K section=risk_factors max_chars=12000",
                f"finance filings.read {symbol} form=10-K section=mda max_chars=12000",
                f"finance filings.read {symbol} form=10-K section=financial_statements max_chars=12000",
            ],
        ),
        _step(
            "transcripts",
            "Read recent earnings calls and analyst Q&A to capture current opportunities and concerns.",
            [
                f"finance transcripts.search {symbol} limit=4",
                f"finance transcripts.read {symbol} quarter=latest max_chars=12000",
                f"finance transcripts.qa {symbol} quarter=latest limit=10",
            ],
        ),
        _step(
            "kpis",
            "Extract KPI evidence without forcing a normalized conclusion.",
            [
                f"finance kpi.extract {symbol} source=both metrics=arr,net_new_arr,large_customers,nrr,rpo,revenue_growth,operating_margin,fcf_margin limit=40",
                f"finance kpi.history {symbol} metrics=arr,large_customers,nrr,revenue_growth limit=4 per_document_limit=12",
            ],
        ),
        _step(
            "price_history",
            "Find major stock moves, then gather source-linked evidence around selected dates.",
            [
                f"finance price.moves {symbol} years=3 threshold=8% limit=20",
                f"finance price.context {symbol} date=MOVE_DATE lookback=3D news_limit=5",
            ],
        ),
        _step(
            "fundamentals",
            "Fetch statement data for revenue, margins, cash flow, debt, and share information.",
            [
                f"finance fundamentals.statement {symbol} statement=income period=annual",
                f"finance fundamentals.statement {symbol} statement=cashflow period=annual",
                f"finance fundamentals.statement {symbol} statement=balance period=annual",
            ],
        ),
        _step(
            "valuation",
            "Calculate current multiples and user-supplied valuation scenarios after assumptions are chosen.",
            [
                f"finance valuation.multiples {symbol}",
                f"finance valuation.scenario {symbol} revenue=REVENUE_ASSUMPTION bear_multiple=BEAR base_multiple=BASE bull_multiple=BULL",
                "finance valuation.dcf cashflows=FCF1,FCF2,FCF3 discount_rate=WACC terminal_growth=G",
            ],
        ),
        {
            "id": "open_gaps",
            "status": "partially_supported",
            "objective": "Note remaining workflow gaps that require judgment outside the CLI.",
            "commands": [],
            "missing": [
                "Investor Day deck retrieval",
                "Expert call transcripts",
                "Market consensus estimate comparison",
            ],
        },
    ]


def _step(step_id: str, objective: str, commands: list[str]) -> dict[str, Any]:
    return {
        "id": step_id,
        "status": "supported",
        "objective": objective,
        "commands": commands,
    }
