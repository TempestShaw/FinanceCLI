"""Meta: did the business become more efficient after the Year of Efficiency?"""
from __future__ import annotations

import re
from typing import Any

from evidence import EvidenceError, billions, load, pct, quote, source, statement_value, trace_entry
from finance_cli.services.formulas import formula_margin

CASE = "meta-efficiency"
REVENUE = "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax"
COSTS = "us-gaap_CostsAndExpenses"
OPERATING = "us-gaap_OperatingIncomeLoss"
YEARS = {  # year -> (statement step, period, MD&A step)
    2022: ("03-income-fy24", "2022-12-31", "04-mda-fy22"),
    2023: ("02-income-fy25", "2023-12-31", "05-mda-fy23"),
    2024: ("02-income-fy25", "2024-12-31", "06-mda-fy24"),
    2025: ("02-income-fy25", "2025-12-31", "07-mda-fy25"),
}
RESTRUCTURING_QUOTES = {  # year -> (phrase to quote, amount in USD stated by that phrase)
    2022: ("which resulted in total restructuring charges of $4.61 billion in 2022", 4.61e9),
    2023: ("Total$2,506 $1,170 $(224)$3,452", 3.452e9),
}


def _headcount(year: int, mda_step: str) -> tuple[int, str]:
    ev = load(CASE, mda_step)
    sentence = quote(ev, "Headcount was")
    match = re.search(r"Headcount was ([\d,]+) as of December 31, (\d{4})", sentence)
    if not match or int(match.group(2)) != year:
        raise EvidenceError(f"{ev.path_label}: no year-end {year} headcount")
    return int(match.group(1).replace(",", "")), sentence


def _year(year: int) -> dict[str, Any]:
    step, period, mda_step = YEARS[year]
    ev = load(CASE, step)
    revenue = statement_value(ev, REVENUE, "Revenue", period)
    costs = statement_value(ev, COSTS, "Total costs and expenses", period)
    operating = statement_value(ev, OPERATING, "Income (loss) from operations", period)
    headcount, headcount_quote = _headcount(year, mda_step)
    restructuring = RESTRUCTURING_QUOTES.get(year)
    charge = restructuring[1] if restructuring else None
    if restructuring:
        quote(load(CASE, mda_step), restructuring[0])
    return {
        "year": year, "revenue": revenue, "costs": costs, "operating": operating, "headcount": headcount,
        "headcount_quote": headcount_quote, "restructuring": charge,
        "margin": formula_margin(numerator=operating, denominator=revenue)["margin"],
        "margin_ex": formula_margin(numerator=operating + charge, denominator=revenue)["margin"] if charge else None,
        "revenue_per_head": revenue / headcount,
        "url": ev.filing["filing_url"], "accession": ev.filing["accession_no"],
    }


def _per_head(year: dict[str, Any]) -> str:
    return f"${year['revenue_per_head'] / 1e6:.2f}M"


