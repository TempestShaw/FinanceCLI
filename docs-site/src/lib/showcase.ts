import raw from "../data/showcase.json";

export type Status = "verified" | "caveat" | "missing" | "supported" | "mixed" | "untested";

export interface TraceStep { id: string; tool: string; command: string; purpose: string; result: string; retrieved_at?: string; evidence?: string; note?: string }
export interface Check { status: Status; label: string; detail: string }
export interface Metric { label: string; value: string; delta: string }
export interface Column { key: string; label: string; align?: "end" }
export interface Claim { claim: string; status: Status; evidence: string; source: string; kind: string }
export interface Source { label: string; company: string; form: string; filing_date: string; period: string; accession: string; url: string }
export interface Calculation { label: string; method: string; inputs: string; result: string }

export interface ShowcaseCase {
  slug: string;
  title: string;
  kicker: string;
  question: string;
  headline: string;
  answer: string[];
  metrics: Metric[];
  checks: Check[];
  trace: TraceStep[];
  sources: Source[];
  quotes: { text: string; source: string }[];
  calculations?: Calculation[];
  table?: { caption: string; columns: Column[]; rows: Record<string, string>[] };
  claims?: Claim[];
  alignment?: { ticker: string; fy_note: string; periods: { fy: string; period_end: string }[] }[];
  gap?: { available: string; missing: string; reason: string; policy: string };
  prompt: string;
}

const dataset = raw as unknown as { recorded: { first: string; last: string }; note: string; cases: ShowcaseCase[] };

export const cases = dataset.cases;
export const showcaseNote = dataset.note;
export const recordedOn = new Date(dataset.recorded.first).toLocaleDateString("en-US", {
  year: "numeric", month: "long", day: "numeric", timeZone: "America/New_York",
});

const base = import.meta.env.BASE_URL.replace(/\/$/, "");
/** Prefix a site path with the deployment base (/FinanceCLI). */
export const href = (path: string) => `${base}/${path.replace(/^\//, "")}`;

export const videoFor = (slug: string) => ({ src: href(`videos/${slug}.mp4`), poster: href(`videos/${slug}.jpg`) });

export const caseBySlug = (slug: string) => {
  const found = cases.find((c) => c.slug === slug);
  if (!found) throw new Error(`Unknown showcase case: ${slug}`);
  return found;
};

/** Short labels shown on cards and in navigation. */
export const SHORT_TITLES: Record<string, string> = {
  "apple-services": "Apple · Services dependence",
  "chip-rnd": "NVDA · AMD · AVGO · R&D intensity",
  "meta-efficiency": "Meta · Year of Efficiency",
  "costco-thesis": "Costco · thesis test",
  "data-gap": "Apple · App Store revenue",
};

export const STATUS_META: Record<Status, { icon: string; word: string; tone: "good" | "warn" | "bad" }> = {
  verified: { icon: "✓", word: "Verified", tone: "good" },
  supported: { icon: "✓", word: "Supported", tone: "good" },
  caveat: { icon: "!", word: "Caveat", tone: "warn" },
  mixed: { icon: "~", word: "Mixed", tone: "warn" },
  missing: { icon: "✕", word: "Not disclosed", tone: "bad" },
  untested: { icon: "?", word: "Untested", tone: "bad" },
};
