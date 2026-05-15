---
title: Quick Start
description: Install Finance CLI and run the first research commands.
---

## Install

```bash
python -m pip install -U finresearch-cli
```

## Verify The CLI

Check the command registry and local source readiness:

```bash
finance --list
finance sources.status --output json
```

Run a first set of research commands:

```bash
finance filings.recent AAPL forms=10-K,10-Q limit=3
finance filings.statement COST statement=balance query="Common Stock"
finance formula.margin numerator=11969 denominator=254453
finance market.quote AAPL
finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31 fast=20 slow=100
```

## First JSON Output

Most commands return JSON by default. `formula.*` commands are a good first check because they do not need network access:

```bash
finance formula.margin numerator=11969 denominator=254453 --output json
```

```json
{
  "ok": true,
  "data": {
    "margin": 0.04703815635893466,
    "margin_pct": 4.7038156358934655,
    "inputs": {
      "numerator": 11969.0,
      "denominator": 254453.0
    },
    "method": "numerator / denominator"
  },
  "error": null,
  "warnings": []
}
```

Use `--output text` for readable terminal output when a command supports it.

## Documents

Use document commands after you have a local PDF, local HTML file, or URL:

```bash
finance document.read ./deck.pdf max_pages=3 --output json
finance document.scan ./filing.html format=html query="operating lease costs" window=1200 --output json
finance document.window ./filing.html format=html match_id=char_52000_52200 direction=next chars=4000 --output json
```

## Help

```bash
finance help filings
finance filings.statement --help
finance document.scan --help
```
