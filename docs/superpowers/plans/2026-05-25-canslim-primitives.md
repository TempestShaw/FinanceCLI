# CANSLIM Primitives Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make FinanceCLI strong enough for LLM-composed CANSLIM research without adding a CANSLIM-specific command or fixed workflow.

**Architecture:** Add small reusable primitives for fundamental growth, relative price strength, and market trend evidence. Keep missing data honest: do not use paid providers, do not fake market breadth, and document unresolved source gaps as TODOs for future crawler/open-source source discovery.

**Tech Stack:** Python CLI command registry, yfinance/OHLCV data already available through `HistoricalMarketDataService`, SEC/edgartools financial statement access, compact/schema record adapters, generated `tools.json` / `openapi.json` / `llms.txt`.

---

## Decisions Locked

- Do not add `canslim.*`, `research.canslim`, `canslim.snapshot`, or any fixed checklist command.
- Add reusable primitives that an LLM can compose freely.
- Do not use paid providers for basic support.
- If a free/current source cannot support a field, document the gap and acceptance criteria for future source discovery.
- Do not implement a market breadth proxy.
- `price.relative` auto-adds a sector ETF from existing Yahoo sector metadata and `SECTOR_ETFS["US"]`; explicit `sector_etfs=` replaces auto sector ETF.
- `price.relative` defaults to `benchmarks=SPY,QQQ`, auto sector ETF, and no peers.
- Peer comparison is explicit-only through `peers=...`.
- `fundamentals.growth` returns raw values plus calculated growth rows.
- EPS should prefer reported diluted EPS when available, then fall back to `net_income / diluted_shares`; always label the method.
- New primitives must support compact output and generated agent-facing metadata.

## Success Criteria

- `finance fundamentals.growth NVDA periods=quarterly,annual years=5 --output compact` returns history and growth rows for revenue, EPS, margins, and ROE where data exists.
- `finance price.relative NVDA peers=AMD,AVGO periods=1M,3M,6M,1Y --output compact` returns relative rows against `SPY`, `QQQ`, auto sector ETF, and explicit peers.
- `finance price.relative NVDA sector_etfs=SMH --output compact` uses `SMH` instead of auto `XLK`.
- `finance market.trend US --output compact` returns trend rows for `SPY`, `QQQ`, `DIA`, `IWM`, and `^VIX`, including 50/200 DMA and returns.
- No command claims true market breadth or ownership-change support.
- `tools.json`, `openapi.json`, `llms.txt`, and docs-site public copies include the new commands after generation.
- Focused tests and full local test suite pass.

## File Structure

- Modify `finance_cli/services/fundamentals.py`: add `fundamentals_growth()` and local helpers for raw period extraction, YoY, CAGR, EPS method labeling.
- Modify `finance_cli/cli/commands/fundamentals.py`: register `fundamentals.growth`.
- Modify `finance_cli/services/market_data.py`: add `relative_price_performance()` and `market_trend()`.
- Modify `finance_cli/cli/commands/price.py`: register `price.relative`.
- Modify `finance_cli/cli/commands/market.py`: register `market.trend`.
- Modify `finance_cli/records.py`: add adapters for `fundamentals.growth`, `price.relative`, and `market.trend`.
- Modify `finance_cli/tools/research/market_data.py` and `finance_cli/tools/research/price.py`: expose LLM tool wrappers if the current tool pattern supports these primitives.
- Modify `tests/test_finance_architecture.py`: service and registry tests.
- Modify `tests/test_agent_records.py`: compact rendering tests.
- Modify `tests/test_cli_smoke.py`: generated schema/metadata tests if needed.
- Modify `docs/canslim-coverage.md`: update support matrix and TODO/source-gap list.
- Regenerate `tools.json`, `openapi.json`, `llms.txt`, `docs-site/public/*`, and schema artifacts with `python scripts/generate_cli_docs.py`.

---

### Task 1: Fundamental Growth Service

**Files:**
- Modify: `finance_cli/services/fundamentals.py`
- Test: `tests/test_finance_architecture.py`

- [ ] **Step 1: Write failing tests for annual history, YoY, CAGR, and EPS method**

Add tests using a fake provider so no network is required:

