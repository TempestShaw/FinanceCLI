<h1 align="center">Finance CLI</h1>

<p align="center">
  Research a company. Keep the evidence.
</p>

<p align="center">
  <a href="https://pypi.org/project/finresearch-cli/"><img alt="PyPI" src="https://img.shields.io/badge/PyPI-finresearch--cli-blue"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB">
  <img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-111827">
</p>

Finance CLI helps you read company filings, inspect financial statements, and check calculations with traceable inputs. Run it in your terminal or let your research agent choose and combine commands.

**Start with a question:** [choose a company research task](https://tempestshaw.github.io/FinanceCLI/#starter-title), [see worked examples](https://tempestshaw.github.io/FinanceCLI/research-examples/), or [follow the installation guide](https://tempestshaw.github.io/FinanceCLI/quickstart/).

For example, ask what Apple does and what risks it discloses:

```bash
finance filings.read AAPL section=business max_chars=4000 --output md
finance filings.read AAPL section=risk_factors max_chars=4000 --output md
```

These commands return filing excerpts to inspect, with source information when available. Check filing dates and truncation before summarizing. They require SEC access and the current source version described below.

It is designed for repeatable public-company research: commands in, structured output out.

## Why This Exists

You can already combine notebooks, yfinance, SEC downloads, PDF parsers, spreadsheet formulas, and backtesting libraries by hand. That works until every company or question needs a slightly different glue script.

Finance CLI packages those recurring research steps into terminal commands with consistent JSON output. The goal is not to hide the underlying sources. It is to make common research moves easy to repeat, inspect, diff, and automate.

Use it when you want to:

- pull a 10-K section without rewriting EDGAR retrieval code
- inspect filing tables without manually searching raw HTML
- scan a long filing and keep stable offsets for follow-up reading
- run finance formulas with explicit inputs and methods
- fetch market context from the same command surface as filings and documents
- run quick strategy checks without starting from a blank notebook

## Install

```bash
python -m pip install -U finresearch-cli
```

From a local checkout:

The website and this README describe the current repository. The published package may lag behind; use the source installation below for current commands and output formats. The [Quick Start](https://tempestshaw.github.io/FinanceCLI/quickstart/) includes an isolated environment and SEC contact setup.

```bash
git clone https://github.com/TempestShaw/FinanceCLI.git
cd FinanceCLI
python -m pip install -U .
```

Check the install:

```bash
finance --list
finance sources.status --output json
```

The base install includes SEC filing access, native PDF/HTML reading, Yahoo market data, and finance formulas. Starting with 0.1.0b1, install advanced capabilities only when needed:

```bash
python -m pip install -U "finresearch-cli[tables]"
python -m pip install -U "finresearch-cli[ocr]"
python -m pip install -U "finresearch-cli[backtest]"
```

Combine extras with `"finresearch-cli[tables,ocr,backtest]"`. For a local checkout, use `".[tables,ocr,backtest]"`. OCR may download model files on first use.

## First Minute

```bash
finance filings.recent AAPL forms=10-K,10-Q limit=3
finance filings.statement COST statement=balance query="Common Stock"
finance formula.margin numerator=11969 denominator=254453
finance market.quote AAPL
finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31 fast=20 slow=100
```

Most commands return JSON by default:

```json
{
  "ok": true,
  "data": {
    "margin": 0.04703815635893466,
    "margin_pct": 4.7038156358934655,
    "inputs": {
      "numerator": 11969.0,
      "denominator": 254453.0
    },
    "method": "numerator / denominator"
  },
  "error": null,
  "warnings": []
}
```

For output that is readable by **both humans and LLMs**, use `--output md`. It leads with a one-line headline answer, follows with humanized tables (percentages, thousands separators), and ends with a source line:

```bash
finance formula.margin numerator=11969 denominator=254453 --output md
```

```text
**margin = 4.70%**

_Inputs_
| Field | Value |
| --- | --- |
| numerator | 11,969 |
| denominator | 254,453 |

method: numerator / denominator
```

`--output table` and `--output report` give rich terminal views; `--output pretty-json` is for debugging. To make a human format the default for interactive shells, configure it once:

```bash
finance config.set output.default md
finance config.set output.non_interactive_default json
```

Explicit `--output` flags still override the config. Non-interactive output can stay JSON so pipes, CI, and agents keep a stable parser contract.

### Shell Completion

Install completion automatically for your current shell:

```bash
scripts/install_completion.sh zsh
```

When installed from a wheel, the same helper is available as `install_completion.sh`.

FinanceCLI can print shell completion scripts without modifying your shell files:

```bash
finance completion bash > ~/.local/share/bash-completion/completions/finance
finance completion zsh > ~/.zfunc/_finance
finance completion fish > ~/.config/fish/completions/finance.fish
```

Completions are generated from the live command registry and usage metadata, so command names, global options, and key=value argument enums stay aligned with the CLI.

## Mental Model

```mermaid
flowchart LR
    A["finance command"] --> B["research service"]
    B --> C["SEC filings"]
    B --> D["document parsers"]
    B --> E["market data"]
    B --> F["formulas and backtests"]
    C --> G["structured JSON"]
    D --> G
    E --> G
    F --> G
    G --> H["terminal, notebooks, scripts, automation"]
```

Commands are grouped by research job:

| Namespace | Use it for |
| --- | --- |
| `filings.*` | SEC filings, filing sections, XBRL statements, and filing reports. |
| `document.*` | PDF/HTML reading, text search, windows, table extraction, and OCR. |
| `market.*`, `price.*` | Quotes, OHLCV, market moves, regimes, sectors, and event context. |
| `transcripts.*`, `ir.*` | Earnings transcripts, analyst Q&A, and investor presentations. |
| `formula.*`, `valuation.*`, `estimates.*` | Finance formulas, DCF/NPV/IRR, multiples, scenarios, and consensus estimates. |
| `backtest.*` | VectorBT strategy runs, tuning, custom strategy files, and factor payload helpers. |

## Automation Workflows

Finance CLI works well in local scripts, notebooks, CI jobs, and research automation because commands are small, explicit, and machine-readable.

The document examples below assume a filing or report has been saved locally as `./filing.html`.

```bash
finance document.scan ./filing.html format=html query="operating lease costs" window=1200
finance document.window ./filing.html format=html match_id=char_52000_52200 direction=next chars=4000
finance filings.statement COST statement=balance query="Common Stock"
finance formula.net_debt debt=11415 cash=11144 operating_cash=5089
```

A typical automated research workflow is:

1. discover the filing or presentation
2. scan for the relevant section, metric, table, or phrase
3. continue reading from a stable match id or character window
4. calculate the metric with explicit inputs
5. preserve the command and JSON output as audit trail

## What You Can Do

| Task | Example |
| --- | --- |
| Find recent filings | `finance filings.recent NVDA forms=10-Q,8-K limit=5` |
| Read a 10-K section | `finance filings.read AAPL section=mda max_chars=4000` |
| Search filing text | `finance document.scan ./filing.html format=html query="lease liabilities"` |
| Extract PDF tables | `finance document.tables ./report.pdf pages=10-12 flavor=stream` |
| OCR a scanned deck | `finance document.ocr ./deck.pdf max_pages=3` |
| Pull market data | `finance market.ohlcv NVDA timeframe=1d limit=20` |
| Calculate finance metrics | `finance formula.net_debt debt=11415 cash=11144 operating_cash=5089` |
| Run a backtest | `finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31 fast=20 slow=100` |
| Compare symbols side by side | `finance compare AAPL MSFT GOOG market.quote --output md` |

More examples are in [EXAMPLES.md](EXAMPLES.md).

## Trust Model

Finance research needs traceable inputs. Finance CLI is built around a few practical rules:

- Source handles: filing commands return accessions, URLs, report names, sections, offsets, or provider names when available.
- Explicit calculations: formula commands include the inputs and method used.
- Scriptable results: commands return predictable JSON with `ok`, `data`, `error`, and `warnings` fields.
- Local credentials: API keys are read from environment variables at runtime and are not written by the CLI.
- No telemetry: the CLI does not track commands, symbols, queries, or usage.
- Freshness: provider-backed commands reflect the source response at runtime; there is no general stale-cache layer.

## Why Not Just A Notebook?

| Research job | Notebook-first workflow | Finance CLI workflow |
| --- | --- | --- |
| Pull a 10-K section | Write SEC lookup, filing selection, parser setup, and cleanup code. | `finance filings.read AAPL section=mda` |
| Inspect a filing table | Search raw HTML or build one-off XBRL/table parsing. | `finance filings.statement COST statement=balance query="Common Stock"` |
| Continue reading a long document | Copy text into cells and lose the original location. | `finance document.window ./filing.html match_id=char_52000_52200 direction=next` |
| Reuse finance formulas | Reimplement formulas and unit conventions in each notebook. | `finance formula.roic nopat=7113 invested_capital=28077` |
| Run a quick strategy check | Build the data fetch, signals, portfolio, and metrics before testing the idea. | `finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31` |
| Make research reproducible | Commit notebooks with hidden state and noisy diffs. | Commit commands, JSON outputs, and CI checks as plain text. |

Notebooks are still useful for exploration and visualization. Finance CLI is for the repeated research steps you want to make portable, auditable, and easy to run again.

## Data Sources And Keys

Many commands work without a paid key. Some provider-backed commands use environment variables:

| Variable | Enables |
| --- | --- |
| `FMP_API_KEY` | Financial Modeling Prep consensus estimates. |
| `ALPHAVANTAGE_API_KEY` or `ALPHA_VANTAGE_API_KEY` | Alpha Vantage market data fallback. |
| `ALPACA_API_KEY` and `ALPACA_API_SECRET` | Alpaca market-data fallback. |

SEC filings, native document reading, formulas, and Yahoo market data are included in the base install. PDF tables, OCR, and local backtests use the optional installs above.

## Help

```bash
finance help filings
finance filings.statement --help
finance document.scan --help
```

## Disclaimer

Finance CLI is for research and automation workflows only. It is not financial advice, investment advice, tax advice, or a recommendation to buy or sell securities.
