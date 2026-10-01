"""Recorded agent research sessions for the showcase.

Each case is one research question and the Finance CLI calls an agent made to
answer it, in order. ``purpose`` is the agent's reason for the call. The
commands are replayed by ``collect.py`` and their raw JSON output is saved under
``showcase/evidence/<case>/<step>.json`` so every figure on the site can be
traced back to a CLI response.
"""
from __future__ import annotations

from dataclasses import dataclass, field

AAPL_FY25 = "0000320193-25-000079"
AAPL_FY23 = "0000320193-23-000106"
AAPL_FY22 = "0000320193-22-000108"
NVDA_FY26 = "0001045810-26-000021"
AMD_FY25 = "0000002488-26-000018"
AVGO_FY25 = "0001730168-25-000121"
META_FY25 = "0001628280-26-003942"
META_FY24 = "0001326801-25-000017"
META_FY23 = "0001326801-24-000012"
META_FY22 = "0001326801-23-000013"
COST_FY25 = "0000909832-25-000101"
COST_FY22 = "0000909832-22-000021"

APPLE_DISAGG_REPORT = "Revenue - Disaggregated Net Sales and Portion of Net Sales That Was Previously Deferred (Details)"
APPLE_SEGMENT_REPORT = "Segment Information and Geographic Data - Information by Reportable Segment (Details)"


@dataclass(frozen=True)
class Step:
    id: str
    args: tuple[str, ...]
    purpose: str

    @property
    def tool(self) -> str:
        return self.args[0]

    @property
    def command(self) -> str:
        return " ".join(["finance", *(_quote(arg) for arg in self.args), "--output", "json"])


@dataclass(frozen=True)
class Case:
    slug: str
    question: str
    steps: tuple[Step, ...] = field(default_factory=tuple)


def _quote(arg: str) -> str:
    if " " not in arg:
        return arg
    key, _, value = arg.partition("=")
    return f'{key}="{value}"' if value else f'"{arg}"'


CASES: tuple[Case, ...] = (
    Case(
        slug="apple-services",
        question=(
            "Has Apple become more dependent on Services over the last five years? "
            "Is growth coming from Services or hardware? Give me each year's numbers and sources."
        ),
        steps=(
            Step("01-annual-filings", ("filings.recent", "AAPL", "forms=10-K", "limit=6"),
                 "List annual reports so every fiscal year maps to one specific filing."),
            Step("02-income-fy25", ("filings.statement", f"accession={AAPL_FY25}", "statement=income"),
                 "Read Products and Services net sales and cost of sales for FY2023–FY2025."),
            Step("03-income-fy22", ("filings.statement", f"accession={AAPL_FY22}", "statement=income"),
                 "Read the same rows for FY2020–FY2022 from the earlier 10-K."),
            Step("04-restatement-check", ("filings.statement", f"accession={AAPL_FY23}", "statement=income"),
                 "Cross-check overlapping years: did a later filing restate FY2022 or FY2021?"),
            Step("05-revenue-mix", ("filings.report", f"accession={AAPL_FY25}", f"name={APPLE_DISAGG_REPORT}"),
                 "Confirm units ($ in millions) and the product-category breakdown in the revenue note."),
            Step("06-mda-drivers", ("filings.read", f"accession={AAPL_FY25}", "section=mda", "max_chars=60000"),
                 "Find management's explanation of what drove Services growth."),
        ),
    ),
    Case(
        slug="chip-rnd",
        question="Compare NVDA, AMD and AVGO R&D intensity over their last three fiscal years. Who increased it fastest?",
        steps=(
            Step("01-nvda-income", ("filings.statement", f"accession={NVDA_FY26}", "statement=income"),
                 "NVIDIA revenue and R&D. Its fiscal year ends in late January."),
            Step("02-amd-income", ("filings.statement", f"accession={AMD_FY25}", "statement=income"),
                 "AMD revenue and R&D. Its fiscal year ends in late December."),
            Step("03-avgo-income", ("filings.statement", f"accession={AVGO_FY25}", "statement=income"),
                 "Broadcom revenue and R&D. Its fiscal year ends in early November."),
            Step("04-avgo-mda", ("filings.read", f"accession={AVGO_FY25}", "section=mda", "max_chars=60000"),
                 "Broadcom's R&D jumped in FY2024. Check for an acquisition before comparing."),
            Step("05-nvda-mda", ("filings.read", f"accession={NVDA_FY26}", "section=mda", "max_chars=60000"),
                 "NVIDIA's ratio fell while R&D dollars rose. Read what drove the expense."),
        ),
    ),
    Case(
        slug="meta-efficiency",
        question="Did Meta actually become more efficient after the Year of Efficiency?",
        steps=(
            Step("01-annual-filings", ("filings.recent", "META", "forms=10-K", "limit=6"),
                 "Find the annual reports covering 2022 through 2025."),
            Step("02-income-fy25", ("filings.statement", f"accession={META_FY25}", "statement=income"),
                 "Revenue, costs and operating income for 2023–2025."),
            Step("03-income-fy24", ("filings.statement", f"accession={META_FY24}", "statement=income"),
                 "The 2022 baseline, before the efficiency push."),
            Step("04-mda-fy22", ("filings.read", f"accession={META_FY22}", "section=mda", "max_chars=90000"),
                 "Headcount and restructuring charges at the end of 2022."),
            Step("05-mda-fy23", ("filings.read", f"accession={META_FY23}", "section=mda", "max_chars=90000"),
                 "Headcount and restructuring charges for 2023."),
            Step("06-mda-fy24", ("filings.read", f"accession={META_FY24}", "section=mda", "max_chars=90000"),
                 "Headcount at the end of 2024."),
            Step("07-mda-fy25", ("filings.read", f"accession={META_FY25}", "section=mda", "max_chars=90000"),
                 "Headcount at the end of 2025 and what drove cost growth."),
        ),
    ),
    Case(
        slug="costco-thesis",
        question="I think Costco's membership model makes its earnings more resilient. Test this thesis.",
        steps=(
            Step("01-income-fy25", ("filings.statement", f"accession={COST_FY25}", "statement=income"),
                 "Membership fees and operating income for FY2023–FY2025."),
            Step("02-income-fy22", ("filings.statement", f"accession={COST_FY22}", "statement=income"),
                 "The same rows for FY2020–FY2022, including the pandemic year."),
            Step("03-mda-fy25", ("filings.read", f"accession={COST_FY25}", "section=mda", "max_chars=60000"),
                 "Renewal rates and what management says drove membership fee growth."),
        ),
    ),
    Case(
        slug="data-gap",
        question="How much revenue does Apple's App Store generate each year?",
        steps=(
            Step("01-revenue-mix", ("filings.report", f"accession={AAPL_FY25}", f"name={APPLE_DISAGG_REPORT}"),
                 "Look for an App Store line in the revenue disaggregation note."),
            Step("02-report-search", ("filings.reports", f"accession={AAPL_FY25}", "query=App Store"),
                 "Search every XBRL report title in the filing for App Store."),
            Step("03-segments", ("filings.report", f"accession={AAPL_FY25}", f"name={APPLE_SEGMENT_REPORT}"),
                 "Check whether reportable segments split out the App Store."),
            Step("04-mda", ("filings.read", f"accession={AAPL_FY25}", "section=mda", "max_chars=60000"),
                 "Check how management's discussion describes the App Store."),
        ),
    ),
)


def case_by_slug(slug: str) -> Case:
    for case in CASES:
        if case.slug == slug:
            return case
    raise KeyError(f"unknown showcase case: {slug}")