```python
def test_fundamentals_growth_returns_raw_history_yoy_and_cagr():
    class Provider:
        def financial_statement(self, symbol, *, statement, period):
            assert statement == "income"
            if period == "annual":
                return {
                    "symbol": symbol.upper(),
                    "statement": statement,
                    "period": period,
                    "rows": [
                        {"period": "2023", "revenue": 100.0, "net_income": 10.0, "diluted_shares": 10.0, "diluted_eps": 1.0},
                        {"period": "2024", "revenue": 150.0, "net_income": 18.0, "diluted_shares": 10.0, "diluted_eps": 1.8},
                        {"period": "2025", "revenue": 225.0, "net_income": 27.0, "diluted_shares": 10.0, "diluted_eps": 2.7},
                    ],
                    "source": "test_provider",
                }
            return {
                "symbol": symbol.upper(),
                "statement": statement,
                "period": period,
                "rows": [
                    {"period": "2024Q1", "revenue": 50.0, "net_income": 5.0, "diluted_shares": 10.0, "diluted_eps": 0.5},
                    {"period": "2025Q1", "revenue": 75.0, "net_income": 9.0, "diluted_shares": 10.0, "diluted_eps": 0.9},
                ],
                "source": "test_provider",
            }

    data = fundamentals_growth(
        "nvda",
        metrics=["revenue", "eps"],
        periods=["quarterly", "annual"],
        years=3,
        provider=Provider(),
    )

    assert data["symbol"] == "NVDA"
    assert any(row["kind"] == "history" and row["metric"] == "revenue" and row["period"] == "2025" for row in data["rows"])
    assert any(row["kind"] == "growth" and row["metric"] == "revenue" and row["growth_type"] == "yoy" and row["growth_pct"] == 50.0 for row in data["rows"])
    assert any(row["kind"] == "growth" and row["metric"] == "revenue" and row["growth_type"] == "cagr" and round(row["growth_pct"], 2) == 50.0 for row in data["rows"])
    assert any(row["metric"] == "eps" and row["method"] == "reported_diluted_eps" for row in data["rows"])
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```bash
python -m pytest tests/test_finance_architecture.py::test_fundamentals_growth_returns_raw_history_yoy_and_cagr -q
```

Expected: FAIL with `NameError` or import error for `fundamentals_growth`.

- [ ] **Step 3: Implement minimal service**

Implement `fundamentals_growth(symbol, metrics, periods, years, provider)` in `finance_cli/services/fundamentals.py`.

Required behavior:
- Fetch income statements through the selected provider.
- Normalize revenue from `revenue`, `total_revenue`, or `Total Revenue`.
- Normalize EPS from reported diluted EPS keys first, then derived `net_income / diluted_shares`.
- Emit rows with `kind=history` and `kind=growth`.
- Emit annual adjacent YoY rows and oldest-to-newest CAGR rows.
- Emit quarterly latest-vs-same-quarter-prior-year rows when periods can be matched.
- For margin and ROE metrics, emit history and delta rows; do not calculate CAGR.
- Include `warnings` for unavailable metrics or insufficient comparison periods.

- [ ] **Step 4: Run focused tests**

Run:

```bash
python -m pytest tests/test_finance_architecture.py -k "fundamentals_growth" -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finance_cli/services/fundamentals.py tests/test_finance_architecture.py
git commit -m "feat: add fundamental growth primitive"
```

---

### Task 2: Fundamental Growth CLI And Compact Records

**Files:**
- Modify: `finance_cli/cli/commands/fundamentals.py`
- Modify: `finance_cli/records.py`
- Test: `tests/test_agent_records.py`
- Test: `tests/test_finance_architecture.py`

- [ ] **Step 1: Write failing CLI and compact output tests**

Add registry coverage:

```python
def test_fundamentals_growth_command_is_registered():
    names = {command.name for command in list_commands()}
    assert "fundamentals.growth" in names
