---
title: Namespaces
description: Finance CLI command namespaces grouped by research workflow.
---

Finance CLI commands are grouped by the research job they support. Use this page when you know the workflow you want but do not know the exact command namespace yet.

## Setup & Planning

| Namespace | Use it for |
| --- | --- |
| [`sources`](/FinanceCLI/namespaces/sources/) | Inspect installed providers, configured credentials, package readiness, and connectivity. |
| [`research`](/FinanceCLI/namespaces/research/) | Generate a command plan before running a public-company research workflow. |

## Filings & Documents

| Namespace | Use it for |
| --- | --- |
| [`filings`](/FinanceCLI/namespaces/filings/) | Discover SEC filings, read canonical sections, pull XBRL statement rows, and inspect filing reports. |
| [`document`](/FinanceCLI/namespaces/document/) | Read PDFs and HTML, scan text, open windows around matches, extract tables, and run OCR fallback. |
| [`ir`](/FinanceCLI/namespaces/ir/) | Discover investor presentations and extract text from presentation URLs. |

## Market Discovery

| Namespace | Use it for |
| --- | --- |
| [`symbol`](/FinanceCLI/namespaces/symbol/) | Resolve company profile fields, SEC identity, and compact symbol snapshots. |
| [`market`](/FinanceCLI/namespaces/market/) | Fetch quotes, OHLCV bars, market status, regime summaries, and sector heat. |
| [`calendar`](/FinanceCLI/namespaces/calendar/) | Read company calendar fields and earnings-date rows. |
| [`sector`](/FinanceCLI/namespaces/sector/) | Discover sector keys, industries, overview fields, and sector tables. |
| [`industry`](/FinanceCLI/namespaces/industry/) | Discover industry keys, industry overviews, and industry tables. |
| [`screen`](/FinanceCLI/namespaces/screen/) | List and run predefined Yahoo Finance screens. |
| [`fundamentals`](/FinanceCLI/namespaces/fundamentals/) | Fetch provider financial statement rows outside SEC filing context. |

## News & Evidence

| Namespace | Use it for |
| --- | --- |
| [`news`](/FinanceCLI/namespaces/news/) | Search source-attributed news and run GDELT timeline, tone, context, geo, or document analysis. |
| [`price`](/FinanceCLI/namespaces/price/) | Find price moves and gather dated evidence windows around market events. |
| [`transcripts`](/FinanceCLI/namespaces/transcripts/) | Search, read, and extract Q&A from public earnings-call transcripts. |
| [`kpi`](/FinanceCLI/namespaces/kpi/) | Extract KPI evidence from filings and transcripts with source snippets. |

## Calculators & Backtests

| Namespace | Use it for |
| --- | --- |
| [`formula`](/FinanceCLI/namespaces/formula/) | Run deterministic finance formulas from explicit numeric inputs. |
| [`valuation`](/FinanceCLI/namespaces/valuation/) | Run DCF, NPV, IRR, WACC, multiples, and scenario math from explicit assumptions. |
| [`estimates`](/FinanceCLI/namespaces/estimates/) | Compare reported or assumed values against consensus inputs and fetch consensus estimate rows. |
| [`backtest`](/FinanceCLI/namespaces/backtest/) | Inspect strategies, create payloads, run VectorBT simulations, tune grids, and preview factor weights. |
