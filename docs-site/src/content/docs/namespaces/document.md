---
title: document
description: Read, scan, window, extract tables, and run OCR on PDF or HTML documents.
---

# finance document

The `document.*` commands operate on a concrete local path or URL. Use them when you already have a filing page, PDF, investor deck, exhibit, or extracted document URL and need structured text, match offsets, table previews, or OCR fallback.

All document commands return the standard Finance CLI JSON envelope:

```json
{
  "ok": true,
  "data": {},
  "error": null,
  "warnings": []
}
```

## finance document.read

Extract native text and layout blocks from a PDF or HTML document.

### What it does

`finance document.read` reads a local path or URL and returns extracted text, page metadata, block offsets, truncation metadata, and parser warnings. For HTML inputs it uses BeautifulSoup. For PDF inputs it uses the native PDF parser and does not run OCR.

### When to use it

Use this command for the first pass over a known document. It is the right command when you need the raw extracted text and stable offsets before choosing whether to scan, window, parse tables, or run OCR.

### Usage

```bash
finance document.read SOURCE|source=PATH_OR_URL [format=pdf|html max_chars=12000 max_pages=5]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` | Yes, unless `source`, `path`, or `url` is set | None | Local path or URL | Positional document source. |
| `source` | Yes, unless positional `SOURCE`, `path`, or `url` is set | None | Local path or URL | Keyword document source. |
| `path` | Yes, unless another source form is set | None | Local filesystem path | Alias for `source`. |
| `url` | Yes, unless another source form is set | None | HTTP(S) URL | Alias for `source`. |
| `format` | No | Auto-detected | `pdf`, `html` | Parser override. Use `html` for SEC filing pages and `pdf` for PDFs. |
| `max_chars` | No | `12000` | Integer; `0` means unbounded in current readers | Maximum extracted text characters returned. |
| `max_pages` | No | All pages | Integer; `0` means all pages | Maximum PDF pages to process. Ignored for single-page HTML extraction. |

### Basic usage

```bash
finance document.read ./filing.html format=html max_chars=4000 --output json
finance document.read ./deck.pdf max_pages=3 --output json
```

### Example output

This output was generated with `finance document.read /tmp/financecli_sample.html format=html max_chars=1000 --output json`.

```json
{
  "ok": true,
  "data": {
    "source": "/tmp/financecli_sample.html",
    "url": "/tmp/financecli_sample.html",
    "engine": "beautifulsoup",
    "format": "html",
    "text": "Sample filing\nTotal current assets were 100.\nOperating lease costs were 12.\nMetric\nValue\nRevenue\n123",
    "pages": [
      {
        "page": 1,
        "text": "Sample filing\nTotal current assets were 100.\nOperating lease costs were 12.\nMetric\nValue\nRevenue\n123",
        "char_count": 100,
        "returned_chars": 100,
        "truncated": false,
        "blocks": [
          {
            "index": 0,
            "text": "Sample filing\nTotal current assets were 100.\nOperating lease costs were 12.\nMetric\nValue\nRevenue\n123",
            "start_char": 0,
            "end_char": 100,
            "bbox": null
          }
        ]
      }
    ],
    "char_count": 100,
    "returned_chars": 100,
    "truncated": false,
    "warnings": [
      "HTML extraction returned very short text; document may be a wrapper or script-rendered."
    ]
  },
  "error": null,
  "warnings": [
    "HTML extraction returned very short text; document may be a wrapper or script-rendered."
  ]
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.source` | string | Source path or URL passed to the command. |
| `data.url` | string | URL/source value used by the HTML reader. Present for HTML reads. |
| `data.engine` | string | Parser engine, such as `beautifulsoup` or `pymupdf`. |
| `data.format` | string | Resolved document format: `html` or `pdf`. |
| `data.text` | string | Extracted text after `max_chars` truncation. |
| `data.pages` | array | Page-level extraction records. HTML inputs are returned as page `1`. |
| `data.pages[].text` | string | Page text after per-page extraction. |
| `data.pages[].char_count` | integer | Total characters found on the page. |
| `data.pages[].returned_chars` | integer | Characters returned for the page. |
| `data.pages[].truncated` | boolean | Whether page text was truncated. |
| `data.pages[].blocks` | array | Offset-bearing text blocks for follow-up matching. |
| `data.pages[].blocks[].start_char` | integer | Start character offset in the extracted text. |
| `data.pages[].blocks[].end_char` | integer | End character offset in the extracted text. |
| `data.pages[].blocks[].bbox` | array or null | Bounding box when the parser exposes layout coordinates. |
| `data.char_count` | integer | Total extracted character count before truncation. |
| `data.returned_chars` | integer | Total characters returned in `data.text`. |
| `data.truncated` | boolean | Whether `data.text` was truncated by `max_chars`. |
| `data.warnings` | array | Parser-specific warnings. These are also copied to the top-level `warnings` field. |

