---
title: price
description: Build price context around a date and discover large historical price moves.
---

# finance price

The `price.*` commands return price context around a target date and identify large historical moves. Use this namespace when a workflow needs to connect an event, filing, or transcript date to market reaction.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance price.context

Return a source-linked evidence timeline around a date.

### What it does

`finance price.context` returns a source-linked evidence timeline around a date. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `target_date`, `lookback`, `lookback_days`, `start_date`, `end_date`, `timeline`, `count`.

### When to use it

Use when the user asks what filings, news, or transcripts were near a dated price move.

Do not claim causality unless the evidence explicitly supports it.

Behavior details: lookback is calendar time around date: 3D=3 calendar days before and after, 1W=7 calendar days, 1M=30 calendar days. Timeline roles are temporal only: before_move, same_day, after_move. Event/publication dates are explicit to avoid implied causal claims.

### Usage

```bash
finance price.context SYMBOL date=YYYY-MM-DD [lookback=3D news_limit=5 filing_limit=80 transcript_limit=12] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `date` | Yes | None | `YYYY-MM-DD` | Target event or move date to center the evidence window on. |
| `filing_limit` | No | `80` | Integer | Maximum recent filings considered before date filtering. |
| `lookback` | No | `3D` | String | Calendar window around `date`, such as `3D`, `1W`, or `1M`. |
| `news_limit` | No | `5` | Integer | Maximum news items included in the timeline. |
| `transcript_limit` | No | `12` | Integer | Maximum transcripts considered before date filtering. |

### Basic usage

```bash
finance price.context IOT date=2026-03-06 lookback=3D --output json
```

### Example output

This output was generated with `finance price.context IOT date=2026-03-06 lookback=3D --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "target_date": "2026-03-06",
    "lookback": "3D",
    "lookback_days": 3,
    "start_date": "2026-03-03",
    "end_date": "2026-03-09",
    "timeline": [
      {
        "relative_day": -1,
        "date": "2026-03-05",
        "evidence_role": "before_move",
        "source_type": "filing",
        "title": "8-K filed",
        "url": "https://www.sec.gov/Archives/edgar/data/1642896/000162828026015170/iot-20260305.htm",
        "metadata": {
          "form": "8-K",
          "accession_no": "0001628280-26-015170",
          "report_date": "2026-03-05",
          "items": [
            "2.02",
            "9.01"
          ]
        }
      },
      {
        "relative_day": -1,
        "date": "2026-03-05",
        "evidence_role": "before_move",
        "source_type": "transcript",
        "title": "Samsara (IOT) Q4 2026 Earnings Call Transcript",
        "url": "https://www.fool.com/earnings/call-transcripts/2026/03/05/samsara-iot-q4-2026-earnings-call-transcript/",
        "metadata": {
          "quarter": "Q4 2026",
          "published_at": "2026-03-05T23:27:39+00:00",
          "source": "motley_fool"
        }
      },
      {
        "relative_day": 2,
        "date": "2026-03-08",
        "evidence_role": "after_move",
        "source_type": "news",
        "title": "10 Stocks Investors Are Watching Closely This Week",
        "url": "https://www.insidermonkey.com/blog/10-stocks-investors-are-watching-closely-this-week-1711585/",
        "metadata": {
          "domain": "insidermonkey.com",
          "source_country": "United States",
          "language": "English",
          "published_at": "20260308T034500Z"
        },
        "excerpt": "20260308T034500Z"
      },
      {
        "relative_day": 3,
        "date": "2026-03-09",
        "evidence_role": "after_move",
        "source_type": "news",
        "title": "Buddha / Nature : MFAH pairs ancient masterpieces with contemporary global visions",
        "url": "https://artdaily.com/news/193701/Buddha-Nature--MFAH-pairs-ancient-masterpieces-with-contemporary-global-visions",
        "metadata": {
          "domain": "artdaily.com",
          "source_country": "United States",
          "language": "English",
          "published_at": "20260309T011500Z"
        },
        "excerpt": "20260309T011500Z"
      },
      {
        "relative_day": 3,
        "date": "2026-03-09",
        "evidence_role": "after_move",
        "source_type": "news",
        "title": "FinancialContent - Samsara Inc . ( IOT ): The Digital Backbone of the Physical World – 2026 Research Feature",
        "url": "https://markets.financialcontent.com/stocks/article/finterra-2026-3-9-samsara-inc-iot-the-digital-backbone-of-the-physical-world-2026-research-feature",
        "metadata": {
          "domain": "markets.financialcontent.com",
          "source_country": "United States",
          "language": "English",
          "published_at": "20260309T141500Z"
        },
        "excerpt": "20260309T141500Z"
      },
      {
        "relative_day": 3,
        "date": "2026-03-09",
        "evidence_role": "after_move",
        "source_type": "news",
        "title": "NVIDIA Upgraded , Eli Lilly Downgraded : Updated Rankings on Top Blue - Chip Stocks",
        "url": "https://investorplace.com/market360/2026/03/20260309-blue-chip-upgrades-downgrades/",
        "metadata": {
          "domain": "investorplace.com",
          "source_country": "United States",
          "language": "English",
          "published_at": "20260309T163000Z"
        },
        "excerpt": "20260309T163000Z"
      },
      {
        "relative_day": 3,
        "date": "2026-03-09",
        "evidence_role": "after_move",
        "source_type": "news",
        "title": "Samsara Q4 Earnings Call Highlights",
        "url": "https://www.tickerreport.com/banking-finance/13372020/samsara-q4-earnings-call-highlights.html",
        "metadata": {
          "domain": "tickerreport.com",
          "source_country": "United States",
          "language": "English",
          "published_at": "20260309T081500Z"
        },
        "excerpt": "20260309T081500Z"
      }
    ],
    "count": 7,
    "warnings": [],
    "notes": [
      "Timeline roles are temporal only: before_move, same_day, or after_move.",
      "Event/publication dates are shown explicitly to avoid implied causality."
    ]
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
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.end_date` | string | End date used by the command. |
| `data.lookback` | string | Calendar lookback window requested by the command. |
| `data.lookback_days` | integer | Lookback converted to calendar days. |
| `data.notes` | array | Additional notes that affect interpretation. |
| `data.notes[]` | string | Additional notes that affect interpretation. |
| `data.start_date` | string | Start date used by the command. |
| `data.symbol` | string | Ticker symbol used for the timeline. |
| `data.target_date` | string | Target event date used by the command. |
| `data.timeline` | array | Chronological evidence records around the target date. |
| `data.timeline[]` | object | Chronological evidence records around the target date. |
| `data.warnings` | array | Non-fatal warnings returned by the command. |
| `data.timeline[].date` | string | Event, bar, filing, or publication date. |
| `data.timeline[].evidence_role` | string | Temporal role relative to the target date. |
| `data.timeline[].excerpt` | string | Short excerpt or source snippet. |
| `data.timeline[].metadata` | object | Source metadata for the evidence record. |
| `data.timeline[].relative_day` | integer | Day offset from the target date. |
| `data.timeline[].source_type` | string | Type of evidence source. |
| `data.timeline[].title` | string | Filing, transcript, or article title shown in the timeline. |
| `data.timeline[].url` | string | Source URL. |
| `data.timeline[].metadata.accession_no` | string | SEC accession number for filing evidence. |
| `data.timeline[].metadata.domain` | string | Article domain. |
| `data.timeline[].metadata.form` | string | SEC form type for filing evidence. |
| `data.timeline[].metadata.items` | array | SEC form items for filing evidence. |
| `data.timeline[].metadata.items[]` | string | Individual SEC form item code. |
| `data.timeline[].metadata.language` | string | Article language. |
| `data.timeline[].metadata.published_at` | string | Publication timestamp returned by the provider. |
| `data.timeline[].metadata.quarter` | string | Fiscal quarter label. |
| `data.timeline[].metadata.report_date` | string | Reporting period date. |
| `data.timeline[].metadata.source` | string | Provider or source identifier for the returned data. |
| `data.timeline[].metadata.source_country` | string | Article source country. |

## finance price.moves

Find large deterministic close-to-close stock moves.

### What it does

`finance price.moves` finds large deterministic close-to-close stock moves. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `window`, `trading_window_days`, `years`, `threshold_pct`, `moves`, `count`, `source`.

### When to use it

Use for price move discovery and evidence timelines around a date.

Do not infer causality from price.context alone.

Behavior details: window is a trading-day window: 1d=1 trading day, 1w=5 trading days, 1m=21 trading days. threshold accepts decimal or percentage-point inputs: 0.08, 8, and 8% all mean 8%. Uses one OHLCV fetch and deterministic close-to-close math. Returns move dates and magnitude only; it does not infer causality.

### Usage

```bash
finance price.moves SYMBOL [window=1d|3d|1w|1m years=3 threshold=8|8% limit=20 provider=auto] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `limit` | No | `20` | Integer | Maximum number of records returned. |
| `provider` | No | `auto` | String | Market data provider selection. Use `auto` unless you need to force a supported provider. |
| `threshold` | No | None | `8`, `8%` | Minimum absolute close-to-close move. `8`, `8%`, and `0.08` are treated as 8%. |
| `window` | No | None | `1d`, `3d`, `1w`, `1m` | Trading-day move window. |
| `years` | No | `3` | Integer | Historical lookback period in years. |

