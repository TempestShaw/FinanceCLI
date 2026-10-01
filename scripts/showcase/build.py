"""Derive the showcase dataset from saved CLI evidence.

Usage:
    python scripts/showcase/build.py           # write docs-site/src/data/showcase.json
    python scripts/showcase/build.py --check   # fail if the committed file is stale

Every number is computed from ``showcase/evidence`` with Finance CLI's own
formula functions, and every quote is matched against the saved CLI text.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT)]

import case_apple  # noqa: E402
import case_chips  # noqa: E402
import case_costco  # noqa: E402
import case_gap  # noqa: E402
import case_meta  # noqa: E402
from plan import CASES  # noqa: E402

OUTPUT = ROOT / "docs-site" / "src" / "data" / "showcase.json"
BUILDERS = {
    "apple-services": case_apple.build,
    "chip-rnd": case_chips.build,
    "meta-efficiency": case_meta.build,
    "costco-thesis": case_costco.build,
    "data-gap": case_gap.build,
}


def build_dataset() -> dict:
    cases = [BUILDERS[case.slug]() for case in CASES]
    retrieved = sorted(step["retrieved_at"] for case in cases for step in case["trace"] if "retrieved_at" in step)
    return {
        "recorded": {"first": retrieved[0], "last": retrieved[-1]},
        "note": "Recorded agent sessions. Commands and CLI outputs are real and saved in showcase/evidence; the written answers were produced by the agent from that evidence.",
        "cases": cases,
    }


def render(dataset: dict) -> str:
    return json.dumps(dataset, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    content = render(build_dataset())
    if "--check" in argv:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != content:
            print(f"{OUTPUT.relative_to(ROOT)} is stale; run python scripts/showcase/build.py", file=sys.stderr)
            return 1
        print("showcase dataset is up to date")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
