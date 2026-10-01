import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadSerif } from "@remotion/google-fonts/InstrumentSerif";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

const inter = loadInter("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin"] });
const serif = loadSerif("italic", { weights: ["400"], subsets: ["latin"] });
const mono = loadMono("normal", { weights: ["400", "500"], subsets: ["latin"] });

export const FONT = {
  sans: inter.fontFamily,
  serif: serif.fontFamily,
  mono: mono.fontFamily,
} as const;

export const COLOR = {
  ink: "#0b1511",
  panel: "#111f19",
  panelRaised: "#16281f",
  line: "#24382f",
  lineStrong: "#36503f",
  text: "#f3f1e7",
  muted: "#a9bbaf",
  faint: "#71877a",
  accent: "#b6e6af",
  accentDeep: "#6fbf6a",
  // Status colors carry an icon and a label wherever they appear.
  verified: "#0ca30c",
  caveat: "#fab219",
  missing: "#ec835a",
  // Categorical slots 1–3, validated all-pairs against the ink surface.
  series: ["#3987e5", "#d95926", "#199e70"],
  pair: ["#199e70", "#3987e5"],
} as const;

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const seconds = (s: number) => Math.round(s * FPS);
