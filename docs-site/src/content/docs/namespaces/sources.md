---
title: sources
description: Inspect Finance CLI provider inventory, local configuration, and provider connectivity.
---

# finance sources

The `sources.*` commands inspect the providers Finance CLI can use for market data, SEC filings, documents, news, transcripts, estimates, and local document parsing.

Run these commands before a workflow when you want to confirm which providers are installed, which credentials are configured, and whether a provider can answer a lightweight validation request.

## finance sources.list

List known Finance CLI data providers and the capabilities attached to each provider.

### What it does

`finance sources.list` returns the provider inventory compiled into Finance CLI. It reports each provider's machine-readable name, display label, supported capabilities, package dependency, environment variables, and setup notes.

This command does not contact remote providers. It only checks whether package-backed providers can be imported locally.

### When to use it

Use this command when you want to see what Finance CLI can route to before running a workflow. It is the fastest way to discover provider names such as `yfinance`, `sec`, `gdelt`, `fmp`, `pymupdf`, `camelot`, and `paddleocr`.

### Usage

```bash
finance sources.list
```

### Arguments

No command-specific arguments.

### Basic usage

```bash
finance sources.list --output json
```

### Example output

This output was generated with `finance sources.list --output json`.

```json
{
  "ok": true,
  "data": {
    "sources": [
      {
        "name": "yfinance",
        "label": "Yahoo Finance via yfinance",
        "capabilities": [
          "quote",
          "ohlcv",
          "fundamentals",
          "calendar",
          "sector",
          "industry",
          "screen"
        ],
        "required_env": [],
        "optional_env": [],
        "package": "yfinance",
        "notes": "Public market, company calendar, sector, industry, and screener data via yfinance.",
        "package_installed": true
      },
      {
        "name": "sec",
        "label": "SEC EDGAR",
        "capabilities": [
          "filings",
          "filing_sections",
          "company_metadata"
        ],
        "required_env": [],
        "optional_env": [
          "FINANCE_SEC_USER_AGENT"
        ],
        "package": null,
        "notes": "Public SEC JSON plus edgartools for filing reads.",
        "package_installed": true
      },
      {
        "name": "gdelt",
        "label": "GDELT",
        "capabilities": [
          "news",
          "timeline",
          "tone",
          "geo"
        ],
        "required_env": [],
        "optional_env": [],
        "package": null,
        "notes": "Public global news APIs with article and timeline metadata.",
        "package_installed": true
      }
    ],
    "count": 11
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.sources` | array | Provider inventory rows. The full command returns all known providers. |
| `data.sources[].name` | string | Provider key accepted by commands such as `finance sources.test SOURCE`. |
| `data.sources[].label` | string | Human-readable provider label. |
| `data.sources[].capabilities` | array | Capability tags used to describe what the provider can support. |
| `data.sources[].required_env` | array | Environment variables required before the provider is considered configured. |
| `data.sources[].optional_env` | array | Environment variables that can improve or identify provider access but are not required. |
| `data.sources[].package` | string or null | Import name checked for package-backed providers. `null` means no import check is needed. |
| `data.sources[].package_installed` | boolean | Whether the package import check succeeded. |
| `data.sources[].notes` | string | Setup or coverage note for the provider. |
| `data.count` | integer | Number of known provider rows returned. |

## finance sources.status

Check local provider setup state without making provider network requests.

### What it does

`finance sources.status` checks installed package dependencies and expected environment variables for every known provider. It adds `configured` and `status` fields to each provider row and returns a summary of local readiness.

This command does not prove that a provider can answer a live request. Use `finance sources.test` for connectivity checks.

### When to use it

Use this command after installation, before debugging a workflow, or before running provider-backed examples in another namespace. It tells you whether local setup is missing credentials or importable packages.

### Usage

```bash
finance sources.status
```

### Arguments

No command-specific arguments.

### Basic usage

```bash
finance sources.status --output json
```

### Example output

This output was generated with `finance sources.status --output json`.

```json
{
  "ok": true,
  "data": {
    "sources": [
      {
        "name": "yfinance",
        "label": "Yahoo Finance via yfinance",
        "configured": true,
        "status": "configured",
        "package": "yfinance",
        "package_installed": true,
        "required_env": [],
        "optional_env": [],
        "capabilities": [
          "quote",
          "ohlcv",
          "fundamentals",
          "calendar",
          "sector",
          "industry",
          "screen"
        ],
        "notes": "Public market, company calendar, sector, industry, and screener data via yfinance."
      },
      {
        "name": "fmp",
        "label": "Financial Modeling Prep",
        "configured": false,
        "status": "missing_config",
        "package": null,
        "package_installed": true,
        "required_env": [
          {
            "name": "FMP_API_KEY",
            "present": false
          }
        ],
        "optional_env": [],
        "capabilities": [
          "analyst_estimates",
          "consensus_estimates"
        ],
        "notes": "Analyst estimate provider via FMP stable analyst-estimates endpoint."
      }
    ],
    "count": 11,
    "summary": {
      "total": 11,
      "configured": 8,
      "ok": 0,
      "failed": 0,
      "missing_config": 3
    }
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.sources` | array | Provider setup rows. The full command returns all known providers. |
| `data.sources[].name` | string | Provider key. |
| `data.sources[].configured` | boolean | `true` when required environment variables are present and package import checks pass. |
| `data.sources[].status` | string | `configured` or `missing_config`. |
| `data.sources[].package` | string or null | Import name checked for package-backed providers. |
| `data.sources[].package_installed` | boolean | Whether the package import check succeeded. |
| `data.sources[].required_env` | array | Required environment variables with `name` and `present`. |
| `data.sources[].optional_env` | array | Optional environment variables with `name` and `present`. |
| `data.sources[].capabilities` | array | Capability tags available from the provider. |
| `data.sources[].notes` | string | Setup or coverage note for the provider. |
| `data.count` | integer | Number of provider rows returned. |
| `data.summary.total` | integer | Total provider rows inspected. |
| `data.summary.configured` | integer | Providers with local configuration ready. |
| `data.summary.ok` | integer | Connectivity successes. This is `0` for `sources.status` because the command does not run probes. |
| `data.summary.failed` | integer | Connectivity failures. This is `0` for `sources.status` because the command does not run probes. |
| `data.summary.missing_config` | integer | Providers missing required local configuration. |

