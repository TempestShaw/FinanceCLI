---
name: finance-cli
description: Use when Codex or another coding/research agent needs to use the installed Finance CLI for public-company research, SEC filings, document reading, document scanning/windowing/OCR, market data, finance formulas, valuation math, backtests, source checks, or provider setup. This skill routes work to `finance <command> [arguments] --output json`, uses Finance CLI docs and `tools.json` for command discovery, and keeps command output source-aware.
---

# Finance CLI

Finance CLI is an installed command-line tool for repeatable public-company research. Use it through the local `finance` executable and preserve its JSON result envelope.

## Hard Rules

- Use the installed CLI for supported operations: `finance <command> [arguments] --output json`.
- Treat the `finance` executable as the public interface for supported workflows.
- Do not generate custom Python entrypoints to replace supported CLI commands.
- Do not fabricate missing provider data. If a command returns `ok=false`, surface the error.

## First Commands

Use these commands to discover the local installation and provider state:

```bash
finance --list
finance sources.status --output json
```

Use this pattern for command execution:

```bash
finance filings.statement COST statement=income --output json
finance document.scan source=report.pdf query=revenue max_pages=5 --output json
finance formula.margin numerator=10 denominator=20 --output json
```

## Discovery Order

1. Read `finance --list` for commands available in the installed version.
2. Read `https://tempestshaw.github.io/FinanceCLI/tools.json` for parameter schemas, output schemas, side-effect labels, citation fields, and routing hints.
3. Read `https://tempestshaw.github.io/FinanceCLI/llms.txt` for compact agent guidance.
4. Read `https://tempestshaw.github.io/FinanceCLI/llms-full.txt` only when a task needs full routing context.
5. Read namespace docs under `https://tempestshaw.github.io/FinanceCLI/namespaces/` for examples and result shapes.

## Local References

- Read `docs/ROUTING.md` when choosing between command namespaces.
- Read `docs/PLAYBOOKS.md` for common multi-step research workflows.
- Read `docs/TRUST.md` before summarizing evidence, failures, provider output, or finance calculations.

## Output Handling

Every command should be requested as JSON. Expect:

```json
{"ok": true, "data": {}, "error": null, "warnings": []}
```

Preserve `warnings`. Cite source fields when present, especially `accession`, `accession_no`, `url`, `report_name`, `section`, `page`, `start_char`, `end_char`, `match_id`, `source`, `provider`, and `timestamp`.
