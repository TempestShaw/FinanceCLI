---
title: Agent Output Formats
description: Normalized records and token-efficient rendering for LLM agents.
---

Finance CLI already has command-level schemas in [`tools.json`](/FinanceCLI/tools.json), an OpenAPI-style adapter contract in [`openapi.json`](/FinanceCLI/openapi.json), and a stable JSON result envelope:

```json
{"ok": true, "data": {}, "error": null, "warnings": []}
```

Those remain the canonical audit and integration format. The record formats are an additive rendering layer for cases where an LLM needs dense structured facts rather than the full provider payload.

## Architecture

The current flow is:

```text
provider response -> service/command payload -> FinanceCommandResult -> output renderer
```

The agent-oriented path adds one internal step:

```text
provider response -> service/command payload -> normalized Record[] -> generic renderer
```

Adapters should only normalize provider-specific shapes into `Record` objects. Renderers should not know whether a row came from SEC, Yahoo, GDELT, FMP, transcripts, or a future provider.

## Folder Shape

```text
finance_cli/
  schemas.py          # FinanceCommandResult and normalized Record dataclass
  records.py          # RecordAdapter protocol, dict normalizer, generic renderers
  cli/
    main.py           # --output and renderer controls
    formatting.py     # bridges FinanceCommandResult to record renderers
scripts/
  generate_cli_docs.py # publishes result envelope, record schema, output formats
docs-site/
  src/content/docs/   # human and agent-facing docs
```

This keeps the existing command registry and generated schema files as the source of truth. Future APIs should add or adapt service payloads, not write one-off compact formatters.

## Record Schema

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Record:
    entity: str
    kind: str
    period: str | None = None
    timestamp: str | None = None
    fields: dict[str, Any] = field(default_factory=dict)
    source: str | None = None
    metadata: dict[str, Any] | None = None
```

Use `entity` for the subject, such as `AAPL`, `NVDA`, `US`, or a query string. Use `kind` for the semantic row type, such as `filings_statement_row`, `market_quote`, `news_article`, or `earning`. Put source-specific facts in `fields`, not in renderer code.

## Adapter Interface

```python
from typing import Any, Protocol

class RecordAdapter(Protocol):
    def to_records(self, payload: Any, *, command: str | None = None) -> list[Record]:
        """Normalize a provider or command payload into records."""
