"""Export precise building silhouettes and lit-window geometry from the saved island.

python3 tools/export_building_layers.py ISLAND.blend OUTPUT.json
  (bpy module; or: blender --background ISLAND.blend --python tools/export_building_layers.py -- OUTPUT.json)
No new render is needed; the SVG coordinates use the saved camera and resolution.
Buildings are the objects tools/render_island.py tagged with a `place` property.
"""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
if len(args) > 1:
    bpy.ops.wm.open_mainfile(filepath=args[0])
output = Path(args[-1])
scene = bpy.context.scene
camera = scene.camera
width, height = scene.render.resolution_x, scene.render.resolution_y
# Original Quaternius window glass, plus the greenhouse's own glass.
GLASS = ('WindowGlass', 'glass')


def project(point):
    p = world_to_camera_view(scene, camera, point)
    return (round(p.x*width, 2), round((1-p.y)*height, 2))


def hull(points):
    points = sorted(set(points))
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]


data = {}
depsgraph = bpy.context.evaluated_depsgraph_get()
view_direction = (camera.matrix_world.to_quaternion()@Vector((0, 0, 1))).normalized()
for root in sorted((o for o in scene.objects if 'place' in o), key=lambda o: o['place']):
    key = root['place']
    objects = [o.evaluated_get(depsgraph) for o in root.children_recursive if o.type in ('MESH', 'CURVE')]
    meshes = [(o, o.to_mesh()) for o in objects]
    world_points = [o.matrix_world@v.co for o, me in meshes for v in me.vertices]
    outline = hull([project(p) for p in world_points])
    minx, miny = min(p[0] for p in outline), min(p[1] for p in outline)
    maxx, maxy = max(p[0] for p in outline), max(p[1] for p in outline)
    # The flag stands on the highest point of the building (ridge, greenhouse rail).
    roof = max(world_points, key=lambda p: p.z)
    glassy = {o.original for o, me in meshes
              if any(s.material and any(g in s.material.name for g in GLASS) for s in o.material_slots)}
    polygons = []
    for o, me in meshes:
        for poly in me.polygons:
            material = o.material_slots[poly.material_index].material if o.material_slots else None
            if not material or not any(g in material.name for g in GLASS):
                continue
            normal = o.matrix_world.to_3x3()@poly.normal
            center = o.matrix_world@poly.center
            # Greenhouse panes are single planes: either side may face the camera.
            if normal.dot(camera.location - center) < 0 and not material.name.startswith('glass'):
                continue
            # Reject windows hidden behind roofs/walls. Facing the camera
            # alone is insufficient for a projected light overlay.
            hit = scene.ray_cast(depsgraph, center + view_direction*100, -view_direction, distance=100.01)
            if not hit[0] or hit[4].original not in glassy:
                continue
            coords = [project(o.matrix_world@me.vertices[i].co) for i in poly.vertices]
            polygons.append('M'+' L'.join(f'{x},{y}' for x, y in coords)+' Z')
    data[key] = {
        'left': round(minx/width*100, 3), 'top': round(miny/height*100, 3),
        'width': round((maxx-minx)/width*100, 3), 'height': round((maxy-miny)/height*100, 3),
        'clip': 'polygon('+','.join(f'{(x-minx)/(maxx-minx)*100:.2f}% {(y-miny)/(maxy-miny)*100:.2f}%' for x, y in outline)+')',
        'roof': project(roof),
        'lights': ' '.join(polygons),
    }
    for o, _ in meshes:
        o.to_mesh_clear()
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(data, indent=2)+'\n')
print('Exported silhouettes, roof flags and window geometry for', len(data), 'buildings:',
      {k: v['lights'].count('M') for k, v in data.items()})
