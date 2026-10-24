# Website analytics

Analytics is optional. With no `GOATCOUNTER_CODE` repository variable, the
GitHub Pages build loads no analytics script. The CLI has no telemetry.

## Enable and verify

1. Use a GoatCounter account you own. Its initial registration must be performed
   manually under the [service terms](https://www.goatcounter.com/help/terms).
2. Set the GitHub Actions repository variable `GOATCOUNTER_CODE` to that site's
   code (the part before `.goatcounter.com`, not a URL or credential). The Docs
   workflow passes it as `PUBLIC_GOATCOUNTER_CODE` at build time.
3. Re-run the latest successful Docs workflow for the current `main` commit.
   Confirm the deployed homepage, a showcase page and a reference page contain
   exactly one script pointing to the intended site's `/count` endpoint.
4. In a browser, open an existing case with
   `?utm_source=launch-check&utm_campaign=analytics-validation`. Open its agent
   setup link, then return to the case and open a filing source.
5. Confirm the corresponding page, campaign and events in the account dashboard.
   Record the time window and mark this traffic as maintainer validation, not
   external adoption. HTTP/build success alone does not prove receipt.
6. Exclude routine maintainer visits using the provider's
   [own-traffic controls](https://www.goatcounter.com/help/skip-dev).

To disable analytics, remove the variable and rebuild/redeploy. Existing data
is managed separately in the account. Local previews are ignored by GoatCounter
by default; do not enable local traffic against the production account.

## What the measurements mean

| Measurement | Meaning | Does not prove |
|---|---|---|
| Case page views and UTM campaigns | Visits grouped by landing page and campaign | Installation, research success or causal lift |
| `showcase-<slug>-source` | Click on a filing source in that case's Sources box | Reading or understanding the source |
| `showcase-<slug>-setup` | Click on that case's agent setup link | Successful installation or CLI execution |

The slug identifies one of the five published cases. Event names and titles are
fixed by the page; they do not include clipboard contents or user-entered text.
The events use GoatCounter's built-in
[click attributes](https://www.goatcounter.com/help/events), so no extra tracking
code runs when analytics is disabled. Links still work if the script is blocked.

[Campaign parameters](https://www.goatcounter.com/help/campaigns) identify the
arrival campaign. Do not infer a cross-page conversion funnel or divide raw
click totals by visitors without checking the dashboard's counting semantics.
Successful first research and later reuse require separate, voluntary user
feedback; they cannot be inferred from these website events.
