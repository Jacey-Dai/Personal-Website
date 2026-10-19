"""Run with blender --background --python tools/inspect_art_models.py -- SOURCE_DIR."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

root = Path(sys.argv[sys.argv.index("--") + 1])
for path in sorted(root.rglob("*.gltf")):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(path))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    points = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
    print("MODEL " + json.dumps({"name": path.stem, "min": [round(min(p[i] for p in points),3) for i in range(3)], "max": [round(max(p[i] for p in points),3) for i in range(3)], "materials": list({slot.name for o in meshes for slot in o.data.materials})}))
