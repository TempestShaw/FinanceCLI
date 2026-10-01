import { useCurrentFrame } from "remotion";
import { COLOR, FONT } from "../theme";
import { progress } from "../motion";

interface Lane { ticker: string; fy_note: string; periods: { fy: string; period_end: string }[] }

const DAY = 86_400_000;

/** Each company's fiscal years drawn on one calendar axis, so misaligned periods are visible. */
export const FiscalTimeline = ({ lanes, colors, width = 1720, start = 0 }: { lanes: Lane[]; colors: readonly string[]; width?: number; start?: number }) => {
  const frame = useCurrentFrame();
  const spans = lanes.map((lane) => lane.periods.map((p) => {
    const end = new Date(p.period_end).getTime();
    return { fy: p.fy, end, begin: end - 364 * DAY };
  }));
  const all = spans.flat();
  const min = Math.min(...all.map((s) => s.begin));
  const max = Math.max(...all.map((s) => s.end));
  const labelW = 300;
  const x = (t: number) => labelW + ((t - min) / (max - min)) * (width - labelW);
  const years = [];
  for (let y = new Date(min).getUTCFullYear() + 1; y <= new Date(max).getUTCFullYear(); y++) years.push(y);

  return (
    <svg width={width} height={lanes.length * 130 + 70} style={{ overflow: "visible" }}>
      {years.map((y) => {
        const t = Date.UTC(y, 0, 1);
        return (
          <g key={y}>
            <line x1={x(t)} x2={x(t)} y1={0} y2={lanes.length * 130} stroke={COLOR.lineStrong} strokeWidth={1.5} />
            <text x={x(t)} y={lanes.length * 130 + 44} textAnchor="middle" fill={COLOR.muted} fontSize={24} fontFamily={FONT.mono}>Jan {y}</text>
          </g>
        );
      })}
      {lanes.map((lane, li) => (
        <g key={lane.ticker} transform={`translate(0 ${li * 130 + 20})`}>
          <text x={0} y={38} fill={COLOR.text} fontSize={34} fontWeight={600}>{lane.ticker}</text>
          <text x={0} y={74} fill={COLOR.faint} fontSize={21}>FY {lane.fy_note}</text>
          {spans[li].map((s, si) => {
            const p = progress(frame, start + li * 8 + si * 5, 18);
            const x0 = x(s.begin) + 3;
            const w = (x(s.end) - x(s.begin) - 6) * p;
            return (
              <g key={s.fy}>
                <rect x={x0} y={10} width={w} height={64} rx={8} fill={`${colors[li]}33`} stroke={colors[li]} strokeWidth={2} />
                <text x={x0 + 18} y={52} fill={COLOR.text} fontSize={24} fontFamily={FONT.mono} opacity={p}>{s.fy}</text>
              </g>
            );
          })}
        </g>
      ))}
    </svg>
  );
};
