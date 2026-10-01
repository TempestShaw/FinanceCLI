"""Apple App Store revenue: showing that the filing does not disclose it."""
from __future__ import annotations

import re
from typing import Any

from evidence import EvidenceError, load, quote, source, trace_entry

CASE = "data-gap"
SERVICES_LINE = re.compile(r"Services.*?Net sales \$ ([\d,]+)", re.S)


def build() -> dict[str, Any]:
    mix, search, segments, mda = (load(CASE, s) for s in ("01-revenue-mix", "02-report-search", "03-segments", "04-mda"))
    mix_text = mix.text()
    if "App Store" in mix_text:
        raise EvidenceError("revenue note now mentions the App Store; revisit the data-gap case")
    services = SERVICES_LINE.search(mix_text)
    if not services:
        raise EvidenceError("could not find the Services net sales line")
    if search.data["count"] != 0:
        raise EvidenceError("an XBRL report now matches 'App Store'; revisit the data-gap case")
    segment_names = [name for name in ("Americas", "Europe", "Greater China", "Japan", "Rest of Asia Pacific") if name in segments.text()]
    named = quote(mda, "higher net sales from advertising, the App Store and cloud services")
    services_m = services.group(1)

    return {
        "slug": CASE,
        "title": "When the filing doesn’t say",
        "kicker": "Missing data, reported honestly",
        "question": "How much revenue does Apple’s App Store generate each year?",
        "headline": "The 10-K doesn’t disclose it. The right answer says so.",
        "answer": [
            f"Apple’s 10-K does not disclose App Store revenue. Services is reported as one line (${services_m} million in FY2025), with no amount for the App Store or any other service.",
            "Management names the App Store as one driver of Services growth, alongside advertising and cloud services, without sizing it. Reportable segments are geographic, so they don’t help either.",
            "Any App Store figure would have to come from a third-party estimate. That would be a different kind of evidence, and it should be labelled as such rather than presented as a reported number.",
        ],
        "gap": {
            "available": f"FY2025 Services net sales: ${services_m} million (reported)",
            "missing": "App Store revenue, for any year",
            "reason": "Apple reports Services as a single revenue category and names its drivers without amounts.",
            "policy": "Finance CLI returns what the filing contains. It does not interpolate, estimate or substitute a missing value.",
        },
        "metrics": [
            {"label": "Places checked", "value": "4", "delta": "revenue note, report index, segments, MD&A"},
            {"label": "App Store amounts found", "value": "0", "delta": "named once, never sized"},
            {"label": "Services, FY2025", "value": f"${services_m}M", "delta": "the closest reported figure"},
        ],
        "checks": [
            {"status": "missing", "label": "Revenue note", "detail": f"Disaggregation lists iPhone, Mac, iPad, Wearables, Home and Accessories, and Services (${services_m}M). No App Store line."},
            {"status": "missing", "label": "XBRL report index", "detail": "A search of every report title in the filing for “App Store” returned 0 reports."},
            {"status": "missing", "label": "Reportable segments", "detail": f"Segments are geographic: {', '.join(segment_names)}."},
            {"status": "caveat", "label": "MD&A names, doesn’t size", "detail": named},
        ],
        "quotes": [{"text": named, "source": source(mda)["label"]}],
        "trace": [
            trace_entry(mix, f"Five categories. Services ${services_m}M as a single line."),
            trace_entry(search, "0 matching reports."),
            trace_entry(segments, f"Segments: {', '.join(segment_names)}."),
            trace_entry(mda, "App Store named as a growth driver. No amount."),
        ],
        "sources": [source(mix)],
        "prompt": "Use Finance CLI to find how much revenue Apple's App Store generates. Search the 10-K's revenue note, report index, segments and MD&A. If the filing does not disclose it, say so, show where you looked, and do not substitute an estimate.",
    }
