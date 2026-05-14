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
      "id": "profile",
      "status": "supported",
      "commands": ["finance symbol.profile IOT"]
    },
    {
      "id": "kpis",
      "status": "supported",
      "commands": ["finance kpi.extract IOT source=both metrics=arr,..."]
    }
  ],
  "count": 8,
  "notes": [
    "This is a navigation checklist, not an investment conclusion.",
    "Read returned evidence and choose assumptions before valuation."
  ]
}
```

The command does not fetch all data itself. It produces an auditable set of follow-up commands so a script or analyst can run the workflow step by step.