## finance document.scan

Search extracted document text for topics or literal phrases and return match offsets.

### What it does

`finance document.scan` reads the document, searches the extracted text using deterministic matching, and returns matched blocks with `match_id`, score, page, character offsets, and optional surrounding context.

The command supports fuzzy matching and an `all_terms` mode for table-style queries where every meaningful query term should be present.

### When to use it

Use this command when you need evidence discovery inside a filing, PDF, or HTML page. It is the command to run before `finance document.window` when you need stable offsets for follow-up reading.

### Usage

```bash
finance document.scan SOURCE|source=PATH_OR_URL [query=TEXT topics=TOPICS format=pdf|html match=fuzzy|all_terms threshold=80 max_chars=12000 max_pages=5 limit=50 window=0 start_char=0 end_char=0]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` | Yes, unless `source`, `path`, or `url` is set | None | Local path or URL | Positional document source. |
| `source` / `path` / `url` | Yes, unless positional `SOURCE` is set | None | Local path or URL | Keyword source forms. |
| `query` | No | None | Text | Literal query. When set, it becomes the only scan topic. |
| `topics` | No | Built-in default topics | Comma-separated topic names or literal queries | Topic list. Known topics include `disclosure`, `risk`, `financial_reporting`, `portfolio`, and `guidance`. Unknown topics are treated as literal queries. |
| `topic` | No | Same as `topics` | Comma-separated topic names or literal queries | Alias for `topics`. |
| `format` | No | Auto-detected | `pdf`, `html` | Parser override. |
| `match` | No | `fuzzy` | `fuzzy`, `all_terms` | Match mode. |
| `threshold` | No | `80.0` | Number | Minimum fuzzy score. Use `100` with `match=all_terms` for strict term coverage. |
| `max_chars` | No | `12000` | Integer; `0` means unbounded in current readers | Maximum extracted characters to scan. |
| `max_pages` | No | All pages | Integer; `0` means all pages | Maximum PDF pages to process. |
| `limit` | No | `50` | Integer | Maximum matches returned. |
| `window` | No | `0` | Integer | Adds surrounding text to each match when greater than zero. |
| `start_char` | No | None | Integer | Restricts scanning to blocks overlapping this start offset. |
| `end_char` | No | None | Integer | Restricts scanning to blocks overlapping this end offset. |

### Basic usage

```bash
finance document.scan ./filing.html format=html query="operating lease costs" window=80 max_chars=0 --output json
finance document.scan ./report.pdf topics=risk,financial_reporting max_pages=5 --output json
finance document.scan ./filing.html format=html match=all_terms threshold=100 query="Receivables net Total current assets" max_chars=0 --output json
```

### Example output

This output was generated with `finance document.scan /tmp/financecli_sample.html format=html query="operating lease costs" window=80 max_chars=0 --output json`.

