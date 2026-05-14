---
title: news
description: Search and summarize public news context.
---

Use `news.*` for public news context from GDELT. News APIs are live services and can rate limit; Finance CLI returns the provider error rather than filling in fake articles.

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
