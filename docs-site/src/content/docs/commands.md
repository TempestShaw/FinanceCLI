---
title: Commands
description: Generated command reference for Finance CLI.
---

# Commands

This page is generated from the Finance CLI command registry.

Run `python scripts/generate_cli_docs.py` after changing command metadata.

## `backtest.*`

### `backtest.describe`

Describe a backtest strategy and its parameters

**Usage**

```bash
finance backtest.describe STRATEGY
```

**Examples**

```bash
finance backtest.describe sma_cross
finance backtest.describe custom
```

### `backtest.factor.payload`

Build a normalized factor backtest payload

**Usage**

```bash
finance backtest.factor.payload FACTOR_NAME SYMBOLS START_DATE END_DATE [timeframe=1d top_pct=0.2 bottom_pct=0.2]
```

**Examples**

```bash
finance backtest.factor.payload rsi_14 AAPL,MSFT,NVDA 2024-01-01 2024-12-31
```

### `backtest.factor.weights`

Preview quantile factor target weights

**Usage**

```bash
finance backtest.factor.weights FACTOR_NAME scores='{"AAPL":1.2,"MSFT":0.4}' [top_pct=0.2 bottom_pct=0.2]
```

**Examples**

```bash
finance backtest.factor.weights rsi_14 scores='{"AAPL":1.1,"MSFT":0.3,"NVDA":2.0}'
```

### `backtest.run`

Run a VectorBT strategy backtest

**Usage**

```bash
finance backtest.run STRATEGY SYMBOLS START_DATE END_DATE [params='{}' strategy_file=./rule.py]
```

**Examples**

```bash
finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31 fast=20 slow=100
finance backtest.run custom AAPL 2020-01-01 2024-12-31 strategy_file=./rule.py params='{}'
```

### `backtest.strategies`

List VectorBT-backed strategy presets

**Usage**

```bash
finance backtest.strategies
```

**Examples**

```bash
finance backtest.strategies
```

### `backtest.strategy.payload`

Build a normalized strategy backtest payload

**Usage**

```bash
finance backtest.strategy.payload STRATEGY_ID START_DATE END_DATE [initial_cash=100000 parameters='{}']
```

**Examples**

```bash
finance backtest.strategy.payload mean_reversion 2024-01-01 2024-12-31
```

### `backtest.tune`

Run a bounded VectorBT parameter grid

**Usage**

```bash
finance backtest.tune STRATEGY SYMBOLS START_DATE END_DATE grid='{}' [metric=sharpe_ratio max_runs=100]
```

**Examples**

```bash
finance backtest.tune sma_cross AAPL 2020-01-01 2024-12-31 grid='{"fast":[10,20],"slow":[50,100]}'
```

## `document.*`

### `document.ocr`

Run PaddleOCR/PP-StructureV3 OCR fallback on a local or remote document

**Usage**

```bash
finance document.ocr SOURCE|source=PATH_OR_URL [max_chars=12000 max_pages=5]
```

**Examples**

```bash
finance document.ocr ./deck.pdf max_pages=3
finance document.ocr url=https://example.com/deck.pdf max_chars=4000
```

**Notes**

- Prefer document.read or document.scan for text-based PDFs.
- Uses the default Finance CLI OCR stack.
- Use as fallback for scanned or image-heavy documents.

### `document.read`

Extract native PDF or HTML text and layout/search blocks

**Usage**

```bash
finance document.read SOURCE|source=PATH_OR_URL [format=pdf|html max_chars=12000 max_pages=5]
```

**Examples**

```bash
finance document.read ./deck.pdf max_pages=3
finance document.read url=https://example.com/deck.pdf max_chars=4000
finance document.read url=https://www.sec.gov/.../filing.htm format=html max_chars=4000
```

**Notes**

- Lightweight first-pass parser for text-based PDFs and HTML filings; does not run OCR.
- Returns page text plus positioned or offset-bearing blocks for downstream matching or agent analysis.

### `document.scan`

Scan document text/layout for configured topics or literal queries with RapidFuzz

**Usage**