## finance sources.test

Run a lightweight provider connectivity test against one provider or all providers.

### What it does

`finance sources.test` runs a minimal validation query for the selected provider. For example, `yfinance` requests a quote, `sec` resolves company metadata, and document parser providers check that their package import path works.

The command returns one result row per provider. The top-level command can be `ok: true` even when an individual provider row reports `status: failed` or `status: missing_config`; inspect `data.results` and `data.summary` for provider-level readiness.

### When to use it

Use this command when a workflow fails and you need to separate local setup problems from provider connectivity problems. It is also useful before running examples that depend on a specific provider.

### Usage

```bash
finance sources.test [SOURCE|source=SOURCE] [symbol=SYMBOL] [timeout=SECONDS]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `SOURCE` | No | all providers | `yfinance`, `sec`, `gdelt`, `motley_fool`, `company_ir`, `fmp`, `pymupdf`, `camelot`, `paddleocr`, `alphavantage`, `alpaca`, `all` | Positional provider key. Omit it or pass `all` to test every provider. |
| `source` | No | all providers | Same as `SOURCE` | Keyword form of the provider key. Use either `SOURCE` or `source=SOURCE`, not both. |
| `symbol` | No | `AAPL` | Public ticker symbol | Symbol used by probes that need a ticker. The value is uppercased in the result. |
| `timeout` | No | `30` | Seconds as a number | Timeout passed to provider probes. Some providers can still take most of the timeout window. |

### Basic usage

```bash
finance sources.test yfinance symbol=AAPL --output json
finance sources.test sec symbol=AAPL timeout=60 --output json
finance sources.test source=all symbol=MSFT timeout=60 --output json
```

### Example output

This output was generated with `finance sources.test yfinance symbol=AAPL --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "AAPL",
    "results": [
      {
        "name": "yfinance",
        "configured": true,
        "ok": true,
        "status": "ok",
        "latency_ms": 1167.07,
        "error": null,
        "required_env": [],
        "optional_env": [],
        "capabilities": [
          "quote",
          "ohlcv",
          "fundamentals",
          "calendar",
          "sector",
          "industry",
          "screen"
        ]
      }
    ],
    "count": 1,
    "summary": {
      "total": 1,
      "configured": 1,
      "ok": 1,
      "failed": 0,
      "missing_config": 0
    }
  },
  "error": null,
  "warnings": []
}
```

Provider failures are returned inside `data.results`. This output was generated with `finance sources.test sec symbol=AAPL timeout=60 --output json` in an environment where the SEC request was rejected:

```json
{
  "ok": true,
  "data": {
    "symbol": "AAPL",
    "results": [
      {
        "name": "sec",
        "configured": true,
        "ok": false,
        "status": "failed",
        "latency_ms": 366.72,
        "error": "SEC request failed: Client error '403 Forbidden' for url 'https://www.sec.gov/files/company_tickers.json'\nFor more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403",
        "required_env": [],
        "optional_env": [
          {
            "name": "FINANCE_SEC_USER_AGENT",
            "present": false
          }
        ],
        "capabilities": [
          "filings",
          "filing_sections",
          "company_metadata"
        ]
      }
    ],
    "count": 1,
    "summary": {
      "total": 1,
      "configured": 1,
      "ok": 0,
      "failed": 1,
      "missing_config": 0
    }
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.symbol` | string | Uppercased ticker symbol used by provider probes. |
| `data.results` | array | One result row per selected provider. |
| `data.results[].name` | string | Provider key that was tested. |
| `data.results[].configured` | boolean | Whether local setup was sufficient to attempt the probe. |
| `data.results[].ok` | boolean | Provider-level probe result. |
| `data.results[].status` | string | `ok`, `failed`, or `missing_config`. |
| `data.results[].latency_ms` | number or null | Probe duration in milliseconds. `null` when no probe ran because configuration was missing. |
| `data.results[].error` | string or null | Provider-level error message. |
| `data.results[].required_env` | array | Required environment variable status rows. |
| `data.results[].optional_env` | array | Optional environment variable status rows. |
| `data.results[].capabilities` | array | Capability tags attached to the provider. |
| `data.count` | integer | Number of provider result rows returned. |
| `data.summary.total` | integer | Number of provider result rows summarized. |
| `data.summary.configured` | integer | Providers locally configured. |
| `data.summary.ok` | integer | Providers whose probe succeeded. |
| `data.summary.failed` | integer | Providers whose probe failed or could not run. |
| `data.summary.missing_config` | integer | Providers skipped because required configuration is missing. |
