import { useCurrentFrame } from "remotion";
import type { Claim } from "../data";
import { COLOR, FONT } from "../theme";
import { enter } from "../motion";
import { StatusBadge } from "./Checks";

/** Claim → evidence → source → verdict, one row per claim. */
export const ClaimsTable = ({ claims, start = 0, interval = 34 }: { claims: Claim[]; start?: number; interval?: number }) => {
  const frame = useCurrentFrame();
  const template = "430px 1fr 250px";
  return (
    <div style={{ border: `1px solid ${COLOR.line}`, borderRadius: 18, overflow: "hidden", background: COLOR.panel }}>
      <div style={{ display: "grid", gridTemplateColumns: template, gap: 30, padding: "16px 28px", background: COLOR.panelRaised,
        fontFamily: FONT.mono, fontSize: 19, letterSpacing: 1.5, textTransform: "uppercase", color: COLOR.faint }}>
        <div>Claim</div><div>Evidence · source</div><div>Verdict</div>
      </div>
      {claims.map((c, i) => {
        const at = start + 8 + i * interval;
        return (
          <div key={c.claim} style={{ display: "grid", gridTemplateColumns: template, gap: 30, padding: "15px 28px", borderTop: `1px solid ${COLOR.line}`, alignItems: "center", ...enter(frame, at, 12, 12) }}>
            <div style={{ fontSize: 26, fontWeight: 600, lineHeight: 1.25 }}>{c.claim}</div>
            <div>
              <div style={{ fontSize: 22, lineHeight: 1.35, color: COLOR.muted }}>{c.kind === "quoted" ? `“${c.evidence}”` : c.evidence}</div>
              <div style={{ fontFamily: FONT.mono, fontSize: 16, color: COLOR.faint, marginTop: 6 }}>{c.kind.toUpperCase()} · {c.source}</div>
            </div>
            <div style={enter(frame, at + 14, 8, 10)}><StatusBadge status={c.status} size={20} /></div>
          </div>
        );
      })}
    </div>
  );
};
