---
title: research
description: Generate command-oriented research plans for a company or workflow style.
---

# finance research

The `research.*` commands generate reproducible command plans for a ticker and research style. Use this namespace to turn a broad question into a concrete sequence of Finance CLI commands.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance research.plan

Return a deterministic research command checklist.

### What it does

`finance research.plan` returns a deterministic research command checklist. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `style`, `plan_type`, `steps`, `count`, `notes`.

### When to use it

Use before executing a complex public-company research workflow.

Behavior details: This returns suggested commands only; it does not execute research or form conclusions. Use this as a navigation layer for repeatable research workflows.

### Usage

```bash
finance research.plan SYMBOL [style=fundamental] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `style` | No | `fundamental` | String | Research-plan style. The current public workflow centers on `fundamental`. |

### Basic usage

```bash
finance research.plan IOT style=fundamental --output json
```

### Example output

This output was generated with `finance research.plan IOT style=fundamental --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "style": "fundamental",
    "plan_type": "deterministic_cli_checklist",
    "steps": [
      {
        "id": "profile",
        "status": "supported",
        "objective": "Establish company identity, quote, market cap, and SEC CIK.",
        "commands": [
          "finance symbol.profile IOT",
          "finance market.quote IOT"
        ]
      },
      {
        "id": "filings",
        "status": "supported",
        "objective": "Read core 10-K sections for business model, risk, MD&A, and financial statement detail.",
        "commands": [
          "finance filings.recent IOT forms=10-K,10-Q,8-K limit=8",
          "finance filings.sections IOT form=10-K",
          "finance filings.read IOT form=10-K section=business max_chars=12000",
          "finance filings.read IOT form=10-K section=risk_factors max_chars=12000",
          "finance filings.read IOT form=10-K section=mda max_chars=12000",
          "finance filings.read IOT form=10-K section=financial_statements max_chars=12000"
        ]
      },
      {
        "id": "transcripts",
        "status": "supported",
        "objective": "Read recent earnings calls and analyst Q&A to capture current opportunities and concerns.",
        "commands": [
          "finance transcripts.search IOT limit=4",
          "finance transcripts.read IOT quarter=latest max_chars=12000",
          "finance transcripts.qa IOT quarter=latest limit=10"
        ]
      },
      {
        "id": "kpis",
        "status": "supported",
        "objective": "Extract KPI evidence without forcing a normalized conclusion.",
        "commands": [
          "finance kpi.extract IOT source=both metrics=arr,net_new_arr,large_customers,nrr,rpo,revenue_growth,operating_margin,fcf_margin limit=40",
          "finance kpi.history IOT metrics=arr,large_customers,nrr,revenue_growth limit=4 per_document_limit=12"
        ]
      },
      {
        "id": "price_history",
        "status": "supported",
        "objective": "Find major stock moves, then gather source-linked evidence around selected dates.",
        "commands": [
          "finance price.moves IOT years=3 threshold=8% limit=20",
          "finance price.context IOT date=MOVE_DATE lookback=3D news_limit=5"
        ]
      },
      {
        "id": "fundamentals",
        "status": "supported",
        "objective": "Fetch statement data for revenue, margins, cash flow, debt, and share information.",
        "commands": [
          "finance fundamentals.statement IOT statement=income period=annual",
          "finance fundamentals.statement IOT statement=cashflow period=annual",
          "finance fundamentals.statement IOT statement=balance period=annual"
        ]
      },
      {
        "id": "valuation",
        "status": "supported",
        "objective": "Calculate current multiples and user-supplied valuation scenarios after assumptions are chosen.",
        "commands": [
          "finance valuation.multiples IOT",
          "finance valuation.scenario IOT revenue=REVENUE_ASSUMPTION bear_multiple=BEAR base_multiple=BASE bull_multiple=BULL",
          "finance valuation.dcf cashflows=FCF1,FCF2,FCF3 discount_rate=WACC terminal_growth=G"
        ]
      },
      {
        "id": "open_gaps",
        "status": "partially_supported",
        "objective": "Note remaining workflow gaps that require judgment outside the CLI.",
        "commands": [],
        "missing": [
          "Investor Day deck retrieval",
          "Expert call transcripts",
          "Market consensus estimate comparison"
        ]
      }
    ],
    "count": 8,
    "notes": [
      "This is a navigation checklist, not an investment conclusion.",
      "Read returned evidence and choose assumptions before valuation."
    ]
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.notes` | array | Additional notes that affect interpretation. |
| `data.notes[]` | string | Additional notes that affect interpretation. |
| `data.plan_type` | string | Research plan template selected by the command. |
| `data.steps` | array | Research plan command steps. |
| `data.steps[]` | object | Research plan command steps. |
| `data.style` | string | Research style requested by the caller. |
| `data.symbol` | string | Ticker symbol used by the command. |
| `data.steps[].commands` | array | Commands included in a plan step. |
| `data.steps[].commands[]` | string | Commands included in a plan step. |
| `data.steps[].id` | string | Stable step identifier in the generated plan. |
| `data.steps[].missing` | array | Inputs still needed before the plan step can be completed. |
| `data.steps[].missing[]` | string | Inputs still needed before the plan step can be completed. |
| `data.steps[].objective` | string | Purpose of a plan step. |
| `data.steps[].status` | string | Whether the step is supported or partially supported by the CLI. |
