# Spatial building experience — current contract

This supersedes the map-plus-cards framework documented in `framework.md`.

## Owner's four corrections

1. Names and purpose appear when hovering a building. Equivalent keyboard focus and touch identification are required.
2. The homepage contains the world, not a below-map collection of buildings or a portfolio introduction.
3. Visiting changes the actual building rather than showing a `visited` badge.
4. Entering a building should preserve its character as a space, not merely open another webpage.

## Homepage

One viewport, map-only, on both desktop and mobile. A compact fixed quick-navigation bar keeps About, Projects, Experience, Beyond, Resume and Contact direct. Small help/reset/credit controls do not create a lower content section.

`building-layers.json` is exported from the saved Blender scene: each building has a projected convex-hull silhouette, roof coordinate and visible glass geometry. Camera-space ray tests exclude windows hidden behind roofs/walls. The native HTML links expose names and categories to assistive technology while their visual names live in a single tooltip. Hit surfaces follow the building shapes, not detached name cards.

Desktop pointer hover and keyboard focus show the name, standard category and short preview. On touch, first tap identifies and second tap enters. Quick navigation remains one tap. Mobile enlarges the central map within a clipped viewport; the main island and all five buildings remain reachable without scrolling a long map. It intentionally no longer uses the earlier route/card layout, per the latest user correction.

## Physical visit changes

An SVG overlay in the same 1800×1400 camera space adds warm light to the building's authored glass faces and raises a small pennant on its roof. These are scene geometry, not text badges or counters. Only visited buildings show them. Greenhouse glass uses lower light opacity.

`localStorage` key `island-building-lights-v1` retains the state in that browser. Storage failure does not block exploration. Reset lights clears only this local decorative state. It does not erase content. Flags are decoration and do not unlock anything.

## Two-stage interiors

Entering opens a full-viewport cutaway room with the same soft colors, wood, trim and isometric camera language as the exterior. Each room has three keyboard-accessible object hotspots and a fast route to its index. These are original rendered interior geometries, not third-party game screenshots.

| Exterior | Interior | Objects / readable artifact |
|---|---|---|
| Welcome Center | Reception desk, map board, brochures, letterbox | Guestbook, resume brochure, contact letters |
| Project Studio | Workbench, prototype table, project wall, shelves | Blueprint and prototype case studies, project file index |
| Experience Museum | Columns, framed exhibits, plinth, timeline rail, archive cabinet | Work archive and education exhibit records |
| Curiosity Garden | Greenhouse ribs, growing beds, plants, potting bench | Community stories and curiosity field journal |
| Currently | Pinned bulletin board, update desk, supplies | Learning and making notes |

Selecting an object opens a separate readable artifact while keeping the room behind it: blueprint grid, archive record, ruled garden journal, pinned note, or guestbook. Long content remains semantic HTML; it is never baked into an image. Missing personal content remains explicit placeholders.

Routes such as `#projects/project-01`, `#experience/work`, `#beyond/community` and `#currently/learning` can be shared and reloaded. `#resume` and `#contact` enter reception and open the corresponding artifact directly.

Escape closes the artifact first, then the room. Back buttons and browser history also work. Keyboard focus returns to the map building, or to the object after reading. A compact quick-destination selector remains available while reading; visitors do not have to close a book to find Resume or Contact. `prefers-reduced-motion` removes transitions and shimmer.

## Implementation

- `src/main.js`: map controls, persistent lights, tooltips and layered routing.
- `src/interiors.js`: room identity, object names, room markup and image references.
- `src/notebooks.js`: reading artifacts and use of real/placeholder content data.
- `src/content.js`: personal content, draft cases and utility copy.
- `src/building-layers.json`: generated map silhouettes, flags and light paths.
- `src/interior-layout.json`: generated room-object positions.
- `public/interiors/*.webp`: five room renders, requested only when entering their room.
- `tools/export_building_layers.py`: exports overlays/hit shapes from the original island blend and camera.
- `tools/render_interiors.py`, `tools/prepare_interiors.py`: render and encode interiors plus object coordinates.

No runtime 3D/game engine is used. Original Quaternius notices remain in `docs/licenses/`; exterior model provenance is unchanged.

## Reproduce

First reproduce the exterior with `framework.md`, preserving its scene/camera. Then:

```sh
blender --background /tmp/soft-island/island.blend --threads 4 --python tools/export_building_layers.py -- "$PWD/src/building-layers.json"
blender --background --threads 4 --python tools/render_interiors.py -- /tmp/island-interiors
python3 tools/prepare_interiors.py /tmp/island-interiors
npm test
npm run build
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium npx playwright test
```

Blender 4.3.2, CPU Cycles 32 samples, 1600×1100, Pillow encoding. These are authoring dependencies, not browser downloads. Do not edit exported geometry by hand when changing camera or objects.

## Validation

The spatial browser suite replaces obsolete assertions for persistent labels and the mobile building list. It checks map-only layout at 320–1440px, hover/focus identification, actual nonempty roof/light overlays and persistence, each room/artifact pair, reading→room→map Escape behavior, direct project routes/history, two-tap touch behavior, and reduced motion/direct resume/contact access. The earlier art-study page remains available as a historical comparison.
