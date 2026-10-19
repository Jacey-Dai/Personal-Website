# Soft-color personal island framework

Historical framework iteration. Its composition/render reproduction still applies. The homepage lists, persistent labels, visited badges and generic content layers have been superseded by `spatial-experience.md` according to the owner's latest corrections.

## Scope

The owner liked the Quaternius sample palette and requested lower overall saturation and a working web skeleton. The active homepage is now a complete island, replacing the original flat SVG illustration. It is still a content scaffold: no employers, achievements, project outcomes or social URLs have been invented.

## Composition and palette

All five layers remain: complete miniature world, sea-surrounded floating island, compact creative town, amusement details, and connected exploration map. The central Welcome kiosk/plaza connects a coral-roof studio, blue-gray museum, sage greenhouse and pink noticeboard kiosk. A small wheel, pier, boat and short bridge add playfulness. They do not gate any content; the wheel and bridge remain decorative.

Scene colors live in `tools/render_island.py`: coral `#cc7d73`, blue-gray `#576c88`, sea `#91cbd0`, meadow `#afc58a`, cream `#f0d6a3`. These are quieter than the saturated A/B samples, while retaining clear silhouettes and material contrast. UI text uses independent dark colors; do not reduce text contrast when tuning illustration colors.

## Files and layers

- `src/content.js`: stable place IDs, content placeholders, project draft structures and credit copy.
- `src/world.js`: rendered-image URL and decorative scene wrapper.
- `src/map-layout.json`: world-space anchors projected to percentage image coordinates by Blender.
- `src/main.js`: navigation, visible location links, pointer shortcuts, route rendering, native dialog, optional visited storage and focus/scroll restoration.
- `src/styles.css`: responsive map, mobile route and section-specific layouts. Formatted source for shared maintenance.
- `public/island/soft-island.webp`: optimized 1800×1400 render. The browser does not load models, Blender or WebGL.
- `tools/render_island.py` and `tools/prepare_island.py`: reproducible scene construction and encoding.

Changing the camera or composition requires regenerating both image and anchors. The label offsets in `src/main.js` are intentional layout adjustments to avoid obscuring buildings. Cropped mobile/detail thumbnails use the source anchors, not label offsets.

## Content layers

- About: explicit name/tagline placeholders, short introduction sections, resume/contact entry points.
- Projects: two explicitly marked draft cards, each with its own reloadable hash route and six-section case-study structure.
- Experience: work/internship and education timeline scaffolds.
- Beyond: community and personal-interest story cards.
- Currently: two updateable noticeboard entries with an explicit missing-date state.
- Resume/Contact: explain missing verified content; no broken downloads or invented addresses.
- Credits: records Quaternius and CC0 provenance.

Desktop shows the complete island within a typical first viewport and fixed quick navigation. Mobile uses the same world overview, then a vertical route with destination thumbnails and permanently visible previews. Details are readable full-width modal layers, with Escape, back-to-island, browser history and focus restoration. Motion is decorative and disabled by prefers-reduced-motion.

## Reproduce artwork

Uses the same fixed owner-supplied CC0 commit and extraction script as `docs/art-study.md`. Blender 4.3.2 and Pillow are authoring tools only.

```sh
git fetch origin refs/heads/assets/source-packs:refs/remotes/origin/assets/source-packs
python3 tools/extract_art_sample.py /tmp/island-art-sources
blender --background --threads 4 --python tools/render_island.py -- /tmp/island-art-sources /tmp/soft-island
python3 tools/prepare_island.py /tmp/soft-island
npm test
npm run build
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium npx playwright test
```

The model scene uses supplied wall, roof, door, window, wooden-floor, crate, tree, bush and rock geometry. Original elements include terrain, fountain/plaza, greenhouse, wheel, sign, bridge, sailboat, paths and pier supports. Source notices remain in `docs/licenses/`; Downtown is not used.

## Next content work

Replace name/positioning and biography, choose real projects, fill experience dates and records, supply resume/social links, then add real garden stories and Currently updates. Further interaction and camera effects should follow content and feedback rather than precede them.
