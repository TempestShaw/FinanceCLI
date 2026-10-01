import { useCurrentFrame, useVideoConfig } from "remotion";
import type { TraceStep } from "../data";
import { COLOR, FONT, seconds } from "../theme";
import { enter, progress, sceneOpacity } from "../motion";
import { Eyebrow, Scene } from "./Stage";

interface AgentLogProps { title: string; steps: TraceStep[]; interval?: number; aside?: string }

const Spinner = ({ frame }: { frame: number }) => (
  <svg width="30" height="30" viewBox="0 0 30 30" style={{ transform: `rotate(${frame * 14}deg)` }}>
    <circle cx="15" cy="15" r="11" fill="none" stroke={COLOR.lineStrong} strokeWidth="3" />
    <path d="M15 4 a11 11 0 0 1 11 11" fill="none" stroke={COLOR.accent} strokeWidth="3" strokeLinecap="round" />
  </svg>
);

/** The agent's tool calls, one row at a time: tool, why, then what came back. */
const ROW = 118; // fixed row pitch (row height + gap) so the list can scroll smoothly
const VISIBLE = 6;

export const AgentLog = ({ title, steps, interval = seconds(1.8), aside }: AgentLogProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const resolveAfter = Math.round(interval * 0.55);
  const scroll = steps.reduce((acc, _, i) => acc + (i >= VISIBLE ? progress(frame, 14 + i * interval - 6, 14) * ROW : 0), 0);
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginTop: 12 }}>
        <Eyebrow>Agent activity</Eyebrow>
        {aside && <div style={{ ...enter(frame, 6), fontSize: 26, color: COLOR.muted }}>{aside}</div>}
      </div>
      <div style={{ fontFamily: FONT.serif, fontSize: 54, fontWeight: 600, letterSpacing: -0.5, margin: "18px 0 34px", ...enter(frame, 0) }}>{title}</div>
      <div style={{ height: VISIBLE * ROW, overflow: "hidden", maskImage: scroll > 0 ? "linear-gradient(transparent, black 90px)" : undefined }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 14, transform: `translateY(${-scroll}px)` }}>
        {steps.map((step, i) => {
          const start = 14 + i * interval;
          if (frame < start) return null;
          const done = frame >= start + resolveAfter;
          const isGap = Boolean(step.note);
          return (
            <div key={step.id} style={{ ...enter(frame, start, 18, 12), display: "grid", gridTemplateColumns: "48px 300px 1fr", alignItems: "start", gap: 24,
              height: ROW - 14, boxSizing: "border-box", padding: "16px 24px", borderRadius: 14, background: isGap && done ? `${COLOR.caveat}14` : COLOR.panel,
              border: `1px solid ${isGap && done ? `${COLOR.caveat}66` : COLOR.line}` }}>
              <div style={{ paddingTop: 4 }}>
                {done ? <span style={{ color: isGap ? COLOR.caveat : COLOR.accent, fontSize: 30, fontWeight: 700 }}>{isGap ? "!" : "✓"}</span> : <Spinner frame={frame} />}
              </div>
              <div style={{ fontFamily: FONT.mono, fontSize: 25, color: COLOR.accent, paddingTop: 6 }}>{step.tool}</div>
              <div>
                <div style={{ fontSize: 27, lineHeight: 1.35, color: COLOR.text }}>{step.purpose}</div>
                <div style={{ opacity: progress(frame, start + resolveAfter, 10), fontSize: 24, lineHeight: 1.4, color: isGap ? COLOR.caveat : COLOR.muted, marginTop: 6 }}>
                  → {step.note ?? step.result}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      </div>
    </Scene>
  );
};
