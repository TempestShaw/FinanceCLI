import { useCurrentFrame, useVideoConfig } from "remotion";
import type { Check, Status } from "../data";
import { COLOR, FONT, seconds } from "../theme";
import { enter, sceneOpacity } from "../motion";
import { Eyebrow, Scene } from "./Stage";

const STATUS: Record<Status, { icon: string; color: string; word: string }> = {
  verified: { icon: "✓", color: COLOR.verified, word: "Verified" },
  supported: { icon: "✓", color: COLOR.verified, word: "Supported" },
  caveat: { icon: "!", color: COLOR.caveat, word: "Caveat" },
  mixed: { icon: "~", color: COLOR.caveat, word: "Mixed" },
  missing: { icon: "✕", color: COLOR.missing, word: "Not disclosed" },
  untested: { icon: "?", color: COLOR.missing, word: "Untested" },
};

export const StatusBadge = ({ status, size = 22 }: { status: Status; size?: number }) => {
  const s = STATUS[status];
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 10, padding: "6px 14px", borderRadius: 999, border: `1.5px solid ${s.color}`,
      color: s.color, fontFamily: FONT.mono, fontSize: size, letterSpacing: 1, textTransform: "uppercase", whiteSpace: "nowrap" }}>
      <b>{s.icon}</b>{s.word}
    </span>
  );
};

interface ChecksProps { eyebrow: string; title: string; checks: Check[]; interval?: number }

/** Verification results: what was confirmed, what needs a caveat, what is missing. */
export const Checks = ({ eyebrow, title, checks, interval = seconds(1.4) }: ChecksProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <Eyebrow>{eyebrow}</Eyebrow>
      <div style={{ fontFamily: FONT.serif, fontSize: 58, fontWeight: 600, letterSpacing: -0.5, margin: "18px 0 40px", maxWidth: 1500, ...enter(frame, 0) }}>{title}</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        {checks.map((check, i) => (
          <div key={check.label} style={{ ...enter(frame, 12 + i * interval), display: "grid", gridTemplateColumns: "280px 1fr", gap: 32, alignItems: "start",
            padding: "22px 28px", background: COLOR.panel, border: `1px solid ${COLOR.line}`, borderRadius: 16 }}>
            <div style={{ paddingTop: 4 }}><StatusBadge status={check.status} /></div>
            <div>
              <div style={{ fontSize: 32, fontWeight: 600 }}>{check.label}</div>
              <div style={{ fontSize: 26, lineHeight: 1.45, color: COLOR.muted, marginTop: 8 }}>{check.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </Scene>
  );
};
