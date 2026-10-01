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
      {chrome && (
        <div style={{ position: "absolute", top: 44, left: 96, right: 96, display: "flex", justifyContent: "space-between",
          fontFamily: FONT.sans, fontWeight: 600, fontSize: 20, letterSpacing: 1.6, color: COLOR.muted, textTransform: "uppercase", borderBottom: `2px solid ${COLOR.text}`, paddingBottom: 14 }}>
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
  <div style={{ fontFamily: FONT.sans, fontWeight: 600, fontSize: 22, letterSpacing: 2, textTransform: "uppercase", color: COLOR.muted, display: "flex", alignItems: "center", gap: 16 }}><span style={{ width: 36, height: 3, background: color }} />{children}</div>
);
