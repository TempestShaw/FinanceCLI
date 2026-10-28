// Cookie-free page-view counting with GoatCounter, enabled only when the site is
// built with PUBLIC_GOATCOUNTER_CODE (e.g. "financecli" for financecli.goatcounter.com).
// Without it, no analytics script is added. GoatCounter stores no cookies and no
// personal data; see https://www.goatcounter.com/help/gdpr.
const code = (process.env.PUBLIC_GOATCOUNTER_CODE ?? "").trim();

if (code && !/^[a-z0-9-]+$/.test(code)) {
  throw new Error(`PUBLIC_GOATCOUNTER_CODE must be a GoatCounter site code, got: ${code}`);
}

export const goatcounterEndpoint = code ? `https://${code}.goatcounter.com/count` : null;

// Shared by the marketing pages and Starlight documentation.
export const googleAnalyticsId = "G-DTS3DTSHXC";
export const googleAnalyticsHead = [
  {
    tag: "script",
    content: `
const financeCliAnalyticsDebug = new URLSearchParams(location.search).get("analytics_debug") === "1";
const financeCliAnalyticsLive = location.hostname === "tempestshaw.github.io" && location.pathname.startsWith("/FinanceCLI/");
window["ga-disable-${googleAnalyticsId}"] = !financeCliAnalyticsLive && !financeCliAnalyticsDebug;
`,
  },
  { tag: "script", attrs: { async: true, src: `https://www.googletagmanager.com/gtag/js?id=${googleAnalyticsId}` } },
  {
    tag: "script",
    content: `
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag("js", new Date());
gtag("config", "${googleAnalyticsId}", financeCliAnalyticsDebug ? { debug_mode: true } : {});
`,
  },
];
