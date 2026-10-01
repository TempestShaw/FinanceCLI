"""Read saved CLI evidence and turn it into traceable values, quotes and sources."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "showcase" / "evidence"
REPO_URL = "https://github.com/TempestShaw/FinanceCLI/blob/main"
FOOTNOTE_MARKER = re.compile(r"\(\d+\)")


class EvidenceError(ValueError):
    """Raised when a figure or quote cannot be found in saved evidence."""


@dataclass(frozen=True)
class Evidence:
    case: str
    step: str
    record: dict[str, Any]

    @property
    def data(self) -> dict[str, Any]:
        output = self.record["output"]
        if not output.get("ok"):
            raise EvidenceError(f"{self.path_label} returned an error: {output.get('error')}")
        return output["data"]

    @property
    def path_label(self) -> str:
        return f"showcase/evidence/{self.case}/{self.step}.json"

    @property
    def filing(self) -> dict[str, Any]:
        return self.data["filing"]

    def text(self) -> str:
        return self.data["text"]


def load(case: str, step: str) -> Evidence:
    path = EVIDENCE_DIR / case / f"{step}.json"
    if not path.exists():
        raise EvidenceError(f"missing evidence file {path}; run scripts/showcase/collect.py {case}")
    return Evidence(case, step, json.loads(path.read_text(encoding="utf-8")))


def statement_value(ev: Evidence, concept: str, label: str, period: str) -> float:
    """Return one statement cell, matched by XBRL concept and row label."""
    for row in ev.data["rows"]:
        if row["concept"] == concept and row["label"].lower() == label.lower():
            value = row.get(period)
            if value is None:
                raise EvidenceError(f"{ev.path_label}: {label} has no value for {period}")
            return float(value)
    raise EvidenceError(f"{ev.path_label}: no row {concept} / {label}")


def quote(ev: Evidence, phrase: str) -> str:
    """Return the sentence containing ``phrase`` exactly as the CLI returned it.

    Filing text keeps headings and table rows on their own lines, so a sentence
    starts after the previous full stop, bullet or line break.
    """
    raw = ev.text()
    flat = re.sub(r"\s+", " ", phrase)
    match = re.search(r"\s+".join(map(re.escape, flat.split(" "))), raw)
    if not match:
        raise EvidenceError(f"{ev.path_label}: phrase not found: {phrase!r}")
    before = raw[: match.start()]
    footnotes = [m.end() - 1 for m in FOOTNOTE_MARKER.finditer(before)]
    start = max(before.rfind(". "), before.rfind("•"), before.rfind("\n"), *footnotes, -1)
    end = raw.find(". ", match.end())
    newline = raw.find("\n", match.end())
    end = min(e for e in (end + 1 if end >= 0 else len(raw), newline if newline >= 0 else len(raw)))
    sentence = re.sub(r"\s+", " ", raw[start + 1 : end]).strip(" •")
    # A page break can split a sentence; mark the cut instead of ending on a comma.
    return sentence[:-1] + "…" if sentence.endswith(",") else sentence


def source(ev: Evidence, label: str | None = None) -> dict[str, Any]:
    filing = ev.filing
    company = filing["company"]
    return {
        "label": label or f"{company} {filing['form']} · period ended {filing['period_of_report']}",
        "company": company,
        "form": filing["form"],
        "filing_date": filing["filing_date"],
        "period": filing["period_of_report"],
        "accession": filing["accession_no"],
        "url": filing["filing_url"],
    }


def trace_entry(ev: Evidence, result: str, note: str | None = None) -> dict[str, Any]:
    record = ev.record
    entry = {
        "id": ev.step,
        "tool": record["command"].split()[1],
        "command": record["command"],
        "purpose": record["purpose"],
        "result": result,
        "retrieved_at": record["retrieved_at"],
        "evidence": f"{REPO_URL}/{ev.path_label}",
    }
    return {**entry, "note": note} if note else entry


def billions(value: float, digits: int = 1) -> str:
    sign = "−" if value < 0 else ""
    return f"{sign}${abs(value) / 1e9:,.{digits}f}B"


def millions(value: float) -> str:
    return f"${value / 1e6:,.0f}M"


def pct(ratio: float, digits: int = 1) -> str:
    return f"{ratio * 100:.{digits}f}%"


def points(delta: float) -> str:
    return f"{delta * 100:+.1f} pts"