```bash
finance document.scan SOURCE|source=PATH_OR_URL [query=... topics=risk,disclosure format=pdf|html match=fuzzy|all_terms threshold=80 max_chars=12000 max_pages=5 limit=50 window=0 start_char=0 end_char=0]
```

**Examples**

```bash
finance document.scan ./report.pdf topics=risk,financial_reporting
finance document.scan ./deck.pdf topics=guidance threshold=75 max_pages=10
finance document.scan url=https://www.sec.gov/.../filing.htm format=html query='Operating lease costs' max_chars=0 window=1200
finance document.scan url=https://www.sec.gov/.../filing.htm format=html match=all_terms threshold=100 query='Receivables net Total current assets' max_chars=0
finance document.scan url=https://www.sec.gov/.../filing.htm format=html start_char=122000 query='Accounts payable'
```

**Notes**

- Uses PyMuPDF for native PDF layout, BeautifulSoup for HTML text, and RapidFuzz for deterministic fuzzy matching.
- Known topics include disclosure, risk, financial_reporting, portfolio, and guidance.
- Unknown topics are treated as literal fuzzy queries.
- Use match=all_terms threshold=100 for table-style queries where every meaningful query word should appear.
- Use start_char/end_char to restrict a follow-up scan to a known section or window.
- HTML matches include char offsets and match IDs that can be passed to document.window.

### `document.tables`

Extract compact table previews from text-based PDFs with Camelot

**Usage**

```bash
finance document.tables SOURCE|source=PATH_OR_URL [pages=1-end flavor=stream|lattice max_tables=20 max_rows=25]
```

**Examples**

```bash
finance document.tables ./report.pdf pages=10-12 flavor=stream
finance document.tables ./filing.pdf pages=all max_tables=5 max_rows=10
```

**Notes**

- Uses the default Finance CLI table extraction stack.
- Use flavor=stream for whitespace-separated tables and flavor=lattice for ruled-line tables.
- Returns compact row previews with page, shape, accuracy, and truncation metadata.

### `document.window`

Read a bounded text window around a document offset or scan match ID

**Usage**

```bash
finance document.window SOURCE|source=PATH_OR_URL [format=pdf|html start_char=0|match_id=char_START_END chars=4000 direction=around|next|previous]
```

**Examples**

```bash
finance document.window url=https://www.sec.gov/.../filing.htm format=html start_char=52000 chars=4000
finance document.window url=https://www.sec.gov/.../filing.htm format=html match_id=char_52000_52200 direction=next chars=4000
```

**Notes**

- Designed for follow-up reading after document.scan.
- Use direction=next or direction=previous to move through a table or section without re-scanning.

## `estimates.*`

### `estimates.compare`

Compare user assumptions against explicit consensus inputs

**Usage**

```bash
finance estimates.compare [SYMBOL] revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027
```

**Examples**

```bash
finance estimates.compare IOT revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027
```

**Notes**

- No network calls. Compares only values explicitly supplied by the user or agent.

### `estimates.consensus`

Fetch FMP analyst consensus estimates when configured

**Usage**

```bash
finance estimates.consensus SYMBOL [period=annual|quarter limit=10 page=0]
```

**Examples**

```bash
finance estimates.consensus IOT period=annual limit=5
```

**Notes**

- Requires FMP_API_KEY. Makes one short FMP request and returns a structured configuration error when unconfigured.

## `filings.*`

### `filings.read`

Read a canonical 10-K section with edgartools

**Usage**

```bash
finance filings.read [SYMBOL] [accession=...|url=...] [form=10-K section=business|risk_factors|mda|segments max_chars=8000]
```

**Examples**

```bash
finance filings.read IOT section=business max_chars=3000
finance filings.read accession=0001628280-26-018167 section=risk_factors max_chars=3000
finance filings.read url=https://www.sec.gov/Archives/edgar/data/1642896/000162828026018167/iot-20260131.htm section=mda
```

**Notes**

- Uses edgartools for filing retrieval, then returns bounded text for CLI/agent consumption.

### `filings.recent`

Fetch recent SEC filings, optionally classified

**Usage**

