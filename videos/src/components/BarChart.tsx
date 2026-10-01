import { useCurrentFrame } from "remotion";
import type { Point } from "../data";
import { COLOR, FONT } from "../theme";
import { niceTicks, progress } from "../motion";

interface BarChartProps {
  points: Point[];
  primaryLabel: string;
  secondaryLabel?: string;
  max: number;
  width?: number;
  height?: number;
  start?: number;
  unit?: string;
}

// Two-measure charts use a validated categorical pair; a single measure keeps the brand accent.
const PAIR = COLOR.pair;

/** Bars grow from the baseline, one per period; an optional second measure sits beside each bar. */
export const BarChart = ({ points, primaryLabel, secondaryLabel, max, width = 1040, height = 560, start = 0, unit = "%" }: BarChartProps) => {
  const frame = useCurrentFrame();
  const pad = { top: 30, right: 20, bottom: 64, left: 72 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const group = plotW / points.length;
  const hasSecondary = points.some((p) => p.secondary !== undefined);
  const barW = hasSecondary ? Math.min(54, group * 0.32) : Math.min(84, group * 0.56);
  const ticks = niceTicks(0, max);
  const y = (v: number) => pad.top + plotH - (v / max) * plotH;
  const last = points.length - 1;
  const primary = hasSecondary ? PAIR[0] : COLOR.accent;

  const bar = (value: number, x: number, color: string, delay: number) => {
    const h = (value / max) * plotH * progress(frame, start + delay, 22);
    const top = pad.top + plotH - h;
    const r = Math.min(4, h);
    return <path d={`M${x},${pad.top + plotH} V${top + r} q0,-${r} ${r},-${r} H${x + barW - r} q${r},0 ${r},${r} V${pad.top + plotH} Z`} fill={color} />;
  };

  return (
    <div>
      <div style={{ display: "flex", gap: 36, fontSize: 24, color: COLOR.muted, marginBottom: 18 }}>
        <span><i style={{ display: "inline-block", width: 18, height: 18, borderRadius: 4, background: primary, marginRight: 10, verticalAlign: -2 }} />{primaryLabel}</span>
        {secondaryLabel && <span><i style={{ display: "inline-block", width: 18, height: 18, borderRadius: 4, background: PAIR[1], marginRight: 10, verticalAlign: -2 }} />{secondaryLabel}</span>}
      </div>
      <svg width={width} height={height} style={{ overflow: "visible" }}>
        {ticks.map((t) => (
          <g key={t}>
            <line x1={pad.left} x2={width - pad.right} y1={y(t)} y2={y(t)} stroke={COLOR.line} strokeWidth={1.5} />
            <text x={pad.left - 16} y={y(t) + 8} textAnchor="end" fill={COLOR.faint} fontSize={22} fontFamily={FONT.mono}>{Math.round(t)}{unit}</text>
          </g>
        ))}
        {points.map((p, i) => {
          const cx = pad.left + group * i + group / 2;
          const x1 = hasSecondary ? cx - barW - 2 : cx - barW / 2;
          const labelled = i === 0 || i === last;
          const grown = progress(frame, start + i * 5, 22);
          return (
            <g key={p.x}>
              {bar(p.value, x1, primary, i * 5)}
              {p.secondary !== undefined && bar(p.secondary, cx + 2, PAIR[1], i * 5 + 3)}
              <text x={cx} y={pad.top + plotH + 44} textAnchor="middle" fill={COLOR.muted} fontSize={24} fontFamily={FONT.mono}>{p.x}</text>
              {labelled && (
                <g opacity={grown}>
                  <text x={x1 + barW / 2} y={y(p.value) - 14} textAnchor="middle" fill={COLOR.text} fontSize={26} fontWeight={600}>{p.value.toFixed(1)}{unit}</text>
                  {p.secondary !== undefined && (
                    <text x={cx + 2 + barW / 2} y={y(p.secondary) - 14} textAnchor="middle" fill={COLOR.text} fontSize={26} fontWeight={600}>{p.secondary.toFixed(1)}{unit}</text>
                  )}
                </g>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
};
