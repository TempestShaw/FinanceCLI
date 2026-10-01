import { Easing, interpolate, spring } from "remotion";
import { FPS } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.22, 1, 0.36, 1);

/** 0 → 1 over `duration` frames starting at `start`. */
export const progress = (frame: number, start: number, duration: number) =>
  interpolate(frame, [start, start + duration], [0, 1], { ...clamp, easing: ease });

/** Opacity + upward drift for an element entering at `start`. */
export const enter = (frame: number, start: number, distance = 24, duration = 18) => {
  const p = progress(frame, start, duration);
  return { opacity: p, transform: `translateY(${(1 - p) * distance}px)` };
};

/** Fade a whole scene in at its start and out before its end. */
export const sceneOpacity = (frame: number, length: number, fade = 12) =>
  interpolate(frame, [0, fade, length - fade, length], [0, 1, 1, 0], clamp);

export const pop = (frame: number, start: number) =>
  spring({ frame: frame - start, fps: FPS, config: { damping: 14, stiffness: 160 } });

/** Characters of `text` visible at `frame`, typed at `cps` characters per second. */
export const typed = (text: string, frame: number, start: number, cps = 40) => {
  const count = Math.max(0, Math.floor(((frame - start) / FPS) * cps));
  return text.slice(0, count);
};

/** Evenly spaced axis ticks on a round step (5, 10, 20, 25 or 50) with at most six intervals. */
export const niceTicks = (min: number, max: number) => {
  const span = max - min;
  const step = [5, 10, 20, 25, 50].find((s) => span % s === 0 && span / s <= 6) ?? span / 4;
  return Array.from({ length: Math.round(span / step) + 1 }, (_, i) => min + i * step);
};