```bash
finance filings.recent SYMBOL [forms=8-K,10-Q limit=20 classify=false]
```

**Examples**

```bash
finance filings.recent NVDA forms=10-Q,8-K limit=5
finance filings.recent NVDA forms=8-K limit=10 classify=true
```

### `filings.report`

Read an edgartools filing summary report

**Usage**

```bash
finance filings.report [SYMBOL] [accession=...|url=...] name='Report Short Name' [form=10-K query=... max_rows=25 (0=unlimited) max_chars=8000]
```

**Examples**

```bash
finance filings.report COST name='Consolidated Balance Sheets (Parenthetical)'
finance filings.report COST name='Leases, Supplemental Balance Sheet Information' query='operating lease liabilities'
finance filings.report url=https://www.sec.gov/Archives/edgar/data/909832/000090983224000049/cost-20240901.htm name='Debt'
```

### `filings.reports`

List edgartools filing summary reports

**Usage**

```bash
finance filings.reports [SYMBOL] [accession=...|url=...] [form=10-K query=lease]
```

**Examples**

```bash
finance filings.reports COST form=10-K
finance filings.reports COST form=10-K query=lease
finance filings.reports url=https://www.sec.gov/Archives/edgar/data/909832/000090983224000049/cost-20240901.htm
```

### `filings.sections`

List supported and discovered filing sections

**Usage**

```bash
finance filings.sections [SYMBOL] [accession=...|url=...] [form=10-K]
```

**Examples**

```bash
finance filings.sections IOT form=10-K
finance filings.sections accession=0001628280-26-018167
```

### `filings.statement`

Read structured XBRL statement rows with edgartools

**Usage**

```bash
finance filings.statement [SYMBOL] [accession=...|url=...] [form=10-K statement=income|balance|cashflow query=... max_rows=0]
```

**Examples**

```bash
finance filings.statement COST statement=balance query='Common Stock'
finance filings.statement url=https://www.sec.gov/Archives/edgar/data/909832/000090983224000049/cost-20240901.htm statement=income max_rows=20
```

**Notes**

- Returns raw XBRL values plus reported values scaled by XBRL decimals.

## `formula.*`

### `formula.adjusted_ebitda`

Calculate adjusted EBITDA from explicit addbacks

**Usage**

```bash
finance formula.adjusted_ebitda ebit=9285 d_and_a=2237 addbacks=284,163
```

**Examples**

```bash
finance formula.adjusted_ebitda ebit=9285 d_and_a=2237 addbacks=284,163
```

### `formula.cagr`

Calculate compound annual growth rate

**Usage**

```bash
finance formula.cagr start=100 end=150 periods=3
```

**Examples**

```bash
finance formula.cagr start=100 end=150 periods=3
```

### `formula.capm`

Calculate CAPM cost of equity

**Usage**

```bash
finance formula.capm risk_free=4.617% beta=0.79 market_return=11%
```

**Examples**

```bash
finance formula.capm risk_free=4.617% beta=0.79 market_return=11%
```

### `formula.days`

Calculate average-balance days

**Usage**

```bash
finance formula.days current=2721 prior=2285 denominator=254453 [days=365]
```

**Examples**

```bash
finance formula.days current=2721 prior=2285 denominator=254453
```

### `formula.ebitda`

Calculate EBITDA from explicit EBIT and D&A inputs

**Usage**

```bash
finance formula.ebitda ebit=9285 d_and_a=2237
```

**Examples**

```bash
finance formula.ebitda ebit=9285 d_and_a=2237
```

### `formula.enterprise_value`

Calculate enterprise value with explicit operating cash

**Usage**

```bash
finance formula.enterprise_value market_equity=418856 debt=11415 cash=11144 operating_cash=5089
```

**Examples**

```bash
finance formula.enterprise_value market_equity=418856 debt=11415 cash=11144 operating_cash=5089
```

### `formula.lease_equivalent`

Estimate lease equivalent from cost ratio

**Usage**

```bash
finance formula.lease_equivalent base_liability=2554 variable_cost=163 operating_cost=284
```

**Examples**

