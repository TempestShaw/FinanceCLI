<p align="center">
  <img src="docs/assets/financecli_logo.svg" alt="Finance CLI logo" width="200">
</p>

<h1 align="center">Finance CLI</h1>

<p align="center">Financial research tools for your AI agent. Evidence you can check.</p>

<p align="center">
  <strong>English</strong> | <a href="https://github.com/TempestShaw/FinanceCLI/blob/main/README.zh-CN.md" lang="zh-CN">简体中文</a>
</p>

<p align="center">
  <a href="https://tempestshaw.github.io/FinanceCLI/">Website</a> ·
  <a href="https://tempestshaw.github.io/FinanceCLI/ai/">AI Integration &amp; Skills</a> ·
  <a href="https://tempestshaw.github.io/FinanceCLI/quickstart/">Quick Start</a> ·
  <a href="https://tempestshaw.github.io/FinanceCLI/research-examples/">Research Examples</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/finresearch-cli/"><img alt="PyPI: finresearch-cli" src="https://img.shields.io/badge/PyPI-finresearch--cli-blue"></a>
  <img alt="Python 3.10 or later" src="https://img.shields.io/badge/Python-3.10%2B-3776AB">
  <a href="https://github.com/TempestShaw/FinanceCLI/blob/main/LICENSE"><img alt="Apache-2.0 license" src="https://img.shields.io/badge/license-Apache--2.0-111827"></a>
</p>

Finance CLI gives your agent tools to retrieve SEC filings, inspect financial statements, read documents, and run calculations. Ask a company question in your own words, then follow the sources and inputs behind the answer. You can also run every command directly in your terminal.

## Start with a question

After [setting up the CLI and skill](https://tempestshaw.github.io/FinanceCLI/ai/), ask your agent:

```text
Use Finance CLI to research Apple's latest annual filing. Explain how it
makes money and three risks it discloses. Cite the filing date and source
for each finding. Retrieve more evidence if an excerpt is truncated, and
report missing data or source errors.
```

Your agent chooses the commands and writes the explanation. Finance CLI supplies filing evidence and calculation results. Review the cited sources to check the agent's interpretation.

For a small, reproducible example, this command calculates annual compound growth from 100 to 150 over three years:

```bash
finance formula.cagr start=100 end=150 periods=3 --output md
```

Actual CLI output with illustrative inputs, requiring no external data:

```text
**CAGR = 14.47%**

_Inputs_
| Field | Value |
| --- | --- |
| start | 100 |
| end | 150 |
| periods | 3 |

method: (end / start) ** (1 / periods) - 1
```

## Why use Finance CLI?

- **Check the evidence.** Filing commands retain source identifiers such as URLs and accessions when available. Missing data and provider errors stay visible.
- **Reproduce the calculation.** Formula commands return their inputs and method. Save readable Markdown or structured JSON to rerun and inspect research steps.
- **Let your agent choose the workflow.** Combine small tools for your question, from finding a filing to reading a table and calculating a metric. Reuse them across companies without writing another retrieval script.

## Use with your AI agent

1. Install the CLI using the command below. Your agent needs access to the terminal environment where `finance` is installed.
2. [Download the skill](https://tempestshaw.github.io/FinanceCLI/skills/finance-cli-skills.zip) and follow the [skill setup guide](https://tempestshaw.github.io/FinanceCLI/ai/#3-install-the-skill) to add it to your agent's local skills directory.
3. Ask the research question above. For SEC requests, first set your real contact identity using the Quick Start guide.

The skill teaches tool selection and source handling; downloading it alone does not install the CLI. You bring an agent that can run local commands and its AI model. Finance CLI does not include a hosted chat service.

## Use directly in your terminal

Requires Python 3.10 or later. We recommend an isolated environment; [Quick Start](https://tempestshaw.github.io/FinanceCLI/quickstart/) covers macOS, Linux, and Windows setup.

```bash
python -m pip install -U finresearch-cli
finance formula.cagr start=100 end=150 periods=3 --output md
```

To read an annual filing, set your name and real email for SEC requests. On macOS or Linux, replace the example contact below:

```bash
export FINANCE_SEC_USER_AGENT="Your Name your.email@example.com"
finance filings.read AAPL section=business max_chars=4000 --output md
```

This returns a filing excerpt. Check its date, source, and truncation information before drawing conclusions. The [Quick Start](https://tempestshaw.github.io/FinanceCLI/quickstart/) includes the equivalent Windows setup.

## What is included?

| Research task | Tools |
| --- | --- |
| Find and read company disclosures | SEC filings, sections, XBRL financial statements, filing reports |
| Read research documents | Native PDF/HTML text, text search, bounded reading windows |
| Add company and market context | Quotes, price history, fundamentals, public transcripts, IR presentation discovery |
| Check assumptions and calculations | Finance formulas, valuation scenarios, DCF/NPV/IRR |

SEC research and basic calculators need no paid data key. Provider-backed results depend on availability and coverage; consensus estimates require an FMP key. See [Data Sources](https://tempestshaw.github.io/FinanceCLI/data-sources/) for details.

Install advanced capabilities only when needed:

```bash
python -m pip install -U "finresearch-cli[tables]"
python -m pip install -U "finresearch-cli[ocr]"
python -m pip install -U "finresearch-cli[backtest]"
```

These add PDF table extraction, OCR, and VectorBT backtesting respectively. Combine them as `"finresearch-cli[tables,ocr,backtest]"`. OCR may download models on first use.

## Explore and contribute

- [Worked research examples](https://tempestshaw.github.io/FinanceCLI/research-examples/) and [more command examples](https://github.com/TempestShaw/FinanceCLI/blob/main/EXAMPLES.md).
- [Command reference](https://tempestshaw.github.io/FinanceCLI/commands/), [output formats](https://tempestshaw.github.io/FinanceCLI/agent-output-formats/), and [shell completion](https://github.com/TempestShaw/FinanceCLI/blob/main/EXAMPLES.md#shell-completion).
- For integrations: [Agent Guide](https://tempestshaw.github.io/FinanceCLI/agents/), [llms.txt](https://tempestshaw.github.io/FinanceCLI/llms.txt), and [tools.json](https://tempestshaw.github.io/FinanceCLI/tools.json).
- [Report a problem or suggest a research question](https://github.com/TempestShaw/FinanceCLI/issues/new). Include the command and error, excluding credentials and private documents. If it helped your research, share a reproducible example or star the repository.

English and Chinese READMEs follow the same structure and examples; please update both when changing setup or capabilities. The detailed documentation is currently in English.

## Trust and license

The CLI runs locally and does not collect usage telemetry. API credentials are read from environment variables. See the [trust guide](https://tempestshaw.github.io/FinanceCLI/trust/) and [Apache-2.0 license](https://github.com/TempestShaw/FinanceCLI/blob/main/LICENSE).

Finance CLI is for research and automation. It does not provide investment advice or recommendations to buy or sell securities.
