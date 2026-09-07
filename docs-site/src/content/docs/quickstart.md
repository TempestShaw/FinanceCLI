---
title: Quick Start
description: Install Finance CLI, read your first company filing, and save a readable result.
---

You need Python 3.10 or later and a terminal. Commands run on your computer. See the [worked examples](/FinanceCLI/research-examples/) before installing.

## Install

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the published package:

```bash
python -m pip install -U finresearch-cli
```

Starting with 0.1.0b1, the base install includes SEC research, native document reading, market data, and calculators. OCR, PDF tables, and backtests are [optional installs](/FinanceCLI/data-sources/#optional-capabilities). This website documents the current repository; the published version may have fewer commands or output formats. Check `finance --list` and `finance --help`. For the current source version used in these examples, install with Git available:

```bash
python -m pip install -U "git+https://github.com/TempestShaw/FinanceCLI.git"
```

If your system provides `python3` instead of `python`, use it in the setup commands above.

## Check your first result

This calculation needs no network connection or API key:

```bash
finance formula.cagr start=100 end=150 periods=3 --output md
```

The headline should be **CAGR = 14.47%**: compound annual growth from 100 to 150 over three years. [Inspect the full example](/FinanceCLI/research-examples/#check-a-growth-calculation).

## Read a company's business

For SEC requests, declare your name and real contact email. Replace the example contact below. On macOS or Linux:

```bash
export FINANCE_SEC_USER_AGENT="Your Name your.email@example.com"
```

On Windows PowerShell:

```powershell
$env:FINANCE_SEC_USER_AGENT="Your Name your.email@example.com"
```

Read an excerpt from Apple's annual filing:

```bash
finance filings.read AAPL section=business max_chars=4000 --output md
```

Check the returned filing date and source. `max_chars` limits the excerpt length. Replace `AAPL` with another US company ticker. [Continue with risks and statements](/FinanceCLI/research-examples/).

## Save and reuse

Save a readable excerpt to a new file (choose another filename if this one exists):

```bash
finance filings.read AAPL section=business max_chars=4000 --output md > aapl-business.md
```

For scripts and agents, use `--output json` to preserve the result envelope, including errors and warnings.

## If something fails

- **`finance` not found:** activate the environment where you installed it.
- **Unknown command or format:** check `finance --list` and `finance --help`; use the source install above for these examples.
- **SEC request fails:** check your contact string and run `finance sources.test sec symbol=AAPL --output json`. Keep the reported error; availability depends on the source.
- **Need options:** run `finance filings.read --help`.

See [Data Sources](/FinanceCLI/data-sources/) or [report a problem](https://github.com/TempestShaw/FinanceCLI/issues/new) with the command and error, excluding credentials.