```bash
finance formula.lease_equivalent base_liability=2554 variable_cost=163 operating_cost=284
```

### `formula.margin`

Calculate numerator / denominator

**Usage**

```bash
finance formula.margin numerator=11969 denominator=254453
```

**Examples**

```bash
finance formula.margin numerator=11969 denominator=254453
```

### `formula.net_debt`

Calculate net debt with explicit operating cash

**Usage**

```bash
finance formula.net_debt debt=11415 cash=11144 [operating_cash=5089]
```

**Examples**

```bash
finance formula.net_debt debt=11415 cash=11144 operating_cash=5089
```

### `formula.operating_cash`

Calculate operating cash as min(percent of revenue, cash-like assets)

**Usage**

```bash
finance formula.operating_cash revenue=254453 cash_like_assets=11144 [percent_revenue=2%]
```

**Examples**

```bash
finance formula.operating_cash revenue=254453 cash_like_assets=11144 percent_revenue=2%
```

### `formula.operating_current_assets`

Calculate operating current assets

**Usage**

```bash
finance formula.operating_current_assets current_assets=34246 [cash_like_assets=11144 operating_cash=5089]
```

**Examples**

```bash
finance formula.operating_current_assets current_assets=34246 cash_like_assets=11144 operating_cash=5089
```

### `formula.operating_current_liabilities`

Calculate operating current liabilities

**Usage**

```bash
finance formula.operating_current_liabilities current_liabilities=35464 [interest_bearing_current_debt=103]
```

**Examples**

```bash
finance formula.operating_current_liabilities current_liabilities=35464 interest_bearing_current_debt=103
```

### `formula.roic`

Calculate ROIC from NOPAT and invested capital

**Usage**

```bash
finance formula.roic nopat=7113 invested_capital=28077
```

**Examples**

```bash
finance formula.roic nopat=7113 invested_capital=28077
```

### `formula.turnover`

Calculate turnover using average balance

**Usage**

```bash
finance formula.turnover numerator=222358 current=18647 prior=16651
```

**Examples**

```bash
finance formula.turnover numerator=222358 current=18647 prior=16651
```

### `formula.wacc`

Calculate WACC with explicit debt tax convention

**Usage**

```bash
finance formula.wacc equity_value=418856 debt_value=11415 cost_of_equity=9.66% cost_of_debt=6% tax_rate=24% debt_tax=pretax|after_tax
```

**Examples**

```bash
finance formula.wacc equity_value=418856 debt_value=11415 cost_of_equity=9.66% cost_of_debt=6% tax_rate=24% debt_tax=pretax
```

### `formula.working_capital`

Calculate operating working capital

**Usage**

```bash
finance formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035
```

**Examples**

```bash
finance formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035
```

## `fundamentals.*`

### `fundamentals.statement`

Fetch income/balance/cashflow statement data

**Usage**

```bash
finance fundamentals.statement SYMBOL [statement=income|balance|cashflow period=annual|quarterly]
```

**Examples**

```bash
finance fundamentals.statement NVDA statement=income period=quarterly
```

## `ir.*`

### `ir.presentations`

Discover IR and investor day presentations from SEC 8-K Exhibit 99 filings

**Usage**

```bash
finance ir.presentations SYMBOL [limit=20 source=auto|sec|company_ir|all]
```

**Examples**

```bash
finance ir.presentations IOT
finance ir.presentations IOT limit=10 source=all
finance ir.presentations NVDA limit=5 source=sec
```

**Notes**

- Scans recent 8-K filings for Exhibit 99 files with presentation or slides keywords.
- source=auto uses SEC first, then company IR fallback when SEC finds no candidates.
- source=all combines SEC and company IR candidates.
- Press releases and earnings releases are filtered unless a distinct deck/slides signal is present.
- confidence: high = strong presentation signal, medium = weaker or conflicting signal.
- kind: investor_day | earnings_presentation | ir_presentation | exhibit_99
- Use ir.read url=URL to extract text from a candidate.

### `ir.read`

Extract text from an IR presentation exhibit URL

**Usage**

```bash
finance ir.read url=URL [max_chars=12000 ocr=off|auto|force]
```

