# Personal island: design and development plan

## Composition

An imaginary island inside a floating patch of sea. A visible soil underside makes this a complete miniature world; water fading outward suggests further exploration. Use a shallow isometric viewpoint, a compact silhouette, and short internal routes. No globe rotation, geographic travel, or mandatory game mechanics.

The Welcome Center sits centrally; Experience Museum is northwest; Project Studio southwest; Curiosity Garden southeast; Currently northeast. A southern pier meets a small boat. A short eastern bridge leads to a nearby rock. Keep all essential information on the main island. Distant scenery must not appear interactive without content.

## Current visual direction

Owner approved the Quaternius-based local sample, with lower saturation. The complete island now uses soft coral roofs, blue-gray museum, sage greenhouse, cream walls, and muted sea blue. Buildings retain toy-like volume. Typography and bespoke personal details remain provisional. Use horizontal readable labels and paper-backed text.

The framework now uses an optimized model-rendered WebP scene with HTML location links, pointer shortcuts over buildings, and separately maintained projected map anchors. The image is decorative; content and navigation remain accessible HTML. Original SVG and earlier saturated samples are historical iterations, not the active homepage artwork. See docs/framework.md for reproduction. Personal details should eventually determine objects and architecture.

## Interaction

Direct quick navigation: About, Projects, Experience, Beyond, Resume, Contact. All five map locations are links with visible standard labels. Hover and focus reveal previews. Hash links open a native accessible dialog; Escape, close, back-to-island, and browser history work. Return focus to the originating control. Visited marks are optional session-local decoration, never a gate.

First implementation uses a short panel entrance rather than a map zoom; validate composition before adding camera movement. The boat opens Currently. The wheel and bridge are decorative in this iteration. No fake interactive scenery.

Mobile shows a small world overview followed by a vertical path of full-sized destination cards with cropped scene thumbnails and previews. Desktop building shortcuts are hidden on mobile. It does not shrink desktop hotspots. Closing details restores route position.

## Content

Projects: problem, role/team, methods, process/decisions, outcome/evidence, reflection/links. Experience: readable work/internship and education records, later connected to related projects. Garden: community, volunteering, leadership, and small personal stories. Currently: short dated learning/making/exploring entries. Missing real data remains explicitly marked.

## Stages

1. Framework: original vector world, five places, mobile route, details, hash links, motion preferences, documentation and build pipeline.
2. Visual prototype feedback: island/sea balance, illustration style, color tests, navigation readability. Confirm primary language; current English copy is provisional.
3. Real content and distinctive details: verified profile, project case studies, timeline, garden stories, resume/social links.
4. Refinement: scene fragments on mobile, optional tiny camera approach, a meaningful personal Easter egg, accessibility/performance review and publication.

Professional version can reuse content data in a linear reading layout. Do not create a second source of truth for projects or resume information.
