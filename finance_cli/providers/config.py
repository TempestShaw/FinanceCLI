"""Provider-level deterministic configuration.

Keep provider heuristics here so API clients stay thin and the matching rules
are easy to audit without digging through request code.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PresentationRules:
    high_terms: tuple[str, ...]
    medium_terms: tuple[str, ...]
    exclude_terms: tuple[str, ...]
    override_terms: tuple[str, ...]
    investor_day_terms: tuple[str, ...]
    earnings_terms: tuple[str, ...]
    ir_terms: tuple[str, ...]
    ir_page_hints: tuple[str, ...]
    navigation_labels: tuple[str, ...]
    match_threshold: float = 90.0
    exclude_threshold: float = 90.0
    override_threshold: float = 90.0


PRESENTATION_RULES = PresentationRules(
    high_terms=(
        "investor day",
        "investor presentation",
        "analyst day",
        "capital markets day",
        "capital markets presentation",
        "earnings presentation",
        "results presentation",
    ),
    medium_terms=(
        "presentation",
        "presentations",
        "slides",
        "slide deck",
        "deck",
        "investor",
        "overview",
        "earnings results",
    ),
    exclude_terms=(
        "press release",
        "press releases",
        "pressrelease",
        "pressrele",
        "news release",
        "news releases",
        "earnings release",
        "financial results",
        "exhibit index",
        "signature",
        "sec filing",
        "sec filings",
        "governance",
        "proxy",
        "code of conduct",
        "privacy",
        "terms of use",
        "email alert",
    ),
    override_terms=("presentation", "slides", "slide deck", "deck"),
    investor_day_terms=("investor day", "analyst day", "capital markets day"),
    earnings_terms=(
        "earnings",
        "quarterly results",
        "q1 ",
        "q2 ",
        "q3 ",
        "q4 ",
        "results presentation",
    ),
    ir_terms=("presentation", "slides", "deck", "investor"),
    ir_page_hints=(
        "investor",
        "investors",
        "investor-relations",
        "events",
        "presentations",
        "financial-results",
        "quarterly-results",
    ),
    navigation_labels=(
        "events",
        "events presentations",
        "presentations",
        "financials",
        "quarterly results",
        "view all events",
        "see all quarter results",
    ),
)


SECTOR_QUERY_EXPANSIONS: dict[str, str] = {
    "TECHNOLOGY": "(technology OR software OR semiconductor OR cloud)",
    "FINANCE": '("financial services" OR banks OR fintech)',
    "ENERGY": "(energy OR oil OR gas OR renewables)",
    "HEALTHCARE": "(healthcare OR biotech OR pharmaceutical)",
    "POLITICS": "(politics OR election OR government)",
}


GDELT_GEO_MODE_ALIASES: dict[str, str] = {
    "animation": "locationtime",
    "article": "article",
    "locationtime": "locationtime",
    "pointanimation": "locationtime",
    "pointdata": "article",
}


GDELT_TIMESPAN_UNIT_MINUTES: dict[str, int] = {
    "min": 1,
    "minute": 1,
    "minutes": 1,
    "mins": 1,
    "h": 60,
    "hr": 60,
    "hrs": 60,
    "hour": 60,
    "hours": 60,
    "d": 1440,
    "day": 1440,
    "days": 1440,
    "w": 10080,
    "wk": 10080,
    "wks": 10080,
    "week": 10080,
    "weeks": 10080,
    "m": 43200,
    "mo": 43200,
    "mon": 43200,
    "month": 43200,
    "months": 43200,
}

GDELT_GEO_MIN_TIMESPAN_MINUTES = 15
GDELT_GEO_MAX_TIMESPAN_MINUTES = 1440


MARKET_BENCHMARKS: dict[str, dict[str, str]] = {
    "US": {
        "primary": "SPY",
        "growth": "QQQ",
        "small_caps": "IWM",
        "volatility": "^VIX",
    }
}


SECTOR_ETFS: dict[str, dict[str, str]] = {
    "US": {
        "Technology": "XLK",
        "Communication Services": "XLC",
        "Consumer Discretionary": "XLY",
        "Consumer Staples": "XLP",
        "Energy": "XLE",
        "Financials": "XLF",
        "Health Care": "XLV",
        "Industrials": "XLI",
        "Materials": "XLB",
        "Real Estate": "XLRE",
        "Utilities": "XLU",
    }
}


DOCUMENT_TOPIC_QUERIES: dict[str, tuple[str, ...]] = {
    "disclosure": (
        "investment disclosure",
        "regulation fd disclosure",
        "forward looking statements",
        "non gaap financial measures",
    ),
    "risk": (
        "risk factors",
        "customer concentration risk",
        "competition risk",
        "macroeconomic risk",
        "cybersecurity risk",
    ),
    "financial_reporting": (
        "financial statements",
        "management discussion and analysis",
        "revenue",
        "gross margin",
        "operating income",
        "free cash flow",
    ),
    "portfolio": (
        "portfolio holdings",
        "holdings",
        "assets under management",
        "investment portfolio",
    ),
    "guidance": (
        "guidance",
        "outlook",
        "annual recurring revenue",
        "remaining performance obligations",
        "net retention",
    ),
}


TRANSCRIPT_QA_START_TERMS: tuple[str, ...] = (
    "open the line up for questions",
    "open the call for questions",
    "take your questions",
    "move to the q&a",
    "begin the question-and-answer",
    "begin the question and answer",
    "question and answer portion",
)

TRANSCRIPT_OPERATOR_TURN_TERMS: tuple[str, ...] = (
    "next question comes from",
    "the next question is from",
    "your next question comes from",
    "this concludes the question",
)

TRANSCRIPT_MARKER_THRESHOLD = 90.0
