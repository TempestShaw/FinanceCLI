---
title: news
description: Search and summarize market news from configured news providers.
---

# finance news

The `news.*` commands search and summarize market news. Use this namespace when the user needs recent articles, event timelines, or news context tied to a ticker or query.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance news.analyze

Analyze news volume, tone, context, or geography.

### What it does

`finance news.analyze` analyzes news volume, tone, context, or geography. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `scope`, `mode`, `payload`, `source`.

### When to use it

Use this command when you need an aggregate GDELT analysis view, such as timeline volume, tone, context, or geography for a ticker, query, sector, or industry.

Behavior details: Use this only when you need trend, tone, context, geo, or raw DOC analysis. Use timespan for relative lookback from now, such as 30D, 1W, 1M, 24H, or 90min. date/start_date/end_date are preferred for routine use; datetime inputs provide precision controls.

### Usage

```bash
finance news.analyze analysis=timeline|tone|context|geo|doc [query=TEXT | symbol=SYMBOL | sector=SECTOR] [mode=MODE max_records=50 timespan=30D|1W|1M|24H date=YYYY-MM-DD start_date=YYYY-MM-DD end_date=YYYY-MM-DD start_datetime=YYYYMMDDHHMMSS end_datetime=YYYYMMDDHHMMSS] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `analysis` | Yes | None | `timeline`, `tone`, `context`, `geo`, `doc` | Analysis mode. |
| `query` | No | None | String | Query string or predefined query key accepted by this command. |
| `symbol` | No | `SYMBOL` | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `date` | No | `YYYY-MM-DD` | `YYYY-MM-DD` | Date. |
| `end_date` | No | `YYYY-MM-DD` | `YYYY-MM-DD` | End date in `YYYY-MM-DD` format. |
| `end_datetime` | No | `YYYYMMDDHHMMSS` | String | Explicit GDELT end timestamp. |
| `max_records` | No | `50` | Integer | Maximum records requested from the provider. |
| `mode` | No | `MODE` | String | Analysis mode, such as timeline, tone, context, or geography when supported. |
| `sector` | No | `SECTOR` | String | Optional sector filter for the query. |
| `start_date` | No | `YYYY-MM-DD` | `YYYY-MM-DD` | Start date in `YYYY-MM-DD` format. |
| `start_datetime` | No | `YYYYMMDDHHMMSS` | String | Explicit GDELT start timestamp. |
| `timespan` | No | None | `30D`, `1W`, `1M`, `24H` | Relative GDELT lookback window. |

### Basic usage

```bash
finance news.analyze symbol=NVDA analysis=timeline timespan=1d --output json
```

### Example output

This output was generated with `finance news.analyze symbol=NVDA analysis=timeline timespan=1d --output json`.

```json
{
  "ok": true,
  "data": {
    "scope": {
      "type": "symbol",
      "value": "NVDA"
    },
    "mode": "timelinevolraw",
    "payload": {
      "query_details": {
        "title": "\"NVIDIA\" sourcelang:english",
        "date_resolution": "15m"
      },
      "timeline": [
        {
          "series": "Article Count",
          "data": [
            {
              "date": "20260514T014500Z",
              "value": 18,
              "norm": 2478
            },
            {
              "date": "20260514T020000Z",
              "value": 4,
              "norm": 673
            },
            {
              "date": "20260514T021500Z",
              "value": 9,
              "norm": 2354
            },
            {
              "date": "20260514T023000Z",
              "value": 2,
              "norm": 199
            },
            {
              "date": "20260514T024500Z",
              "value": 10,
              "norm": 1303
            },
            {
              "date": "20260514T030000Z",
              "value": 13,
              "norm": 2225
            },
            {
              "date": "20260514T031500Z",
              "value": 15,
              "norm": 1664
            },
            {
              "date": "20260514T033000Z",
              "value": 11,
              "norm": 2746
            },
            {
              "date": "20260514T034500Z",
              "value": 6,
              "norm": 874
            },
            {
              "date": "20260514T040000Z",
              "value": 9,
              "norm": 2433
            },
            {
              "date": "20260514T041500Z",
              "value": 15,
              "norm": 1943
            },
            {
              "date": "20260514T050000Z",
              "value": 26,
              "norm": 2919
            },
            {
              "date": "20260514T051500Z",
              "value": 15,
              "norm": 2214
            },
            {
              "date": "20260514T053000Z",
              "value": 4,
              "norm": 675
            },
            {
              "date": "20260514T054500Z",
              "value": 25,
              "norm": 2619
            },
            {
              "date": "20260514T060000Z",
              "value": 26,
              "norm": 2933
            },
            {
              "date": "20260514T061500Z",
              "value": 2,
              "norm": 442
            },
            {
              "date": "20260514T063000Z",
              "value": 8,
              "norm": 1595
            },
            {
              "date": "20260514T064500Z",
              "value": 6,
              "norm": 464
            },
            {
              "date": "20260514T071500Z",
              "value": 22,
              "norm": 2955
            },
            {
              "date": "20260514T073000Z",
              "value": 1,
              "norm": 259
            },
            {
              "date": "20260514T074500Z",
              "value": 14,
              "norm": 1568
            },
            {
              "date": "20260514T080000Z",
              "value": 16,
              "norm": 2376
            },
            {
              "date": "20260514T081500Z",
              "value": 1,
              "norm": 995
            },
            {
              "date": "20260514T083000Z",
              "value": 13,
              "norm": 3180
            },
            {
              "date": "20260514T084500Z",
              "value": 1,
              "norm": 227
            },
            {
              "date": "20260514T091500Z",
              "value": 12,
              "norm": 3576
            },
            {
              "date": "20260514T093000Z",
              "value": 12,
              "norm": 4652
            },
            {
              "date": "20260514T094500Z",
              "value": 5,
              "norm": 1771
            },
            {
              "date": "20260514T101500Z",
              "value": 1,
              "norm": 502
            },
            {
              "date": "20260514T103000Z",
              "value": 6,
              "norm": 1551
            },
            {
              "date": "20260514T104500Z",
              "value": 4,
              "norm": 1302
            },
            {
              "date": "20260514T110000Z",
              "value": 0,
              "norm": 461
            },
            {
              "date": "20260514T111500Z",
              "value": 2,
              "norm": 1462
            },
            {
              "date": "20260514T113000Z",
              "value": 32,
              "norm": 5355
            },
            {
              "date": "20260514T114500Z",
              "value": 17,
              "norm": 2941
            },
            {
              "date": "20260514T120000Z",
              "value": 14,
              "norm": 2624
            },
            {
              "date": "20260514T121500Z",
              "value": 17,
              "norm": 2730
            },
            {
              "date": "20260514T123000Z",
              "value": 9,
              "norm": 2348
            },
            {
              "date": "20260514T124500Z",
              "value": 7,
              "norm": 2047
            },
            {
              "date": "20260514T130000Z",
              "value": 5,
              "norm": 874
            },
            {
              "date": "20260514T131500Z",
              "value": 9,
              "norm": 1866
            },
            {
              "date": "20260514T133000Z",
              "value": 26,
              "norm": 4951
            },
            {
              "date": "20260514T134500Z",
              "value": 5,
              "norm": 495
            },
            {
              "date": "20260514T140000Z",
              "value": 2,
              "norm": 231
            },
            {
              "date": "20260514T141500Z",
              "value": 1,
              "norm": 489
            },
            {
              "date": "20260514T143000Z",
              "value": 5,
              "norm": 1169
            },
            {
              "date": "20260514T144500Z",
              "value": 2,
              "norm": 459
            },
            {
              "date": "20260514T150000Z",
              "value": 3,
              "norm": 475
            },
            {
              "date": "20260514T151500Z",
              "value": 3,
              "norm": 431
            },
            {
              "date": "20260514T153000Z",
              "value": 2,
              "norm": 467
            },
            {
              "date": "20260514T154500Z",
              "value": 11,
              "norm": 1670
            },
            {
              "date": "20260514T160000Z",
              "value": 13,
              "norm": 1868
            },
            {
              "date": "20260514T161500Z",
              "value": 0,
              "norm": 232
            },
            {
              "date": "20260514T163000Z",
              "value": 10,
              "norm": 1887
            },
            {
              "date": "20260514T170000Z",
              "value": 22,
              "norm": 4420
            },
            {
              "date": "20260514T171500Z",
              "value": 1,
              "norm": 684
            },
            {
              "date": "20260514T173000Z",
              "value": 0,
              "norm": 227
            },
            {
              "date": "20260514T174500Z",
              "value": 5,
              "norm": 966
            },
            {
              "date": "20260514T180000Z",
              "value": 22,
              "norm": 4373
            },
            {
              "date": "20260514T181500Z",
              "value": 12,
              "norm": 4061
            },
            {
              "date": "20260514T183000Z",
              "value": 5,
              "norm": 2820
            },
            {
              "date": "20260514T184500Z",
              "value": 13,
              "norm": 4185
            },
            {
              "date": "20260514T190000Z",
              "value": 10,
              "norm": 1587
            },
            {
              "date": "20260514T191500Z",
              "value": 1,
              "norm": 1084
            },
            {
              "date": "20260514T193000Z",
              "value": 10,
              "norm": 3149
            },
            {
              "date": "20260514T194500Z",
              "value": 6,
              "norm": 2096
            },
            {
              "date": "20260514T201500Z",
              "value": 13,
              "norm": 3551
            },
            {
              "date": "20260514T203000Z",
              "value": 9,
              "norm": 1338
            },
            {
              "date": "20260514T204500Z",
              "value": 11,
              "norm": 1852
            },
            {
              "date": "20260514T210000Z",
              "value": 9,
              "norm": 1255
            },
            {
              "date": "20260514T211500Z",
              "value": 0,
              "norm": 198
            },
            {
              "date": "20260514T213000Z",
              "value": 5,
              "norm": 1422
            },
            {
              "date": "20260514T220000Z",
              "value": 3,
              "norm": 433
            },
            {
              "date": "20260514T221500Z",
              "value": 7,
              "norm": 2884
            },
            {
              "date": "20260514T223000Z",
              "value": 3,
              "norm": 461
            },
            {
              "date": "20260514T224500Z",
              "value": 2,
              "norm": 924
            },
            {
              "date": "20260514T230000Z",
              "value": 4,
              "norm": 1290
            },
            {
              "date": "20260514T231500Z",
              "value": 4,
              "norm": 643
            },
            {
              "date": "20260514T233000Z",
              "value": 11,
              "norm": 2554
            },
            {
              "date": "20260514T234500Z",
              "value": 6,
              "norm": 2880
            },
            {
              "date": "20260515T000000Z",
              "value": 2,
              "norm": 842
            },
            {
              "date": "20260515T003000Z",
              "value": 16,
              "norm": 2598
            },
            {
              "date": "20260515T010000Z",
              "value": 3,
              "norm": 213
            },
            {
              "date": "20260515T011500Z",
              "value": 16,
              "norm": 2239
            }
          ]
        }
      ]
    },
    "source": "gdelt_doc"
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
| `data.mode` | string | News analysis mode. |
| `data.payload` | object | Mode-specific payload. |
| `data.scope` | object | Ticker or query scope used by a news command. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.payload.query_details` | object | Provider metadata for a screen query. |
| `data.payload.timeline` | array | Chronological evidence records around the target date. |
| `data.payload.timeline[]` | object | Chronological evidence records around the target date. |
| `data.scope.type` | string | Scope type used for the GDELT query, such as `symbol` or `query`. |
| `data.scope.value` | string | Scope value sent to the provider. |
| `data.payload.query_details.date_resolution` | string | Time bucket resolution used by the GDELT analysis. |
| `data.payload.query_details.title` | string | Provider title for the returned analysis. |
| `data.payload.timeline[].data` | array | Timeline buckets for the series. |
| `data.payload.timeline[].data[]` | object | Individual timeline bucket. |
| `data.payload.timeline[].series` | string | Timeline series label. |
| `data.payload.timeline[].data[].date` | string | Event, bar, filing, or publication date. |
| `data.payload.timeline[].data[].norm` | integer | Normalized GDELT volume value for the bucket. |
| `data.payload.timeline[].data[].value` | integer | Article count or analysis value for the time bucket. |

## finance news.search

Search finance news through GDELT.

### What it does

`finance news.search` searches finance news through GDELT. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `scope`, `articles`, `count`, `source`.

### When to use it

Use this command when you need source-attributed article rows for a ticker, query, sector, or industry.

Behavior details: Use date for one full day, or start_date/end_date for a full-day range. Use timespan for relative lookback from now, such as 30D, 1W, 1M, 24H, or 90min. Use start_datetime/end_datetime only when you need second-level precision. Use either timespan or fixed date/date-time inputs, not both.

### Usage

```bash
finance news.search [query=TEXT | symbol=SYMBOL | sector=SECTOR] [max_records=50 timespan=30D|1W|1M|24H date=YYYY-MM-DD start_date=YYYY-MM-DD end_date=YYYY-MM-DD start_datetime=YYYYMMDDHHMMSS end_datetime=YYYYMMDDHHMMSS] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `query` | No | None | String | Query string or predefined query key accepted by this command. |
| `symbol` | No | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `date` | No | `YYYY-MM-DD` | `YYYY-MM-DD` | Date. |
| `end_date` | No | `YYYY-MM-DD` | `YYYY-MM-DD` | End date in `YYYY-MM-DD` format. |
| `end_datetime` | No | `YYYYMMDDHHMMSS` | String | Explicit GDELT end timestamp. |
| `max_records` | No | `50` | Integer | Maximum records requested from the provider. |
| `sector` | No | None | String | Sector query. |
| `start_date` | No | `YYYY-MM-DD` | `YYYY-MM-DD` | Start date in `YYYY-MM-DD` format. |
| `start_datetime` | No | `YYYYMMDDHHMMSS` | String | Explicit GDELT start timestamp. |
| `timespan` | No | None | `30D`, `1W`, `1M`, `24H` | Relative GDELT lookback window. |

### Basic usage

```bash
finance news.search symbol=NVDA max_records=5 --output json
```

### Example output

This output was generated with `finance news.search symbol=NVDA max_records=5 --output json`.

```json
{
  "ok": true,
  "data": {
    "scope": {
      "type": "symbol",
      "value": "NVDA"
    },
    "articles": [
      {
        "url": "https://www.news-gazette.com/news/nation-world/trump-insists-us-china-relations-are-in-a-good-place-despite-differences-as-he-wraps/article_299a1bc2-6c7d-5ca8-bc41-9e504ce1d7b3.html",
        "url_mobile": "",
        "title": "Trump insists US - China relations are in a good place despite differences as he wraps up Beijing trip",
        "seendate": "20260515T011500Z",
        "socialimage": "https://bloximages.newyork1.vip.townnews.com/news-gazette.com/content/tncms/custom/image/3d3bfbd4-3cf5-11ec-9461-574a9d514a20.jpg",
        "domain": "news-gazette.com",
        "language": "English",
        "sourcecountry": "United States"
      },
      {
        "url": "https://www.straitstimes.com/business/companies-markets/wall-street-ends-higher-on-tech-rally-investors-eye-beijing-talks",
        "url_mobile": "",
        "title": "Wall Street ends higher on tech rally ; investors eye Beijing talks",
        "seendate": "20260515T011500Z",
        "socialimage": "https://cassette.sphdigital.com.sg/image/straitstimes/747c83f30ff3a86b3dd59fa74cd950dff855867fc3a69b39711b4f902f686ee8",
        "domain": "straitstimes.com",
        "language": "English",
        "sourcecountry": "Singapore"
      },
      {
        "url": "https://finance.yahoo.com/news/nvidia-soon-more-apple-microsoft-124840404.html",
        "url_mobile": "",
        "title": "Nvidia Will Soon Make More than Apple and Microsoft Combined",
        "seendate": "20260515T011500Z",
        "socialimage": "https://s.yimg.com/ny/api/res/1.2/elUs4YO87wqsdHAuJv7ErQ--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyMDA7aD04MDA-/https://media.zenfs.com/en/24_7_wall_st__718/4fdf3fc67f9ba6ee23a3d2991c1d2a65",
        "domain": "finance.yahoo.com",
        "language": "English",
        "sourcecountry": "United States"
      },
      {
        "url": "https://newafricanmagazine.com/innovation/the-future-is-now-says-africas-ai-pioneer/",
        "url_mobile": "",
        "title": "The future is now , says Africa AI pioneer - New African Magazine",
        "seendate": "20260515T011500Z",
        "socialimage": "https://newafricanmagazine.com/wordpress/wp-content/uploads/2024/09/000_34NZ67U.jpg",
        "domain": "newafricanmagazine.com",
        "language": "English",
        "sourcecountry": "Nigeria"
      },
      {
        "url": "https://www.fool.com/coverage/stock-market-today/2026/05/14/stock-market-today-may-14-u-s-indexes-move-higher-as-cisco-pops-and-ai-chipmaker-cerebras-debuts/?source=iedfolrf0000001",
        "url_mobile": "",
        "title": "Stock Market Today , May 14 : U . S . Indexes Move Higher as Cisco Pops and AI - Chipmaker Cerebras Debuts",
        "seendate": "20260515T011500Z",
        "socialimage": "",
        "domain": "fool.com",
        "language": "English",
        "sourcecountry": "United States"
      }
    ],
    "count": 5,
    "source": "gdelt"
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
| `data.articles` | array | News article records returned by the provider. |
| `data.articles[]` | object | News article records returned by the provider. |
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.scope` | object | Ticker or query scope used by a news command. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.articles[].domain` | string | Article domain. |
| `data.articles[].language` | string | Article language. |
| `data.articles[].seendate` | string | GDELT seen-date timestamp. |
| `data.articles[].socialimage` | string | Provider image URL for the article. |
| `data.articles[].sourcecountry` | string | Country code or country name reported by GDELT for the article source. |
| `data.articles[].title` | string | Article title. |
| `data.articles[].url` | string | Source URL. |
| `data.articles[].url_mobile` | string | Mobile article URL when GDELT returns one. |
| `data.scope.type` | string | Scope type used for the GDELT query, such as `symbol` or `query`. |
| `data.scope.value` | string | Scope value sent to the provider. |