### Basic usage

```bash
finance price.moves IOT years=1 threshold=8% limit=5 --output json
```

### Example output

This output was generated with `finance price.moves IOT years=1 threshold=8% limit=5 --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "window": "1d",
    "trading_window_days": 1,
    "years": 1,
    "threshold_pct": 8.0,
    "moves": [
      {
        "symbol": "IOT",
        "end_date": "2026-03-06",
        "start_date": "2026-03-05",
        "window": "1 trading day",
        "start_close": 29.58,
        "end_close": 35.36,
        "return_pct": 19.54,
        "direction": "up",
        "volume": 33401800,
        "volume_vs_20d": 3.84,
        "avg_abs_return_20d_pct": 3.8994,
        "move_vs_20d_avg_abs_return": 5.01,
        "source": "yfinance"
      },
      {
        "symbol": "IOT",
        "end_date": "2025-09-05",
        "start_date": "2025-09-04",
        "window": "1 trading day",
        "start_close": 35.84,
        "end_close": 42.09,
        "return_pct": 17.44,
        "direction": "up",
        "volume": 23981800,
        "volume_vs_20d": 4.46,
        "avg_abs_return_20d_pct": 2.8561,
        "move_vs_20d_avg_abs_return": 6.11,
        "source": "yfinance"
      },
      {
        "symbol": "IOT",
        "end_date": "2025-12-05",
        "start_date": "2025-12-04",
        "window": "1 trading day",
        "start_close": 40.71,
        "end_close": 45.22,
        "return_pct": 11.08,
        "direction": "up",
        "volume": 21626700,
        "volume_vs_20d": 4.64,
        "avg_abs_return_20d_pct": 2.5703,
        "move_vs_20d_avg_abs_return": 4.31,
        "source": "yfinance"
      },
      {
        "symbol": "IOT",
        "end_date": "2026-04-15",
        "start_date": "2026-04-14",
        "window": "1 trading day",
        "start_close": 26.51,
        "end_close": 28.85,
        "return_pct": 8.83,
        "direction": "up",
        "volume": 9531500,
        "volume_vs_20d": 1.64,
        "avg_abs_return_20d_pct": 2.7308,
        "move_vs_20d_avg_abs_return": 3.23,
        "source": "yfinance"
      },
      {
        "symbol": "IOT",
        "end_date": "2026-04-23",
        "start_date": "2026-04-22",
        "window": "1 trading day",
        "start_close": 32.04,
        "end_close": 29.28,
        "return_pct": -8.61,
        "direction": "down",
        "volume": 6673700,
        "volume_vs_20d": 1.1,
        "avg_abs_return_20d_pct": 3.3912,
        "move_vs_20d_avg_abs_return": 2.54,
        "source": "yfinance"
      }
    ],
    "count": 5,
    "source": "yfinance",
    "notes": [
      "Moves are close-to-close and deterministic.",
      "No causal explanation is inferred by this command."
    ]
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
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.moves` | array | Large price-move records. |
| `data.moves[]` | object | Large price-move records. |
| `data.notes` | array | Additional notes that affect interpretation. |
| `data.notes[]` | string | Additional notes that affect interpretation. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Ticker symbol used for move discovery. |
| `data.threshold_pct` | number | Move threshold as a percentage. |
| `data.trading_window_days` | integer | Trading-day count represented by `window`. |
| `data.window` | string | Window size used for the calculation. |
| `data.years` | integer | Historical window length in years. |
| `data.moves[].avg_abs_return_20d_pct` | number | Trailing 20-day average absolute return percentage. |
| `data.moves[].direction` | string | Direction of the close-to-close move: `up` or `down`. |
| `data.moves[].end_close` | number | Close price at the end of a move window. |
| `data.moves[].end_date` | string | End date used by the command. |
| `data.moves[].move_vs_20d_avg_abs_return` | number | Move size divided by trailing average absolute move. |
| `data.moves[].return_pct` | number | Return percentage for the period. |
| `data.moves[].source` | string | Provider or source identifier for the returned data. |
| `data.moves[].start_close` | number | Close price at the start of a move window. |
| `data.moves[].start_date` | string | Start date used by the command. |
| `data.moves[].symbol` | string | Ticker symbol for the move row. |
| `data.moves[].volume` | integer | Trading volume. |
| `data.moves[].volume_vs_20d` | number | Volume compared with trailing 20-day average. |
| `data.moves[].window` | string | Window size used for the calculation. |
