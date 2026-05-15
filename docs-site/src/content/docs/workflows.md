---
title: Workflows
description: Repeatable research workflows for filings, documents, formulas, and automation.
---

## Automated Research

Finance CLI works well in local scripts, notebooks, CI jobs, and research automation because commands are small, explicit, and machine-readable.

The document examples below assume you have already downloaded or saved the filing HTML as `./filing.html`. Use `filings.recent`, `filings.read`, or the SEC website to choose the filing first.

```bash
finance document.scan ./filing.html format=html query="operating lease costs" window=1200
finance document.window ./filing.html format=html match_id=char_52000_52200 direction=next chars=4000
finance filings.statement COST statement=balance query="Common Stock"
finance formula.net_debt debt=11415 cash=11144 operating_cash=5089
```

A typical automated research workflow is:

1. discover the filing or presentation
2. scan for the relevant section, metric, table, or phrase
3. continue reading from a stable match id or character window
4. calculate the metric with explicit inputs
5. preserve the command and JSON output as audit trail

## Agent Playbooks

These playbooks are templates for agents. They are also included in [`tools.json`](/FinanceCLI/tools.json).

### Extract A Metric From A 10-K

```yaml
task: extract_metric_from_10k
steps:
  - filings.recent
  - filings.statement
  - document.scan
  - document.window
  - formula.margin
failure_modes:
  - if no XBRL row matches, fall back to filings.reports then filings.report
  - if the table is narrative or HTML-only, use document.scan with match=all_terms
  - cite accession/url/report_name/section/start_char/end_char when available
```

### Explain A Dated Price Move

```yaml
task: explain_price_move
steps:
  - price.moves
  - price.context
  - news.search
  - filings.recent
  - transcripts.search
failure_modes:
  - if no evidence is found, say no direct evidence was found
  - do not infer causality from price movement alone
  - preserve source/provider/date/url fields
```

### Discover And Contextualize A Screen

```yaml
task: screen_and_contextualize_equities
steps:
  - screen.predefined
  - screen.run
  - symbol.snapshot
  - market.quote
  - filings.recent
failure_modes:
  - if a screen returns fewer rows than requested, keep the returned count
  - do not describe screen membership as a recommendation
```

### Run A Reproducible Backtest

```yaml
task: run_reproducible_backtest
steps:
  - backtest.strategies
  - backtest.describe
  - backtest.run
  - backtest.tune
failure_modes:
  - require explicit symbols and dates
  - preserve strategy name, params, provider, and JSON output
```

## Why Not Just A Notebook?

| Research job | Notebook-first workflow | Finance CLI workflow |
| --- | --- | --- |
| Pull a 10-K section | Write SEC lookup, filing selection, parser setup, and cleanup code. | `finance filings.read AAPL section=mda` |
| Inspect a filing table | Search raw HTML or build one-off XBRL/table parsing. | `finance filings.statement COST statement=balance query="Common Stock"` |
| Continue reading a long document | Copy text into cells and lose the original location. | `finance document.window ./filing.html match_id=char_52000_52200 direction=next` |
| Reuse finance formulas | Reimplement formulas and unit conventions in each notebook. | `finance formula.roic nopat=7113 invested_capital=28077` |
| Run a quick strategy check | Build the data fetch, signals, portfolio, and metrics before testing the idea. | `finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31` |
| Make research reproducible | Commit notebooks with hidden state and noisy diffs. | Commit commands, JSON outputs, and CI checks as plain text. |

Notebooks are still useful for exploration and visualization. Finance CLI is for repeated research steps you want to make portable, auditable, and easy to run again.