```json
{
  "ok": true,
  "data": {
    "source": "/tmp/financecli_sample.html",
    "engine": "beautifulsoup",
    "format": "html",
    "topics": [
      "operating lease costs"
    ],
    "threshold": 80.0,
    "match_mode": "fuzzy",
    "start_char": null,
    "end_char": null,
    "window_chars": 80,
    "matches": [
      {
        "match_id": "char_0_100",
        "topic": "operating lease costs",
        "score": 100.0,
        "query": "operating lease costs",
        "match_mode": "fuzzy",
        "page": 1,
        "block_index": 0,
        "bbox": null,
        "start_char": 0,
        "end_char": 100,
        "snippet": "Sample filing\nTotal current assets were 100.\nOperating lease costs were 12.\nMetric\nValue\nRevenue\n123",
        "text": "Sample filing\nTotal current assets were 100.\nOperating lease costs were 12.\nMetric\nValue\nRevenue\n123",
        "window_start_char": 0,
        "window_end_char": 100
      }
    ],
    "count": 1,
    "pages_scanned": 1,
    "char_count": 100,
    "warnings": [
      "HTML extraction returned very short text; document may be a wrapper or script-rendered."
    ]
  },
  "error": null,
  "warnings": [
    "HTML extraction returned very short text; document may be a wrapper or script-rendered."
  ]
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.source` | string | Document path or URL passed to the command. |
| `data.engine` | string | Parser engine used before matching. |
| `data.format` | string | Resolved document format. |
| `data.topics` | array or string | Topics or literal query terms scanned. |
| `data.threshold` | number | Fuzzy score threshold used. |
| `data.match_mode` | string | Matching mode: `fuzzy` or `all_terms`. |
| `data.start_char` | integer or null | Lower scan bound when supplied. |
| `data.end_char` | integer or null | Upper scan bound when supplied. |
| `data.window_chars` | integer | Context window requested for each match. |
| `data.matches` | array | Match records. |
| `data.matches[].match_id` | string | Stable `char_START_END` identifier that can be passed to `document.window`. |
| `data.matches[].topic` | string | Topic or query that produced the match. |
| `data.matches[].score` | number | Match score. |
| `data.matches[].page` | integer | Page number. |
| `data.matches[].block_index` | integer | Matched block index on the page. |
| `data.matches[].bbox` | array or null | Bounding box when available. |
| `data.matches[].start_char` | integer | Start offset of the matched block. |
| `data.matches[].end_char` | integer | End offset of the matched block. |
| `data.matches[].text` | string | Full matched block text. |
| `data.matches[].snippet` | string | Context snippet when `window` is greater than zero. |
| `data.matches[].window_start_char` | integer | Start offset of the snippet window. |
| `data.matches[].window_end_char` | integer | End offset of the snippet window. |
| `data.count` | integer | Number of matches returned. |
| `data.pages_scanned` | integer | Number of pages scanned after offset filtering. |
| `data.char_count` | integer | Total extracted characters available to the scanner. |
| `data.warnings` | array | Parser warnings copied to the top-level `warnings` field. |

## finance document.window

Read a bounded text window around a character offset or a `document.scan` match ID.

### What it does

`finance document.window` re-reads the document, locates a character offset, and returns a bounded text window. The anchor can be a raw `start_char` value or a `match_id` returned by `finance document.scan`.

### When to use it

Use this command after `document.scan` when a match identifies the right part of a filing but you need nearby text for interpretation, citation, or table continuation.

### Usage

```bash
finance document.window SOURCE|source=PATH_OR_URL [format=pdf|html start_char=0|match_id=char_START_END chars=4000 direction=around|next|previous]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` | Yes, unless `source`, `path`, or `url` is set | None | Local path or URL | Positional document source. |
| `source` / `path` / `url` | Yes, unless positional `SOURCE` is set | None | Local path or URL | Keyword source forms. |
| `format` | No | Auto-detected | `pdf`, `html` | Parser override. |
| `start_char` | Required unless `match_id` is set | None | Integer | Character offset used as the anchor. |
| `start` | Required unless `start_char` or `match_id` is set | None | Integer | Alias for `start_char`. |
| `match_id` | Required unless `start_char` or `start` is set | None | `char_START_END` | Match ID returned by `document.scan`. |
| `chars` | No | `4000` | Integer greater than `0` | Maximum window size. |
| `direction` | No | `around` | `around`, `next`, `previous` | Whether to read around the anchor, after the match, or before the anchor. Aliases such as `after`, `forward`, `prev`, `before`, and `back` are also accepted. |

### Basic usage

