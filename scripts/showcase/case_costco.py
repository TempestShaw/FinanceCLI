"""Costco: does the membership model make earnings more resilient?"""
from __future__ import annotations

from typing import Any

from evidence import billions, load, pct, quote, source, statement_value, trace_entry
from finance_cli.services.formulas import formula_cagr, formula_margin

CASE = "costco-thesis"
REVENUE = "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax"
OPERATING = "us-gaap_OperatingIncomeLoss"
YEARS = {  # fiscal year -> (step, period, operating income label as filed)
    2020: ("02-income-fy22", "2020-08-30", "Operating Income"),
    2021: ("02-income-fy22", "2021-08-29", "Operating Income"),
    2022: ("02-income-fy22", "2022-08-28", "Operating Income"),
    2023: ("01-income-fy25", "2023-09-03", "Operating income"),
    2024: ("01-income-fy25", "2024-09-01", "Operating income"),
    2025: ("01-income-fy25", "2025-08-31", "Operating income"),
}


def _year(fy: int) -> dict[str, Any]:
    step, period, op_label = YEARS[fy]
    ev = load(CASE, step)
    fees = statement_value(ev, REVENUE, "Membership", period)
    operating = statement_value(ev, OPERATING, op_label, period)
    return {"fy": fy, "period_end": period, "fees": fees, "operating": operating,
            "fee_share": formula_margin(numerator=fees, denominator=operating)["margin"],
            "url": ev.filing["filing_url"], "accession": ev.filing["accession_no"]}


