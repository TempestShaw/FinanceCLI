---
title: research
description: Generate a deterministic public-company research checklist.
---

Use `research.plan` when you want the next commands for a company research workflow.

```bash
finance research.plan IOT style=fundamental
```

A tested run returned a navigation checklist with steps for profile, filings, transcripts, KPIs, price history, fundamentals, valuation, and open gaps.

```json
{
  "symbol": "IOT",
  "style": "fundamental",
  "steps": [
    {
      "name": "profile",
      "commands": ["finance symbol.profile IOT"]
    },
    {
      "name": "kpis",
      "commands": ["finance kpi.extract IOT source=both metrics=arr,..."]
    }
  ],
  "notes": ["This is a workflow checklist, not an investment conclusion."]
}
```

The command does not fetch all data itself. It produces an auditable set of follow-up commands so a script or analyst can run the workflow step by step.
