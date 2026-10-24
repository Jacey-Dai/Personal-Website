# Illustration, animation, and asset sources

## Assets actually used

Storybook redesign (2026-10): the homepage island (`public/island/storybook-island-day.webp`) and all five rooms (`public/interiors/`) are rendered from the owner's Quaternius Medieval Village and Stylized Nature Standard models with their original textures, by `tools/render_island.py` and `tools/render_interiors.py` (shared helpers in `tools/quaternius_kit.py`). Same pinned source commit and CC0 1.0 licenses; no new external assets. Terrain, sea, foam, greenhouse frame, wheel, boat, noticeboard and furniture are original geometry, mostly wearing the pack's own wood, plaster and brick materials. See `docs/visual-redesign.md`. The notes below describe earlier iterations.

Current spatial layer: the original model-rendered exterior remains; `src/building-layers.json` exports its actual glass faces and roof positions as SVG overlays. `public/interiors/` contains original cutaway-room renders made by `tools/render_interiors.py`. No new external models or licenses are involved. Room object positions are generated with their images. See `docs/spatial-experience.md`.

The active homepage now uses `public/island/soft-island.webp`, built from the same owner-supplied CC0 Medieval and Nature models with softer colors. `tools/render_island.py` assembles the full scene and `tools/prepare_island.py` encodes it and exports projected map anchors. See `docs/framework.md`. The original SVG notes below describe the first iteration only; no SVG map remains in the current homepage.

The separate `art-study.html` prototype uses owner-supplied Quaternius models from `assets/source-packs`, pinned at `7b16930628d5adc01c6e5f98afde99199ea21e3a`. Medieval Village and Stylized Nature Standard license files explicitly state CC0 1.0 and are retained in `docs/licenses/`. See `docs/art-study.md` and `tools/extract_art_sample.py` for selection and reproduction. Downtown was reviewed but is not used. The main island below remains the original SVG version.

- src/world.js: original SVG geometry authored for this repository: terrain, sea, buildings, greenhouse, wheel, boat, bridge, pier, trees and flowers. No third-party image files.
- Fonts: local system font stack and Georgia. No remote font requests.
- Motion: local CSS transforms/opacity. No animation library or video assets.

The generated comparison image discussed in chat is a reference, not a shipped production asset. An AI-generated single image can help explore composition but does not provide independently editable buildings or accessible controls.

## Optional references, not incorporated

- https://undraw.co/illustrations — possible supporting illustrations. Check the current license before use and adapt only if compatible with the world.
- https://www.opendoodles.com/ — possible loose hand-drawn motifs; verify the current license for the exact downloaded asset.
- https://fonts.google.com/ — possible later font trials, e.g. Bricolage Grotesque and DM Sans. Verify each font license and prefer self-hosting if selected.

Prefer original cohesive vectors over mixing stock packs. If external assets are added, record the exact asset URL, author, license, required attribution, local path, and modifications here. Do not assume a website-wide label covers every download.

## Motion budget

First version: gentle boat bob, subtle wave opacity, small hover movement, short dialog entrance. No audio, autoplay video, large canvas, WebGL, or perpetual JavaScript animation loop. Disable decorative motion when prefers-reduced-motion is enabled. Future motion must explain an action or add a meaningful personal detail.
