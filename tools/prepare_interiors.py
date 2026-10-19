"""Encode room renders and their object coordinates for the browser."""
import json
import sys
from pathlib import Path
from PIL import Image

source=Path(sys.argv[1])
root=Path(__file__).resolve().parents[1]
target=root/'public'/'interiors'
target.mkdir(parents=True,exist_ok=True)
layout=json.loads((source/'interior-layout.json').read_text())
for room in ['about','projects','experience','beyond','currently']:
    with Image.open(source/f'{room}.png') as image:
        image.save(target/f'{room}.webp',quality=90,method=6)
    print(room,(target/f'{room}.webp').stat().st_size,'bytes')
(root/'src'/'interior-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
