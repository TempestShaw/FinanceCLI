---
title: Public Data Beyond SEC Filings
description: Official company releases, macro series, Taiwan issuer data, market breadth, short data, futures positioning and energy statistics.
---

These commands retrieve source data independently. Your agent chooses which commands to combine. All support canonical JSON and the existing Markdown, compact, schema and table formats.

## Commands at a glance

| Data | Command | Source |
| --- | --- | --- |
| Company releases and investor events | `ir.releases`, `ir.events` | Company-linked RSS/Atom and IR page links |
| Economic series and historical vintages | `macro.search`, `macro.series` | FRED / ALFRED |
| Monthly revenue | `fundamentals.revenue` | TWSE listed-company snapshot |
| Material announcements | `disclosures.recent` | TWSE daily snapshot |
| Advancing, declining and unchanged issues | `market.breadth` | Nasdaq Trader |
| Equity short positions | `short.interest` | FINRA consolidated short interest |
| Daily reported short-sale activity | `short.volume` | FINRA CNMS daily files |
| Futures positions by trader category | `positioning.cot` | CFTC Commitments of Traders |
| Petroleum and gas inventories | `energy.inventory` | EIA |
| State electricity sales and prices | `energy.electricity` | EIA |

## Set up keys and inspect readiness

FRED and EIA require keys. Register your own at [FRED](https://fred.stlouisfed.org/docs/api/api_key.html) and [EIA](https://www.eia.gov/opendata/register.php), then set `FRED_API_KEY` and `EIA_API_KEY` in your shell environment. FRED requires each user to use their own key. Credentials are read at runtime and are not stored in CLI config files.

The other sources have public read paths. FINRA access policies may require credentials; `FINRA_ACCESS_TOKEN` supplies an existing Bearer token. Obtain credentials through FINRA's documented process when required. The CLI does not register accounts or refresh access tokens.

```bash
finance sources.status --output json
finance sources.test twse symbol=2330.TW --output json
finance sources.test nasdaq_breadth --output json
finance sources.test finra symbol=AAPL --output json
finance sources.test cftc --output json
finance sources.test fred --output json
finance sources.test eia --output json
```

`sources.status` checks local setup without network requests. `sources.test` checks a small source-appropriate sample: FRED CPI, CFTC gold, EIA crude, Nasdaq breadth, or TWSE 2330 when the requested symbol is not a Taiwan issuer. A health result distinguishes `missing_config`, `failed`, `empty`, `partial` (data with warnings), and `ok`. A successful probe does not establish every command's coverage.

## Company releases and events

```bash
finance ir.releases NVDA limit=5 --output json
finance ir.releases NVDA url=https://nvidianews.nvidia.com/cats/press_release.xml limit=5 --output md
finance ir.events NVDA url=https://investor.nvidia.com/investor-resources/rss/default.aspx limit=5 --output json
```

Automatic discovery starts from company profile websites and follows a bounded set of company-linked pages and feeds. Pass `url=` for a known official page or RSS/Atom feed when discovery is incomplete. Source failures and empty discoveries are visible; feed availability varies by company. Use `document.read URL format=html` to read a returned release.

Feed publication dates can differ from scheduled event dates. Preserve the returned date kind and source text instead of treating every timestamp as an event start time. [NVIDIA's official feed directory](https://investor.nvidia.com/investor-resources/rss/default.aspx) illustrates the supported source type.

## Economic observations and historical vintages

```bash
finance macro.search "consumer price index" limit=5 --output json
finance macro.series CPIAUCSL start=2020-01-01 limit=1000 --output json
finance macro.series GDP as_of=2024-01-01 limit=8 --output json
```

`as_of` pins both FRED real-time boundaries to retrieve information known on that date. Observation periods are distinct from retrieval dates and revision vintages. Missing source values remain null. Results retain units, frequency, series identifiers and source links. The latest bounded observations are returned in chronological order; `total_available` and `truncated` disclose omitted history. See [FRED API documentation](https://fred.stlouisfed.org/docs/api/fred/) and [real-time periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html).

## Taiwan monthly revenue and disclosures

```bash
finance fundamentals.revenue 2330.TW period=monthly source=twse --output json
finance disclosures.recent 2330.TW source=twse limit=5 --output json
```

The [official TWSE OpenAPI](https://openapi.twse.com.tw/) serves listed-company snapshots. The CLI normalizes Republic of China calendar dates and Chinese source fields. Revenue amounts retain **thousands of TWD**; percent fields use 10 for 10%. Monthly periods, snapshot generation dates and disclosure timestamps remain distinct.

These endpoints do not supply a queryable monthly or announcement history. TPEx companies are outside this source's scope. An empty daily snapshot is not proof that the issuer made no earlier announcements.

## Nasdaq market breadth

```bash
finance market.breadth NASDAQ limit=20 --output json
finance market.breadth NASDAQ year=2025 limit=366 --output compact
```

Returns actual advancing, declining and unchanged issue counts from the [official annual file](https://nasdaqtrader.com/Trader.aspx?id=DailyMarketFiles). This covers Nasdaq-listed issues across trading venues. It does not supply NYSE, all-market, 50/200 DMA, new-high/new-low or up/down volume breadth. [Field definitions](https://classic.nasdaqtrader.com/Trader.aspx?id=DailyMarketSummaryDefs) describe the exchange's scope.

`latest_date`, `age_calendar_days` and `missing_dates` expose freshness and missing source cells. Empty counts are excluded rather than converted to zero. Historical-year age is expected; current-year observations older than four calendar days produce a warning.

## FINRA short data

```bash
finance short.interest AAPL periods=6 --output json
finance short.volume AAPL days=5 --output json
```

`short.interest` returns settlement-date position snapshots, previous positions, changes, average daily volume and days to cover. Settlement dates are not publication dates; the CLI does not invent exact publication timestamps. The bounded symbol-history query fails if its response cap prevents establishing the latest records. See [FINRA equity short interest](https://www.finra.org/finra-data/browse-catalog/equity-short-interest).

`short.volume` downloads at most `days` previous weekday files, excluding today in New York, with a maximum of 60. Holidays, HTTP 403/404 files and absent symbols remain explicit gaps. It does not replace unavailable dates with older ones. CNMS files cover reported off-exchange NMS activity; the ratio uses that file's volume only. **Daily short-sale volume is not outstanding short interest or total market volume.** See [FINRA daily files](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files) and [the distinction](https://syndication.finra.org/content/short-interest-what-it-what-it-not).

FINRA's access and data-use terms apply, including commercial and redistribution restrictions. Availability through a public endpoint does not grant unrestricted reuse.

## Futures positioning

```bash
finance positioning.cot market=gold report=disaggregated weeks=8 --output json
finance positioning.cot market=sp500 report=tff weeks=8 --output json
finance positioning.cot market=088691 report=legacy weeks=8 --output json
```

The [CFTC COT datasets](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) provide futures-only disaggregated, financial-futures (`tff`) and legacy reports. `market` accepts `gold`, `sp500`, or an exact six-character CFTC contract-market code. Each report week produces rows for its trader categories, including long, short, net and available spreading positions.

`as_of_date` is the position date, not the date the public could know it. Exact publication timestamps are not supplied. Keep report families separate because trader taxonomies differ; net positions are calculated within each category.

## Energy inventories and electricity

```bash
finance energy.inventory product=crude limit=12 --output json
finance energy.inventory product=natural_gas limit=12 --output json
finance energy.electricity region=TX frequency=monthly limit=12 --output json
```

Inventory products are `crude`, `gasoline`, `distillate` and `natural_gas`. Crude excludes the Strategic Petroleum Reserve. Natural gas covers the Lower 48 states. Petroleum amounts are thousand barrels; gas is billion cubic feet, with the source unit retained in each row.

Electricity returns all-sector **retail sales and average price**, by state or `US`, at monthly or annual frequency. These observations describe consumption periods, not publication dates. Each request is bounded to at most 5,000 rows; omitted older observations are disclosed. See [EIA API v2](https://www.eia.gov/opendata/documentation.php).

## Capture evidence

Use `--output json` to retain the complete payload and warnings. Non-JSON CLI formats write warnings to standard error, keeping compact record output usable in pipelines. Retain source URLs, period or settlement dates, units, retrieval times, coverage and truncation information with any calculations. These commands read data; they do not place orders or decide investment conclusions.
