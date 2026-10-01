"""Apple: has the business become more dependent on Services?"""
from __future__ import annotations

from typing import Any

from evidence import EvidenceError, billions, load, pct, points, quote, source, statement_value, trace_entry
from finance_cli.services.formulas import formula_cagr, formula_margin

CASE = "apple-services"
REVENUE = "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax"
COST = "us-gaap_CostOfGoodsAndServicesSold"
FY_SOURCES = {  # fiscal year -> (evidence step, statement period column)
    2020: ("03-income-fy22", "2020-09-26"),
    2021: ("03-income-fy22", "2021-09-25"),
    2022: ("03-income-fy22", "2022-09-24"),
    2023: ("02-income-fy25", "2023-09-30"),
    2024: ("02-income-fy25", "2024-09-28"),
    2025: ("02-income-fy25", "2025-09-27"),
}
RESTATEMENT_CHECKS = ((2021, "2021-09-25"), (2022, "2022-09-24"))


def _year(fy: int) -> dict[str, Any]:
    step, period = FY_SOURCES[fy]
    ev = load(CASE, step)
    total = statement_value(ev, REVENUE, "Net sales", period)
    products = statement_value(ev, REVENUE, "Products", period)
    services = statement_value(ev, REVENUE, "Services", period)
    services_cost = statement_value(ev, COST, "Services", period)
    products_cost = statement_value(ev, COST, "Products", period)
    if abs(products + services - total) > 1:
        raise EvidenceError(f"FY{fy}: Products + Services does not equal Net sales")
    services_gm = services - services_cost
    total_gm = total - services_cost - products_cost
    return {
        "fy": fy,
        "period_end": period,
        "total": total,
        "products": products,
        "services": services,
        "services_gross_margin": services_gm,
        "total_gross_margin": total_gm,
        "services_share": formula_margin(numerator=services, denominator=total)["margin"],
        "services_gm_share": formula_margin(numerator=services_gm, denominator=total_gm)["margin"],
        "services_gm_pct": formula_margin(numerator=services_gm, denominator=services)["margin"],
        "accession": ev.filing["accession_no"],
        "url": ev.filing["filing_url"],
    }


def _restatements() -> list[dict[str, Any]]:
    later = load(CASE, "04-restatement-check")
    checks = []
    for fy, period in RESTATEMENT_CHECKS:
        original = _year(fy)
        for label, key in (("Products", "products"), ("Services", "services")):
            restated = statement_value(later, REVENUE, label, period)
            checks.append({"fy": fy, "line": label, "original": original[key], "later": restated,
                           "match": abs(restated - original[key]) < 1})
    return checks


