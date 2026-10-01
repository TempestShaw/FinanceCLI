import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLOR, FONT } from "../theme";
import { enter, pop, sceneOpacity } from "../motion";
import { Eyebrow, Scene } from "./Stage";

// A slice of the real `finance --list` catalog: the agent sees all of these.
const CATALOG = [
  "filings.recent", "filings.sections", "filings.statement", "filings.reports", "filings.report", "filings.read",
  "transcripts.search", "transcripts.read", "transcripts.qa", "document.read", "document.scan", "document.window",
  "fundamentals.statement", "fundamentals.metrics", "fundamentals.growth", "market.quote", "market.ohlcv", "price.moves",
  "price.context", "ir.presentations", "valuation.multiples", "valuation.dcf", "formula.margin", "formula.cagr",
] as const;

interface ToolMapProps { title: string; subtitle: string; chosen: string[]; start?: number; interval?: number }

/** The full toolbox on screen, with the tools this agent actually picked lighting up in order. */
export const ToolMap = ({ title, subtitle, chosen, start = 40, interval = 14 }: ToolMapProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const order = new Map<string, number>();
  chosen.forEach((tool) => { if (!order.has(tool)) order.set(tool, order.size); });
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <Eyebrow>No fixed workflow</Eyebrow>
      <div style={{ ...enter(frame, 0), fontSize: 64, fontWeight: 600, letterSpacing: -2, lineHeight: 1.1, margin: "18px 0 10px" }}>{title}</div>
      <div style={{ ...enter(frame, 8), fontSize: 32, color: COLOR.muted, marginBottom: 46 }}>{subtitle}</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 16 }}>
        {CATALOG.map((tool, i) => {
          const rank = order.get(tool);
          const litAt = rank === undefined ? Infinity : start + rank * interval;
          const lit = frame >= litAt;
          const scale = lit ? 1 + 0.06 * (1 - Math.min(1, pop(frame, litAt))) : 1;
          return (
            <div key={tool} style={{ ...enter(frame, 10 + i, 10, 10), position: "relative", padding: "20px 18px", borderRadius: 12, fontFamily: FONT.mono, fontSize: 22,
              border: `1.5px solid ${lit ? COLOR.accent : COLOR.line}`, background: lit ? `${COLOR.accent}1c` : COLOR.panel,
              color: lit ? COLOR.text : COLOR.faint, transform: `scale(${scale})` }}>
              {tool}
              {lit && (
                <span style={{ position: "absolute", top: -14, right: -10, width: 34, height: 34, borderRadius: 17, background: COLOR.accent, color: COLOR.ink,
                  display: "grid", placeItems: "center", fontFamily: FONT.sans, fontWeight: 700, fontSize: 18 }}>{(rank ?? 0) + 1}</span>
              )}
            </div>
          );
        })}
      </div>
    </Scene>
  );
};
