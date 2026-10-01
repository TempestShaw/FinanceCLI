import { useCurrentFrame } from "remotion";
import type { Column } from "../data";
import { COLOR, FONT } from "../theme";
import { enter } from "../motion";

interface EvidenceTableProps { columns: Column[]; rows: Record<string, string>[]; start?: number; interval?: number; fontSize?: number; highlight?: (row: Record<string, string>) => boolean }

/** A research table whose rows arrive one by one; source columns render in mono. */
export const EvidenceTable = ({ columns, rows, start = 0, interval = 6, fontSize = 27, highlight }: EvidenceTableProps) => {
  const frame = useCurrentFrame();
  const template = columns.map((c) => (c.key === "source" ? "1.6fr" : c.align === "end" ? "1fr" : "0.9fr")).join(" ");
  const cell = (c: Column) => ({ textAlign: c.align === "end" ? ("right" as const) : ("left" as const), fontVariantNumeric: "tabular-nums" as const });
  return (
    <div style={{ border: `1px solid ${COLOR.line}`, borderRadius: 18, overflow: "hidden", background: COLOR.panel }}>
      <div style={{ display: "grid", gridTemplateColumns: template, gap: 24, padding: "18px 30px", background: COLOR.panelRaised,
        fontFamily: FONT.mono, fontSize: 19, letterSpacing: 1.5, textTransform: "uppercase", color: COLOR.faint, ...enter(frame, start, 12) }}>
        {columns.map((c) => <div key={c.key} style={cell(c)}>{c.label}</div>)}
      </div>
      {rows.map((row, i) => (
        <div key={i} style={{ display: "grid", gridTemplateColumns: template, gap: 24, padding: "16px 30px", borderTop: `1px solid ${COLOR.line}`,
          fontSize, background: highlight?.(row) ? `${COLOR.accent}12` : "transparent", ...enter(frame, start + 8 + i * interval, 14, 12) }}>
          {columns.map((c) => (
            <div key={c.key} style={{ ...cell(c), fontFamily: c.key === "source" ? FONT.mono : FONT.sans, fontSize: c.key === "source" ? fontSize - 6 : fontSize,
              color: c.key === "source" ? COLOR.muted : COLOR.text, fontWeight: c.align === "end" ? 500 : 400, paddingTop: c.key === "source" ? 3 : 0 }}>
              {row[c.key]}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};
