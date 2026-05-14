---
title: MCP And Plugins
description: Schema contract for MCP servers, plugins, and tool adapters.
---

Finance CLI is ready to be wrapped by an MCP server or plugin through its generated schema files. The schema is the contract; an adapter should not scrape prose docs.

## Schema Files

| File | Use |
| --- | --- |
| [`tools.json`](/FinanceCLI/tools.json) | Canonical command catalog for tools, agents, and MCP adapters. |
| [`schemas/finance-cli-tools.schema.json`](/FinanceCLI/schemas/finance-cli-tools.schema.json) | JSON Schema for validating `tools.json`. |
| [`openapi.json`](/FinanceCLI/openapi.json) | OpenAPI-style adapter contract for HTTP/tool runtimes. |
| [`llms.txt`](/FinanceCLI/llms.txt) | Compact LLM entry point. |
| [`llms-full.txt`](/FinanceCLI/llms-full.txt) | Full agent context with playbooks and command routing. |

## Tool Contract

Every command in `tools.json` includes:

| Field | Meaning |
| --- | --- |
| `name` | CLI command name, such as `filings.statement`. |
| `description` | Human and agent-readable command summary. |
| `args` | Structured parameter map with type, required flag, default, enum, aliases, and description when available. |
| `input_schema` | JSON Schema object for adapter validation. |
| `output_schema` | JSON Schema for the standard result envelope and command payload. |
| `side_effects` | One of `pure_calculation`, `local_file_read`, `network_read_only`, or `local_or_network_read`. |
| `auth_required` | Whether the command uses public providers, optional environment credentials, or no auth. |
| `rate_limit_notes` | Provider-specific rate-limit notes when useful. |
| `citation_fields` | Fields an agent should preserve in citations. |
| `agent` | `use_when`, `avoid_when`, and `next_steps` routing hints. |

## Adapter Behavior

An MCP/plugin adapter should:

1. Validate input against `input_schema`.
2. Execute the matching local CLI command.
3. Return the raw JSON envelope unchanged.
4. Preserve `warnings`.
5. Surface `ok=false` errors directly.
6. Apply side-effect labels before deciding whether to call a command automatically.

## Side-Effect Labels

| Label | Meaning |
| --- | --- |
| `pure_calculation` | No network and no filesystem read. |
| `local_file_read` | Reads a caller-supplied local file. |
| `network_read_only` | Reads public/provider data and does not mutate external state. |
| `local_or_network_read` | Reads either a local path or URL supplied by the caller. |

Finance CLI commands are designed as read-only research tools. They do not place trades, send emails, mutate provider state, or write API keys.