def build() -> dict[str, Any]:
    years = [_year(y) for y in sorted(YEARS)]
    y22, y23, y24, y25 = years
    growth = lambda a, b, key: b[key] / a[key] - 1  # noqa: E731
    layoff_note = quote(load(CASE, "04-mda-fy22"), "Our reported headcount includes a substantial majority")
    mda25 = load(CASE, "07-mda-fy25")
    philosophy = quote(mda25, "We remain focused on operating efficiently while investing in significant opportunities")
    filings = load(CASE, "01-annual-filings")
    listed = len(filings.data["filings"])

    return {
        "slug": CASE,
        "title": "Meta after the Year of Efficiency",
        "kicker": "Open-ended investigation",
        "question": "Did Meta actually become more efficient after the Year of Efficiency?",
        "headline": f"Operating margin went from {pct(y22['margin'])} to {pct(y24['margin'])} in two years. Excluding restructuring charges, the improvement still holds.",
        "answer": [
            f"Yes, by the filings’ own numbers. In 2023 total costs and expenses rose {pct(growth(y22, y23, 'costs'))} while revenue grew {pct(growth(y22, y23, 'revenue'))}. Operating margin moved from {pct(y22['margin'])} (2022) to {pct(y23['margin'])} (2023) and {pct(y24['margin'])} (2024).",
            f"Restructuring charges flatter the jump, but don’t explain it. Adding back {billions(y22['restructuring'], 2)} in 2022 and {billions(y23['restructuring'], 2)} in 2023, the margin still rises from {pct(y22['margin_ex'])} to {pct(y23['margin_ex'])}.",
            f"Revenue per year-end employee rose from {_per_head(y22)} to {_per_head(y25)}. The 2022 headcount still counted most of the roughly 11,000 employees laid off that November, which inflates the before-and-after contrast.",
            f"2025 points the other way: costs grew {pct(growth(y24, y25, 'costs'))} against {pct(growth(y24, y25, 'revenue'))} revenue growth and the margin slipped to {pct(y25['margin'])}, as AI infrastructure and hiring resumed.",
        ],
        "metrics": [
            {"label": "Operating margin, 2022 → 2024", "value": f"{pct(y22['margin'])} → {pct(y24['margin'])}", "delta": f"2025: {pct(y25['margin'])}"},
            {"label": "Costs vs revenue growth, 2023", "value": f"{pct(growth(y22, y23, 'costs'))} vs {pct(growth(y22, y23, 'revenue'))}", "delta": "costs held flat"},
            {"label": "Headcount, year-end", "value": f"{y22['headcount']:,} → {y23['headcount']:,}", "delta": f"2025: {y25['headcount']:,}"},
        ],
        "table": {
            "caption": "Meta consolidated results. Calendar fiscal years. Restructuring charges are taken from MD&A; 2024–2025 amounts were not separately quantified in the sections read.",
            "columns": [
                {"key": "year", "label": "Year"},
                {"key": "revenue", "label": "Revenue", "align": "end"},
                {"key": "costs", "label": "Costs & expenses", "align": "end"},
                {"key": "margin", "label": "Operating margin", "align": "end"},
                {"key": "margin_ex", "label": "Ex-restructuring", "align": "end"},
                {"key": "headcount", "label": "Headcount", "align": "end"},
            ],
            "rows": [
                {"year": str(y["year"]), "revenue": billions(y["revenue"]), "costs": billions(y["costs"]), "margin": pct(y["margin"]),
                 "margin_ex": pct(y["margin_ex"]) if y["margin_ex"] is not None else "n/q", "headcount": f"{y['headcount']:,}", "url": y["url"]}
                for y in years
            ],
        },
        "chart": {
            "kind": "lines",
            "label": "Operating margin",
            "series": [
                {"key": "Reported", "points": [{"x": str(y["year"]), "value": round(y["margin"] * 100, 1)} for y in years]},
                {"key": "Ex-restructuring", "points": [{"x": str(y["year"]), "value": round(y["margin_ex"] * 100, 1)} for y in years if y["margin_ex"]]},
            ],
            "headcount": [{"x": str(y["year"]), "value": y["headcount"]} for y in years],
        },
        "calculations": [
            {"label": "Operating margin, 2023", "method": "Income from operations / revenue",
             "inputs": f"{y23['operating']:,.0f} / {y23['revenue']:,.0f}", "result": pct(y23["margin"], 2)},
            {"label": "Margin ex-restructuring, 2023", "method": "(Income from operations + restructuring) / revenue",
             "inputs": f"({y23['operating']:,.0f} + {y23['restructuring']:,.0f}) / {y23['revenue']:,.0f}", "result": pct(y23["margin_ex"], 2)},
            {"label": "Revenue per year-end employee, 2025", "method": "Revenue / year-end headcount",
             "inputs": f"{y25['revenue']:,.0f} / {y25['headcount']:,}", "result": _per_head(y25)},
        ],
        "checks": [
            {"status": "caveat", "label": "2022 headcount includes announced layoffs", "detail": layoff_note},
            {"status": "missing", "label": "Restructuring after 2023 not quantified",
             "detail": "The 2024 and 2025 MD&A sections mention lower restructuring costs without a total, so those years are shown as reported only."},
            {"status": "caveat", "label": "Filing list was incomplete",
             "detail": f"filings.recent listed only the {listed} most recent 10-Ks for Meta, because it reads SEC’s recent-submissions window and Meta files thousands of insider forms. The agent passed the FY2022 and FY2023 accession numbers directly; the CLI confirmed each one’s company, form and period."},
            {"status": "verified", "label": "Management’s framing", "detail": philosophy},
        ],
        "quotes": [{"text": layoff_note, "source": source(load(CASE, "04-mda-fy22"))["label"]}],
        "trace": [
            trace_entry(filings, f"Only {listed} annual reports listed (FY2024, FY2025). Older ones are outside SEC’s recent window.",
                        note="Gap found: the agent supplied the FY2022 and FY2023 accession numbers directly."),
            trace_entry(load(CASE, "02-income-fy25"), "Revenue, total costs and operating income for 2023–2025."),
            trace_entry(load(CASE, "03-income-fy24"), "The 2022 baseline."),
            trace_entry(load(CASE, "04-mda-fy22"), f"Headcount {y22['headcount']:,}, restructuring {billions(y22['restructuring'], 2)}, layoffs still counted."),
            trace_entry(load(CASE, "05-mda-fy23"), f"Headcount {y23['headcount']:,} (−22%), restructuring {billions(y23['restructuring'], 3)}."),
            trace_entry(load(CASE, "06-mda-fy24"), f"Headcount {y24['headcount']:,}."),
            trace_entry(mda25, f"Headcount {y25['headcount']:,}; R&D up on AI compensation and infrastructure."),
            {"id": "08-calculate", "tool": "formula.margin", "command": f"finance formula.margin numerator={y23['operating'] / 1e6:.0f}M denominator={y23['revenue'] / 1e6:.0f}M",
             "purpose": "Margins, ex-restructuring margins and revenue per head, with inputs.",
             "result": f"2023 operating margin {pct(y23['margin'], 2)}; ex-restructuring {pct(y23['margin_ex'], 2)}."},
        ],
        "sources": [source(load(CASE, s)) for s in ("02-income-fy25", "03-income-fy24", "04-mda-fy22", "05-mda-fy23")],
        "prompt": "Use Finance CLI to test whether Meta became more efficient after its 2023 Year of Efficiency. Choose your own tools. Use 10-K statements and MD&A, separate restructuring charges, compare operating margin and headcount from 2022 to the latest year, and cite every source. Flag anything that makes the comparison unfair.",
    }
