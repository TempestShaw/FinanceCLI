---
title: Quick Start
description: Install Finance CLI and run the first research commands.
---

Check the install:

```bash
finance --list
finance sources.status
```

Run a first set of research commands:

```bash
finance filings.recent AAPL forms=10-K,10-Q limit=3
finance filings.statement COST statement=balance query="Common Stock"
finance document.scan url=https://www.sec.gov/.../filing.htm format=html query="operating lease costs" window=1200
finance formula.margin numerator=11969 denominator=254453
finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31 fast=20 slow=100
```

Most commands return JSON by default:

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

## Help

```bash
finance help filings
finance filings.statement --help
finance document.scan --help
```
