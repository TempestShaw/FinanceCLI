---
title: AI Integration & Skills
description: Give your AI agent financial research tools. Install Finance CLI and its skill, then ask company questions with traceable sources and calculations.
---

Ask your agent to investigate a company, read its filings, or check a financial calculation. Finance CLI provides the tools and source evidence; the skill helps your agent choose commands and handle the results.

You need an agent that can run terminal commands on your computer. The CLI supplies data retrieval and calculations, while your existing agent supplies the model and reasoning. Downloading the skill alone does not install the CLI.

**Get started:** [Install the CLI](#1-install-finance-cli) → [add the skill](#3-install-the-skill) → [ask your first question](#ask-your-first-research-question).

[Download the Finance CLI skill](/FinanceCLI/skills/finance-cli-skills.zip)

## Ask your first research question

Once setup is complete, paste this into your agent:

```text
Use Finance CLI to research Apple's latest annual filing. Explain its
business and three disclosed risks. Cite the filing date and source for
each finding. Retrieve more evidence when excerpts are truncated, and
report missing data or source errors.
```

The agent can discover the filing, read the relevant sections, and follow up with other commands. You should receive an explanation tied to filing evidence. Review the cited sources: the skill guides source handling, but does not guarantee that an agent's interpretation is correct.

For another task, ask it to compare financial statement rows for companies you specify, or calculate growth from verified period values. [See worked examples](/FinanceCLI/research-examples/).

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
| [`Agent Output Formats`](/FinanceCLI/agent-output-formats/) | Normalized records and compact renderers for LLM context compression. |
| [`finance-cli-skills.zip`](/FinanceCLI/skills/finance-cli-skills.zip) | Local skill package for agents that support skills. |

## 3. Install The Skill

The Finance CLI skill is a compact routing guide for agents. It points them to the installed `finance` CLI, JSON output, `tools.json` schemas, and source-aware citation rules.

Copy this setup prompt into an agent that can manage local files:

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
| `SKILL.md` | Core routing rules for using `finance <command> [arguments] --output json` and the generated schema files. |
| `docs/ROUTING.md` | Namespace and command-family routing hints. |
| `docs/PLAYBOOKS.md` | Common multi-step workflows for filings, documents, market context, screens, and backtests. |
| `docs/TRUST.md` | Result-envelope handling, citation policy, credentials, and calculator boundaries. |

The command schema truth remains [`tools.json`](/FinanceCLI/tools.json). The skill links to schema files instead of duplicating them.

## Usage Details

- Use `finance --list` to inspect commands in the installed version.
- Use `finance sources.status --output json` before assuming provider availability.
- Use `tools.json` for arguments, defaults, enums, output schemas, side effects, and citation fields.
- Preserve `ok`, `data`, `error`, and `warnings` from command output.
- Use compact record output only after deciding that the full JSON envelope is not needed for audit or replay.
- Keep finance calculations research-oriented and source-aware.