```

Add compact rendering coverage:

```python
def test_cli_compact_output_renders_fundamentals_growth(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.fundamentals.fundamentals_growth",
        lambda *args, **kwargs: {
            "symbol": "NVDA",
            "rows": [
                {
                    "kind": "growth",
                    "metric": "revenue",
                    "period_type": "quarterly",
                    "current_period": "2025Q1",
                    "comparison_period": "2024Q1",
                    "current_value": 75.0,
                    "comparison_value": 50.0,
                    "growth_type": "yoy",
                    "growth_pct": 50.0,
                    "source": "test_provider",
                }
            ],
            "source": "test_provider",
        },
    )

    code = main(["fundamentals.growth", "nvda", "--output", "compact", "--fields", "metric,growth_type,growth_pct"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert output == "NVDA|fundamental_growth|metric=revenue|growth_type=yoy|growth_pct=50.0|src=test_provider"
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest tests/test_finance_architecture.py -k "fundamentals_growth_command_is_registered" -q
python -m pytest tests/test_agent_records.py -k "fundamentals_growth" -q
```

Expected: FAIL because command and adapter do not exist.

- [ ] **Step 3: Register command and adapter**

Add CLI command:

```text
finance fundamentals.growth SYMBOL [metrics=revenue,eps,operating_margin,net_margin,roe periods=quarterly,annual years=5 provider=sec]
```

Record adapter requirements:
- `history` rows render as `fundamental_history`.
- `growth` and `delta` rows render as `fundamental_growth`.
- Entity is the ticker.
- Source comes from row source first, then payload source.

- [ ] **Step 4: Run focused tests**

Run:

```bash
python -m pytest tests/test_finance_architecture.py -k "fundamentals_growth" -q
python -m pytest tests/test_agent_records.py -k "fundamentals_growth" -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finance_cli/cli/commands/fundamentals.py finance_cli/records.py tests/test_agent_records.py tests/test_finance_architecture.py
git commit -m "feat: expose fundamental growth command"
```

---

### Task 3: Relative Price Service

**Files:**
- Modify: `finance_cli/services/market_data.py`
- Test: `tests/test_finance_architecture.py`

- [ ] **Step 1: Write failing tests for default benchmark, auto sector ETF, explicit override, and peers**

Add tests with fake OHLCV and quote providers:

```python
def test_relative_price_performance_defaults_to_benchmarks_and_auto_sector_etf():
    class Attempt:
        provider = "test_provider"

    class MarketData:
        def load_ohlcv(self, symbol, **_kwargs):
            end = {"NVDA": 130.0, "SPY": 110.0, "QQQ": 120.0, "XLK": 115.0}[symbol]
            rows = [{"date": "2026-01-01", "close": 100.0}, {"date": "2026-02-01", "close": end}]
            return rows, Attempt(), []

    class QuoteProvider:
        def quote(self, symbol):
            return {"symbol": symbol.upper(), "sector": "Technology", "source": "test_quote"}

    data = relative_price_performance(
        "nvda",
        periods=["1M"],
        market="US",
        service=MarketData(),
        quote_provider=QuoteProvider(),
    )

    comparisons = {(row["comparison"], row["comparison_type"]) for row in data["relative_performance"]}
    assert ("SPY", "benchmark") in comparisons
    assert ("QQQ", "benchmark") in comparisons
    assert ("XLK", "sector_etf") in comparisons
```

Add explicit override/peer assertion:

```python
def test_relative_price_performance_uses_explicit_sector_etf_and_peers():
    class Attempt:
        provider = "test_provider"

    class MarketData:
        def load_ohlcv(self, symbol, **_kwargs):
            end = {"NVDA": 130.0, "SPY": 110.0, "SMH": 125.0, "AMD": 140.0}[symbol]
            rows = [{"date": "2026-01-01", "close": 100.0}, {"date": "2026-02-01", "close": end}]
            return rows, Attempt(), []

    data = relative_price_performance(
        "nvda",
        benchmarks=["SPY"],
        peers=["AMD"],
        sector_etfs=["SMH"],
        periods=["1M"],
        service=MarketData(),
    )

    comparisons = {(row["comparison"], row["comparison_type"]) for row in data["relative_performance"]}
    assert comparisons == {("SPY", "benchmark"), ("SMH", "sector_etf"), ("AMD", "peer")}
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest tests/test_finance_architecture.py -k "relative_price_performance" -q
```

Expected: FAIL because `relative_price_performance` does not exist.

- [ ] **Step 3: Implement service**

Implement `relative_price_performance()` in `finance_cli/services/market_data.py`.

Required behavior:
- Inputs: `symbol`, `benchmarks=None`, `peers=None`, `sector_etfs=None`, `periods=None`, `market="US"`, `provider="auto"`, optional `service`, optional `quote_provider`.
- Default benchmarks: `["SPY", "QQQ"]`.
- If `sector_etfs` is provided, use it and skip auto sector ETF.
- If `sector_etfs` is not provided, fetch quote sector and map through `SECTOR_ETFS[market]`.
- Peers are explicit only; default empty.
- Reuse existing return math helpers where practical.
- Output rows include `symbol`, `period`, `comparison`, `comparison_type`, `symbol_return_pct`, `comparison_return_pct`, `relative_return_pct`, start/end dates and closes, and `source`.
- Include warnings when sector cannot be mapped or comparison data is unavailable.

- [ ] **Step 4: Run focused tests**

Run:

```bash
python -m pytest tests/test_finance_architecture.py -k "relative_price_performance" -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finance_cli/services/market_data.py tests/test_finance_architecture.py
git commit -m "feat: add relative price primitive"
```

---

### Task 4: Relative Price CLI And Compact Records

**Files:**
- Modify: `finance_cli/cli/commands/price.py`
- Modify: `finance_cli/records.py`
- Test: `tests/test_agent_records.py`
- Test: `tests/test_finance_architecture.py`

- [ ] **Step 1: Write failing command and compact rendering tests**

Add registry test:

```python
def test_price_relative_command_is_registered():
    names = {command.name for command in list_commands()}
    assert "price.relative" in names
```

Add compact output test:

```python
def test_cli_compact_output_renders_price_relative(capsys, monkeypatch):
    monkeypatch.setattr(
        "finance_cli.cli.commands.price.relative_price_performance",
        lambda *args, **kwargs: {
            "symbol": "NVDA",
            "relative_performance": [
                {
                    "symbol": "NVDA",
                    "period": "1M",
                    "comparison": "SPY",
                    "comparison_type": "benchmark",
                    "symbol_return_pct": 30.0,
                    "comparison_return_pct": 10.0,
                    "relative_return_pct": 20.0,
                    "source": "test_provider",
                }
            ],
            "source": "test_provider",
        },
    )

    code = main(["price.relative", "nvda", "--output", "compact", "--fields", "period,comparison,comparison_type,relative_return_pct"])
    output = capsys.readouterr().out.strip()

    assert code == 0
    assert output == "NVDA|relative_price|period=1M|comparison=SPY|comparison_type=benchmark|relative_return_pct=20.0|src=test_provider"
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest tests/test_finance_architecture.py -k "price_relative_command_is_registered" -q
python -m pytest tests/test_agent_records.py -k "price_relative" -q
```

Expected: FAIL.

- [ ] **Step 3: Register command and record adapter**

CLI usage:

```text
finance price.relative SYMBOL [benchmarks=SPY,QQQ peers=AMD,AVGO sector_etfs=SMH periods=1M,3M,6M,1Y market=US provider=auto]
```

Important notes:
- If `sector_etfs` is omitted, auto sector ETF is attempted.
- If `sector_etfs` is provided, it replaces auto sector ETF.
- Peers are explicit only.

- [ ] **Step 4: Run focused tests**

Run:

```bash
python -m pytest tests/test_finance_architecture.py -k "price_relative" -q
python -m pytest tests/test_agent_records.py -k "price_relative" -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finance_cli/cli/commands/price.py finance_cli/records.py tests/test_agent_records.py tests/test_finance_architecture.py
git commit -m "feat: expose relative price command"
```

---

### Task 5: Market Trend Service And CLI

**Files:**
- Modify: `finance_cli/services/market_data.py`
- Modify: `finance_cli/cli/commands/market.py`
- Modify: `finance_cli/records.py`
- Test: `tests/test_finance_architecture.py`
- Test: `tests/test_agent_records.py`

- [ ] **Step 1: Write failing tests for trend rows and no breadth proxy**

Add service test:

```python
def test_market_trend_returns_index_and_vix_trend_without_breadth_proxy():
    class Attempt:
        provider = "test_provider"

    class MarketData:
        def load_ohlcv(self, symbol, **_kwargs):
            rows = [{"date": f"2026-01-{day:02d}", "close": 100.0 + day} for day in range(1, 31)]
            return rows, Attempt(), []

    data = market_trend("US", periods=["1M"], service=MarketData())

    roles = {row["role"] for row in data["trend"]}
    assert {"primary", "growth", "dow", "small_caps", "volatility"} <= roles
    assert all(row["kind"] in {"market_trend", "market_volatility"} for row in data["trend"])
    assert "breadth" not in json.dumps(data).lower()
```

Add command registration test:

```python
def test_market_trend_command_is_registered():
    names = {command.name for command in list_commands()}
    assert "market.trend" in names
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest tests/test_finance_architecture.py -k "market_trend" -q
```

Expected: FAIL because `market_trend` does not exist.

- [ ] **Step 3: Implement service and CLI**

Implement:

```text
finance market.trend [MARKET=US] [symbols=SPY,QQQ,DIA,IWM,^VIX periods=1M,3M,6M,1Y provider=auto]
```

Default role mapping:
- `SPY`: `primary`
- `QQQ`: `growth`
- `DIA`: `dow`
- `IWM`: `small_caps`
- `^VIX`: `volatility`

Required output:
- close, SMA50, SMA200 for equity/index ETF roles
- above/below SMA50 and SMA200
- period returns
- VIX close, SMA20, SMA50, and `volatility_state`
- deterministic `market_direction_state` based on raw trend evidence
- no breadth fields, no breadth proxy

- [ ] **Step 4: Add compact adapter and run focused tests**

Run:

```bash
python -m pytest tests/test_finance_architecture.py -k "market_trend" -q
python -m pytest tests/test_agent_records.py -k "market_trend" -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finance_cli/services/market_data.py finance_cli/cli/commands/market.py finance_cli/records.py tests/test_agent_records.py tests/test_finance_architecture.py
git commit -m "feat: add market trend primitive"
```

---

### Task 6: Tool Wrappers And Agent Metadata

**Files:**
- Modify: `finance_cli/tools/research/market_data.py`
- Modify: `finance_cli/tools/research/price.py`
- Modify: `finance_cli/tools/research/__init__.py` if needed
- Test: `tests/test_cli_smoke.py`

- [ ] **Step 1: Write failing metadata tests**

Add assertions that generated command specs include the new commands and agent notes:

```python
def test_canslim_primitives_are_in_generated_tools_metadata():
    specs = build_command_specs()
    by_name = {spec["name"]: spec for spec in specs}

    assert "fundamentals.growth" in by_name
    assert "price.relative" in by_name
    assert "market.trend" in by_name
    assert "CANSLIM" not in by_name
    assert "sector_etfs" in by_name["price.relative"]["args"]
    assert by_name["price.relative"]["args"]["benchmarks"]["default"] == "SPY,QQQ"
```

- [ ] **Step 2: Run test and verify failure**

Run:

```bash
python -m pytest tests/test_cli_smoke.py -k "canslim_primitives" -q
```

Expected: FAIL until command metadata is registered.

- [ ] **Step 3: Add or update tool wrappers**

Add wrapper access where current tool modules already expose related functions:
- `FinanceOHLCV` remains raw OHLCV.
- Add `FinanceRelativePrice` or extend existing `FinancePrice` only if the existing action enum can remain clear.
- Add `FinanceMarketTrend` where market tools are defined.
- Add `FinanceFundamentalsGrowth` if fundamentals wrappers exist; otherwise keep CLI metadata as the primary contract and do not invent a parallel tool structure.

Do not create a CANSLIM-specific tool.

- [ ] **Step 4: Run metadata tests**

Run:

```bash
python -m pytest tests/test_cli_smoke.py -k "canslim_primitives or command_specs" -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finance_cli/tools tests/test_cli_smoke.py
git commit -m "feat: expose primitives to agent metadata"
```

---

### Task 7: Documentation And Source-Gap TODOs

**Files:**
- Modify: `docs/canslim-coverage.md`
- Modify: `docs-site/src/content/docs/workflows.md` if it contains relevant workflow guidance
- Modify: `docs-site/src/content/docs/agents.md` if command routing notes need manual prose

- [ ] **Step 1: Update coverage doc**

Required changes:
- Mark `fundamentals.growth` as the preferred primitive for quarterly YoY and annual history/CAGR.
- Mark `price.relative` as the preferred primitive for leader/laggard relative strength.
- Mark `market.trend` as the preferred primitive for market direction.
- State explicitly that the CLI does not include a CANSLIM command and intentionally leaves framework composition to the LLM.
- Remove any implication that market breadth is partially supported through proxy.

- [ ] **Step 2: Add TODO/source-discovery section**

Add this section to `docs/canslim-coverage.md`:

```markdown
## Source-Discovery TODOs

These are intentionally not implemented until a reliable free/open source or crawler target is selected.

- Market breadth:
  - NYSE/Nasdaq advance-decline line
  - Percentage of stocks above 50/200 DMA
  - New highs/new lows
  - Up/down volume breadth
- Institutional sponsorship history:
  - Institutional ownership changes over time
  - Fund ownership history
  - Feasibility of issuer-level aggregation from SEC 13F filings or open-source datasets
- Macro indicators:
  - Decide which macro series matter for the CLI contract
  - Identify free/open source APIs or datasets with stable terms
```

- [ ] **Step 3: Verify docs mention no paid-provider fallback**

Search:

```bash
rg -n "paid|Payment Required|provider-gated|market breadth|ownership changes|CANSLIM" docs docs-site/src/content
```

Expected: docs say gaps are source-discovery TODOs, not paid-provider fallback work.

- [ ] **Step 4: Commit**

```bash
git add docs/canslim-coverage.md docs-site/src/content/docs
git commit -m "docs: document CANSLIM primitive coverage gaps"
```

---

### Task 8: Regenerate Agent Artifacts And Final Verification

**Files:**
- Modify generated: `tools.json`
- Modify generated: `openapi.json`
- Modify generated: `llms.txt`
- Modify generated: `docs-site/public/tools.json`
- Modify generated: `docs-site/public/openapi.json`
- Modify generated: `docs-site/public/llms.txt`
- Modify generated: `schemas/finance-cli-tools.schema.json` and public copy if generation touches them

- [ ] **Step 1: Regenerate docs**

Run:

```bash
python scripts/generate_cli_docs.py
```

Expected: generated artifacts include `fundamentals.growth`, `price.relative`, and `market.trend`.

- [ ] **Step 2: Verify generated artifacts**

Run:

```bash
rg -n "fundamentals\\.growth|price\\.relative|market\\.trend" tools.json openapi.json llms.txt docs-site/public
```

Expected: all three commands appear in generated agent-facing files.

- [ ] **Step 3: Run focused tests**

Run:

```bash
python -m pytest tests/test_finance_architecture.py tests/test_agent_records.py tests/test_cli_smoke.py -q
```

Expected: PASS.

- [ ] **Step 4: Run full tests**

Run:

```bash
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 5: Ask external model to review substantial work**

Per repo instruction, ask one reviewer and allow up to 5 minutes:

```bash
gemini --yolo "Review the FinanceCLI CANSLIM primitive implementation for overfitting, fake data support, brittle output contracts, and missing tests. Focus on fundamentals.growth, price.relative, market.trend, compact record adapters, and generated agent metadata."
```

If Gemini is unavailable, use:

```bash
claude --dangerously-skip-permissions "Review the FinanceCLI CANSLIM primitive implementation for overfitting, fake data support, brittle output contracts, and missing tests. Focus on fundamentals.growth, price.relative, market.trend, compact record adapters, and generated agent metadata."
```

Expected: reviewer either returns no blockers or concrete issues to fix before completion.

- [ ] **Step 6: Commit generated artifacts**

```bash
git add tools.json openapi.json llms.txt docs-site/public schemas docs-site/src/content/docs tests finance_cli docs/canslim-coverage.md
git commit -m "chore: regenerate agent artifacts for CANSLIM primitives"
```

## Self-Review

- Spec coverage:
  - C/A gaps are covered by `fundamentals.growth`.
  - L gaps are covered by `price.relative`.
  - M index/VIX trend gaps are covered by `market.trend`.
  - Market breadth is not faked; exact future items are in TODO.
  - Ownership changes are not faked; future source discovery is in TODO.
  - No CANSLIM fixed path is introduced.
- Placeholder scan:
  - In-scope tasks include concrete files, tests, commands, and expected outcomes.
  - Out-of-scope work is explicitly documented as source-discovery TODOs.
- Type consistency:
  - `fundamentals_growth`, `relative_price_performance`, and `market_trend` names are used consistently across service, CLI, tests, and metadata tasks.
