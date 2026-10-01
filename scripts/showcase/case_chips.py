"""NVIDIA, AMD and Broadcom: who increased R&D intensity fastest?"""
from __future__ import annotations

from datetime import date
from typing import Any

from evidence import billions, load, statement_value, pct, points, quote, source, trace_entry
from finance_cli.services.formulas import formula_margin

CASE = "chip-rnd"
RND = "us-gaap_ResearchAndDevelopmentExpense"
COMPANIES = (  # ticker, evidence step, revenue concept, revenue label, fiscal-year note
    ("NVDA", "01-nvda-income", "us-gaap_Revenues", "Revenue", "ends late January"),
    ("AMD", "02-amd-income", "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax", "Net revenue", "ends late December"),
    ("AVGO", "03-avgo-income", "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax", "Total net revenue", "ends late Oct / early Nov"),
)


def _fiscal_label(period: str) -> str:
    # All three companies name a fiscal year after the calendar year in which it ends.
    return f"FY{date.fromisoformat(period).year}"


def _company(ticker: str, step: str, concept: str, label: str, fy_note: str) -> dict[str, Any]:
    ev = load(CASE, step)
    periods = sorted(ev.data["periods"])
    years = []
    for period in periods:
        revenue = statement_value(ev, concept, label, period)
        rnd = statement_value(ev, RND, "Research and development", period)
        years.append({"period_end": period, "fy": _fiscal_label(period), "revenue": revenue, "rnd": rnd,
                      "intensity": formula_margin(numerator=rnd, denominator=revenue)["margin"]})
    first, last = years[0], years[-1]
    return {"ticker": ticker, "company": ev.filing["company"], "fy_note": fy_note, "years": years, "ev": ev,
            "change": last["intensity"] - first["intensity"], "rnd_growth": last["rnd"] / first["rnd"] - 1,
            "revenue_growth": last["revenue"] / first["revenue"] - 1}