```bash
finance document.window ./filing.html format=html start_char=0 chars=120 --output json
finance document.window ./filing.html format=html match_id=char_52000_52200 direction=next chars=4000 --output json
```

### Example output

This output was generated with `finance document.window /tmp/financecli_sample.html format=html start_char=0 chars=120 --output json`.

```json
{
  "ok": true,
  "data": {
    "source": "/tmp/financecli_sample.html",
    "engine": "beautifulsoup",
    "format": "html",
    "start_char": 0,
    "end_char": 60,
    "returned_chars": 60,
    "char_count": 100,
    "direction": "around",
    "text": "Sample filing\nTotal current assets were 100.\nOperating lease",
    "warnings": [
      "HTML extraction returned very short text; document may be a wrapper or script-rendered."
    ]
  },
  "error": null,
  "warnings": [
    "HTML extraction returned very short text; document may be a wrapper or script-rendered."
  ]
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.source` | string | Document path or URL passed to the command. |
| `data.engine` | string | Parser engine used. |
| `data.format` | string | Resolved document format. |
| `data.start_char` | integer | Start offset of the returned window. |
| `data.end_char` | integer | End offset of the returned window. |
| `data.returned_chars` | integer | Number of characters returned in `data.text`. |
| `data.char_count` | integer | Total extracted document characters. |
| `data.direction` | string | Direction applied to the anchor. |
| `data.text` | string | Returned text window. |
| `data.warnings` | array | Parser warnings copied to the top-level `warnings` field. |

## finance document.tables

Extract compact table previews from a text-based PDF.

### What it does

`finance document.tables` sends a local or remote PDF to the table extraction stack and returns page, table shape, parsing accuracy, whitespace, row previews, and truncation metadata.

### When to use it

Use this command when `document.read` or `document.scan` finds a table-heavy PDF and you need row previews instead of plain text windows. It is for text/vector PDFs; scanned image PDFs usually need OCR first.

### Usage

```bash
finance document.tables SOURCE|source=PATH_OR_URL [pages=1-end flavor=stream|lattice max_tables=20 max_rows=25]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` | Yes, unless `source`, `path`, or `url` is set | None | Local path or URL | Positional PDF source. |
| `source` / `path` / `url` | Yes, unless positional `SOURCE` is set | None | Local path or URL | Keyword source forms. |
| `pages` | No | `1-end` | Camelot page expression such as `1`, `1-3`, `1-end`, or `all` | Pages passed to the table parser. |
| `flavor` | No | `stream` | `stream`, `lattice` | `stream` works on whitespace-separated tables. `lattice` is for ruled-line tables and may require Ghostscript. |
| `max_tables` | No | `20` | Integer | Maximum detected tables to return. |
| `max_rows` | No | `25` | Integer | Maximum preview rows per table. |

### Basic usage

```bash
finance document.tables ./report.pdf pages=10-12 flavor=stream --output json
finance document.tables ./filing.pdf pages=all max_tables=5 max_rows=10 --output json
```

### Example output

This output was generated with `finance document.tables /tmp/financecli_table.pdf pages=1 flavor=stream max_tables=3 max_rows=5 --output json`.

