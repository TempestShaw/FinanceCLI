import { useCurrentFrame } from "remotion";
import type { Series } from "../data";
import { COLOR, FONT } from "../theme";
import { niceTicks, progress } from "../motion";

interface LineChartProps {
  series: Series[];
  colors: readonly string[];
  xLabels: string[];
  max: number;
  min?: number;
  width?: number;
  height?: number;
  start?: number;
  unit?: string;
  labelFor?: (series: Series) => string;
}

/** Lines draw left to right; each series is labelled directly at its last point. */
export const LineChart = ({ series, colors, xLabels, max, min = 0, width = 1100, height = 560, start = 0, unit = "%", labelFor }: LineChartProps) => {
  const frame = useCurrentFrame();
  const pad = { top: 30, right: 230, bottom: 64, left: 80 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const x = (i: number) => pad.left + (xLabels.length === 1 ? plotW / 2 : (plotW * i) / (xLabels.length - 1));
  const y = (v: number) => pad.top + plotH - ((v - min) / (max - min)) * plotH;
  const ticks = niceTicks(min, max);

  return (
    <svg width={width} height={height} style={{ overflow: "visible" }}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={pad.left} x2={pad.left + plotW} y1={y(t)} y2={y(t)} stroke={COLOR.line} strokeWidth={1.5} />
          <text x={pad.left - 16} y={y(t) + 8} textAnchor="end" fill={COLOR.faint} fontSize={22} fontFamily={FONT.mono}>{Math.round(t)}{unit}</text>
        </g>
      ))}
      {xLabels.map((label, i) => (
        <text key={label} x={x(i)} y={pad.top + plotH + 44} textAnchor="middle" fill={COLOR.muted} fontSize={24} fontFamily={FONT.mono}>{label}</text>
      ))}
      {series.map((s, si) => {
        const p = progress(frame, start + si * 10, 40);
        const pts = s.points.map((pt, i) => [x(i), y(pt.value)] as const);
        const length = pts.slice(1).reduce((acc, [px, py], i) => acc + Math.hypot(px - pts[i][0], py - pts[i][1]), 0);
        const lastPt = pts[pts.length - 1];
        const lastVal = s.points[s.points.length - 1].value;
        // A series that stops early is labelled above its last point so it can't sit on another line.
        const endsEarly = s.points.length < xLabels.length;
        const labelX = endsEarly ? lastPt[0] : lastPt[0] + 24;
        const labelY = endsEarly ? lastPt[1] - 26 : lastPt[1] + 9;
        return (
          <g key={s.key}>
            <polyline points={pts.map(([px, py]) => `${px},${py}`).join(" ")} fill="none" stroke={colors[si]} strokeWidth={4}
              strokeLinejoin="round" strokeLinecap="round" strokeDasharray={length} strokeDashoffset={length * (1 - p)} />
            {pts.map(([px, py], i) => (
              <circle key={i} cx={px} cy={py} r={9} fill={colors[si]} stroke={COLOR.ink} strokeWidth={3}
                opacity={p >= (i / Math.max(1, pts.length - 1)) - 0.001 ? 1 : 0} />
            ))}
            <g opacity={progress(frame, start + si * 10 + 36, 10)}>
              <text x={labelX} y={labelY} textAnchor={endsEarly ? "middle" : "start"} fill={COLOR.text} fontSize={28} fontWeight={600}>
                {labelFor ? labelFor(s) : s.key} <tspan fill={COLOR.muted} fontWeight={400}>{lastVal.toFixed(1)}{unit}</tspan>
              </text>
            </g>
          </g>
        );
      })}
    </svg>
  );
};
