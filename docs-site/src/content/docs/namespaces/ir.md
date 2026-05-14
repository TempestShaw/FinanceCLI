---
title: ir
description: Discover and read investor presentation documents.
---

Use `ir.*` for investor deck discovery and extraction. It can search SEC exhibits, company IR pages, or both.

## Parameters

### `ir.presentations`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SYMBOL` / `symbol` | Yes | None | Public ticker | Company ticker. Positional symbol and `symbol=` are equivalent. |
| `limit` | No | `20` | Integer | Maximum candidates returned. |
| `source` | No | `auto` | `auto`, `sec`, `company_ir`, `all` | Discovery source. `auto` tries SEC first and falls back to company IR when SEC returns no candidates. |

### `ir.read`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `url` | Yes | None | Presentation/exhibit URL | URL to fetch and extract. Usually from `ir.presentations`. |
| `max_chars` | No | `12000` | Integer | Maximum extracted text returned. |
| `ocr` | No | `off` | `off`, `auto`, `force` | OCR behavior. `auto` uses OCR only when native extraction is missing or too short; `force` always attempts OCR. |

## Discover Presentations

```bash
finance ir.presentations NVDA limit=2 source=sec
```

A tested SEC-only NVIDIA run returned an empty presentation list:

```json
{
  "symbol": "NVDA",
  "source": "sec",
  "presentations": [],
  "count": 0,
  "notes": ["No SEC exhibit candidates matched the presentation scoring rules."]
}
```

Empty discovery results are valid. They mean no candidate matched the conservative deck heuristics for that source and limit.

## Read A Deck

```bash
finance ir.read url=https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/aapl-20260328.htm ocr=off max_chars=800
```

Tested `ir.read` result:

```json
{
  "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/aapl-20260328.htm",
  "format": "html",
  "char_count": 98063,
  "returned_chars": 800,
  "truncated": true,
  "pages": [
    {
      "page": 1,
      "char_count": 98063,
      "returned_chars": 800,
      "truncated": true
    }
  ],
  "warnings": []
}
```

`ir.read` first attempts native extraction. With `ocr=auto`, it uses OCR only when native extraction is missing or too short.
