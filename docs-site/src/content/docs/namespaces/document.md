---
title: document
description: Read, scan, window, extract tables, and run OCR on PDF or HTML documents.
---

Use `document.*` when the input is a concrete document path or URL. It works for local PDFs, SEC HTML pages, investor decks, and document snippets produced by other commands.

## Input Conventions

All document commands accept the document as the first positional argument or as `source=`, `path=`, or `url=`.

`format=` is available on text commands when auto-detection is not enough. Supported values are `pdf` and `html`. Leave it unset to infer from the path, URL, or response content.

## Parameters

### `document.read`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` / `source` / `path` / `url` | Yes | None | Local path or URL | Document to read. Positional source and keyed source forms are equivalent. |
| `format` | No | Auto | `pdf`, `html` | Forces the parser. Use `html` for SEC filing pages and `pdf` for local or remote PDFs. |
| `max_chars` | No | `12000` | Integer; `0` means no text truncation in current readers | Maximum text characters returned. Metadata still includes total `char_count`. |
| `max_pages` | No | All pages | Integer; `0` means all pages | Limits page processing for PDFs/OCR-style readers. |

### `document.scan`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` / `source` / `path` / `url` | Yes | None | Local path or URL | Document to scan. |
| `query` | No | None | Text | Literal query. If present, it becomes the only scan topic. |
| `topics` / `topic` | No | None | Comma-separated terms | Topic names or literal fuzzy queries. Known topics include `disclosure`, `risk`, `financial_reporting`, `portfolio`, and `guidance`; unknown values are treated as literal queries. |
| `format` | No | Auto | `pdf`, `html` | Forces document parser. |
| `match` | No | `fuzzy` | `fuzzy`, `all_terms` | `fuzzy` uses RapidFuzz scoring. `all_terms` requires all meaningful query terms to appear. |
| `threshold` | No | `80.0` | Number | Minimum match score. Use `100` with `match=all_terms` for exact term coverage. |
| `max_chars` | No | `12000` | Integer; `0` means scan full extracted text | Maximum extracted text considered. |
| `max_pages` | No | All pages | Integer; `0` means all pages | Limits page processing. |
| `limit` | No | `50` | Integer | Maximum matches returned. |
| `window` | No | `0` | Integer | Adds surrounding text to each match when greater than zero. |
| `start_char` | No | None | Integer | Restricts scanning to text starting at this character offset. |
| `end_char` | No | None | Integer | Restricts scanning to text ending at this character offset. |

### `document.window`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` / `source` / `path` / `url` | Yes | None | Local path or URL | Document to read from. |
| `format` | No | Auto | `pdf`, `html` | Forces document parser. |
| `start_char` / `start` | Required unless `match_id` is set | None | Integer | Character offset to anchor the window. |
| `match_id` | Required unless `start_char` is set | None | `char_START_END` | Match ID returned by `document.scan`. |
| `chars` | No | `4000` | Integer | Window size. |
| `direction` | No | `around` | `around`, `next`, `previous` | Reads around the anchor, after the match/window, or before it. |

### `document.tables`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` / `source` / `path` / `url` | Yes | None | Local path or URL | PDF to parse for tables. |
| `pages` | No | `1-end` | Camelot page expression, such as `1`, `1-3`, `all` | Pages passed to Camelot. |
| `flavor` | No | `stream` | `stream`, `lattice` | `stream` is for whitespace-separated tables. `lattice` is for ruled-line tables and may require Ghostscript. |
| `max_tables` | No | `20` | Integer | Maximum tables returned. |
| `max_rows` | No | `25` | Integer | Maximum preview rows per table. |

### `document.ocr`

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` / `source` / `path` / `url` | Yes | None | Local path or URL | Document to OCR. |
| `max_chars` | No | `12000` | Integer | Maximum OCR text characters returned. |
| `max_pages` | No | All pages | Integer; `0` means all pages | Limits OCR page processing. |

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
