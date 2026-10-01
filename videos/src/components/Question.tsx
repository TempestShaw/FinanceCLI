import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLOR, FONT } from "../theme";
import { enter, sceneOpacity, typed } from "../motion";
import { Eyebrow, Scene } from "./Stage";

interface QuestionProps { lead: string; detail?: string; footnote?: string }

/** Opening beat: the user's question, typed, with no product branding. */
export const Question = ({ lead, detail, footnote }: QuestionProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const shown = typed(lead, frame, 10, 34);
  const done = shown.length === lead.length;
  const caretOn = !done || Math.floor(frame / 15) % 2 === 0;
  return (
    <Scene opacity={sceneOpacity(frame, durationInFrames)}>
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%", maxWidth: 1500 }}>
        <Eyebrow>Your question</Eyebrow>
        <div style={{ fontFamily: FONT.serif, fontSize: 96, lineHeight: 1.08, letterSpacing: -1, fontWeight: 600, marginTop: 36 }}>
          “{shown}{done ? "”" : ""}<span style={{ color: COLOR.accent, opacity: caretOn ? 1 : 0, marginLeft: 6 }}>▍</span>
        </div>
        {detail && (
          <div style={{ ...enter(frame, 10 + (lead.length / 34) * 30 + 6), fontSize: 36, lineHeight: 1.45, color: COLOR.muted, marginTop: 40, maxWidth: 1300 }}>
            {detail}
          </div>
        )}
        {footnote && (
          <div style={{ ...enter(frame, 10 + (lead.length / 34) * 30 + 24), fontFamily: FONT.mono, fontSize: 24, color: COLOR.faint, marginTop: 56 }}>
            {footnote}
          </div>
        )}
      </div>
    </Scene>
  );
};
