# Storybook daylight · visual redesign

Implements `docs/PRD-visual-redesign.md`. Phase 1 compared three directions in `style-study.html`. On 2026-10-24 the owner liked both A (Storybook daylight) and C (Golden-hour lantern) and asked to build one first, with changing light (day/night over time) as a later feature. A is the active direction; C is kept as a `dusk` lighting preset over identical geometry and camera.

## What changed

- **Materials.** The island and rooms use the uploaded Quaternius models' own textures (plaster, round tiles, wood trim, brick, uneven brick, floors, crates, plants), gently desaturated (×0.88) instead of being repainted flat. Each destination keeps an identity through a hue shift of the same tile texture: Project Studio terracotta, Experience Museum slate, Welcome Center sage, Noticeboard mustard, greenhouse glass.
- **Foliage.** The free Nature pack lacks its stylised shader, so leaf cards get spherical custom normals plus 35% translucency and a value lift. Crowns read as soft volumes rather than black clumps; they are still slightly darker than the pack's promotional images.
- **Ground and sea.** The meadow has subtle colour variation and a rounded edge over a sand beach. Paths are pressed RockPath stones over a faint dirt underlay, not raised ribbons. The sea grades from shallow turquoise to deep blue, has a broken foam band, and fades into the page instead of ending in a hard plate rim.
- **Buildings.** Built on the 2-unit module grid from walls, windows, doors, corners, roofs and gable fronts. The museum is the uneven-brick building with a plaster colonnade; the greenhouse remains original geometry with succulents inside and by the door.
- **Interiors.** All five rooms are built from the same modules (walls with real windows, wood/brick floors, crates, plants), with simple furniture wearing the pack's own wood, plaster and brick materials. No text is baked into images. Object hotspot ids are unchanged.
- **Interface.** Warm paper (`#fffaf0`), ink (`#2f2a24`, soft `#5c5144`), terracotta accent (`#a24f3a`), line `#d9cbb0`. Tooltips are paper tags with a pin; object hotspots are larger pulsing rings (static under reduced motion). Minimum font size is 11px and body reading text 15px. The wordmark shows Jacey Dai.
- **Mobile.** The map plane is 190vw on narrow screens so the island fills the width and buildings are easier to tap; quick navigation wraps instead of overflowing at 320px.

## Preserved

Map-only homepage, hover/focus/two-tap identification, window lights and roof flags after visits (persisted under `island-building-lights-v1`), cutaway rooms with three objects each, readable HTML artifacts, Escape/back layering, hash routes, quick navigation, reduced motion, real content and placeholders.

## Reproduce

Python 3.13 with `pip install bpy==5.1.2` (Blender 5.1 as a module) replaces a Blender install; `blender --background --python SCRIPT -- ARGS` also works.

```sh
git fetch origin refs/heads/assets/source-packs:refs/remotes/origin/assets/source-packs
mkdir -p /tmp/island-src && git archive origin/assets/source-packs \
  "assests/Medieval Village MegaKit[Standard]/glTF" "assests/Stylized Nature MegaKit[Standard]/glTF" | tar -x -C /tmp/island-src
python3 tools/render_island.py /tmp/island-src /tmp/island day 96          # ~4 min on 4 CPU cores
python3 tools/export_building_layers.py /tmp/island/island.blend /tmp/island/building-layers.json
python3 tools/prepare_island.py /tmp/island day
python3 tools/render_interiors.py /tmp/island-src /tmp/rooms day 96        # ~12 min for five rooms
python3 tools/prepare_interiors.py /tmp/rooms
```

Shared helpers (model loading, restyling, foliage normals, lighting presets) live in `tools/quaternius_kit.py`. Change the camera, a building or an object, and regenerate the images, `building-layers.json`, `map-layout.json` and `interior-layout.json` together; never edit coordinates by hand. Window lights come from faces using the pack's `MI_WindowGlass` or the greenhouse's `glass…` material.

## Day/night later

Rendering with `dusk` instead of `day` produces matching images (same camera, same hotspots). A time-based switch then only needs the second set of WebP files and a small selection rule in `src/world.js` and `src/interiors.js`. Lit windows in the dusk set would make the visited-state overlay less distinct, so the overlay may need a brighter treatment at night.
