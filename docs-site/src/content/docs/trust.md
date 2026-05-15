---
title: Trust
description: Source attribution, credentials, freshness, and scriptable output.
---

Finance research needs traceable inputs. Finance CLI is built around a few practical rules:

- Source handles: filing commands return accessions, URLs, report names, sections, offsets, or provider names when available.
- Explicit calculations: formula commands include the inputs and method used.
- Scriptable results: commands return predictable JSON with `ok`, `data`, `error`, and `warnings` fields.
- Local credentials: API keys are read from environment variables at runtime and are not written by the CLI.
- No telemetry: the CLI does not track commands, symbols, queries, or usage.
- Freshness: provider-backed commands reflect the source response at runtime; there is no general stale-cache layer.

## Citation Policy

Agents should preserve citation fields whenever a command returns them:

| Evidence type | Cite fields |
| --- | --- |
| SEC filings | `accession`, `accession_no`, `url`, `form`, `report_name`, `section` |
| Documents | `source`, `url`, `path`, `page`, `start_char`, `end_char`, `match_id` |
| Market data | `symbol`, `provider`, `source`, `date`, `timestamp` |
| News/transcripts/IR | `url`, `source`, `published_at`, `quarter`, `speaker`, `filing_url` |
| Calculations | command name, explicit inputs, and `method` |

Never present market data without provider/source and date/timestamp fields when available. Treat Yahoo, FMP, SEC, GDELT, transcript pages, and company IR pages as source-specific records, not ground truth.

## Agent Failure Policy

- If `ok=false`, surface the returned `error` and do not fabricate data.
- If `ok=true` and a result array is empty, report the source returned no matching rows.
- If warnings are present, keep them with the answer and decide whether a narrower follow-up command is needed.
- If a provider key or local dependency is unavailable, let the error remain visible to the caller.
