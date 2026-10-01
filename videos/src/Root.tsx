import { Composition } from "remotion";
import type { ComponentType } from "react";
import { FPS, HEIGHT, WIDTH } from "./theme";
import { AppleServices, APPLE_SCENES } from "./scenes/AppleServices";
import { ChipRnd, CHIP_SCENES } from "./scenes/ChipRnd";
import { MetaEfficiency, META_SCENES } from "./scenes/MetaEfficiency";
import { CostcoThesis, COSTCO_SCENES } from "./scenes/CostcoThesis";
import { DataGap, GAP_SCENES } from "./scenes/DataGap";

const total = (scenes: readonly number[]) => scenes.reduce((sum, n) => sum + n, 0);

// Composition ids match the showcase case slugs so the site can find each video.
export const VIDEOS: { id: string; component: ComponentType; scenes: readonly number[] }[] = [
  { id: "apple-services", component: AppleServices, scenes: APPLE_SCENES },
  { id: "chip-rnd", component: ChipRnd, scenes: CHIP_SCENES },
  { id: "meta-efficiency", component: MetaEfficiency, scenes: META_SCENES },
  { id: "costco-thesis", component: CostcoThesis, scenes: COSTCO_SCENES },
  { id: "data-gap", component: DataGap, scenes: GAP_SCENES },
];

export const Root = () => (
  <>
    {VIDEOS.map((v) => (
      <Composition key={v.id} id={v.id} component={v.component} durationInFrames={total(v.scenes)} fps={FPS} width={WIDTH} height={HEIGHT} />
    ))}
  </>
);
