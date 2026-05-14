---
title: kpi
description: Extract KPI evidence from filings and transcripts.
---

Use `kpi.*` when you need evidence snippets for operating metrics such as ARR, large customers, NRR, RPO, margins, or product-specific metrics.

## Extract

```bash
finance kpi.extract IOT source=transcripts metrics=arr,large_customers limit=3
```

A live run found Samsara's Q4 2026 transcript and returned ARR and large-customer evidence:

```json
{
  "symbol": "IOT",
  "source": "transcripts",
  "metrics": [
    {
      "metric": "arr",
      "value_text": "$1.9 billion",
      "source_title": "Samsara (IOT) Q4 2026 Earnings Call Transcript"
    },
    {
      "metric": "large_customers",
      "value_text": "204"
    }
  ],
  "total_count": 7,
  "truncated": true
}
```

## History

```bash
finance kpi.history IOT metrics=arr,large_customers limit=4
```

Tested `kpi.history` result:

```json
{
  "symbol": "IOT",
  "source": "transcripts",
  "metrics": ["arr", "large_customers"],
  "history": [
    {
      "documents": [
        {
          "title": "Samsara (IOT) Q4 2026 Earnings Call Transcript",
          "quarter": "Q4 2026",
          "source": "motley_fool"
        }
      ],
      "kpis": [
        {
          "metric": "arr",
          "value": { "raw": "$1.9 billion", "number": 1900000000.0, "currency": "USD" },
          "period": "Q4 2026",
          "evidence": "We ended the year with $1.9 billion in ARR, growing 30% year over year."
        }
      ],
      "count": 7
    }
  ],
  "count": 2
}
```

Use history when you want repeated KPI evidence across multiple filings or transcript documents instead of one latest extraction.