**Examples**

```bash
finance ir.read url=https://www.sec.gov/Archives/edgar/data/.../iot_investorday.htm
finance ir.read url=https://www.sec.gov/Archives/edgar/data/.../deck.htm max_chars=20000
finance ir.read url=https://example.com/deck.pdf ocr=auto max_chars=4000
```

**Notes**

- HTML exhibits/pages are fetched and parsed to plain text.
- PDF extraction uses pypdf and returns page-level text when possible.
- ocr=auto or ocr=force uses the default PaddleOCR/PP-StructureV3 stack.
- Pass the url from ir.presentations output.

## `kpi.*`

### `kpi.extract`

Extract KPI evidence from filings or transcripts

**Usage**

```bash
finance kpi.extract SYMBOL [source=transcripts|filings|both metrics=arr,nrr limit=30 quarter=latest form=10-K]
```

**Examples**

```bash
finance kpi.extract IOT source=transcripts metrics=arr,net_new_arr,large_customers,nrr
finance kpi.extract IOT source=both metrics=arr,emerging_products,rpo limit=20
```

**Notes**

- Returns evidence rows, not investment conclusions.

### `kpi.history`

Extract KPI evidence across recent transcripts

**Usage**

```bash
finance kpi.history SYMBOL [source=transcripts metrics=arr,nrr limit=4 per_document_limit=20]
```

**Examples**

```bash
finance kpi.history IOT metrics=arr,large_customers,emerging_products limit=4
```

## `market.*`

### `market.ohlcv`

Fetch normalized OHLCV records for one or more symbols

**Usage**

```bash
finance market.ohlcv SYMBOL[,SYMBOL...] [timeframe=1d start_date=YYYY-MM-DD end_date=YYYY-MM-DD limit=200 provider=auto include_attempts=false]
```

**Examples**

```bash
finance market.ohlcv NVDA timeframe=1d limit=20
finance market.ohlcv AAPL,MSFT,NVDA timeframe=1d limit=5 provider=auto
```

**Notes**

- Arguments use key=value for LLM-friendly calling.

### `market.quote`

Fetch quote via the best available provider

**Usage**

```bash
finance market.quote SYMBOL
```

**Examples**

```bash
finance market.quote NVDA
```

**Notes**

- Uses Alpha Vantage when configured, with Yahoo fallback.

### `market.regime`

Show market regime context

**Usage**

```bash
finance market.regime [MARKET=US] [TIMEFRAME=swing]
```

**Examples**

```bash
finance market.regime US swing
```

### `market.sector_heat`

Show sector heat rankings

**Usage**

```bash
finance market.sector_heat [MARKET=US] [LOOKBACK_DAYS=20] [GROUP_BY=sector]
```

**Examples**

```bash
finance market.sector_heat US 20 sector
```

## `news.*`

### `news.analyze`

Analyze news volume, tone, context, or geography

**Usage**

```bash
finance news.analyze analysis=timeline|tone|context|geo|doc [query=TEXT | symbol=SYMBOL | sector=SECTOR] [mode=MODE max_records=50 timespan=30D|1W|1M|24H date=YYYY-MM-DD start_date=YYYY-MM-DD end_date=YYYY-MM-DD start_datetime=YYYYMMDDHHMMSS end_datetime=YYYYMMDDHHMMSS]
```

**Examples**

```bash
finance news.analyze symbol=NVDA analysis=timeline timespan=1d
finance news.analyze symbol=NVDA analysis=timeline timespan=1M
finance news.analyze query='NVIDIA export controls' analysis=context max_records=5 timespan=24h
finance news.analyze symbol=IOT analysis=timeline start_date=2026-03-03 end_date=2026-03-09
finance news.analyze query=FOOD_SECURITY analysis=geo max_records=3 timespan=1h
```

**Notes**

- Use this only when you need trend, tone, context, geo, or raw DOC analysis.
- Use timespan for relative lookback from now, such as 30D, 1W, 1M, 24H, or 90min.
- date/start_date/end_date are preferred for humans and agents; datetime inputs are optional precision controls.

### `news.search`

