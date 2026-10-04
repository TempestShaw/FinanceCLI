// Cookie-free page-view counting with GoatCounter, enabled only when the site is
// built with PUBLIC_GOATCOUNTER_CODE (e.g. "financecli" for financecli.goatcounter.com).
// Without it, no analytics script is added. GoatCounter stores no cookies and no
// personal data; see https://www.goatcounter.com/help/gdpr.
const code = (process.env.PUBLIC_GOATCOUNTER_CODE ?? "").trim();

if (code && !/^[a-z0-9-]+$/.test(code)) {
  throw new Error(`PUBLIC_GOATCOUNTER_CODE must be a GoatCounter site code, got: ${code}`);
}

export const goatcounterEndpoint = code ? `https://${code}.goatcounter.com/count` : null;
