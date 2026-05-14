---
title: document
description: Read, scan, window, extract tables, and run OCR on PDF or HTML documents.
---

Use `document.*` when the input is a concrete document path or URL. It works for local PDFs, SEC HTML pages, investor decks, and document snippets produced by other commands.

## Read Text

```bash
finance document.read /tmp/financecli_sample.html format=html max_chars=1000
```

Tested `document.read` result:

```json
{
  "source": "/tmp/financecli_sample.html",
  "engine": "beautifulsoup",
  "format": "html",
  "text": "Sample filing\nTotal current assets were 100.\nOperating lease costs were 12.\nMetric\nValue\nRevenue\n123",
  "pages": [
    {
      "page": 1,
      "char_count": 100,
      "returned_chars": 100,
      "truncated": false,
      "blocks": [
        {
          "index": 0,
          "start_char": 0,
          "end_char": 100
        }
      ]
    }
  ],
  "char_count": 100,
  "returned_chars": 100,
  "truncated": false
}
```

`document.read` is the command to use when you need extracted text plus page/block offsets for later navigation.

## Scan For A Topic

```bash
finance document.scan /tmp/financecli_sample.html format=html query="operating lease costs" window=80 max_chars=0
```

Tested `document.scan` result:

```json
{
  "engine": "beautifulsoup",
  "format": "html",
  "topics": ["operating lease costs"],
  "match_mode": "fuzzy",
  "matches": [
    {
      "match_id": "char_0_100",
      "topic": "operating lease costs",
      "score": 100.0,
      "page": 1,
      "start_char": 0,
      "end_char": 100,
      "snippet": "Sample filing\nTotal current assets were 100.\nOperating lease costs were 12.\nMetric\nValue\nRevenue\n123",
      "window_start_char": 0,
      "window_end_char": 100
    }
  ],
  "count": 1,
  "pages_scanned": 1,
  "char_count": 100,
  "warnings": ["HTML extraction returned very short text; document may be a wrapper or script-rendered."]
}
```

`document.scan` is the command to use when you need matching evidence and offsets, not the full document.

## Read A Window

```bash
finance document.window /tmp/financecli_sample.html format=html start_char=0 chars=120
```

Tested `document.window` result:

```json
{
  "source": "/tmp/financecli_sample.html",
  "engine": "beautifulsoup",
  "format": "html",
  "start_char": 0,
  "end_char": 60,
  "returned_chars": 60,
  "char_count": 100,
  "direction": "around",
  "text": "Sample filing\nTotal current assets were 100.\nOperating lease",
  "warnings": ["HTML extraction returned very short text; document may be a wrapper or script-rendered."]
}
```

`document.window` is the command to use after `document.scan` when you want nearby text around a known character range or `match_id`.

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

A tested OCR run used `paddleocr_pp_structure_v3` and returned:

```json
{
  "engine": "paddleocr_pp_structure_v3",
  "text": "Metric\nValue\nRevenue\n123\nGross Profit 45\nOperating Income 12",
  "warnings": []
}
```

The first real PaddleOCR run may download model files; after that, failures should be explicit provider errors rather than empty fabricated text.
