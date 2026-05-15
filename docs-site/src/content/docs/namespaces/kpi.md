---
title: kpi
description: Extract and compare operating KPIs from transcripts and other supported source documents.
---

# finance kpi

The `kpi.*` commands extract operating metrics from transcripts and summarize KPI history across documents. Use this namespace when the user asks for ARR, customer counts, NRR, margins, or similar operating metrics that must be cited to source text.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance kpi.extract

Extract KPI evidence from filings or transcripts.

### What it does

`finance kpi.extract` extracts KPI evidence from filings or transcripts. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `source`, `metrics`, `documents`, `kpis`, `count`, `total_count`, `truncated`.

### When to use it

Use this command when you need cited KPI evidence rows from a specified source set, such as recent transcripts, filings, or both.

Behavior details: Returns evidence rows, not investment conclusions.

### Usage

```bash
finance kpi.extract SYMBOL [source=transcripts|filings|both metrics=arr,nrr limit=30 quarter=latest form=10-K] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `source` | No | None | `transcripts`, `filings`, `both` | Provider/source key accepted by this command. |
| `form` | No | `10-K` | String | SEC form type. |
| `limit` | No | `30` | Integer | Maximum number of records returned. |
| `metrics` | No | `arr,nrr` | String | Comma-separated KPI names to search for, such as `arr,nrr,large_customers`. |
| `quarter` | No | `latest` | String | Quarter selector such as `latest`, `Q4 2026`, or another provider-supported quarter label. |

### Basic usage

```bash
finance kpi.extract IOT source=transcripts metrics=arr,net_new_arr,large_customers,nrr limit=8 --output json
```

### Example output

This output was generated with `finance kpi.extract IOT source=transcripts metrics=arr,net_new_arr,large_customers,nrr limit=8 --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "source": "transcripts",
    "metrics": [
      "arr",
      "net_new_arr",
      "large_customers",
      "nrr"
    ],
    "documents": [
      {
        "doc_ref": 0,
        "kind": "transcript",
        "symbol": "IOT",
        "title": "Samsara (IOT) Q4 2026 Earnings Call Transcript",
        "quarter": "Q4 2026",
        "period": "Q4 2026",
        "published_at": "2026-03-05T23:27:39+00:00",
        "url": "https://www.fool.com/earnings/call-transcripts/2026/03/05/samsara-iot-q4-2026-earnings-call-transcript/",
        "source": "motley_fool"
      }
    ],
    "kpis": [
      {
        "metric": "arr",
        "value": {
          "raw": "$1.9 billion",
          "number": 1900000000.0,
          "currency": "USD"
        },
        "period": "Q4 2026",
        "evidence": "We ended the year with $1.9 billion in ARR, growing 30% year over year.",
        "confidence": "medium",
        "matched_term": "arr",
        "match_score": 100.0,
        "match_method": "exact",
        "related": [
          {
            "v": "30%",
            "r": "yoy"
          }
        ],
        "doc_ref": 0
      },
      {
        "metric": "net_new_arr",
        "value": {
          "raw": "$432 million",
          "number": 432000000.0,
          "currency": "USD"
        },
        "period": "Q4 2026",
        "evidence": "Our $432 million of net new ARR drove this performance, growing 21% year over year and demonstrating our ability to accelerate growth even as we operate at much larger scale.",
        "confidence": "medium",
        "matched_term": "net new arr",
        "match_score": 100.0,
        "match_method": "exact",
        "related": [
          {
            "v": "21%",
            "r": "yoy"
          }
        ],
        "doc_ref": 0
      },
      {
        "metric": "arr",
        "value": {
          "raw": "$1.2 billion",
          "number": 1200000000.0,
          "currency": "USD"
        },
        "period": "Q4 2026",
        "evidence": "We ended the year with $1.2 billion of ARR from our $100K+ ARR customers, an increase of 37% year over year, our second consecutive quarter of sequential acceleration.",
        "confidence": "medium",
        "matched_term": "arr",
        "match_score": 100.0,
        "match_method": "exact",
        "related": [
          {
            "v": "$100K+",
            "r": "threshold",
            "desc": "ARR customers"
          },
          {
            "v": "37%",
            "r": "yoy"
          }
        ],
        "doc_ref": 0
      },
      {
        "metric": "large_customers",
        "value": {
          "raw": "204",
          "number": 204.0
        },
        "period": "FY 2026",
        "evidence": "In Q4, we added 204 new $100K+ ARR customers and ended FY 2026 with 3,194 $100K+ ARR customers.",
        "confidence": "medium",
        "matched_term": "$100k+ arr customers",
        "match_score": 100.0,
        "match_method": "exact",
        "related": [
          {
            "v": "$100K+",
            "r": "threshold",
            "desc": "ARR customers"
          },
          {
            "v": "3,194",
            "r": "count",
            "desc": "customers"
          }
        ],
        "doc_ref": 0
      },
      {
        "metric": "arr",
        "value": {
          "raw": "$1.9 billion",
          "number": 1900000000.0,
          "currency": "USD"
        },
        "period": "FY 2026",
        "evidence": "Q4 and FY 2026 ending ARR was $1.9 billion, an increase of 30% year over year, accelerating sequentially at a larger scale.",
        "confidence": "medium",
        "matched_term": "arr",
        "match_score": 100.0,
        "match_method": "exact",
        "related": [
          {
            "v": "30%",
            "r": "yoy"
          }
        ],
        "doc_ref": 0
      },
      {
        "metric": "net_new_arr",
        "value": {
          "raw": "$145 million",
          "number": 145000000.0,
          "currency": "USD"
        },
        "period": "Q4 2026",
        "evidence": "Within that, we added $145 million of net new ARR in Q4, an increase of 33% year over year or 31% in constant currency, resulting in the third consecutive quarter of accelerating sequential growth and the highest net new ARR growth rate in the past eight quarters.",
        "confidence": "medium",
        "matched_term": "net new arr",
        "match_score": 100.0,
        "match_method": "exact",
        "related": [
          {
            "v": "33%",
            "r": "yoy"
          },
          {
            "v": "31%",
            "r": "yoy"
          }
        ],
        "doc_ref": 0
      },
      {
        "metric": "net_new_arr",
        "value": {
          "raw": "$432 million",
          "number": 432000000.0,
          "currency": "USD"
        },
        "period": "FY 2026",
        "evidence": "Our overall net new ARR in FY 2026 was $432 million, an increase of 21% year over year, which also accelerated year over year at a larger scale.",
        "confidence": "medium",
        "matched_term": "net new arr",
        "match_score": 100.0,
        "match_method": "exact",
        "related": [
          {
            "v": "21%",
            "r": "yoy"
          }
        ],
        "doc_ref": 0
      },
      {
        "metric": "large_customers",
        "value": {
          "raw": "3,194",
          "number": 3194.0
        },
        "period": "Q4 2026",
        "evidence": "In terms of large customers, we ended Q4 with 3,194 $100K+ ARR customers, including a quarterly increase of 204, our second-highest quarter ever.",
        "confidence": "medium",
        "matched_term": "$100k+ arr customers",
        "match_score": 100.0,
        "match_method": "exact",
        "related": [
          {
            "v": "$100K+",
            "r": "threshold",
            "desc": "ARR customers"
          },
          {
            "v": "204",
            "r": "count",
            "desc": "customers"
          }
        ],
        "doc_ref": 0
      }
    ],
    "count": 8,
    "total_count": 11,
    "truncated": true,
    "warnings": []
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
| `data.documents` | array | Source documents inspected by the command. |
| `data.documents[]` | object | Source documents inspected by the command. |
| `data.kpis` | array | Extracted KPI evidence records. |
| `data.kpis[]` | object | Extracted KPI evidence records. |
| `data.metrics` | array | Metrics requested by the caller. |
| `data.metrics[]` | string | Metrics requested by the caller. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Ticker symbol used by the command. |
| `data.total_count` | integer | Total matching records before command-level truncation. |
| `data.truncated` | boolean | Whether the command truncated the result. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |
| `data.documents[].doc_ref` | integer | Stable document reference used inside the result. |
| `data.documents[].kind` | string | Presentation or document kind. |
| `data.documents[].period` | string | Reporting or estimate period. |
| `data.documents[].published_at` | string | Publication timestamp returned by the provider. |
| `data.documents[].quarter` | string | Fiscal quarter label. |
| `data.documents[].source` | string | Provider or source identifier for the returned data. |
| `data.documents[].symbol` | string | Ticker symbol associated with the source document. |
| `data.documents[].title` | string | Source document title. |
| `data.documents[].url` | string | Source URL. |
| `data.kpis[].confidence` | string | Regime confidence score. |
| `data.kpis[].doc_ref` | integer | Stable document reference used inside the result. |
| `data.kpis[].evidence` | string | Source text evidence for a KPI or answer. |
| `data.kpis[].match_method` | string | Matching method used for the KPI or search hit. |
| `data.kpis[].match_score` | number | Similarity or confidence score for the match. |
| `data.kpis[].matched_term` | string | Term that matched the requested KPI. |
| `data.kpis[].metric` | string | Metric name. |
| `data.kpis[].period` | string | Reporting or estimate period. |
| `data.kpis[].related` | array | Nearby related matches for the same KPI evidence row. |
| `data.kpis[].related[]` | object | Related KPI evidence match. |
| `data.kpis[].value` | object | Parsed KPI value object when the extractor identifies a numeric or textual value. |
| `data.kpis[].related[].desc` | string | Description of the related match. |
| `data.kpis[].related[].r` | string | Related match reference or relationship label. |
| `data.kpis[].related[].v` | string | Related match value text. |
| `data.kpis[].value.currency` | string | Trading or reporting currency. |
| `data.kpis[].value.number` | number | Numeric value parsed from text when available. |
| `data.kpis[].value.raw` | string | Raw provider value. |

