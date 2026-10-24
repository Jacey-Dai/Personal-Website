# Shared working agreement

- For the current visual redesign, read docs/PRD-visual-redesign.md first. The owner is reconsidering the current aesthetics; the older soft-palette instruction below is a historical working direction, not a fixed color requirement. English language, resume, profile and public contact links are already supplied in src/profile.js and public/resume/.

- Preserve the five layers: miniature personal world, island silhouette, creative town, playful facilities, exploration map. The approved direction combines B's floating island with A's sea, boat, pier, and short bridge.
- Read docs/spatial-experience.md and docs/decisions.md before changing the design. The owner's latest requirements override the earlier framework: map-only homepage, hover/focus/touch identification, physical building changes after visits, and spatial interiors. Keep the approved storybook daylight direction (docs/visual-redesign.md).
- Never invent personal history, project results, employers, metrics, or contact details. Keep missing content visibly marked.
- Content belongs in src/content.js; room objects in src/interiors.js; readable artifacts in src/notebooks.js; interaction in src/main.js. Scene generation lives in tools/. building-layers.json and interior-layout.json are generated camera-space geometry; regenerate rather than guessing hotspot coordinates.
- Use the existing checkout. Do not create a worktree unless explicitly requested.
- Run npm ci, npm test, npm run build. Browser checks: npx playwright test (browser installation may be needed).
- Preserve keyboard access, layered Escape/back behavior, hash deep links and reduced motion. Both desktop and mobile homepages show only the map with compact navigation. Do not restore the obsolete mobile list of buildings. Touch identifies on first tap and enters on second; quick navigation opens rooms directly.
- Visited state must alter the scene's windows/roof flag and persist locally, not become a visible visited label. Rooms must stay spatial scenes with interactable objects; do not replace them with generic content panels.
- Coordinate file ownership before concurrent edits. Use small commits and reviewable branches; do not overwrite other contributors' work.
- No secrets, invented links, or unlicensed artwork. Record external asset sources and licenses in docs/assets.md.