Search finance news through GDELT

**Usage**

```bash
finance news.search [query=TEXT | symbol=SYMBOL | sector=SECTOR] [max_records=50 timespan=30D|1W|1M|24H date=YYYY-MM-DD start_date=YYYY-MM-DD end_date=YYYY-MM-DD start_datetime=YYYYMMDDHHMMSS end_datetime=YYYYMMDDHHMMSS]
```

**Examples**

```bash
finance news.search symbol=NVDA max_records=5
finance news.search symbol=NVDA timespan=30D max_records=10
finance news.search symbol=NVDA timespan=1W max_records=10
finance news.search query='NVIDIA export controls' timespan=24h
finance news.search symbol=IOT date=2026-03-06 max_records=5
finance news.search symbol=IOT start_date=2026-03-03 end_date=2026-03-09 max_records=5
```

**Notes**

- Use date for one full day, or start_date/end_date for a full-day range.
- Use timespan for relative lookback from now, such as 30D, 1W, 1M, 24H, or 90min.
- Use start_datetime/end_datetime only when you need second-level precision.
- Use either timespan or fixed date/date-time inputs, not both.

## `price.*`

### `price.context`

Return a source-linked evidence timeline around a date

**Usage**

```bash
finance price.context SYMBOL date=YYYY-MM-DD [lookback=3D news_limit=5 filing_limit=80 transcript_limit=12]
```

**Examples**

```bash
finance price.context IOT date=2026-03-06 lookback=3D
finance price.context NVDA date=2025-01-27 lookback=2D news_limit=5
finance price.context IOT date=2026-03-06 lookback=1W news_limit=5
```

**Notes**

- lookback is calendar time around date: 3D=3 calendar days before and after, 1W=7 calendar days, 1M=30 calendar days.
- Timeline roles are temporal only: before_move, same_day, after_move.
- Event/publication dates are explicit to avoid implied causal claims.

### `price.moves`

Find large deterministic close-to-close stock moves

**Usage**

```bash
finance price.moves SYMBOL [window=1d|3d|1w|1m years=3 threshold=8|8% limit=20 provider=auto]
```

**Examples**

```bash
finance price.moves IOT years=3 threshold=8% limit=10
finance price.moves NVDA window=3d years=2 threshold=12%
finance price.moves NVDA window=1w years=2 threshold=15 limit=10
```

**Notes**

- window is a trading-day window: 1d=1 trading day, 1w=5 trading days, 1m=21 trading days.
- threshold accepts decimal or percentage-point inputs: 0.08, 8, and 8% all mean 8%.
- Uses one OHLCV fetch and deterministic close-to-close math.
- Returns move dates and magnitude only; it does not infer causality.

## `research.*`

### `research.plan`

Return a deterministic research command checklist

**Usage**

```bash
finance research.plan SYMBOL [style=fundamental]
```

**Examples**

```bash
finance research.plan IOT style=fundamental
```

**Notes**

- This returns suggested commands only; it does not execute research or form conclusions.
- Use this as a navigation layer for humans or LLM agents.

## `sources.*`

### `sources.list`

List finance data sources and capabilities

**Usage**

```bash
finance sources.list
```

**Examples**

```bash
finance sources.list
```

**Notes**

- No network calls; reports known providers and capabilities.

### `sources.status`

Show package and environment configuration for data sources

**Usage**

```bash
finance sources.status
```

**Examples**

```bash
finance sources.status
```

**Notes**

- No network calls; use sources.test for live provider probes.

### `sources.test`

Run small live probes against one or all data sources

**Usage**

```bash
finance sources.test [SOURCE|source=SOURCE] [symbol=AAPL timeout=30]
```

**Examples**

```bash
finance sources.test yahoo symbol=AAPL
finance sources.test sec symbol=AAPL
finance sources.test source=all symbol=AAPL timeout=30
```

**Notes**

- Makes real provider calls and returns pass/fail plus latency.

## `symbol.*`

### `symbol.profile`

Show real quote and SEC company metadata for a symbol

**Usage**

```bash
finance symbol.profile SYMBOL
```

**Examples**

