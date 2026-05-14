---
title: document
description: Read, scan, window, extract tables, and run OCR on PDF or HTML documents.
---

Use `document.*` when the input is a concrete document path or URL. It works for local PDFs, SEC HTML pages, investor decks, and document snippets produced by other commands.

## Read And Search Text

```bash
finance document.read /tmp/financecli_sample.html format=html max_chars=1000
finance document.scan /tmp/financecli_sample.html format=html query="operating lease costs" window=80 max_chars=0
finance document.window /tmp/financecli_sample.html format=html start_char=0 chars=120
```

Example `document.scan` result:

```json
{
  "matches": [
    {
      "match_id": "char_0_148",
      "score": 100.0,
      "window": "..."
    }
  ],
  "warnings": ["HTML extraction returned very short text; document may be a wrapper or script-rendered."]
}
```

Short-text warnings are not fatal. They tell you the extracted document may be a wrapper, a tiny test file, or a page that needs a different source.

## PDF Tables

```bash
finance document.tables /tmp/financecli_table.pdf pages=1 flavor=stream max_tables=3 max_rows=5
```

A tested PDF table run used Camelot and returned one table with parsing metadata:

```json
{
  "engine": "camelot",
  "count": 1,
  "tables": [
    {
      "shape": [4, 1],
      "parsing_report": { "accuracy": 100.0 },
      "rows": [["Metric Value"], ["Revenue 123"]]
    }
  ]
}
```

## OCR

```bash
finance document.ocr /tmp/financecli_table.pdf max_pages=1 max_chars=1000
```

A tested OCR run used `paddleocr_pp_structure_v3` and returned text lines from the same PDF table. The first real PaddleOCR run may download model files; after that, failures should be explicit provider errors rather than empty fabricated text.