def build() -> dict[str, Any]:
    years = [_year(fy) for fy in sorted(YEARS)]
    first, last = years[0], years[-1]
    for prev, cur in zip(years, years[1:]):
        cur["fee_growth"] = cur["fees"] / prev["fees"] - 1
        cur["op_growth"] = cur["operating"] / prev["operating"] - 1
    fee_growths = [y["fee_growth"] for y in years[1:]]
    op_growths = [y["op_growth"] for y in years[1:]]
    fee_cagr = formula_cagr(start=first["fees"], end=last["fees"], periods=5)["cagr"]
    shares = [y["fee_share"] for y in years]

    mda_ev = load(CASE, "03-mda-fy25")
    renewal = quote(mda_ev, "our member renewal rates were 92.3% in the U.S. and Canada and 89.8% worldwide")
    drivers = quote(mda_ev, "Membership fee revenue increased 10% in 2025, driven by new member sign-ups and membership fee increases")
    online = quote(mda_ev, "Renewal rates were negatively impacted by a higher number of memberships sold online")
    design = quote(mda_ev, "This format is designed to reinforce member loyalty and provide continuing fee revenue")
    fy25, fy22 = load(CASE, "01-income-fy25"), load(CASE, "02-income-fy22")
    src25, src22 = source(fy25)["label"], source(fy22)["label"]

    claims = [
        {"claim": "Membership fees are recurring and growing", "status": "supported",
         "evidence": f"Fees rose every year from {billions(first['fees'], 2)} (FY{first['fy']}) to {billions(last['fees'], 2)} (FY{last['fy']}); annual growth ranged {pct(min(fee_growths))}–{pct(max(fee_growths))}.",
         "source": f"{src22}; {src25}", "kind": "reported"},
        {"claim": "Fees are a large share of operating profit", "status": "supported",
         "evidence": f"Membership fees equalled {pct(min(shares))}–{pct(max(shares))} of operating income each year.",
         "source": "Calculated from the income statements", "kind": "calculated"},
        {"claim": "Members keep renewing", "status": "supported", "evidence": renewal, "source": src25, "kind": "quoted"},
        {"claim": "Growth reflects loyalty, not just pricing", "status": "mixed", "evidence": drivers, "source": src25, "kind": "quoted"},
        {"claim": "Renewal quality is stable", "status": "caveat", "evidence": online, "source": src25, "kind": "quoted"},
        {"claim": "Earnings held up in a downturn", "status": "untested",
         "evidence": f"Operating income grew every year FY{first['fy']}–FY{last['fy']} ({pct(min(op_growths))} to {pct(max(op_growths))}). The window has no year of falling profit to test resilience against.",
         "source": "Calculated from the income statements", "kind": "calculated"},
    ]

    return {
        "slug": CASE,
        "title": "Testing a thesis on Costco",
        "kicker": "Thesis → evidence",
        "question": "I think Costco’s membership model makes its earnings more resilient. Test this thesis.",
        "headline": f"Partly supported: fees equal {pct(last['fee_share'], 0)} of operating income and renewals stay near 90%, but six years of rising profit can’t test resilience.",
        "answer": [
            f"The ingredients of the thesis hold up. Membership fees grew every year, compounding {pct(fee_cagr)} a year from FY{first['fy']} to FY{last['fy']}, and equalled {pct(last['fee_share'])} of operating income in FY{last['fy']}. Renewal rates were 92.3% in the U.S. and Canada and 89.8% worldwide.",
            "Two qualifications. FY2025 fee growth was partly a price increase, not just new members. And management reports that online sign-ups renew at a lower rate.",
            "The conclusion itself is not yet tested. Operating income rose in every year of the window, so these filings cannot show how earnings behave when the business is under pressure. Costco also does not disclose the cost of serving members, so fees cannot be read as pure profit.",
        ],
        "metrics": [
            {"label": f"Membership fees / operating income, FY{last['fy']}", "value": pct(last["fee_share"]), "delta": f"FY{first['fy']}: {pct(first['fee_share'])}"},
            {"label": "Membership fee CAGR, FY2020–FY2025", "value": pct(fee_cagr), "delta": "grew every year"},
            {"label": "Renewal rate, U.S. & Canada", "value": "92.3%", "delta": "89.8% worldwide"},
        ],
        "claims": claims,
        "table": {
            "caption": "Costco membership fees and operating income. Fiscal years end on the Sunday nearest August 31 (FY2023 was a 53-week year). Labels differ between filings (“Operating Income” vs “Operating income”); the XBRL concept is the same.",
            "columns": [
                {"key": "fy", "label": "Fiscal year"},
                {"key": "fees", "label": "Membership fees", "align": "end"},
                {"key": "operating", "label": "Operating income", "align": "end"},
                {"key": "share", "label": "Fees / op. income", "align": "end"},
                {"key": "source", "label": "Source"},
            ],
            "rows": [
                {"fy": f"FY{y['fy']}", "period_end": y["period_end"], "fees": billions(y["fees"], 2), "operating": billions(y["operating"], 2),
                 "share": pct(y["fee_share"]), "source": f"10-K · {y['accession']}", "url": y["url"]}
                for y in years
            ],
        },
        "chart": {"kind": "bars", "label": "Membership fees as % of operating income",
                  "points": [{"x": f"FY{y['fy'] % 100:02d}", "value": round(y["fee_share"] * 100, 1)} for y in years]},
        "calculations": [
            {"label": f"Fees / operating income, FY{last['fy']}", "method": "Membership fees / operating income",
             "inputs": f"{last['fees']:,.0f} / {last['operating']:,.0f}", "result": pct(last["fee_share"], 2)},
            {"label": "Membership fee CAGR", "method": "(end / start) ** (1 / periods) − 1",
             "inputs": f"{first['fees']:,.0f} → {last['fees']:,.0f}, 5 periods", "result": pct(fee_cagr, 2)},
        ],
        "checks": [
            {"status": "missing", "label": "Cost of serving members not disclosed",
             "detail": "Fees are revenue, not profit. The filing does not allocate costs to the membership program, so a membership margin cannot be calculated."},
            {"status": "caveat", "label": "No downturn in the window", "detail": "Operating income rose every year from FY2020 to FY2025."},
            {"status": "verified", "label": "Management’s stated design", "detail": design},
        ],
        "quotes": [{"text": renewal, "source": src25}],
        "trace": [
            trace_entry(fy25, "Membership fees and operating income for FY2023–FY2025."),
            trace_entry(fy22, "FY2020–FY2022 rows. Same XBRL concept, different capitalization in the label."),
            trace_entry(mda_ev, "Renewal rates, fee growth drivers and the online sign-up caveat."),
            {"id": "04-calculate", "tool": "formula.margin", "command": f"finance formula.margin numerator={last['fees'] / 1e6:.0f}M denominator={last['operating'] / 1e6:.0f}M",
             "purpose": "Fee share of operating income and fee CAGR, with inputs.",
             "result": f"FY{last['fy']}: {pct(last['fee_share'], 2)}; CAGR {pct(fee_cagr, 2)}."},
        ],
        "sources": [source(fy25), source(fy22)],
        "prompt": "Use Finance CLI to test this thesis: Costco's membership model makes its earnings more resilient. Break it into claims, find filing evidence for each, calculate what you need, cite every source, and mark each claim supported, mixed, or untested.",
    }
