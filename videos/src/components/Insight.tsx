import { useCurrentFrame, useVideoConfig } from "remotion";
import type { ReactNode } from "react";
import type { Metric } from "../data";
import { COLOR } from "../theme";
import { enter, sceneOpacity } from "../motion";
import { Eyebrow, Scene } from "./Stage";

interface InsightProps { eyebrow: string; title: ReactNode; metrics?: Metric[]; children?: ReactNode; leftWidth?: number }

/** Two columns: the finding in words and numbers on the left, the visual proof on the right. */
export const Insight = ({ eyebrow, title, metrics = [], children, leftWidth = 640 }: InsightProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <div style={{ display: "flex", gap: 80, height: "100%", alignItems: "center" }}>
        <div style={{ width: leftWidth, flexShrink: 0 }}>
          <Eyebrow>{eyebrow}</Eyebrow>
          <div style={{ ...enter(frame, 4), fontSize: 54, fontWeight: 600, letterSpacing: -1.6, lineHeight: 1.12, margin: "22px 0 44px" }}>{title}</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 26 }}>
            {metrics.map((m, i) => (
              <div key={m.label} style={{ ...enter(frame, 20 + i * 10), borderTop: `1px solid ${COLOR.lineStrong}`, paddingTop: 18 }}>
                <div style={{ fontSize: 22, color: COLOR.muted }}>{m.label}</div>
                <div style={{ display: "flex", alignItems: "baseline", gap: 20, marginTop: 6 }}>
                  <span style={{ fontSize: 56, fontWeight: 600, letterSpacing: -1.5, fontVariantNumeric: "tabular-nums" }}>{m.value}</span>
                  <span style={{ fontSize: 22, color: COLOR.faint }}>{m.delta}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div style={{ flex: 1, ...enter(frame, 10, 30, 24) }}>{children}</div>
      </div>
    </Scene>
  );
};
