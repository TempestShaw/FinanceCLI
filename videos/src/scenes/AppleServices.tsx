import { Series, useCurrentFrame, useVideoConfig } from "remotion";
import { caseBySlug } from "../data";
import { COLOR, FONT, seconds } from "../theme";
import { enter, sceneOpacity } from "../motion";
import { Stage, Scene, Eyebrow } from "../components/Stage";
import { Question } from "../components/Question";
import { AgentLog } from "../components/AgentLog";
import { Checks } from "../components/Checks";
import { Insight } from "../components/Insight";
import { BarChart } from "../components/BarChart";
import { EvidenceTable } from "../components/EvidenceTable";
import { QuoteCard } from "../components/QuoteCard";
import { EndCard } from "../components/EndCard";

const data = caseBySlug("apple-services");

export const APPLE_SCENES = [
  seconds(6.5), seconds(14.5), seconds(8), seconds(10), seconds(9), seconds(8), seconds(7),
] as const;

const TableScene = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const table = data.table!;
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <Eyebrow>The research artifact</Eyebrow>
      <div style={{ ...enter(frame, 0), fontFamily: FONT.serif, fontSize: 52, fontWeight: 600, letterSpacing: -0.5, margin: "16px 0 30px" }}>Every number, its fiscal year and its filing.</div>
      <EvidenceTable columns={table.columns} rows={table.rows} start={8} interval={7} />
      <div style={{ ...enter(frame, 60), fontSize: 22, color: COLOR.faint, marginTop: 22 }}>{table.caption}</div>
    </Scene>
  );
};

const GapScene = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const drivers = data.quotes[0];
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%", maxWidth: 1500 }}>
        <Eyebrow color={COLOR.caveat}>! What the filing doesn’t say</Eyebrow>
        <div style={{ ...enter(frame, 4), fontFamily: FONT.serif, fontSize: 60, fontWeight: 600, letterSpacing: -0.6, margin: "20px 0 48px" }}>Growth drivers are named — not sized.</div>
        <QuoteCard text={drivers.text} source={drivers.source} start={18} accent={COLOR.caveat} />
        <div style={{ ...enter(frame, 52), fontSize: 32, color: COLOR.muted, marginTop: 48, lineHeight: 1.45 }}>
          No amount is disclosed for advertising, the App Store or cloud. The answer reports that gap instead of filling it with an estimate.
        </div>
      </div>
    </Scene>
  );
};

export const AppleServices = () => {
  const [q, log, checks, chart, table, gap, end] = APPLE_SCENES;
  return (
    <Stage kicker="AAPL · 10-K · FY2020–FY2025">
      <Series>
        <Series.Sequence durationInFrames={q}>
          <Question lead="Has Apple become more dependent on Services?" detail="Is growth coming from Services or hardware? Give me each year’s numbers — and where every number came from." footnote="No workflow given. The agent chooses the tools." />
        </Series.Sequence>
        <Series.Sequence durationInFrames={log}>
          <AgentLog title="Find the filings. Read the statements. Check them." steps={data.trace} interval={seconds(1.75)} aside="7 tool calls" />
        </Series.Sequence>
        <Series.Sequence durationInFrames={checks}>
          <Checks eyebrow="Normalize before calculating" title="Same units, same fiscal years, no silent restatements." checks={data.checks.slice(0, 3)} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={chart}>
          <Insight eyebrow="Calculated from the filings" title={<>Services went from <span style={{ color: COLOR.accent }}>a fifth</span> of sales to over <span style={{ color: COLOR.accent }}>two-fifths</span> of gross margin.</>} metrics={data.metrics.slice(0, 2)}>
            <BarChart points={data.chart!.points!} primaryLabel="Share of net sales" secondaryLabel="Share of gross margin" max={50} start={14} />
          </Insight>
        </Series.Sequence>
        <Series.Sequence durationInFrames={table}><TableScene /></Series.Sequence>
        <Series.Sequence durationInFrames={gap}><GapScene /></Series.Sequence>
        <Series.Sequence durationInFrames={end}>
          <EndCard lines={["One question.", "Several research tools."]} emphasis="Every number traceable to its source." />
        </Series.Sequence>
      </Series>
    </Stage>
  );
};
