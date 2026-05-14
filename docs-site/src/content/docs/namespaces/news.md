---
title: news
description: Search and summarize public news context.
---

Use `news.*` for public news context from GDELT. News APIs are live services and can rate limit; Finance CLI returns the provider error rather than filling in fake articles.

## Parameters

### Query And Date Controls

Both `news.search` and `news.analyze` use the same query/date controls. Choose one query target: `query`, `symbol`, or `sector`. Choose either relative time (`timespan`) or fixed date/date-time inputs, not both.

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `query` | No | None | Text | Literal GDELT query. |
| `symbol` | No | None | Public ticker | Builds a company-oriented query for the symbol. |
| `sector` | No | None | Sector name/key | Builds a sector-oriented query. |
| `max_records` | No | `50` | Integer | Maximum records requested/returned. |
| `timespan` | No | Provider default | GDELT timespan such as `30D`, `1W`, `1M`, `24H`, `90min` | Relative lookback from now. |
| `date` | No | None | `YYYY-MM-DD` | One full calendar day. |
| `start_date` | No | None | `YYYY-MM-DD` | Start of a full-day date range. |
| `end_date` | No | None | `YYYY-MM-DD` | End of a full-day date range. |
| `start_datetime` | No | None | `YYYYMMDDHHMMSS` | Precise start time. |
| `end_datetime` | No | None | `YYYYMMDDHHMMSS` | Precise end time. |

### `news.analyze` Additional Parameters

| Parameter | Required | Default | Values | Description |
| --- | --- | --- | --- | --- |
| `analysis` / `type` | No | `timeline` | `timeline`, `tone`, `context`, `geo`, `doc` | Analysis endpoint/mode. `type` is accepted as an alias. |
| `mode` | No | Provider default | GDELT mode | Provider-specific mode for supported analysis types. |

## Search

```bash
finance news.search symbol=NVDA timespan=7D max_records=3
finance news.search query="NVIDIA export controls" timespan=24h
```

Expected success shape:

```json
{
  "query": "NVDA",
  "articles": [
    {
      "title": "...",
      "url": "https://...",
      "published_at": "...",
      "source": "..."
    }
  ],
  "source": "gdelt"
}
```

## Analyze

```bash
finance news.analyze symbol=NVDA analysis=timeline timespan=7D
```

During live testing, GDELT returned HTTP 429 for both `news.search` and `news.analyze`:

```json
{
  "ok": false,
  "error": "GDELT request failed after retries: GDELT rate limit returned HTTP 429"
}
```

That is the intended failure mode. The command does not invent fallback articles when the provider is unavailable.
