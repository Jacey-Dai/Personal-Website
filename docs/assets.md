# Illustration, animation, and asset sources

## Assets actually used

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
