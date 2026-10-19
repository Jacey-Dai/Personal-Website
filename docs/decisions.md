# Decision log

## Confirmed by the owner

- Combine A's sea, boat, bridge and exploration feeling with B's overall floating island.
- Preserve all five conceptual layers and recruiter-friendly direct navigation.
- GitHub source control and GitHub Pages hosting; support future collaboration with Claude.
- Missing personal content must be explicit placeholders.

## Implementation choices for review

- Vite + native JavaScript modules + SVG/CSS. A component framework is unnecessary for the current five-destination prototype.
- Hash routes work with project-site GitHub Pages without a server fallback. Base path: /Personal-Website/.
- System fonts avoid external font dependencies. English prototype copy is provisional; primary language remains undecided.
- Native dialog supplies modal semantics and focus containment. Session storage is optional and failures must not break navigation.
- Original SVG scenes use no external illustration assets. CSS animates only small decorative elements and respects reduced motion.
- CI checks data contracts and production build. Browser integration tests run separately using Playwright.

## Not final

Palette, fonts, personal name/positioning, final architecture details, case-study layouts, custom domain, camera movement, mobile scene fragments, and Professional version styling.

## Art direction study after first publication

- Owner rejected the muted SVG illustration style and requested bold colors and game-like volume.
- Owner provided Quaternius Medieval Village, Downtown City and Stylized Nature Standard assets via `assets/source-packs`.
- License notices checked: CC0 1.0. Medieval + Nature are tested in a separate coastal sample, with original sea/terrain/boat and recolored materials.
- `art-study.html` compares two palettes using static pre-rendered WebP images. This does not change the homepage or commit to live 3D.
- Final choice awaits viewing the sample; see `docs/art-study.md`.
