"""Print adoption metrics for Finance CLI as Markdown.

Usage:
    python scripts/launch_metrics.py

Sources:
- PyPI downloads from the public pypistats.org API (no key; rate limited).
- GitHub stars, forks and 14-day traffic via the `gh` CLI. Traffic requires
  push access to the repository, so run it as a maintainer.

Website page views live in the GoatCounter dashboard when the site is built
with PUBLIC_GOATCOUNTER_CODE; this script does not read them.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

PACKAGE = "finresearch-cli"
REPO = "TempestShaw/FinanceCLI"
PYPISTATS = f"https://pypistats.org/api/packages/{PACKAGE}/recent"
TIMEOUT_SECONDS = 20


def pypi_downloads() -> dict[str, Any]:
    request = urllib.request.Request(PYPISTATS, headers={"User-Agent": "finance-cli-launch-metrics"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return {"ok": True, "data": json.load(response)["data"]}
    except urllib.error.HTTPError as exc:
        hint = "rate limited, try again in a minute" if exc.code == 429 else f"HTTP {exc.code}"
        return {"ok": False, "error": f"pypistats: {hint}"}
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"pypistats: {exc}"}


def gh_api(path: str) -> dict[str, Any]:
    completed = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=False)
    if completed.returncode != 0:
        return {"ok": False, "error": f"gh api {path}: {completed.stderr.strip() or 'failed'}"}
    return {"ok": True, "data": json.loads(completed.stdout)}


def render() -> tuple[str, int]:
    lines = [f"# {PACKAGE} metrics", ""]
    failures = 0

    pypi = pypi_downloads()
    lines += ["## PyPI downloads", ""]
    if pypi["ok"]:
        d = pypi["data"]
        lines += [f"- Last day: {d['last_day']}", f"- Last week: {d['last_week']}", f"- Last month: {d['last_month']}"]
    else:
        failures += 1
        lines.append(f"- Unavailable: {pypi['error']}")

    repo = gh_api(f"repos/{REPO}")
    lines += ["", "## GitHub", ""]
    if repo["ok"]:
        r = repo["data"]
        lines += [f"- Stars: {r['stargazers_count']}", f"- Forks: {r['forks_count']}", f"- Open issues: {r['open_issues_count']}"]
    else:
        failures += 1
        lines.append(f"- Unavailable: {repo['error']}")

    lines += ["", "## GitHub traffic, last 14 days", ""]
    for label, path in (("Views", "traffic/views"), ("Clones", "traffic/clones")):
        result = gh_api(f"repos/{REPO}/{path}")
        if result["ok"]:
            t = result["data"]
            lines.append(f"- {label}: {t['count']} ({t['uniques']} unique)")
        else:
            failures += 1
            lines.append(f"- {label}: unavailable ({result['error']})")
    referrers = gh_api(f"repos/{REPO}/traffic/popular/referrers")
    if referrers["ok"] and referrers["data"]:
        lines += ["", "| Referrer | Views | Unique |", "| --- | ---: | ---: |"]
        lines += [f"| {r['referrer']} | {r['count']} | {r['uniques']} |" for r in referrers["data"]]
    elif not referrers["ok"]:
        failures += 1
        lines.append(f"- Referrers unavailable: {referrers['error']}")
    return "\n".join(lines) + "\n", failures


def main() -> int:
    report, failures = render()
    sys.stdout.write(report)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
