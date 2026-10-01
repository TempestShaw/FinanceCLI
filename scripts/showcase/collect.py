"""Replay the showcase research sessions and save raw CLI evidence.

Usage:
    python scripts/showcase/collect.py            # every case
    python scripts/showcase/collect.py apple-services chip-rnd

Requires network access to SEC EDGAR. Set FINANCE_SEC_USER_AGENT to your own
name and email before running.
"""
from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from plan import CASES, Case, Step, case_by_slug  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "showcase" / "evidence"
TIMEOUT_SECONDS = 300
MAX_WORKERS = 4


def run_step(case: Case, step: Step) -> tuple[str, bool]:
    started = datetime.now(timezone.utc)
    completed = subprocess.run(
        ["finance", *step.args, "--output", "json"],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )
    try:
        output = json.loads(completed.stdout)
    except json.JSONDecodeError:
        output = {"ok": False, "data": None, "error": completed.stderr.strip() or "non-JSON output", "warnings": []}
    record = {
        "case": case.slug,
        "step": step.id,
        "command": step.command,
        "purpose": step.purpose,
        "retrieved_at": started.isoformat(timespec="seconds"),
        "exit_code": completed.returncode,
        "output": output,
    }
    target = EVIDENCE_DIR / case.slug / f"{step.id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"{case.slug}/{step.id}", bool(output.get("ok"))


def main(argv: list[str]) -> int:
    cases = [case_by_slug(slug) for slug in argv] if argv else list(CASES)
    jobs = [(case, step) for case in cases for step in case.steps]
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for name, ok in pool.map(lambda job: run_step(*job), jobs):
            print(f"{'ok  ' if ok else 'FAIL'} {name}")
            if not ok:
                failures.append(name)
    if failures:
        print(f"{len(failures)} step(s) returned ok=false; inspect the saved evidence.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
