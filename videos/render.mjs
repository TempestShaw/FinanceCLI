// Render every showcase video to docs-site/public/videos, plus a poster frame for each.
// Usage: npm run render [-- apple-services chip-rnd]
import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = join(here, "..", "docs-site", "public", "videos");

// Poster = a frame from each video's main finding (the chart, claims or gap scene).
const POSTERS = {
  "apple-services": 1120,
  "chip-rnd": 1030,
  "meta-efficiency": 1120,
  "costco-thesis": 840,
  "data-gap": 665,
};

const ids = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(POSTERS);
mkdirSync(outDir, { recursive: true });

for (const id of ids) {
  if (!(id in POSTERS)) throw new Error(`Unknown video id: ${id}`);
  const remotion = (...args) => execFileSync("npx", ["remotion", ...args, "--log=error"], { cwd: here, stdio: "inherit" });
  console.log(`Rendering ${id}…`);
  remotion("render", "src/index.ts", id, join(outDir, `${id}.mp4`), "--crf=23");
  remotion("still", "src/index.ts", id, join(outDir, `${id}.jpg`), `--frame=${POSTERS[id]}`, "--image-format=jpeg", "--jpeg-quality=82");
}