def build() -> dict[str, Any]:
    years = [_year(fy) for fy in sorted(FY_SOURCES)]
    first, base22, last = years[0], years[2], years[-1]
    checks = _restatements()
    if not all(check["match"] for check in checks):
        raise EvidenceError("Apple restatement check found a mismatch; update the narrative")

    services_add_all = last["services"] - first["services"]
    products_add_all = last["products"] - first["products"]
    services_add_22 = last["services"] - base22["services"]
    products_add_22 = last["products"] - base22["products"]
    services_cagr = formula_cagr(start=first["services"], end=last["services"], periods=5)["cagr"]
    products_cagr = formula_cagr(start=first["products"], end=last["products"], periods=5)["cagr"]

    mda = load(CASE, "06-mda-drivers")
    drivers = quote(mda, "higher net sales from advertising, the App Store and cloud services")
    footnote = quote(mda, "Services net sales include amortization of the deferred value")
    fy25, fy22, fy23 = load(CASE, "02-income-fy25"), load(CASE, "03-income-fy22"), load(CASE, "04-restatement-check")
    mix = load(CASE, "05-revenue-mix")
    filings = load(CASE, "01-annual-filings")

    return {
        "slug": CASE,
        "title": "Apple’s shift to Services",
        "kicker": "Financial statement analysis",
        "question": "Has Apple become more dependent on Services over the last five years? Is growth coming from Services or hardware? Give me each year’s numbers and sources.",
        "headline": f"Services grew from {pct(first['services_share'])} to {pct(last['services_share'])} of net sales — and {pct(last['services_gm_share'])} of gross margin.",
        "answer": [
            f"Yes. Services rose from {pct(first['services_share'])} of net sales in FY{first['fy']} to {pct(last['services_share'])} in FY{last['fy']}. Its share of gross margin rose faster, from {pct(first['services_gm_share'])} to {pct(last['services_gm_share'])}, because Services gross margin was {pct(last['services_gm_pct'])} in FY{last['fy']}.",
            f"Where the growth came from depends on the window. Since FY2022, Products net sales changed by {billions(products_add_22)} while Services added {billions(services_add_22)}, so Services accounts for all of the net growth. Over the full five years, Products still added more dollars ({billions(products_add_all)} vs {billions(services_add_all)}), most of it in the FY2021 rebound.",
            f"Services compounded at {pct(services_cagr)} a year from FY2020 to FY2025, against {pct(products_cagr)} for Products.",
        ],
        "metrics": [
            {"label": f"Services share of net sales, FY{last['fy']}", "value": pct(last["services_share"]), "delta": points(last["services_share"] - first["services_share"]) + f" since FY{first['fy']}"},
            {"label": f"Services share of gross margin, FY{last['fy']}", "value": pct(last["services_gm_share"]), "delta": points(last["services_gm_share"] - first["services_gm_share"]) + f" since FY{first['fy']}"},
            {"label": "Net growth from Services since FY2022", "value": billions(services_add_22), "delta": f"Products {billions(products_add_22)}"},
        ],
        "table": {
            "caption": "Apple net sales by category. Fiscal years end on the last Saturday of September. Values reported in millions of US dollars.",
            "columns": [
                {"key": "fy", "label": "Fiscal year"},
                {"key": "services", "label": "Services", "align": "end"},
                {"key": "total", "label": "Net sales", "align": "end"},
                {"key": "share", "label": "Services share", "align": "end"},
                {"key": "gm_share", "label": "Share of gross margin", "align": "end"},
                {"key": "source", "label": "Source"},
            ],
            "rows": [
                {"fy": f"FY{y['fy']}", "period_end": y["period_end"], "services": billions(y["services"]), "total": billions(y["total"]),
                 "share": pct(y["services_share"]), "gm_share": pct(y["services_gm_share"]),
                 "source": f"10-K · {y['accession']}", "url": y["url"]}
                for y in years
            ],
        },
        "chart": {
            "kind": "bars",
            "label": "Services share of Apple net sales",
            "points": [{"x": f"FY{y['fy'] % 100:02d}", "value": round(y["services_share"] * 100, 1),
                        "secondary": round(y["services_gm_share"] * 100, 1)} for y in years],
        },
        "calculations": [
            {"label": "Services share of net sales", "method": "Services net sales / Net sales",
             "inputs": f"FY{last['fy']}: {last['services']:,.0f} / {last['total']:,.0f}", "result": pct(last["services_share"], 2)},
            {"label": "Services share of gross margin", "method": "(Services sales − Services cost of sales) / total gross margin",
             "inputs": f"FY{last['fy']}: {last['services_gross_margin']:,.0f} / {last['total_gross_margin']:,.0f}", "result": pct(last["services_gm_share"], 2)},
            {"label": "Services CAGR FY2020–FY2025", "method": "(end / start) ** (1 / periods) − 1",
             "inputs": f"{first['services']:,.0f} → {last['services']:,.0f}, 5 periods", "result": pct(services_cagr, 2)},
        ],
        "checks": [
            {"status": "verified", "label": "No restatement in overlapping years",
             "detail": "FY2021 and FY2022 Products and Services figures in the FY2023 10-K match the FY2022 10-K exactly."},
            {"status": "verified", "label": "Products + Services = Net sales",
             "detail": "The two categories sum to reported net sales in all six years."},
            {"status": "caveat", "label": "Services includes bundled amortization", "detail": footnote},
            {"status": "caveat", "label": "Drivers are named, not sized", "detail": drivers + " The filing gives no amount for each driver."},
        ],
        "quotes": [{"text": drivers, "source": source(mda)["label"]}],
        "trace": [
            trace_entry(filings, f"{len(filings.data['filings'])} annual reports, FY2020–FY2025, each with an accession number."),
            trace_entry(fy25, "Products and Services rows for FY2023–FY2025 with XBRL concepts."),
            trace_entry(fy22, "The same rows for FY2020–FY2022."),
            trace_entry(fy23, "FY2021 and FY2022 values match the earlier filing. No restatement."),
            trace_entry(mix, "Revenue note is in $ millions. Services is reported as one line."),
            trace_entry(mda, "Management names advertising, the App Store and cloud services as drivers."),
            {"id": "07-calculate", "tool": "formula.margin", "command": "finance formula.margin numerator=109158 denominator=416161",
             "purpose": "Compute shares and growth with stated inputs and method.",
             "result": f"18 ratios and 2 CAGRs, each with inputs. FY{last['fy']} Services share = {pct(last['services_share'], 2)}."},
        ],
        "sources": [source(fy25), source(fy23), source(fy22)],
        "prompt": "Use Finance CLI to test whether Apple has become more dependent on Services over the last five fiscal years. Use 10-K income statements, keep fiscal-year end dates and units, check overlapping years for restatements, calculate the Services share of net sales and gross margin, and cite the accession for every figure. Say what the filings do not disclose.",
    }
