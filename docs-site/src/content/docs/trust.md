---
title: Trust
description: Source attribution, credentials, freshness, and structured errors.
---

Finance research needs traceable inputs. Finance CLI is built around a few practical rules:

- Source handles: filing commands return accessions, URLs, report names, sections, offsets, or provider names when available.
- Explicit calculations: formula commands include the inputs and method used.
- Structured errors: missing keys, rate limits, unavailable documents, and provider errors are returned as JSON errors or warnings.
- Local credentials: API keys are read from environment variables at runtime and are not written by the CLI.
- No telemetry: the CLI does not track commands, symbols, queries, or usage.
- Freshness: live data commands reflect the source response at runtime; there is no general stale-cache layer.
