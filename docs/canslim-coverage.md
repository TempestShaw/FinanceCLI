# CANSLIM Coverage Assessment

Date: 2026-05-25

Example tickers tested: `NVDA`, `AAPL`, `TSLA`.

Purpose: assess whether FinanceCLI can fetch, normalize, and render the data needed for a CANSLIM stock workflow without faking paid or unavailable data.

## Summary

FinanceCLI is useful for CANSLIM research, but it is not yet a one-command CANSLIM evaluator.

The strongest areas are filings, earnings dates, transcripts, OHLCV-derived performance, multi-period fundamental growth calculations, company metadata, sector/industry tables, ownership holder tables, relative strength, and market trend evidence. The weakest areas are ownership changes, true market breadth, and macro indicators where a reliable free/open source still needs to be selected.

FinanceCLI exposes small reusable primitives rather than a CANSLIM-specific command: `fundamentals.growth` for auditable YoY/CAGR/history rows, `price.relative` for benchmark/sector/peer relative return rows, `market.trend` for index/VIX trend evidence, and CANSLIM-relevant Yahoo quote fields through `market.quote` and `symbol.profile`.

## Support Matrix

| CANSLIM item | Needed data | Current support | Provider/API | Existing command(s) | Rendering notes |
|---|---|---:|---|---|---|
| C | Latest quarterly EPS | Fully supported | SEC/edgartools, yfinance | `fundamentals.metrics`, `calendar.earnings`, `fundamentals.statement` | `fundamentals.metrics` is compact and agent-ready; EPS is computed as net income / diluted shares when available. |
| C | YoY EPS growth | Fully supported where comparable periods are available | SEC/edgartools, yfinance | `fundamentals.growth`, `fundamentals.statement period=quarterly provider=sec` | `fundamentals.growth` returns raw current/comparison values, YoY growth, and EPS method. |
| C | Latest quarterly revenue | Fully supported | SEC/edgartools, yfinance | `fundamentals.metrics`, `fundamentals.statement statement=income period=quarterly` | `fundamentals.metrics` avoids statement row scanning. |
| C | YoY revenue growth | Fully supported where comparable periods are available | SEC/edgartools, yfinance | `fundamentals.growth`, `fundamentals.statement statement=income period=quarterly provider=sec` | `fundamentals.growth` returns raw current/comparison values and YoY growth. |
| C | Operating/net margin | Fully supported for latest period | SEC/edgartools, yfinance | `fundamentals.metrics`, `market.quote` | `fundamentals.metrics` can return `operating_margin` and `net_margin`; quote provides Yahoo trailing margins. |
| A | Annual EPS 3-5y | Fully supported where annual rows are available | SEC/edgartools, yfinance | `fundamentals.growth`, `fundamentals.statement statement=income period=annual provider=sec` | `fundamentals.growth` returns annual history plus annual YoY/CAGR rows. |
| A | Annual revenue 3-5y | Fully supported where annual rows are available | SEC/edgartools, yfinance | `fundamentals.growth`, `fundamentals.statement statement=income period=annual provider=sec` | Same as above. |
| A | CAGR | Fully supported for positive revenue/EPS start/end values | SEC/edgartools, yfinance, local formula | `fundamentals.growth`, `formula.cagr` | `fundamentals.growth` computes CAGR from returned annual history rows and warns if fewer annual rows are available than requested. |
| A | ROE | Partially supported | SEC/edgartools, yfinance | `fundamentals.growth`, `fundamentals.metrics`, `market.quote`, `symbol.profile` | Latest ROE is available when equity is available; multi-period ROE comparisons are returned as deltas when the source rows include enough inputs. |
| N | Recent news | Not supported | (removed) | (removed) | The GDELT-backed news provider was removed because the public API consistently timed out; news evidence now relies on SEC filings + transcripts. |
| N | 8-K filings | Fully supported | SEC EDGAR | `filings.recent forms=8-K classify=true` | Compact is strong for agent use. |
| N | Press releases | Partially supported | SEC EDGAR / IR pages | `filings.recent`, `ir.presentations` | Earnings releases appear via 8-K Item 2.02; broader press releases need better IR/news handling. |
| N | Earnings call commentary | Fully supported where public transcript exists | Motley Fool | `transcripts.search`, `transcripts.read`, `transcripts.qa` | Compact search rows are good. |
| N | 52-week high / breakout | Fully supported for latest distance | yfinance | `market.quote`, `price.performance`, `price.moves` | `price.performance` includes `distance_from_52w_high_pct`. |
| S | Shares outstanding | Fully supported | yfinance | `market.quote`, `symbol.profile` | Compact is good. |
| S | Float | Fully supported when Yahoo provides it | yfinance | `market.quote`, `symbol.profile` | Added `float_shares`. |
| S | Average volume | Fully supported | yfinance | `market.quote`, `symbol.profile` | Added `average_volume` and `average_volume_10d`. |
| S | Recent volume | Fully supported | yfinance | `market.quote`, `market.ohlcv` | Added `regular_market_volume`; OHLCV has daily rows. |
| S | Volume vs average | Fully supported | yfinance + local normalization | `market.quote`, `symbol.profile` | Added `volume_vs_average`. |
| S | Market cap | Fully supported | yfinance | `market.quote`, `symbol.profile` | Already good. |
| L | Relative strength vs sector/index | Fully supported for configured/free OHLCV symbols | yfinance/OHLCV | `price.relative`, `price.performance`, `industry.table` | `price.relative` defaults to SPY/QQQ and auto sector ETF; explicit sector ETFs override auto mapping. |
| L | Price performance 1M/3M/6M/1Y | Fully supported | yfinance/OHLCV | `price.performance` | Compact rows are agent-ready and avoid sending raw OHLCV. |
| L | Peer comparison | Fully supported for explicit peers | yfinance/OHLCV | `price.relative`, `industry.table`, `sector.table` | Peer discovery remains caller/LLM-driven; `price.relative peers=...` compares explicit peers only. |
| L | Sector/industry metadata | Fully supported | yfinance | `symbol.profile`, `sector.*`, `industry.*` | Good. |
| I | Institutional ownership percent | Fully supported when Yahoo provides it | yfinance | `market.quote`, `symbol.profile`, `ownership.holders` | Quote exposes percent; holder command exposes major holder breakdown. |
| I | Major holders | Fully supported when Yahoo provides it | yfinance | `ownership.holders` | Returns major holder breakdown plus institutional/fund holder rows. |
| I | Fund ownership | Partially supported | yfinance | `ownership.holders` | Mutual fund holder rows are available; broader fund ownership history still needs a paid/source-specific provider. |
| I | Ownership changes | Missing | paid provider likely needed | none | Requires time-series ownership provider. |
| M | Major index status | Fully supported | yfinance | `market.status US` | Schema output includes S&P 500, Nasdaq, Dow, VIX. |
| M | Index moving averages | Fully supported | yfinance/OHLCV | `market.trend`, `market.ohlcv SPY,QQQ,DIA,IWM,^VIX` | `market.trend` returns 50/200 DMA evidence and multi-period returns. |
| M | Market breadth | Missing | source-discovery TODO | none | Do not use ETF proxy breadth. Needs true breadth source/crawler. |
| M | VIX | Fully supported as current/trend evidence | yfinance/OHLCV | `market.trend`, `market.status US` | `market.trend` returns VIX current, SMA20/SMA50, trend, and state. |
| M | Macro indicators | Missing | unavailable | none | Out of current provider scope. |

