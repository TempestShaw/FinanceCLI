import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadSerif } from "@remotion/google-fonts/SourceSerif4";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

const inter = loadInter("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin"] });
const serif = loadSerif("normal", { weights: ["600"], subsets: ["latin"] });
const mono = loadMono("normal", { weights: ["400", "500"], subsets: ["latin"] });

export const FONT = {
  sans: inter.fontFamily,
  serif: serif.fontFamily,
  mono: mono.fontFamily,
} as const;

export const COLOR = {
  ink: "#fafaf8",        // page surface (kept as "ink" so components stay unchanged)
  panel: "#ffffff",
  panelRaised: "#f4f4f1",
  line: "#e2e2dd",
  lineStrong: "#c9c9c2",
  text: "#111418",
  muted: "#4a5058",
  faint: "#6b7178",
  accent: "#0f7b52",
  accentDeep: "#0b5e3e",
  // Status colors carry an icon and a label wherever they appear.
  verified: "#0f7b52",
  caveat: "#9a6200",
  missing: "#b4462a",
  // Categorical slots 1–3, validated all-pairs against the light surface.
  series: ["#2a78d6", "#eb6834", "#1baf7a"],
  pair: ["#1baf7a", "#2a78d6"],
} as const;

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const seconds = (s: number) => Math.round(s * FPS);
