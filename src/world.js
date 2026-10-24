// Pre-rendered from the owner's CC0 Quaternius assets. See tools/render_island.py.
import layout from "./map-layout.json";
export const mapLayout = layout;
export const islandImage = `${import.meta.env.BASE_URL}island/storybook-island-day.webp`;
export const worldArt = `<img class="island-image" src="${islandImage}" width="1800" height="1400" alt="" fetchpriority="high" decoding="async" /><div class="sea-glimmer" aria-hidden="true"></div>`;
