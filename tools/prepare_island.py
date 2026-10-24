"""Encode the rendered island and publish its camera-projected map anchors and building layers.

python3 tools/prepare_island.py OUTPUT [day|dusk]
OUTPUT is the folder written by tools/render_island.py and tools/export_building_layers.py.
"""
import json
import sys
from pathlib import Path
from PIL import Image

source = Path(sys.argv[1])
light = sys.argv[2] if len(sys.argv) > 2 else 'day'
root = Path(__file__).resolve().parents[1]
destination = root/'public'/'island'
destination.mkdir(parents=True, exist_ok=True)
target = destination/f'storybook-island-{light}.webp'
with Image.open(source/f'island-{light}.png') as image:
    image.save(target, quality=86, method=6)
layout = json.loads((source/'map-layout.json').read_text())
for anchor in layout.values():
    assert 0 <= anchor['x'] <= 100 and 0 <= anchor['y'] <= 100
(root/'src'/'map-layout.json').write_text(json.dumps(layout, indent=2)+'\n')
layers = source/'building-layers.json'
if layers.exists():
    (root/'src'/'building-layers.json').write_text(layers.read_text())
print(f"Island: {target.stat().st_size:,} bytes; {len(layout)} map anchors")
