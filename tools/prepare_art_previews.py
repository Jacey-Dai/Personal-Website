"""Encode rendered PNGs for the website and retain the exact supplied license notices.

python3 tools/prepare_art_previews.py /tmp/island-art-renders /tmp/island-art-sources
Requires Pillow. Encoding only: no retouching or geometry changes.
"""
import sys
from pathlib import Path
from PIL import Image

renders, sources = map(Path, sys.argv[1:])
root = Path(__file__).resolve().parents[1]
destination = root / "public" / "art-study"
destination.mkdir(parents=True, exist_ok=True)
for variant in ("coral-coast", "violet-coast"):
    with Image.open(renders / f"{variant}.png") as image:
        image.save(destination / f"{variant}.webp", quality=90, method=6)
    print(f"{variant}.webp: {(destination / f'{variant}.webp').stat().st_size:,} bytes")
licenses = root / "docs" / "licenses"
licenses.mkdir(parents=True, exist_ok=True)
for pack, name in [("Medieval Village MegaKit[Standard]", "quaternius-medieval-standard.txt"), ("Stylized Nature MegaKit[Standard]", "quaternius-nature-standard.txt")]:
    (licenses / name).write_bytes((sources / "assests" / pack / "License_Standard.txt").read_bytes())
