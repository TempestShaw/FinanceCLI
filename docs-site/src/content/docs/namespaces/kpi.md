---
title: kpi
description: Extract KPI evidence from filings and transcripts.
---

Use `kpi.*` when you need evidence snippets for operating metrics such as ARR, large customers, NRR, RPO, margins, or product-specific metrics.

## Parameters

### `kpi.extract`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Company ticker. |
| `source` | No | `transcripts` | `transcripts`, `filings`, `both` | Evidence source. |
| `metrics` | No | Built-in metric set | Comma-separated metric names | Limits extraction to requested metrics. Examples: `arr`, `nrr`, `large_customers`, `rpo`, `revenue_growth`, `operating_margin`, `fcf_margin`. |
| `limit` | No | `30` | Integer | Maximum evidence rows returned. |
| `quarter` | No | `latest` | Transcript quarter label | Transcript selection when `source=transcripts` or `both`. |
| `form` | No | `10-K` | SEC form | Filing form when `source=filings` or `both`. |

### `kpi.history`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` | Yes | None | Public ticker | Company ticker. |
| `source` | No | `transcripts` | Currently transcript-oriented | Evidence source for history extraction. |
| `metrics` | No | Built-in metric set | Comma-separated metric names | Limits extraction to requested metrics. |
| `limit` | No | `4` | Integer | Maximum historical documents/periods. |
| `per_document_limit` | No | `20` | Integer | Maximum KPI rows per document. |

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
