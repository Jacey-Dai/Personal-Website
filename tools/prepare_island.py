"""Encode the rendered island and publish its camera-projected map anchors.

python3 tools/prepare_island.py /tmp/soft-island
"""
import json
import sys
from pathlib import Path
from PIL import Image

source=Path(sys.argv[1])
root=Path(__file__).resolve().parents[1]
destination=root/'public'/'island'
destination.mkdir(parents=True,exist_ok=True)
with Image.open(source/'island.png') as image:
    image.save(destination/'soft-island.webp',quality=90,method=6)
layout=json.loads((source/'map-layout.json').read_text())
for anchor in layout.values():
    assert 0 <= anchor['x'] <= 100 and 0 <= anchor['y'] <= 100
(root/'src'/'map-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
print(f"Island: {(destination/'soft-island.webp').stat().st_size:,} bytes; {len(layout)} map anchors")
