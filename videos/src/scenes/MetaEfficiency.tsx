import { Series } from "remotion";
import { caseBySlug } from "../data";
import { COLOR, seconds } from "../theme";
import { Stage } from "../components/Stage";
import { Question } from "../components/Question";
import { ToolMap } from "../components/ToolMap";
import { AgentLog } from "../components/AgentLog";
import { Insight } from "../components/Insight";
import { LineChart } from "../components/LineChart";
import { Checks } from "../components/Checks";
import { EndCard } from "../components/EndCard";

const data = caseBySlug("meta-efficiency");

export const META_SCENES = [seconds(6), seconds(7), seconds(16), seconds(10), seconds(10), seconds(6.5)] as const;

export const MetaEfficiency = () => {
  const [q, map, log, chart, checks, end] = META_SCENES;
  const series = data.chart!.series!;
  const years = series[0].points.map((p) => p.x);
  const reported = series[0].points;
  const gain = Math.round(reported[2].value - reported[0].value);
  return (
    <Stage kicker="META · 10-K · 2022–2025">
      <Series>
        <Series.Sequence durationInFrames={q}>
          <Question lead="Did Meta actually become more efficient after the Year of Efficiency?" footnote="That’s the whole prompt. No tools named." />
        </Series.Sequence>
        <Series.Sequence durationInFrames={map}>
          <ToolMap title="You ask the research question." subtitle="Your agent decides which tools to use, and in what order." chosen={data.trace.map((s) => s.tool)} start={36} interval={16} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={log}>
          <AgentLog title="Statements, then headcount, then the fine print." steps={data.trace} interval={seconds(1.75)} aside="8 tool calls · 1 gap recovered" />
        </Series.Sequence>
        <Series.Sequence durationInFrames={chart}>
          <Insight eyebrow="Operating margin, calculated" title={<>Margin rose <span style={{ color: COLOR.accent }}>{gain} points</span> in two years — even without restructuring charges.</>} metrics={data.metrics.slice(0, 2)} leftWidth={600}>
            <LineChart series={series} colors={COLOR.pair} xLabels={years} max={50} min={20} start={14} width={1080} height={600} />
          </Insight>
        </Series.Sequence>
        <Series.Sequence durationInFrames={checks}>
          <Checks eyebrow="What could make this unfair" title="The agent flags what bends the comparison." checks={data.checks.slice(0, 3)} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={end}>
          <EndCard lines={["You ask the research question."]} emphasis="Your agent decides how to investigate it." />
        </Series.Sequence>
      </Series>
    </Stage>
  );
};
