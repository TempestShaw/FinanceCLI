import { Series, useCurrentFrame, useVideoConfig } from "remotion";
import { caseBySlug } from "../data";
import { COLOR, seconds } from "../theme";
import { enter, sceneOpacity } from "../motion";
import { Stage, Scene, Eyebrow } from "../components/Stage";
import { Question } from "../components/Question";
import { AgentLog } from "../components/AgentLog";
import { ClaimsTable } from "../components/ClaimsTable";
import { Insight } from "../components/Insight";
import { BarChart } from "../components/BarChart";
import { EndCard } from "../components/EndCard";

const data = caseBySlug("costco-thesis");

export const COSTCO_SCENES = [seconds(6.5), seconds(8.5), seconds(14), seconds(10), seconds(7)] as const;

const ClaimsScene = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <Eyebrow>Thesis → claims → evidence</Eyebrow>
      <div style={{ ...enter(frame, 0), fontSize: 50, fontWeight: 600, letterSpacing: -1.5, margin: "14px 0 26px" }}>Each claim gets evidence, a source and a verdict.</div>
      <ClaimsTable claims={data.claims!} start={6} interval={seconds(1.6)} />
    </Scene>
  );
};

export const CostcoThesis = () => {
  const [q, log, claims, verdict, end] = COSTCO_SCENES;
  return (
    <Stage kicker="COST · 10-K · FY2020–FY2025">
      <Series>
        <Series.Sequence durationInFrames={q}>
          <Question lead="Costco’s membership model makes its earnings more resilient." detail="Test this thesis." footnote="A thesis, not “tell me about Costco.”" />
        </Series.Sequence>
        <Series.Sequence durationInFrames={log}>
          <AgentLog title="Find the numbers that could prove it wrong." steps={data.trace} interval={seconds(1.6)} aside="4 tool calls" />
        </Series.Sequence>
        <Series.Sequence durationInFrames={claims}><ClaimsScene /></Series.Sequence>
        <Series.Sequence durationInFrames={verdict}>
          <Insight eyebrow="Verdict" title={<>Partly supported. <span style={{ color: COLOR.caveat }}>Resilience itself is untested</span> — profit rose every year.</>} metrics={data.metrics.slice(0, 2)} leftWidth={640}>
            <BarChart points={data.chart!.points!} primaryLabel="Membership fees as % of operating income" max={80} start={12} />
          </Insight>
        </Series.Sequence>
        <Series.Sequence durationInFrames={end}>
          <EndCard lines={["Don’t ask your agent to", "“tell me about Costco.”"]} emphasis="Give it a thesis. Make it prove or disprove it." />
        </Series.Sequence>
      </Series>
    </Stage>
  );
};
