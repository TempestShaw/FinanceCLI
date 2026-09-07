---
title: Research Examples
description: Read company disclosures, inspect an income statement, and reproduce a compound-growth calculation with Finance CLI.
---

Start with a question and keep the evidence behind your answer. These independent examples use the current repository version. Follow [Quick Start](/FinanceCLI/quickstart/) for installation and SEC contact setup.

## Understand a company

**What does Apple do, and what risks does it disclose?**

Find recent annual (10-K) and quarterly (10-Q) filings:

```bash
finance filings.recent AAPL forms=10-K,10-Q limit=3 --output md
```

Read its annual business description and risk factors:

```bash
finance filings.read AAPL section=business max_chars=4000 --output md
finance filings.read AAPL section=risk_factors max_chars=4000 --output md
```

The output is filing evidence, not an AI-written verdict. Check the filing date, source URL or accession, and truncation information. Increase `max_chars` or follow the source to read beyond an excerpt. To use one specific filing across steps, pass its accession with `accession=...` instead of requesting the latest filing again.

## Inspect financial statements

**What revenue and profit does Costco report?**

```bash
finance filings.statement COST statement=income --output md
```

Inspect period labels, currency, units, and rows. Preserve the source with figures you quote. A missing row is not zero; compare figures from matching periods. Use `--output json` to pass structured results to scripts. [Explore statement options](/FinanceCLI/namespaces/filings/).

## Check a growth calculation

**What is annual compound growth from 100 to 150 over three years?**

These are illustrative inputs, not company financial data. The following result was reproduced with the CLI without an external provider:

```bash
finance formula.cagr start=100 end=150 periods=3 --output md
```

**CAGR = 14.47%**

| Input | Value |
| --- | ---: |
| start | 100 |
| end | 150 |
| periods | 3 |

Method: `(end / start) ** (1 / periods) - 1`.

The total increase is 50%. Annual compound growth is about 14.47%, because each year's growth builds on the preceding value. Substitute verified filing figures in the same units and the actual number of years between observations.

## Ask your research agent

After [installing the CLI and skill](/FinanceCLI/ai/), try:

```text
Use Finance CLI to read Apple's latest annual filing. Explain its business
and summarize three disclosed risks. Cite the filing date and source for
each finding. Retrieve more evidence if an excerpt is truncated, and
report missing data or source errors.
```

Your agent can choose and combine commands. Review conclusions against the sources. [Suggest another research question](https://github.com/TempestShaw/FinanceCLI/issues/new).
