---
title: transcripts
description: Search, read, and extract Q&A from earnings-call transcripts.
---

Use `transcripts.*` for public earnings-call transcript pages.

## Search And Read

```bash
finance transcripts.search NVDA limit=2
finance transcripts.read NVDA quarter=latest max_chars=1200
```

A live search found NVIDIA Q4 2026 and Q3 2026 Motley Fool transcript pages. `transcripts.read` returned title, URL, publication date, text, `char_count`, `returned_chars`, and truncation metadata.

```json
{
  "title": "NVIDIA (NVDA) Q4 2026 Earnings Call Transcript",
  "char_count": 40061,
  "returned_chars": 1200,
  "truncated": true,
  "prepared_turn_count": 34
}
```

## Q&A

```bash
finance transcripts.qa NVDA quarter=latest limit=2
```

The same tested transcript returned zero Q&A pairs because the provider page did not expose a clean Q&A split for that article. That is a valid result; use `transcripts.read include_turns=true` when you need to inspect the raw speaker turns.