def build() -> dict[str, Any]:
    companies = [_company(*spec) for spec in COMPANIES]
    by = {c["ticker"]: c for c in companies}
    nvda, amd, avgo = by["NVDA"], by["AMD"], by["AVGO"]
    rising = [c for c in companies if c["change"] > 0]
    avgo_mda, nvda_mda = load(CASE, "04-avgo-mda"), load(CASE, "05-nvda-mda")
    vmware = quote(avgo_mda, "we acquired VMware, Inc.")
    nvda_driver = quote(nvda_mda, "The increases in research and development expenses for fiscal year 2026")

    return {
        "slug": CASE,
        "title": "R&D intensity across three chipmakers",
        "kicker": "Cross-company comparison",
        "question": "Compare NVDA, AMD and AVGO R&D intensity over their last three fiscal years. Who increased it fastest?",
        "headline": f"Only Broadcom’s R&D intensity rose ({points(avgo['change'])}), and an acquisition explains it. NVIDIA grew R&D fastest in dollars while its ratio fell.",
        "answer": [
            f"Of the three, only Broadcom’s R&D intensity rose: {pct(avgo['years'][0]['intensity'])} → {pct(avgo['years'][-1]['intensity'])}. The jump happened in FY2024, the first year after Broadcom closed the VMware acquisition on November 22, 2023. Treat it as an acquisition effect, not a change in organic spending.",
            f"NVIDIA increased R&D the most in dollars ({billions(nvda['years'][0]['rnd'])} → {billions(nvda['years'][-1]['rnd'])}, {pct(nvda['rnd_growth'], 0)}), yet its intensity fell from {pct(nvda['years'][0]['intensity'])} to {pct(nvda['years'][-1]['intensity'])} because revenue grew {pct(nvda['revenue_growth'], 0)}.",
            f"AMD remains the most R&D-intensive at {pct(amd['years'][-1]['intensity'])}, down {abs(amd['change']) * 100:.1f} points as revenue outgrew spending.",
            "The question has no clean answer: “increased fastest” depends on whether you measure the ratio or the dollars, and the only rising ratio comes from M&A.",
        ],
        "metrics": [
            {"label": f"{c['ticker']} R&D / revenue, {c['years'][-1]['fy']}", "value": pct(c["years"][-1]["intensity"]),
             "delta": points(c["change"]) + f" vs {c['years'][0]['fy']}"}
            for c in companies
        ],
        "alignment": [
            {"ticker": c["ticker"], "fy_note": c["fy_note"],
             "periods": [{"fy": y["fy"], "period_end": y["period_end"]} for y in c["years"]]}
            for c in companies
        ],
        "table": {
            "caption": "R&D expense divided by total revenue, from each company’s latest 10-K. Fiscal years are kept as reported; they do not end in the same month.",
            "columns": [
                {"key": "ticker", "label": "Company"},
                {"key": "fy", "label": "Fiscal year"},
                {"key": "period_end", "label": "Period end"},
                {"key": "rnd", "label": "R&D", "align": "end"},
                {"key": "revenue", "label": "Revenue", "align": "end"},
                {"key": "intensity", "label": "R&D / revenue", "align": "end"},
            ],
            "rows": [
                {"ticker": c["ticker"], "fy": y["fy"], "period_end": y["period_end"], "rnd": billions(y["rnd"], 2),
                 "revenue": billions(y["revenue"], 1), "intensity": pct(y["intensity"]), "url": c["ev"].filing["filing_url"]}
                for c in companies for y in c["years"]
            ],
        },
        "chart": {
            "kind": "lines",
            "label": "R&D as % of revenue",
            "series": [
                {"key": c["ticker"], "points": [{"x": f"Y{i + 1}", "fy": y["fy"], "value": round(y["intensity"] * 100, 1)}
                                                for i, y in enumerate(c["years"])]}
                for c in companies
            ],
        },
        "calculations": [
            {"label": f"{c['ticker']} R&D intensity, {c['years'][-1]['fy']}", "method": "R&D expense / total revenue",
             "inputs": f"{c['years'][-1]['rnd']:,.0f} / {c['years'][-1]['revenue']:,.0f}", "result": pct(c["years"][-1]["intensity"], 2)}
            for c in companies
        ],
        "checks": [
            {"status": "caveat", "label": "Fiscal years don’t line up",
             "detail": "NVIDIA’s FY2026 ended January 25, 2026; AMD’s FY2025 ended December 27, 2025; Broadcom’s FY2025 ended November 2, 2025. Each column compares a company with itself, not identical calendar periods."},
            {"status": "caveat", "label": "Acquisition changes the base", "detail": vmware},
            {"status": "verified", "label": "What drove NVIDIA’s R&D", "detail": nvda_driver},
            {"status": "verified", "label": "Rising ratios", "detail": ", ".join(c["ticker"] for c in rising) + " only."},
        ],
        "quotes": [{"text": vmware, "source": source(avgo_mda)["label"]}],
        "trace": [
            trace_entry(nvda["ev"], "Revenue and R&D for FY2024–FY2026 (periods end in January)."),
            trace_entry(amd["ev"], "Net revenue and R&D for FY2023–FY2025 (periods end in December)."),
            trace_entry(avgo["ev"], "Total net revenue and R&D for FY2023–FY2025 (periods end in Oct/Nov)."),
            trace_entry(avgo_mda, "VMware acquisition closed November 22, 2023: explains the FY2024 step-up."),
            trace_entry(nvda_mda, "R&D growth driven by compensation and compute/infrastructure spend."),
            {"id": "06-calculate", "tool": "formula.margin", "command": "finance formula.margin numerator=18497 denominator=215938",
             "purpose": "Compute R&D / revenue for nine company-years with inputs.",
             "result": f"NVIDIA {nvda['years'][-1]['fy']}: {pct(nvda['years'][-1]['intensity'], 2)}."},
        ],
        "sources": [source(c["ev"]) for c in companies],
        "prompt": "Use Finance CLI to compare R&D intensity (R&D / revenue) for NVDA, AMD and AVGO over each company's last three fiscal years. Keep each fiscal-year end date, check for acquisitions or one-offs that change the comparison, and cite the 10-K accession for every figure.",
    }
