---
title: JSON Results
description: Result envelopes and common success/failure shapes for agents.
---

Finance CLI commands return JSON with the same top-level envelope:

```json
{
  "ok": true,
  "data": {},
  "error": null,
  "warnings": []
}
```

Use [`tools.json`](/FinanceCLI/tools.json) for command-specific input and output schemas. The examples below are representative result shapes; provider values and source text vary by response.

## Success

```json
{
  "ok": true,
  "data": {
    "margin": 0.5,
    "margin_pct": 50.0,
    "inputs": {
      "numerator": 10.0,
      "denominator": 20.0
    },
    "method": "numerator / denominator"
  },
  "error": null,
  "warnings": []
}
```

## No Data

```json
{
  "ok": true,
  "data": {
    "symbol": "AAPL",
    "rows": [],
    "count": 0,
    "source": "yfinance"
  },
  "error": null,
  "warnings": []
}
```

For agents, no data is not the same as command failure. Keep the source, query, and filters in the answer.

## Provider Not Configured

```json
{
  "ok": false,
  "data": null,
  "error": "provider is not configured: set the required environment variable",
  "warnings": []
}
```

Surface the error. Do not replace it with stale or synthetic data.

## Rate Limited

```json
{
  "ok": false,
  "data": null,
  "error": "provider request failed: rate limited",
  "warnings": []
}
```

Retry policy belongs to the caller or automation layer. Preserve the provider/source in the surrounding task log when available.

## Parse Failed

```json
{
  "ok": false,
  "data": null,
  "error": "document parse failed: unsupported or encrypted file",
  "warnings": []
}
```

Prefer a fallback command when the workflow supports one, such as `document.ocr` after a native PDF parser cannot extract text.

## Partial Result With Warnings

```json
{
  "ok": true,
  "data": {
    "source": "report.pdf",
    "text": "extracted text excerpt",
    "char_count": 18420,
    "returned_chars": 12000,
    "truncated": true
  },
  "error": null,
  "warnings": [
    "output truncated to max_chars=12000"
  ]
}
```

Use the partial data, but keep the warnings visible and run a narrower follow-up command when needed.
