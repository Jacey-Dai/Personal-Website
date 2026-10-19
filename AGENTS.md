# Shared working agreement

- Preserve the five layers: miniature personal world, island silhouette, creative town, playful facilities, exploration map. The approved direction combines B's floating island with A's sea, boat, pier, and short bridge.
- Read docs/design.md and docs/decisions.md before changing the design. Proposed colors and typography are provisional.
- Never invent personal history, project results, employers, metrics, or contact details. Keep missing content visibly marked.
- Content belongs in src/content.js; artwork in src/world.js; interaction in src/main.js. Keep all public strings under review when adding a language.
- Use the existing checkout. Do not create a worktree unless explicitly requested.
- Run npm ci, npm test, npm run build. Browser checks: npx playwright test (browser installation may be needed).
- Preserve keyboard access, dialog focus restoration, hash deep links, reduced motion, and the dedicated mobile route layout.
- Coordinate file ownership before concurrent edits. Use small commits and reviewable branches; do not overwrite other contributors' work.
- No secrets, invented links, or unlicensed artwork. Record external asset sources and licenses in docs/assets.md.