```bash
finance symbol.profile IOT
```

**Notes**

- Uses yfinance for market metadata and SEC ticker metadata for CIK/company identity.

### `symbol.snapshot`

Show real quote and company metadata for a symbol

**Usage**

```bash
finance symbol.snapshot SYMBOL
```

**Examples**

```bash
finance symbol.snapshot NVDA
```

## `transcripts.*`

### `transcripts.qa`

Extract analyst Q&A pairs from a transcript

**Usage**

```bash
finance transcripts.qa [SYMBOL] [url=...] [quarter=latest limit=10]
```

**Examples**

```bash
finance transcripts.qa IOT quarter=latest limit=5
```

### `transcripts.read`

Read a transcript and split prepared remarks / Q&A

**Usage**

```bash
finance transcripts.read [SYMBOL] [url=...] [quarter=latest max_chars=12000 include_turns=false]
```

**Examples**

```bash
finance transcripts.read IOT quarter=latest max_chars=4000
finance transcripts.read IOT include_turns=true max_chars=2000
finance transcripts.read url=https://www.fool.com/earnings/call-transcripts/2026/03/05/samsara-iot-q4-2026-earnings-call-transcript/
```

### `transcripts.search`

Search public earnings-call transcripts

**Usage**

```bash
finance transcripts.search SYMBOL [limit=4 debug=false]
```

**Examples**

```bash
finance transcripts.search IOT limit=4
finance transcripts.search IOT debug=true
```

**Notes**

- First provider is public Motley Fool transcript pages.

## `valuation.*`

### `valuation.dcf`

Calculate DCF enterprise value from forecast cash flows

**Usage**

```bash
finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% [terminal_growth=3%|exit_multiple=15]
```

**Examples**

```bash
finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% terminal_growth=3%
finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% exit_multiple=15
```

**Notes**

- Pass forecast FCF only; do not include an initial t=0 investment cash flow.
- Forecast cash flows are discounted from t=1.
- Use either terminal_growth or exit_multiple, not both.

### `valuation.irr`

Calculate IRR for periodic cash flows

**Usage**

```bash
finance valuation.irr cashflows=-100M,30M,40M,50M
```

**Examples**

```bash
finance valuation.irr cashflows=-100M,30M,40M,50M
```

**Notes**

- Cash flows are periodic; returns null with a warning when no IRR solution is bracketed.

### `valuation.multiples`

Calculate current sales multiples from market cap and revenue

**Usage**

```bash
finance valuation.multiples SYMBOL
```

**Examples**

```bash
finance valuation.multiples IOT
```

**Notes**

- Deterministic math only; does not judge whether the multiple is fair.

### `valuation.npv`

Calculate NPV for periodic cash flows

**Usage**

```bash
finance valuation.npv cashflows=-100M,30M,40M,50M discount_rate=10%
```

**Examples**

```bash
finance valuation.npv cashflows=-100M,30M,40M,50M discount_rate=10%
```

**Notes**

- First cash flow is treated as t=0. Use this for project-level NPV including initial investment.

### `valuation.scenario`

Build a simple bull/base/bear sales-multiple scenario table

**Usage**

```bash
finance valuation.scenario SYMBOL revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 [shares=580M]
```

**Examples**

```bash
finance valuation.scenario IOT revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 shares=580M
finance valuation.scenario IOT revenue=2200000000 bear_multiple=7 base_multiple=10 bull_multiple=13
```

**Notes**

- Uses current quote for price/share count when available; assumptions remain user-supplied.
- Revenue and shares accept raw numbers or K/M/B suffixes.

### `valuation.wacc`

Calculate weighted average cost of capital

**Usage**

```bash
finance valuation.wacc equity_value=10B debt_value=1B cost_of_equity=10% cost_of_debt=5% tax_rate=21%
```

**Examples**

```bash
finance valuation.wacc equity_value=10B debt_value=1B cost_of_equity=10% cost_of_debt=5% tax_rate=21%
```

**Notes**

- Formula: E/(D+E)*Re + D/(D+E)*Rd*(1-tax). Inputs are user-supplied.
