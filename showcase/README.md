# Research showcase

Five recorded agent research sessions, published at
[tempestshaw.github.io/FinanceCLI/showcase/](https://tempestshaw.github.io/FinanceCLI/showcase/).

| Case | Question |
| --- | --- |
| `apple-services` | Has Apple become more dependent on Services over five fiscal years? |
| `chip-rnd` | Who increased R&D intensity fastest: NVDA, AMD or AVGO? |
| `meta-efficiency` | Did Meta become more efficient after the Year of Efficiency? |
| `costco-thesis` | Does Costco's membership model make earnings more resilient? |
| `data-gap` | How much revenue does Apple's App Store generate? (Not disclosed.) |

## How it fits together

```text
scripts/showcase/plan.py      questions + the CLI calls the agent made, with its reason for each
        │ collect.py          replays the calls against SEC EDGAR (network)
        ▼
showcase/evidence/<case>/     raw `finance ... --output json` responses, committed
        │ build.py            recomputes figures with finance_cli formula functions,
        ▼                     matches every quote against the saved text
docs-site/src/data/showcase.json   what the website and the videos read
        │
        ├─ docs-site/src/pages/showcase/   case pages (Astro)
        └─ videos/                         Remotion compositions → docs-site/public/videos/*.mp4
```

`tests/test_showcase_data.py` fails if `showcase.json` no longer matches a fresh
build from the committed evidence, or if a quote is not verbatim filing text.

## Regenerate

```bash
export FINANCE_SEC_USER_AGENT="Your Name you@example.com"
python scripts/showcase/collect.py             # or: collect.py apple-services
python scripts/showcase/build.py
cd videos && npm install && npm run render     # or: npm run render -- chip-rnd
```

Rendering needs roughly 1 GB of free disk space per video while it runs.
`npm run studio` opens Remotion Studio for editing the videos.

The written answers in each case module (`scripts/showcase/case_*.py`) are
templated from computed values, so numbers in the prose cannot drift from the
tables. If new filings change a conclusion, `build.py` raises instead of
publishing a stale narrative (for example, if the App Store ever gets its own
revenue line).
