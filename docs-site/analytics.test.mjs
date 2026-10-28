import assert from "node:assert/strict";
import test from "node:test";
import vm from "node:vm";
import { googleAnalyticsHead, googleAnalyticsId } from "./analytics.mjs";

test("GA4 stays scoped to FinanceCLI production unless QA is explicitly enabled", () => {
  for (const [url, disabled, debug] of [
    ["https://tempestshaw.github.io/FinanceCLI/", false, undefined],
    ["https://tempestshaw.github.io/FinanceCLI/research-examples/", false, undefined],
    ["https://tempestshaw.github.io/FastPin/", true, undefined],
    ["https://tempestshaw.github.io/FinanceCLI-copy/", true, undefined],
    ["https://tempestshaw.github.io.evil.test/FinanceCLI/", true, undefined],
    ["http://localhost:4321/FinanceCLI/", true, undefined],
    ["http://localhost:4321/FinanceCLI/?analytics_debug=true", true, undefined],
    ["http://localhost:4321/FinanceCLI/?analytics_debug=1", false, true],
  ]) {
    const location = new URL(url);
    const context = { location, URLSearchParams };
    context.window = context;
    vm.runInNewContext(googleAnalyticsHead.map((item) => item.content ?? "").join("\n"), context);
    assert.equal(context[`ga-disable-${googleAnalyticsId}`], disabled, url);
    const configs = context.dataLayer.filter((args) => args[0] === "config");
    assert.equal(configs.length, 1, url);
    assert.equal(configs[0][1], googleAnalyticsId, url);
    assert.equal(configs[0][2].debug_mode, debug, url);
  }
});
