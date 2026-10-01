import { Series, useCurrentFrame, useVideoConfig } from "remotion";
import { caseBySlug } from "../data";
import { COLOR, FONT, seconds } from "../theme";
import { enter, sceneOpacity } from "../motion";
import { Stage, Scene, Eyebrow } from "../components/Stage";
import { Question } from "../components/Question";
import { Checks } from "../components/Checks";
import { EndCard } from "../components/EndCard";

const data = caseBySlug("data-gap");

export const GAP_SCENES = [seconds(5.5), seconds(10), seconds(9), seconds(7)] as const;

const GapCard = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const gap = data.gap!;
  const rows: [string, string, string][] = [
    ["Available", gap.available, COLOR.verified],
    ["Missing", gap.missing, COLOR.missing],
    ["Reason", gap.reason, COLOR.muted],
  ];
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%" }}>
        <Eyebrow>The answer</Eyebrow>
        <div style={{ ...enter(frame, 0), fontSize: 64, fontWeight: 600, letterSpacing: -2, margin: "18px 0 44px" }}>Not disclosed — and here’s exactly what is.</div>
        <div style={{ fontFamily: FONT.mono, background: COLOR.panel, border: `1px solid ${COLOR.lineStrong}`, borderRadius: 18, padding: "34px 40px", fontSize: 30, lineHeight: 1.5 }}>
          {rows.map(([label, value, color], i) => (
            <div key={label} style={{ ...enter(frame, 14 + i * 12), display: "grid", gridTemplateColumns: "220px 1fr", gap: 24, padding: "8px 0" }}>
              <span style={{ color }}>{label}:</span><span style={{ color: COLOR.text }}>{value}</span>
            </div>
          ))}
          <div style={{ ...enter(frame, 60), borderTop: `1px solid ${COLOR.line}`, marginTop: 18, paddingTop: 22, color: COLOR.accent }}>{gap.policy}</div>
        </div>
      </div>
    </Scene>
  );
};

export const DataGap = () => {
  const [q, search, card, end] = GAP_SCENES;
  return (
    <Stage kicker="AAPL · 10-K · FY2025">
      <Series>
        <Series.Sequence durationInFrames={q}>
          <Question lead="How much revenue does the App Store make?" footnote="A plausible-sounding number is one search away. Is it in the filing?" />
        </Series.Sequence>
        <Series.Sequence durationInFrames={search}>
          <Checks eyebrow="Four places checked" title="Named once. Never sized." checks={data.checks} interval={seconds(1.5)} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={card}><GapCard /></Series.Sequence>
        <Series.Sequence durationInFrames={end}>
          <EndCard lines={["Sometimes the right answer is:"]} emphasis="“The filing doesn’t disclose that.”" />
        </Series.Sequence>
      </Series>
    </Stage>
  );
};