```json
{
  "ok": true,
  "data": {
    "source": "/tmp/financecli_table.pdf",
    "engine": "camelot",
    "format": "pdf",
    "pages": "1",
    "flavor": "stream",
    "tables": [
      {
        "table": 1,
        "page": "1",
        "shape": [
          4,
          1
        ],
        "accuracy": 100.0,
        "whitespace": 0.0,
        "rows": [
          [
            "Metric      Value"
          ],
          [
            "Revenue     123"
          ],
          [
            "Gross Profit 45"
          ],
          [
            "Operating Income 12"
          ]
        ],
        "returned_rows": 4,
        "truncated": false
      }
    ],
    "count": 1,
    "total_detected": 1,
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
| `data.source` | string | PDF path or URL passed to the command. |
| `data.engine` | string | Table extraction engine. |
| `data.format` | string | Always `pdf` for this command. |
| `data.pages` | string | Page expression passed to the parser. |
| `data.flavor` | string | Parser flavor used. |
| `data.tables` | array | Table preview rows. |
| `data.tables[].table` | integer | One-based table index in returned results. |
| `data.tables[].page` | string | Page where the table was detected. |
| `data.tables[].shape` | array | Table shape as `[rows, columns]`. |
| `data.tables[].accuracy` | number or null | Parser accuracy score when available. |
| `data.tables[].whitespace` | number or null | Parser whitespace score when available. |
| `data.tables[].rows` | array | Returned row preview. |
| `data.tables[].returned_rows` | integer | Number of preview rows returned. |
| `data.tables[].truncated` | boolean | Whether the row preview was truncated by `max_rows`. |
| `data.count` | integer | Number of tables returned. |
| `data.total_detected` | integer | Total tables detected before `max_tables` truncation. |
| `data.warnings` | array | Parser warnings. |

## finance document.ocr

Run OCR/layout parsing on a PDF or document that native extraction cannot read well.

### What it does

`finance document.ocr` runs the default OCR stack and returns extracted text, optional markdown, page-level OCR text, blocks, character counts, truncation metadata, and warnings.

### When to use it

Use this command as a fallback for scanned PDFs, image-heavy investor decks, or documents where `document.read` returns too little text. For text-based PDFs, prefer `document.read`, `document.scan`, or `document.tables` first.

### Usage

```bash
finance document.ocr SOURCE|source=PATH_OR_URL [max_chars=12000 max_pages=5]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` | Yes, unless `source`, `path`, or `url` is set | None | Local path or URL | Positional document source. |
| `source` / `path` / `url` | Yes, unless positional `SOURCE` is set | None | Local path or URL | Keyword source forms. |
| `max_chars` | No | `12000` | Integer | Maximum OCR text characters returned. |
| `max_pages` | No | All pages | Integer; `0` means all pages | Maximum pages to OCR. |

### Basic usage

```bash
finance document.ocr ./deck.pdf max_pages=3 --output json
finance document.ocr ./deck.pdf max_chars=4000 --output json
```

### Example output

This output was generated with `finance document.ocr /tmp/financecli_table.pdf max_pages=1 max_chars=1000 --output json`.

```json
{
  "ok": true,
  "data": {
    "source": "/tmp/financecli_table.pdf",
    "engine": "paddleocr_pp_structure_v3",
    "format": "pdf",
    "text": "Metric\nValue\nRevenue\n123\nGross Profit 45\nOperating Income 12",
    "markdown": null,
    "pages": [
      {
        "page": 1,
        "text": "Metric\nValue\nRevenue\n123\nGross Profit 45\nOperating Income 12",
        "markdown": "",
        "char_count": 60,
        "returned_chars": 60,
        "truncated": false,
        "blocks": [
          {
            "type": "text",
            "text": "Metric Value Revenue 123Gross Profit 45Operating Income 12"
          }
        ]
      }
    ],
    "char_count": 60,
    "returned_chars": 60,
    "truncated": false,
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
| `data.source` | string | Document path or URL passed to the command. |
| `data.engine` | string | OCR engine, usually `paddleocr_pp_structure_v3`. |
| `data.format` | string | Resolved document format. |
| `data.text` | string | OCR text after truncation. |
| `data.markdown` | string or null | Markdown output when the OCR stack provides it. |
| `data.pages` | array | Page-level OCR records. |
| `data.pages[].page` | integer | One-based page number. |
| `data.pages[].text` | string | OCR text for the page. |
| `data.pages[].markdown` | string or null | Page markdown when available. |
| `data.pages[].char_count` | integer | Page OCR character count before truncation. |
| `data.pages[].returned_chars` | integer | Characters returned for the page. |
| `data.pages[].truncated` | boolean | Whether page text was truncated. |
| `data.pages[].blocks` | array | OCR/layout blocks emitted by the parser. |
| `data.char_count` | integer | Total OCR character count before truncation. |
| `data.returned_chars` | integer | Total characters returned. |
| `data.truncated` | boolean | Whether `data.text` was truncated. |
| `data.warnings` | array | OCR warnings. |