## Example Commands

### Quote / Supply-Demand / Ownership Snapshot

```bash
finance market.quote NVDA --output compact \
  --fields last_price,market_cap,shares_outstanding,float_shares,average_volume,regular_market_volume,volume_vs_average,fifty_two_week_high,trailing_eps,profit_margins,operating_margins,return_on_equity,held_percent_institutions
```

Observed compact shape:

```text
NVDA|market_quote|last_price=215.33|market_cap=5215507972096|shares_outstanding=24221000000|float_shares=23222320000|average_volume=169915488|regular_market_volume=169275710|volume_vs_average=0.9962|fifty_two_week_high=236.54|trailing_eps=6.52|profit_margins=0.62966|operating_margins=0.65596|return_on_equity=1.14288|held_percent_institutions=0.70777|src=yfinance
```

### Current Earnings

```bash
finance calendar.earnings NVDA limit=4 --output compact --max-records 4
```

This gives recent and upcoming EPS estimates/reported EPS. It does not include revenue.

### Quarterly / Annual Fundamentals

```bash
finance fundamentals.statement NVDA statement=income period=quarterly provider=sec --output schema --max-records 6
finance fundamentals.statement NVDA statement=income period=annual provider=sec --output schema --max-records 12
finance fundamentals.metrics NVDA period=quarterly metrics=revenue,eps,net_income,operating_income,operating_margin,net_margin --output compact
finance fundamentals.growth NVDA metrics=revenue,eps,operating_margin,net_margin,roe periods=quarterly,annual years=5 --output compact
```

`fundamentals.metrics` is the agent-native latest-period path. `fundamentals.growth` is the reusable multi-period path for raw history, YoY, deltas, and CAGR rows. CAGR is for positive revenue/EPS start/end values; margins and ROE are comparison deltas, not CAGR rows.

### New Catalyst / Filings

```bash
finance filings.recent NVDA forms=8-K,10-Q,10-K limit=8 classify=true --output compact
```

This is one of the strongest outputs. It returns classified events such as earnings releases, financial exhibits, quarterly reports, annual reports, and executive changes.

### News

The GDELT-backed news provider has been removed because the public API consistently timed out. Recent news is now sourced from classified 8-K filings and earnings-call transcripts instead.

### Transcripts

```bash
finance transcripts.search NVDA limit=3 --output compact
```

This works well when Motley Fool transcript pages exist.

### Price / Breakout Context

```bash
finance price.moves NVDA window=1d years=1 threshold=5% limit=5 --output compact
finance price.performance NVDA benchmark=SPY periods=1M,3M,6M,1Y --output compact \
  --fields symbol_return_pct,benchmark_return_pct,relative_return_pct,distance_from_52w_high_pct
finance price.relative NVDA peers=AMD,AVGO,TSM periods=1M,3M,6M,1Y --output compact
finance price.relative NVDA sector_etfs=SMH benchmarks=SPY,QQQ periods=1M,3M --output compact
```