## finance kpi.history

Extract KPI evidence across recent transcripts.

### What it does

`finance kpi.history` extracts KPI evidence across recent transcripts. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `source`, `metrics`, `history`, `count`.

### When to use it

Use this command when you need to compare KPI evidence across recent documents rather than inspect only one document.

### Usage

```bash
finance kpi.history SYMBOL [source=transcripts metrics=arr,nrr limit=4 per_document_limit=20] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `source` | No | `transcripts` | String | Provider/source key accepted by this command. |
| `limit` | No | `4` | Integer | Maximum number of records returned. |
| `metrics` | No | `arr,nrr` | String | Comma-separated KPI names to search for, such as `arr,nrr,large_customers`. |
| `per_document_limit` | No | `20` | Integer | Maximum KPI evidence rows kept per source document. |

### Basic usage

```bash
finance kpi.history IOT metrics=arr,large_customers limit=2 per_document_limit=4 --output json
```

### Example output

This output was generated with `finance kpi.history IOT metrics=arr,large_customers limit=2 per_document_limit=4 --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "source": "transcripts",
    "metrics": [
      "arr",
      "large_customers"
    ],
    "history": [
      {
        "documents": [
          {
            "doc_ref": 0,
            "kind": "transcript",
            "symbol": "IOT",
            "title": "Samsara (IOT) Q4 2026 Earnings Call Transcript",
            "quarter": "Q4 2026",
            "period": "Q4 2026",
            "published_at": "2026-03-05T23:27:39+00:00",
            "url": "https://www.fool.com/earnings/call-transcripts/2026/03/05/samsara-iot-q4-2026-earnings-call-transcript/",
            "source": "motley_fool"
          }
        ],
        "kpis": [
          {
            "metric": "arr",
            "value": {
              "raw": "$1.9 billion",
              "number": 1900000000.0,
              "currency": "USD"
            },
            "period": "Q4 2026",
            "evidence": "We ended the year with $1.9 billion in ARR, growing 30% year over year.",
            "confidence": "medium",
            "matched_term": "arr",
            "match_score": 100.0,
            "match_method": "exact",
            "related": [
              {
                "v": "30%",
                "r": "yoy"
              }
            ],
            "doc_ref": 0
          },
          {
            "metric": "arr",
            "value": {
              "raw": "$1.2 billion",
              "number": 1200000000.0,
              "currency": "USD"
            },
            "period": "Q4 2026",
            "evidence": "We ended the year with $1.2 billion of ARR from our $100K+ ARR customers, an increase of 37% year over year, our second consecutive quarter of sequential acceleration.",
            "confidence": "medium",
            "matched_term": "arr",
            "match_score": 100.0,
            "match_method": "exact",
            "related": [
              {
                "v": "$100K+",
                "r": "threshold",
                "desc": "ARR customers"
              },
              {
                "v": "37%",
                "r": "yoy"
              }
            ],
            "doc_ref": 0
          },
          {
            "metric": "large_customers",
            "value": {
              "raw": "204",
              "number": 204.0
            },
            "period": "FY 2026",
            "evidence": "In Q4, we added 204 new $100K+ ARR customers and ended FY 2026 with 3,194 $100K+ ARR customers.",
            "confidence": "medium",
            "matched_term": "$100k+ arr customers",
            "match_score": 100.0,
            "match_method": "exact",
            "related": [
              {
                "v": "$100K+",
                "r": "threshold",
                "desc": "ARR customers"
              },
              {
                "v": "3,194",
                "r": "count",
                "desc": "customers"
              }
            ],
            "doc_ref": 0
          },
          {
            "metric": "arr",
            "value": {
              "raw": "$1.9 billion",
              "number": 1900000000.0,
              "currency": "USD"
            },
            "period": "FY 2026",
            "evidence": "Q4 and FY 2026 ending ARR was $1.9 billion, an increase of 30% year over year, accelerating sequentially at a larger scale.",
            "confidence": "medium",
            "matched_term": "arr",
            "match_score": 100.0,
            "match_method": "exact",
            "related": [
              {
                "v": "30%",
                "r": "yoy"
              }
            ],
            "doc_ref": 0
          }
        ],
        "count": 4
      },
      {
        "documents": [
          {
            "doc_ref": 0,
            "kind": "transcript",
            "symbol": "IOT",
            "title": "Samsara (IOT) Q3 2026 Earnings Call Transcript",
            "quarter": "Q3 2026",
            "period": "Q3 2026",
            "published_at": "2025-12-05T15:06:48+00:00",
            "url": "https://www.fool.com/earnings/call-transcripts/2025/12/05/samsara-iot-q3-2026-earnings-call-transcript/",
            "source": "motley_fool"
          }
        ],
        "kpis": [
          {
            "metric": "arr",
            "value": {
              "raw": "$1.75 billion",
              "number": 1750000000.0,
              "currency": "USD"
            },
            "period": "Q3 2026",
            "evidence": "We ended Q3 with $1.75 billion in ARR, growing 29% year-over-year.",
            "confidence": "medium",
            "matched_term": "arr",
            "match_score": 100.0,
            "match_method": "exact",
            "related": [
              {
                "v": "29%",
                "r": "pct"
              }
            ],
            "doc_ref": 0
          },
          {
            "metric": "arr",
            "value": {
              "raw": "$100,000",
              "number": 100000.0,
              "currency": "USD"
            },
            "period": "Q3 2026",
            "evidence": "In Q3, we added 219 customers with $100,000 plus in ARR, a quarterly record.",
            "confidence": "medium",
            "matched_term": "arr",
            "match_score": 100.0,
            "match_method": "exact",
            "related": [
              {
                "v": "219",
                "r": "count",
                "desc": "customers"
              }
            ],
            "doc_ref": 0
          },
          {
            "metric": "arr",
            "value": {
              "raw": "$1 billion",
              "number": 1000000000.0,
              "currency": "USD"
            },
            "period": "Q3 2026",
            "evidence": "Our $100,000-plus ARR customers now contribute more than $1 billion of ARR, growing 36% year-over-year.",
            "confidence": "medium",
            "matched_term": "arr",
            "match_score": 100.0,
            "match_method": "exact",
            "related": [
              {
                "v": "$100,000",
                "r": "threshold",
                "desc": "ARR customers"
              },
              {
                "v": "36%",
                "r": "mix"
              }
            ],
            "doc_ref": 0
          },
          {
            "metric": "arr",
            "value": {
              "raw": "$1 million",
              "number": 1000000.0,
              "currency": "USD"
            },
            "period": "Q3 2026",
            "evidence": "We also added 17 $1 million-plus ARR customers tied for a quarterly record.",
            "confidence": "medium",
            "matched_term": "arr",
            "match_score": 100.0,
            "match_method": "exact",
            "related": [
              {
                "v": "17",
                "r": "count",
                "desc": "customers"
              }
            ],
            "doc_ref": 0
          }
        ],
        "count": 4
      }
    ],
    "count": 2
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
| `data.history` | array | Historical KPI records grouped by metric or document. |
| `data.history[]` | object | Historical KPI records grouped by metric or document. |
| `data.metrics` | array | Metrics requested by the caller. |
| `data.metrics[]` | string | Metrics requested by the caller. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Ticker symbol used by the command. |
| `data.history[].count` | integer | Number of records included in the adjacent result array. |
| `data.history[].documents` | array | Source documents inspected by the command. |
| `data.history[].documents[]` | object | Source documents inspected by the command. |
| `data.history[].kpis` | array | Extracted KPI evidence records. |
| `data.history[].kpis[]` | object | Extracted KPI evidence records. |
| `data.history[].documents[].doc_ref` | integer | Stable document reference used inside the result. |
| `data.history[].documents[].kind` | string | Presentation or document kind. |
| `data.history[].documents[].period` | string | Reporting or estimate period. |
| `data.history[].documents[].published_at` | string | Publication timestamp returned by the provider. |
| `data.history[].documents[].quarter` | string | Fiscal quarter label. |
| `data.history[].documents[].source` | string | Provider or source identifier for the returned data. |
| `data.history[].documents[].symbol` | string | Ticker symbol associated with the historical source document. |
| `data.history[].documents[].title` | string | Source document title for the historical KPI record. |
| `data.history[].documents[].url` | string | Source URL. |
| `data.history[].kpis[].confidence` | string | Regime confidence score. |
| `data.history[].kpis[].doc_ref` | integer | Stable document reference used inside the result. |
| `data.history[].kpis[].evidence` | string | Source text evidence for a KPI or answer. |
| `data.history[].kpis[].match_method` | string | Matching method used for the KPI or search hit. |
| `data.history[].kpis[].match_score` | number | Similarity or confidence score for the match. |
| `data.history[].kpis[].matched_term` | string | Term that matched the requested KPI. |
| `data.history[].kpis[].metric` | string | Metric name. |
| `data.history[].kpis[].period` | string | Reporting or estimate period. |
| `data.history[].kpis[].related` | array | Nearby related matches for the KPI evidence row. |
| `data.history[].kpis[].related[]` | object | Related KPI evidence match. |
| `data.history[].kpis[].value` | object | Parsed KPI value object for the historical evidence row. |
| `data.history[].kpis[].related[].desc` | string | Description of the related match. |
| `data.history[].kpis[].related[].r` | string | Related match reference or relationship label. |
| `data.history[].kpis[].related[].v` | string | Related match value text. |
| `data.history[].kpis[].value.currency` | string | Trading or reporting currency. |
| `data.history[].kpis[].value.number` | number | Numeric value parsed from text when available. |
| `data.history[].kpis[].value.raw` | string | Raw provider value. |
