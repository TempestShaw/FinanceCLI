"""The website's research showcase must stay derivable from saved CLI evidence."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts" / "showcase"
DATASET = ROOT / "docs-site" / "src" / "data" / "showcase.json"

# The source distribution ships tests but not the website or its evidence.
pytestmark = pytest.mark.skipif(
    not (ROOT / "showcase" / "evidence").is_dir() or not DATASET.exists(),
    reason="showcase evidence is only present in a repository checkout",
)


def _load_module(name: str):
    sys.path[:0] = [str(SCRIPTS)]
    try:
        spec = importlib.util.spec_from_file_location(f"showcase_{name}", SCRIPTS / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module  # dataclasses resolve annotations via sys.modules
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


@pytest.fixture(scope="module")
def committed() -> dict:
    return json.loads(DATASET.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def evidence_module():
    return _load_module("evidence")


def test_committed_dataset_matches_a_fresh_build(committed):
    build = _load_module("build")
    assert build.build_dataset() == committed, "run python scripts/showcase/build.py"


def test_every_planned_step_has_saved_successful_evidence():
    plan = _load_module("plan")
    for case in plan.CASES:
        for step in case.steps:
            path = ROOT / "showcase" / "evidence" / case.slug / f"{step.id}.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            assert record["output"]["ok"], f"{path} recorded an error"
            assert record["command"] == step.command


def test_every_quote_is_verbatim_filing_text(committed):
    evidence_dir = ROOT / "showcase" / "evidence"
    corpus = " ".join(
        re.sub(r"\s+", " ", json.loads(path.read_text(encoding="utf-8"))["output"]["data"].get("text", ""))
        for path in evidence_dir.glob("*/*.json")
    )
    for case in committed["cases"]:
        for item in case["quotes"]:
            assert item["text"].rstrip("…") in corpus, f"{case['slug']}: quote not found in evidence"


def test_every_case_cites_sec_sources_and_flags_limits(committed):
    assert [case["slug"] for case in committed["cases"]] == [
        "apple-services", "chip-rnd", "meta-efficiency", "costco-thesis", "data-gap",
    ]
    for case in committed["cases"]:
        assert case["sources"], case["slug"]
        assert all(src["url"].startswith("https://www.sec.gov/Archives/") for src in case["sources"])
        assert any(check["status"] in {"missing", "caveat"} for check in case["checks"]), case["slug"]
        for row in case.get("table", {}).get("rows", []):
            assert row["url"].startswith("https://www.sec.gov/Archives/")


def test_statement_lookup_rejects_missing_rows(evidence_module):
    ev = evidence_module.load("apple-services", "02-income-fy25")
    with pytest.raises(evidence_module.EvidenceError):
        evidence_module.statement_value(ev, "us-gaap_Revenues", "App Store", "2025-09-27")


def test_quote_rejects_text_the_filing_does_not_contain(evidence_module):
    ev = evidence_module.load("data-gap", "04-mda")
    with pytest.raises(evidence_module.EvidenceError):
        evidence_module.quote(ev, "App Store net sales were")


def test_negative_amounts_use_a_leading_minus(evidence_module):
    assert evidence_module.billions(-9_196_000_000) == "−$9.2B"
