# Personal Website · A Little World

An interactive floating personal island surrounded by an explorable sea. Original SVG scenery, five destinations, readable details, a dedicated mobile route, and direct navigation for recruiters. This is a framework prototype with explicit placeholders, not a completed biography.

## Local development

Node.js 24 and npm are used in development and CI.

```sh
npm ci
npm run dev
```

Vite prints the development address. Project base path: `/Personal-Website/`.

```sh
npm test
npm run build
npm run preview
npx playwright install chromium
npx playwright test
```

`npm test` validates content/navigation contracts; Playwright checks actual routing, keyboard return focus, history, mobile layout and reduced motion. The production build outputs `dist/`.

On machines with an existing Chromium installation, use `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium npx playwright test` instead of downloading another browser. If the default npm cache is not writable, pass `--cache /tmp/personal-island-npm-cache` to installation commands.

## Structure and collaboration

An isolated art-direction sample lives at `art-study.html`: two color treatments using the owner-supplied CC0 Quaternius models. It does not replace the homepage. Reproduction and decisions: [docs/art-study.md](docs/art-study.md).

- `src/content.js`: personal content and explicit placeholders.
- `src/world.js`: original editable SVG artwork.
- `src/main.js`: accessible navigation, dialogs, visits and hash routes.
- `src/styles.css`: responsive layout, provisional palette, motion preferences.
- `docs/design.md`: world composition and development stages.
- `docs/decisions.md`: confirmed vs provisional decisions.
- `docs/assets.md`: asset provenance and animation strategy.
- `docs/content-guide.md`: real content needed next.
- `AGENTS.md`: shared conventions for Codex, Claude, and human contributors.

Use short branches and reviewable commits. Agree on file ownership before concurrent editing. Keep real content separate from the world illustration. Never invent personal history or achievements.

## GitHub Pages

The included workflow builds and deploys pushes to `main`. In GitHub repository Settings → Pages, select **GitHub Actions** as the source. This settings change may require repository administrator access. Actual deployment success must be checked in Actions; the presence of a workflow does not mean the site is published.

Hash links such as `/Personal-Website/#projects` can be shared and refreshed without a server rewrite. If the repository name or hosting base changes, update `vite.config.js`. A future Professional version can consume the same content data.

Before sharing as a finished portfolio, replace the placeholders and add the real resume, contact links and project evidence. Language, final palette and bespoke illustration details are still open for review.
