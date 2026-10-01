import { useCurrentFrame } from "remotion";
import { COLOR, FONT } from "../theme";
import { enter } from "../motion";

/** A verbatim filing excerpt with its source line. */
export const QuoteCard = ({ text, source, start = 0, accent = COLOR.accent }: { text: string; source: string; start?: number; accent?: string }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ ...enter(frame, start), borderLeft: `4px solid ${accent}`, padding: "8px 0 8px 36px" }}>
      <div style={{ fontFamily: FONT.serif, fontSize: 46, lineHeight: 1.28, color: COLOR.text }}>“{text}”</div>
      <div style={{ fontFamily: FONT.mono, fontSize: 21, color: COLOR.faint, marginTop: 18, letterSpacing: 1 }}>{source}</div>
    </div>
  );
};
