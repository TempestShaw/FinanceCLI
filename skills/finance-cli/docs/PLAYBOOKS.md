# Playbooks

Run commands with `--output json` and keep the raw result envelope available until the answer is written.

## Extract A Metric From A 10-K

1. Run `finance filings.recent SYMBOL form=10-K --output json`.
2. Try `finance filings.statement SYMBOL statement=income query=METRIC --output json` or the relevant statement family.
3. If the XBRL row is missing, run `filings.reports` and `filings.report` for table discovery.
4. Use `document.scan` for phrase/table discovery in the filing URL.
5. Use `document.window` around candidate `match_id` or offsets.
6. Use `formula.*` only after numeric inputs are explicit and cited.

Failure handling: if no XBRL row or text match appears, report that the source returned no matching record. Do not invent a value.

## Explain A Dated Price Move

1. Run `price.moves` or `market.ohlcv` for the dated move.
2. Run `price.context` for nearby filings, news, and transcript context.
3. Add `news.search`, `filings.recent`, or `transcripts.search` when the initial context is sparse.
4. Preserve dates, providers, URLs, accessions, and warnings.

Failure handling: describe evidence timing and source attribution. Do not claim causality unless the cited evidence states it.

## Screen And Contextualize Companies

1. Run `screen.predefined` or inspect `tools.json` for screen commands.
2. Run `screen.run` for the selected screen.
3. Use `symbol.snapshot`, `market.quote`, and `filings.recent` for company context.
4. Summarize membership as source output, not a recommendation.

Failure handling: if fewer rows return than requested, keep the returned count and source.

## Run A Reproducible Backtest

1. Run `backtest.strategies` to list available strategies.
2. Run `backtest.describe` for required parameters.
3. Run `backtest.run` with explicit symbols, dates, and parameters.
4. Keep strategy name, symbols, date range, parameters, provider, metrics, and warnings.

Failure handling: if provider data is unavailable, surface the provider error from the JSON envelope.