`price.moves` gives deterministic large-move dates. `price.performance` gives single-benchmark relative rows. `price.relative` compares against SPY/QQQ, an auto or explicit sector ETF, and explicit peers without sending raw OHLCV.

### Leader / Peer Context

```bash
finance industry.table semiconductors table=top_companies limit=5 --output schema
```

This gives peer names, symbols, ratings, and market weights. Use `price.relative peers=...` once the LLM/user has selected explicit comparison companies.

### Market Direction

```bash
finance market.status US --output schema
finance market.ohlcv NVDA,SPY,QQQ,DIA timeframe=1d limit=5 --output schema
finance market.trend US periods=1M,3M,6M,1Y --output compact
```

`market.status` is compact enough for current index/VIX context. `market.trend` is the preferred reusable primitive for index/VIX moving averages and return trend rows; use `market.ohlcv` only when the agent needs the underlying bars.

## Source-Discovery TODOs

1. Institutional sponsorship:
   - Ownership changes over time

2. Market breadth:
   - NYSE/Nasdaq advance-decline line
   - Percentage of stocks above 50/200 DMA
   - New highs/new lows
   - Up/down volume breadth

3. Macro indicators:
   - Decide which macro series belong in the CLI contract.
   - Identify free/open source APIs, datasets, or crawler targets.

Do not solve these basic gaps with paid-provider assumptions. If existing free/current providers cannot supply a field reliably, keep it documented as a source-discovery TODO until a suitable source is selected.

## Recommended Command Surface

Keep this practical and avoid a large CANSLIM mega-command. CANSLIM is one investment framework; FinanceCLI should expose reusable data primitives that an agent can combine across many frameworks.

Implemented small commands:

```text
price.performance SYMBOL [benchmark=SPY periods=1M,3M,6M,1Y]
fundamentals.metrics SYMBOL [period=quarterly metrics=revenue,eps,net_income,operating_income]
fundamentals.growth SYMBOL [metrics=revenue,eps periods=quarterly,annual years=5]
price.relative SYMBOL [benchmarks=SPY,QQQ peers=PEERS sector_etfs=SECTOR_ETFS periods=1M,3M,6M,1Y]
market.trend [MARKET=US] [periods=1M,3M,6M,1Y]
```

Potential future commands/options:

```text
ownership.changes SYMBOL
market.breadth MARKET=US
```

The implemented commands intentionally do not decide whether a stock passes CANSLIM. They only reduce token waste and row-selection errors for facts that many frameworks need.

## Output Format Assessment

| Format | Assessment |
|---|---|
| JSON | Best for programmatic use; sometimes verbose for LLM context. |
| compact | Best for event rows, quote snapshots, transcripts, filings, price moves. |
| schema | Good for row/table data; useful for statements and OHLCV, but statement rows still require calculation. |
| human table/text | Not the main strength; current project is more agent-oriented. |

## Validation Commands

Representative checks:

```bash
finance market.quote NVDA --output compact --fields last_price,market_cap,float_shares,volume_vs_average,fifty_two_week_high,return_on_equity,held_percent_institutions
finance ownership.holders NVDA limit=5 --output compact --fields section,breakdown,value,holder,shares,pct_held,pct_change
finance symbol.profile AAPL --output json
finance calendar.earnings TSLA limit=4 --output compact
finance fundamentals.metrics NVDA period=quarterly metrics=revenue,eps,net_income,operating_income,operating_margin,net_margin --output compact
finance fundamentals.growth NVDA metrics=revenue,eps,operating_margin,net_margin,roe periods=quarterly,annual years=5 --output compact
finance fundamentals.statement NVDA statement=income period=quarterly provider=sec --output schema --max-records 12
finance filings.recent NVDA forms=8-K,10-Q,10-K limit=8 classify=true --output compact
finance transcripts.search NVDA limit=3 --output compact
finance price.moves NVDA window=1d years=1 threshold=5% limit=5 --output compact
finance price.performance NVDA benchmark=SPY periods=1M,3M,6M,1Y --output compact
finance price.relative NVDA peers=AMD,AVGO,TSM periods=1M,3M,6M,1Y --output compact
finance industry.table semiconductors table=top_companies limit=5 --output schema
finance market.status US --output schema
finance market.trend US periods=1M,3M,6M,1Y --output compact
finance market.ohlcv NVDA,SPY,QQQ,DIA timeframe=1d limit=5 --output schema
```

Automated coverage includes:

- Yahoo quote normalization for CANSLIM fields.
- `symbol.profile` propagation of those quote fields.
- `fundamentals.metrics` provider delegation and compact rendering.
- `price.performance` benchmark-relative return math and compact rendering.
- `fundamentals.growth` history/growth calculations and compact rendering.
- `price.relative` auto sector ETF, explicit peer, and compact rendering.
- `market.trend` index/VIX trend evidence and compact rendering.
