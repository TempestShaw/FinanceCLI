---
title: AI Integration & Skills
description: Install Finance CLI for agent workflows and add the Finance CLI skill.
---

This page is the starting point for using Finance CLI with coding agents and research agents. The package installation and the skill installation are separate on purpose: the package provides the `finance` executable, while the skill teaches an agent how to route research tasks to that executable.

## 1. Install Finance CLI

Install or update the CLI first:

```bash
python -m pip install -U finresearch-cli
```

Verify the executable and local provider status:

```bash
finance --list
finance sources.status --output json
```

## 2. Download AI Docs

Agents should prefer the machine-readable files over scraping prose pages.

| File | Use |
| --- | --- |
| [`llms.txt`](/FinanceCLI/llms.txt) | Compact read order, routing rules, and trust reminders. |
| [`llms-full.txt`](/FinanceCLI/llms-full.txt) | Full routing context and common playbooks. |
| [`tools.json`](/FinanceCLI/tools.json) | Canonical command schema, argument metadata, side effects, and citation fields. |
| [`openapi.json`](/FinanceCLI/openapi.json) | Adapter contract for MCP/plugin/tool wrappers. |
| [`finance-cli-skills.zip`](/FinanceCLI/skills/finance-cli-skills.zip) | Local skill package for agents that support skills. |

## 3. Install The Skill

The Finance CLI skill is a compact routing guide for agents. It points them to the installed `finance` CLI, JSON output, `tools.json` schemas, and source-aware citation rules.

Use this one-click prompt in an agent that can manage local files:

```text
Download https://tempestshaw.github.io/FinanceCLI/skills/finance-cli-skills.zip, extract it, copy the extracted skills/finance-cli folder into my local agent skills directory, verify that the copied folder contains SKILL.md, and then stop. Do not run pip install. Do not run finance commands during skill installation.
```

Package installation remains separate:

```bash
python -m pip install -U finresearch-cli
```

## Manual Install

For Codex, install the skill folder into the local skills directory:

```bash
curl -L -o finance-cli-skills.zip https://tempestshaw.github.io/FinanceCLI/skills/finance-cli-skills.zip
rm -rf /tmp/finance-cli-skills
mkdir -p /tmp/finance-cli-skills
unzip -q finance-cli-skills.zip -d /tmp/finance-cli-skills
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R /tmp/finance-cli-skills/skills/finance-cli "${CODEX_HOME:-$HOME/.codex}/skills/"
test -f "${CODEX_HOME:-$HOME/.codex}/skills/finance-cli/SKILL.md"
```

For other agents that support local skills, copy the extracted `skills/finance-cli` folder into that agent's skills directory.

## Skill Overview

The skill is intentionally small:

| File | Purpose |
| --- | --- |
| `SKILL.md` | Core routing rules for using `finance ... --output json` and the generated schema files. |
| `docs/ROUTING.md` | Namespace and command-family routing hints. |
| `docs/PLAYBOOKS.md` | Common multi-step workflows for filings, documents, market context, screens, and backtests. |
| `docs/TRUST.md` | Result-envelope handling, citation policy, credentials, and calculator boundaries. |

The command schema truth remains [`tools.json`](/FinanceCLI/tools.json). The skill links to schema files instead of duplicating them.

## Usage Notes

- Use `finance --list` to inspect commands in the installed version.
- Use `finance sources.status --output json` before assuming provider availability.
- Use `tools.json` for arguments, defaults, enums, output schemas, side effects, and citation fields.
- Preserve `ok`, `data`, `error`, and `warnings` from command output.
- Keep finance calculations research-oriented and source-aware.