```

Command adapters own source semantics. For example, the filings adapter decides that `filing_date` is the filing timestamp and `report_date` is the reporting period; the OHLCV adapter decides that `date` is the bar timestamp. The fallback dict adapter is only best-effort for already record-like payloads. For a new provider with an unusual shape, write a small adapter that returns `Record[]`; do not add a provider-specific renderer.

## Renderer Controls

Use JSON when you need the full command contract:

```bash
finance market.quote AAPL --output json
```

Use compact formats when the agent only needs normalized facts:

```bash
finance market.quote AAPL --output compact --fields last_price,market_cap,currency
finance filings.statement AAPL statement=income --output schema --fields label,value,unit --max-records 20
finance news.search symbol=NVDA max_records=5 --output schema --fields title,url,domain
finance calendar.earnings AAPL --output schema --fields earnings_date,eps_estimate,reported_eps
```

Global record-renderer controls:

| Option | Applies To | Use |
| --- | --- | --- |
| `--fields a,b,c` | compact, schema | Select record `fields` to render. Structural fields stay available. |
| `--max-records N` | compact, schema | Bound repeated rows before rendering. |
| `--max-chars N` | compact, schema | Apply an approximate final character cap. |

Adapters may preserve source-native fields while also mapping them into the normalized record. For example, `market.ohlcv` keeps `date` in `fields` and maps it to `Record.timestamp`; `filings.recent` keeps `filing_date` and `report_date` in `fields` while mapping them to `Record.timestamp` and `Record.period`. The renderer only consumes those adapter-declared records; it does not infer finance semantics globally.

## Output Examples

Normalized record:

```python
Record(
    entity="AAPL",
    kind="financial_metric",
    period="2024Q4",
    fields={"revenue": "119.6B USD", "net_income": "36.3B USD"},
    source="10-K",
)
```

Compact:

```text
AAPL|financial_metric|2024Q4|revenue=119.6B USD|net_income=36.3B USD|src=10-K
```

Schema-once rows:

```text
schema|entity|kind|period|source|revenue|net_income
row|AAPL|financial_metric|2024Q4|10-K|119.6B USD|36.3B USD
```

The `schema` renderer derives its header from the present `Record` structural fields plus the selected or discovered field names. It does not use command-specific column templates.

When an adapter declares that a source-native field maps to a structural field, selecting the source-native field does not duplicate the canonical column:

```text
schema|entity|kind|source|date|close|volume
row|AAPL|market_ohlcv_row|yfinance|2025-08-07 00:00:00-04:00|220.03|90224800
```

For filings, `filing_date` and `report_date` remain distinguishable even though both are normalized into the common record shape:

```text
schema|entity|kind|source|filing_date|report_date|form|accession_no
row|AAPL|filing|sec_edgar|2025-10-31|2025-09-27|10-K|0000320193-25-000079
```

## Domain Examples

SEC filing statement row:

```python
Record(
    entity="AAPL",
    kind="filings_statement_row",
    period="2024",
    fields={
        "statement": "income",
        "label": "Net sales",
        "value": 391035000000,
        "unit": "USD",
        "accession_no": "0000320193-24-000123",
    },
    source="sec_edgar",
)
```

Stock quote:

```python
Record(
    entity="AAPL",
    kind="market_quote",
    timestamp="2026-05-20T14:30:00Z",
    fields={"last_price": 190.12, "market_cap": 2960000000000, "currency": "USD"},
    source="yfinance",
)
```

News article:

```python
Record(
    entity="NVDA",
    kind="news_article",
    timestamp="2026-05-20T12:15:00Z",
    fields={"title": "NVIDIA supplier shares rise", "domain": "example.com", "url": "https://example.com/a"},
    source="gdelt",
)
```

Earnings date:

```python
Record(
    entity="AAPL",
    kind="earning",
    timestamp="2026-07-30",
    fields={"eps_estimate": 1.42, "reported_eps": None, "surprise": None},
    source="yfinance",
)
```

## Serialization Tradeoffs

| Format | Best For | Tradeoff |
| --- | --- | --- |
| JSON envelope | Audits, MCP/tool wrappers, tests, replay | Verbose repeated keys and nested payloads. |
| Normalized JSON records | Programmatic adapter boundaries | Still key-heavy, but schema is stable. |
| Compact text | Dense inline facts for LLM context | Less self-describing than JSON. |
| Schema-once rows | Many records with the same fields | Requires the consumer to retain the header. |
| Markdown table | Human scan plus LLM comparison | Prefer schema rows in CLI output; render Markdown at the presentation layer if needed. |
| TSV | Very compact tabular data | Harder to preserve nested citations and escaping. |
| YAML | Readable config-like data | Usually more tokens than compact rows and easier to misparse. |
| MessagePack | Binary transport/storage | Not useful inside LLM context because models see text tokens. |

Default recommendation: keep `--output json` for source-of-truth capture, then render selected records as `compact` or `schema` for agent context. `compact` is best for a few records; `schema` is best when many rows share fields.

## RAG And Chunking

Records are good retrieval units because each row has stable subject, kind, time, fields, and source. A practical RAG pipeline can:

1. Store `Record.to_dict()` as metadata.
2. Embed the `compact` rendering as chunk text, or `schema` rows when the chunk contains repeated records.
3. Build chunk IDs from `entity`, `kind`, `period` or `timestamp`, and `source`.
4. Keep long document text out of default compact fields and retrieve it with `document.window` or command-specific JSON when needed.
5. Re-render retrieved records into `schema` rows before passing many similar rows back to an LLM.

This avoids one formatter per API while preserving enough structure for citation, ranking, and deterministic replay.
