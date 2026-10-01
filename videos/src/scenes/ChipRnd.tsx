import { Series, useCurrentFrame, useVideoConfig } from "remotion";
import { caseBySlug } from "../data";
import { COLOR, FONT, seconds } from "../theme";
import { enter, sceneOpacity } from "../motion";
import { Stage, Scene, Eyebrow } from "../components/Stage";
import { Question } from "../components/Question";
import { AgentLog } from "../components/AgentLog";
import { Insight } from "../components/Insight";
import { LineChart } from "../components/LineChart";
import { FiscalTimeline } from "../components/FiscalTimeline";
import { QuoteCard } from "../components/QuoteCard";
import { EndCard } from "../components/EndCard";

const data = caseBySlug("chip-rnd");

export const CHIP_SCENES = [seconds(6), seconds(12), seconds(8), seconds(10), seconds(9), seconds(6.5)] as const;

const AlignmentScene = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <Eyebrow>Align periods before comparing</Eyebrow>
      <div style={{ ...enter(frame, 0), fontFamily: FONT.serif, fontSize: 56, fontWeight: 600, letterSpacing: -0.5, margin: "18px 0 56px" }}>
        Three companies. Three fiscal calendars.
      </div>
      <FiscalTimeline lanes={data.alignment!} colors={COLOR.series} start={10} />
      <div style={{ ...enter(frame, 70), fontSize: 28, color: COLOR.muted, marginTop: 34 }}>
        “FY2025” means a different twelve months at each company. The agent keeps every period end date with its numbers.
      </div>
    </Scene>
  );
};

const TwistScene = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const vmware = data.quotes[0];
  const nvda = data.table!.rows.filter((r) => r.ticker === "NVDA");
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <Eyebrow color={COLOR.caveat}>! The question has a trap</Eyebrow>
      <div style={{ ...enter(frame, 4), fontFamily: FONT.serif, fontSize: 56, fontWeight: 600, letterSpacing: -0.5, margin: "18px 0 48px", maxWidth: 1600 }}>
        “Fastest” depends on what you measure — and the only rising ratio came from an acquisition.
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 64 }}>
        <div style={{ ...enter(frame, 20), background: COLOR.panel, border: `1px solid ${COLOR.line}`, borderRadius: 18, padding: 36 }}>
          <div style={{ fontSize: 26, color: COLOR.muted }}>NVIDIA R&D spending</div>
          <div style={{ fontSize: 64, fontWeight: 600, marginTop: 8 }}>{nvda[0].rnd} → {nvda[2].rnd}</div>
          <div style={{ fontSize: 26, color: COLOR.muted, marginTop: 14 }}>Fastest growth in dollars — yet intensity fell {nvda[0].intensity} → {nvda[2].intensity}, because revenue grew faster.</div>
        </div>
        <QuoteCard text={vmware.text} source={vmware.source} start={36} accent={COLOR.caveat} />
      </div>
    </Scene>
  );
};

export const ChipRnd = () => {
  const [q, log, align, chart, twist, end] = CHIP_SCENES;
  const series = data.chart!.series!;
  return (
    <Stage kicker="NVDA · AMD · AVGO · latest 10-Ks">
      <Series>
        <Series.Sequence durationInFrames={q}>
          <Question lead="Who increased R&D intensity fastest?" detail="Compare NVDA, AMD and AVGO over their last three fiscal years." footnote="Same question, three companies, one workflow." />
        </Series.Sequence>
        <Series.Sequence durationInFrames={log}>
          <AgentLog title="Pull three filings. Then read the fine print." steps={data.trace} interval={seconds(1.7)} aside="3 companies · 6 tool calls" />
        </Series.Sequence>
        <Series.Sequence durationInFrames={align}><AlignmentScene /></Series.Sequence>
        <Series.Sequence durationInFrames={chart}>
          <Insight eyebrow="R&D / revenue, calculated" title={<>Only one ratio went <span style={{ color: COLOR.accent }}>up</span>.</>} metrics={data.metrics} leftWidth={560}>
            <LineChart series={series} colors={COLOR.series} xLabels={["Oldest FY", "Middle FY", "Latest FY"]} max={30} start={14} width={1100} height={600} />
          </Insight>
        </Series.Sequence>
        <Series.Sequence durationInFrames={twist}><TwistScene /></Series.Sequence>
        <Series.Sequence durationInFrames={end}>
          <EndCard lines={["Turn “compare these companies”", "into reproducible research —"]} emphasis="not twenty browser tabs." />
        </Series.Sequence>
      </Series>
    </Stage>
  );
};
