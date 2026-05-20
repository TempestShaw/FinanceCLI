---
title: Agent Output Formats
description: Normalized records and token-efficient rendering for LLM agents.
---

Finance CLI already has command-level schemas in [`tools.json`](/FinanceCLI/tools.json), an OpenAPI-style adapter contract in [`openapi.json`](/FinanceCLI/openapi.json), and a stable JSON result envelope:

```json
{"ok": true, "data": {}, "error": null, "warnings": []}
```

Those remain the canonical audit and integration format. The compact agent formats are an additive rendering layer for cases where an LLM needs dense structured facts rather than the full provider payload.

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

The built-in dict adapter handles existing Finance CLI payloads by looking for common row containers such as `rows`, `filings`, `articles`, `events`, `estimates`, `transcripts`, and grouped `symbols`. For a new provider with an unusual shape, write a small adapter that returns `Record[]`; do not add a provider-specific renderer.

## Renderer Controls

Use JSON when you need the full command contract:

```bash
finance market.quote AAPL --output json
```

Use compact formats when the agent only needs normalized facts:

```bash
finance market.quote AAPL --output compact --fields last_price,market_cap,currency
finance filings.statement AAPL statement=income --output schema --fields label,value,unit --max-records 20
finance news.search symbol=NVDA max_records=5 --output agent --fields title,url,domain
finance calendar.earnings AAPL --output table --fields earnings_date,eps_estimate,reported_eps
```

Global record-renderer controls:

| Option | Applies To | Use |
| --- | --- | --- |
| `--fields a,b,c` | compact, agent, table, schema | Select record `fields` to render. Structural fields stay available. |
| `--max-records N` | compact, agent, table, schema | Bound repeated rows before rendering. |
| `--max-chars N` | compact, agent, table, schema | Apply an approximate final character cap. |

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

Agent:

```text
AAPL financial metric 2024Q4: revenue 119.6B USD; net income 36.3B USD. Source: 10-K.
```

Table:

```text
| entity | kind | period | revenue | net_income | source |
| --- | --- | --- | --- | --- | --- |
| AAPL | financial_metric | 2024Q4 | 119.6B USD | 36.3B USD | 10-K |
```

Schema-once rows:

```text
schema|entity|kind|period|revenue|net_income|source
row|AAPL|financial_metric|2024Q4|119.6B USD|36.3B USD|10-K
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
| Markdown table | Human scan plus LLM comparison | More tokens than schema rows. |
| TSV | Very compact tabular data | Harder to preserve nested citations and escaping. |
| YAML | Readable config-like data | Usually more tokens than compact rows and easier to misparse. |
| MessagePack | Binary transport/storage | Not useful inside LLM context because models see text tokens. |

Default recommendation: keep `--output json` for source-of-truth capture, then render selected records as `compact` or `schema` for agent context. Use `agent` when the next step is natural-language reasoning. Use `table` when row comparison matters.

## RAG And Chunking

Records are good retrieval units because each row has stable subject, kind, time, fields, and source. A practical RAG pipeline can:

1. Store `Record.to_dict()` as metadata.
2. Embed the `agent` or `compact` rendering as chunk text.
3. Build chunk IDs from `entity`, `kind`, `period` or `timestamp`, and `source`.
4. Keep long document text out of default compact fields and retrieve it with `document.window` or command-specific JSON when needed.
5. Re-render retrieved records into `schema` rows before passing many similar rows back to an LLM.

This avoids one formatter per API while preserving enough structure for citation, ranking, and deterministic replay.
