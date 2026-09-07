# Changelog

All notable changes to Finance CLI will be documented here.

## 0.1.0b2 - Beta

- Constrained the optional backtesting stack to Plotly below 7, whose removed `scattermapbox` template field prevents VectorBT from initializing. Base research installations are unaffected.

## 0.1.0b1 - Beta

- Added a question-based website entry point, worked research examples, and a guided first-use path.
- Made PDF table extraction, OCR, and backtesting optional installs: `finresearch-cli[tables]`, `finresearch-cli[ocr]`, and `finresearch-cli[backtest]`. Existing full installations keep working; new base installations retain SEC research, native PDF/HTML reading, market data, and calculations.
- Added readable Markdown output, symbol comparison, configurable output defaults, and shell completions.
- Expanded financial statement, growth, ownership, and relative-performance research commands.
- Removed unavailable GDELT news commands and the KPI command family.
- Updated package license metadata to Apache-2.0 to match the repository license.

## 0.1.0b0 - Beta

- Added the Finance CLI command framework with JSON output for scripting and automation.
- Added SEC filings, XBRL statements, filing reports, document read/scan/window/table/OCR workflows, and source attribution.
- Added market data, news, transcripts, IR presentation discovery, valuation helpers, formulas, and VectorBT backtests.
- Added the Starlight documentation site with namespace guides and generated command reference pages.
- Added CI, docs build, package build, and package metadata checks for release readiness.
