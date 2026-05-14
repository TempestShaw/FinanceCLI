---
title: ir
description: Discover and read investor presentation documents.
---

Use `ir.*` for investor deck discovery and extraction. It can search SEC exhibits, company IR pages, or both.

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
finance ir.read url=https://example.com/deck.pdf ocr=auto max_chars=4000
```

`ir.read` first attempts native extraction. With `ocr=auto`, it uses OCR only when native extraction is missing or too short.
