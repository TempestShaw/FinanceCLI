# Trust

Finance CLI is for research workflows and deterministic calculations. It is not a trading system and does not make investment recommendations.

## Result Envelope

Commands return:

```json
{"ok": true, "data": {}, "error": null, "warnings": []}
```

- If `ok=false`, quote or summarize `error` and stop that path.
- If `ok=true` with empty arrays, say the source returned no matching records.
- If `warnings` is non-empty, preserve the warning context in the final answer.

## Citation Policy

Cite fields when present:

- SEC: `accession`, `accession_no`, `form`, `report_name`, `section`, `url`.
- Documents: `source`, `path`, `url`, `page`, `start_char`, `end_char`, `match_id`.
- Market/news/providers: `source`, `provider`, `timestamp`, `date`, `published_at`, `url`.

Treat provider output as source-specific records. Do not merge Yahoo, FMP, SEC, GDELT, transcripts, and company IR into a single unstated ground truth.

## Credentials And Local State

Finance CLI reads provider keys from environment variables at runtime. Do not write API keys into repo files, generated docs, skill files, command examples, or persistent local config unless the user explicitly asks for that storage mechanism.

## Calculators

Use `formula.*` and `valuation.*` only when inputs are explicit in the prompt or extracted from cited command output. State assumptions for valuation math and avoid investment-advice language.
