# Finance CLI Examples

This file keeps practical command examples out of the README. Run `finance help <namespace>` or `finance <command> --help` for command-specific usage.

## Install Checks

```bash
finance --list
finance sources.status
```

```bash
finance sources.test yahoo symbol=AAPL
finance sources.test sec symbol=AAPL
```

## Public-Company Research Flow

```bash
finance research.plan IOT style=fundamental
finance symbol.profile IOT
finance filings.recent IOT forms=10-K,10-Q,8-K limit=10 classify=true
finance transcripts.search IOT limit=4
finance kpi.history IOT metrics=arr,large_customers,emerging_products limit=4
finance price.moves IOT years=3 threshold=8% limit=10
```

## SEC Filings

```bash
finance filings.recent NVDA forms=10-Q,8-K limit=5
finance filings.sections IOT form=10-K
finance filings.read IOT section=business max_chars=3000
finance filings.read accession=0001628280-26-018167 section=risk_factors max_chars=3000
finance filings.read url=https://www.sec.gov/Archives/edgar/data/1642896/000162828026018167/iot-20260131.htm section=mda
```

## Filing Statements And Reports

```bash
finance filings.statement COST statement=balance query="Common Stock"
finance filings.statement url=https://www.sec.gov/Archives/edgar/data/909832/000090983224000049/cost-20240901.htm statement=income max_rows=20
finance filings.reports COST form=10-K query=lease
finance filings.report COST name="Consolidated Balance Sheets (Parenthetical)"
finance filings.report COST name="Leases, Supplemental Balance Sheet Information" query="operating lease liabilities"
```

Use `filings.statement` or `filings.report` when EDGAR/XBRL structure is available. Use `document.scan` and `document.window` when you need to inspect arbitrary filing text.

## Document Reading

```bash
finance document.read ./deck.pdf max_pages=3
finance document.read url=https://example.com/deck.pdf max_chars=4000
finance document.read url=https://www.sec.gov/.../filing.htm format=html max_chars=4000

finance document.scan ./report.pdf topics=risk,financial_reporting
finance document.scan ./deck.pdf topics=guidance threshold=75 max_pages=10
finance document.scan url=https://www.sec.gov/.../filing.htm format=html query="Operating lease costs" max_chars=0 window=1200
finance document.scan url=https://www.sec.gov/.../filing.htm format=html match=all_terms threshold=100 query="Receivables net Total current assets" max_chars=0
finance document.window url=https://www.sec.gov/.../filing.htm format=html match_id=char_52000_52200 direction=next chars=4000
```

Optional table and OCR commands:

```bash
finance document.tables ./report.pdf pages=10-12 flavor=stream
finance document.tables ./filing.pdf pages=all max_tables=5 max_rows=10
finance document.ocr ./deck.pdf max_pages=3
```

## Market Data And News Context

```bash
finance market.quote NVDA
finance market.ohlcv NVDA timeframe=1d limit=20
finance market.ohlcv AAPL,MSFT,NVDA timeframe=1d limit=5 provider=auto
finance market.regime US swing
finance market.sector_heat US 20 sector

finance news.search symbol=NVDA timespan=30D max_records=10
finance news.search query="NVIDIA export controls" timespan=24h
finance news.analyze symbol=NVDA analysis=timeline timespan=1M
finance price.context NVDA date=2025-01-27 lookback=2D news_limit=5
```

## Transcripts, KPIs, And IR

```bash
finance transcripts.search IOT limit=4
finance transcripts.read IOT quarter=latest max_chars=4000
finance transcripts.read IOT include_turns=true max_chars=2000
finance transcripts.qa IOT quarter=latest limit=5

finance kpi.extract IOT source=transcripts metrics=arr,net_new_arr,large_customers,nrr
finance kpi.extract IOT source=both metrics=arr,emerging_products,rpo limit=20
finance kpi.history IOT metrics=arr,large_customers,emerging_products limit=4

finance ir.presentations IOT limit=10 source=all
finance ir.presentations NVDA limit=5 source=sec
finance ir.read url=https://example.com/deck.pdf ocr=auto max_chars=4000
```

## Valuation And Finance Math

```bash
finance valuation.multiples IOT
finance valuation.scenario IOT revenue=2.2B bear_multiple=7 base_multiple=10 bull_multiple=13 shares=580M
finance valuation.npv cashflows=-100M,30M,40M,50M discount_rate=10%
finance valuation.irr cashflows=-100M,30M,40M,50M
finance valuation.wacc equity_value=10B debt_value=1B cost_of_equity=10% cost_of_debt=5% tax_rate=21%
finance valuation.dcf cashflows=100M,120M,140M discount_rate=10% terminal_growth=3%

finance formula.ebitda ebit=9285 d_and_a=2237
finance formula.adjusted_ebitda ebit=9285 d_and_a=2237 addbacks=284,163
finance formula.margin numerator=11969 denominator=254453
finance formula.days current=2721 prior=2285 denominator=254453
finance formula.turnover numerator=222358 current=18647 prior=16651
finance formula.roic nopat=7113 invested_capital=28077
finance formula.cagr start=100 end=150 periods=3
finance formula.net_debt debt=11415 cash=11144 operating_cash=5089
finance formula.working_capital operating_current_assets=28191 operating_current_liabilities=35035
```

## Estimates

```bash
finance estimates.compare IOT revenue=2.2B consensus_revenue=2.0B eps=0.50 consensus_eps=0.45 fiscal_year=2027
finance estimates.consensus IOT period=annual limit=5
```

`estimates.consensus` requires `FMP_API_KEY`. FMP means Financial Modeling Prep, a third-party financial-data provider.

## Backtesting

```bash
finance backtest.strategies
finance backtest.describe sma_cross
finance backtest.run sma_cross AAPL 2020-01-01 2024-12-31 fast=20 slow=100
finance backtest.tune sma_cross AAPL 2020-01-01 2024-12-31 grid='{"fast":[10,20],"slow":[50,100]}'
```

Custom strategy files are supported when built-in presets are not enough:

```bash
finance backtest.describe custom
finance backtest.run custom AAPL 2020-01-01 2024-12-31 strategy_file=./rule.py params='{}'
```

Factor payload helpers:

```bash
finance backtest.strategy.payload mean_reversion 2024-01-01 2024-12-31
finance backtest.factor.payload rsi_14 AAPL,MSFT,NVDA 2024-01-01 2024-12-31
finance backtest.factor.weights rsi_14 scores='{"AAPL":1.1,"MSFT":0.3,"NVDA":2.0}'
```

## Output Format

The CLI defaults to JSON for agent-friendly use. Add `--output text` when reading manually:

```bash
finance --output text sources.status
finance --output json formula.margin numerator=10 denominator=20
```
