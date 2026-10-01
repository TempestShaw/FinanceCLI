import raw from "../../docs-site/src/data/showcase.json";

export type Status = "verified" | "caveat" | "missing" | "supported" | "mixed" | "untested";

export interface TraceStep { id: string; tool: string; command: string; purpose: string; result: string; note?: string }
export interface Check { status: Status; label: string; detail: string }
export interface Metric { label: string; value: string; delta: string }
export interface Column { key: string; label: string; align?: "end" }
export interface Point { x: string; value: number; secondary?: number; fy?: string }
export interface Series { key: string; points: Point[] }
export interface Claim { claim: string; status: Status; evidence: string; source: string; kind: string }
export interface Source { label: string; form: string; filing_date: string; period: string; accession: string; url: string }

export interface CaseData {
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
  table?: { caption: string; columns: Column[]; rows: Record<string, string>[] };
  chart?: { kind: "bars" | "lines"; label: string; points?: Point[]; series?: Series[]; headcount?: Point[] };
  claims?: Claim[];
  alignment?: { ticker: string; fy_note: string; periods: { fy: string; period_end: string }[] }[];
  gap?: { available: string; missing: string; reason: string; policy: string };
}

const dataset = raw as unknown as { recorded: { first: string }; cases: CaseData[] };

export const caseBySlug = (slug: string): CaseData => {
  const found = dataset.cases.find((item) => item.slug === slug);
  if (!found) throw new Error(`Unknown showcase case: ${slug}`);
  return found;
};

export const recordedOn = new Date(dataset.recorded.first).toLocaleDateString("en-US", {
  year: "numeric", month: "short", day: "numeric", timeZone: "America/New_York",
});
