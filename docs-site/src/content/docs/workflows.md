---
title: Workflows
description: Repeatable research workflows for filings, documents, formulas, and automation.
---

## Automated Research

Finance CLI works well in local scripts, notebooks, CI jobs, and research automation because commands are small, explicit, and machine-readable.

```bash
finance document.scan url=https://www.sec.gov/.../filing.htm format=html query="operating lease costs" window=1200
finance document.window url=https://www.sec.gov/.../filing.htm format=html match_id=char_52000_52200 direction=next chars=4000
finance filings.statement COST statement=balance query="Common Stock"
finance formula.net_debt debt=11415 cash=11144 operating_cash=5089
```

A typical automated research workflow is:

1. discover the filing or presentation
2. scan for the relevant section, metric, table, or phrase
3. continue reading from a stable match id or character window
4. calculate the metric with explicit inputs
5. preserve the command and JSON output as audit trail

## Why Not Just A Notebook?

| Research job | Notebook-first workflow | Finance CLI workflow |
| --- | --- | --- |
| Pull a 10-K section | Write SEC lookup, filing selection, parser setup, and cleanup code. | `finance filings.read AAPL section=mda` |
| Inspect a filing table | Search raw HTML or build one-off XBRL/table parsing. | `finance filings.statement COST statement=balance query="Common Stock"` |
| Continue reading a long document | Copy text into cells and lose the original location. | `finance document.window ... match_id=char_52000_52200 direction=next` |
| Reuse finance formulas | Reimplement formulas and unit conventions in each notebook. | `finance formula.roic nopat=7113 invested_capital=28077` |
| Run a quick strategy check | Build the data fetch, signals, portfolio, and metrics before testing the idea. | `finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31` |
| Make research reproducible | Commit notebooks with hidden state and noisy diffs. | Commit commands, JSON outputs, and CI checks as plain text. |

Notebooks are still useful for exploration and visualization. Finance CLI is for repeated research steps you want to make portable, auditable, and easy to run again.
