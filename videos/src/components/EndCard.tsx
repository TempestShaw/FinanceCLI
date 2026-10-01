import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLOR, FONT } from "../theme";
import { enter, sceneOpacity } from "../motion";
import { Scene } from "./Stage";

interface EndCardProps { lines: string[]; emphasis?: string }

export const Logo = ({ size = 72 }: { size?: number }) => (
  <div style={{ display: "flex", alignItems: "center", gap: size * 0.3 }}>
    <div style={{ width: size, height: size, borderRadius: size * 0.24, background: COLOR.accent, color: COLOR.ink, display: "grid", placeItems: "center",
      fontFamily: FONT.serif, fontSize: size * 0.82, lineHeight: 1 }}>ƒ</div>
    <div style={{ fontSize: size * 0.62, fontWeight: 700, letterSpacing: -1.5 }}>Finance CLI</div>
  </div>
);

/** Closing beat: the takeaway, then the product, then how to install it. */
export const EndCard = ({ lines, emphasis }: EndCardProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const brandAt = 12 + lines.length * 16 + (emphasis ? 18 : 0);
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames, 10)}>
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%" }}>
        {lines.map((line, i) => (
          <div key={line} style={{ ...enter(frame, 12 + i * 16), fontFamily: FONT.serif, fontSize: 76, fontWeight: 600, letterSpacing: -0.8, lineHeight: 1.12 }}>{line}</div>
        ))}
        {emphasis && (
          <div style={{ ...enter(frame, 12 + lines.length * 16), fontFamily: FONT.serif, fontSize: 84, color: COLOR.accent, lineHeight: 1.12, marginTop: 4 }}>{emphasis}</div>
        )}
        <div style={{ ...enter(frame, brandAt), marginTop: 84, display: "flex", alignItems: "center", gap: 56 }}>
          <Logo />
          <div style={{ fontSize: 30, color: COLOR.muted, lineHeight: 1.4 }}>Financial research tools for AI agents.<br />Open source · runs locally · SEC data needs no paid key.</div>
        </div>
        <div style={{ ...enter(frame, brandAt + 12), marginTop: 40, display: "flex", gap: 40, fontFamily: FONT.mono, fontSize: 28 }}>
          <span style={{ padding: "14px 22px", border: `1px solid ${COLOR.lineStrong}`, borderRadius: 12, background: COLOR.panel }}>
            <span style={{ color: COLOR.faint }}>$ </span>pip install finresearch-cli</span>
          <span style={{ padding: "14px 0", color: COLOR.muted }}>tempestshaw.github.io/FinanceCLI</span>
        </div>
      </div>
    </Scene>
  );
};
