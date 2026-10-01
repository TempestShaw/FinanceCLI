import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { ReactNode } from "react";
import { COLOR, FONT } from "../theme";
import { recordedOn } from "../data";

interface StageProps { kicker: string; children: ReactNode; chrome?: boolean }

/** Shared backdrop: ink surface, hairline grid, soft glow, session chrome and a progress rule. */
export const Stage = ({ kicker, children, chrome = true }: StageProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: COLOR.ink, fontFamily: FONT.sans, color: COLOR.text }}>
      <AbsoluteFill style={{
        backgroundImage: `linear-gradient(${COLOR.line}55 1px, transparent 1px), linear-gradient(90deg, ${COLOR.line}55 1px, transparent 1px)`,
        backgroundSize: "80px 80px",
        maskImage: "radial-gradient(ellipse 80% 70% at 50% 40%, black 30%, transparent 100%)",
      }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 82% 8%, ${COLOR.accent}1f, transparent 42%)` }} />
      {chrome && (
        <div style={{ position: "absolute", top: 44, left: 96, right: 96, display: "flex", justifyContent: "space-between",
          fontFamily: FONT.mono, fontSize: 20, letterSpacing: 2.4, color: COLOR.faint, textTransform: "uppercase" }}>
          <span><span style={{ display: "inline-block", width: 10, height: 10, borderRadius: 5, background: COLOR.accent, marginRight: 14 }} />
            Recorded agent session · real CLI output · {recordedOn}</span>
          <span>{kicker}</span>
        </div>
      )}
      <AbsoluteFill>{children}</AbsoluteFill>
      <div style={{ position: "absolute", left: 0, bottom: 0, height: 4, width: `${(frame / durationInFrames) * 100}%`, background: COLOR.accent, opacity: 0.6 }} />
    </AbsoluteFill>
  );
};

/** Fade wrapper so each scene enters and leaves softly. */
export const Scene = ({ children, opacity }: { children: ReactNode; opacity: number }) => (
  <AbsoluteFill style={{ opacity, padding: "140px 96px 96px" }}>{children}</AbsoluteFill>
);

export const Eyebrow = ({ children, color = COLOR.accent }: { children: ReactNode; color?: string }) => (
  <div style={{ fontFamily: FONT.mono, fontSize: 22, letterSpacing: 3, textTransform: "uppercase", color }}>{children}</div>
);
