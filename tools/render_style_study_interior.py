"""Style study 02: Project Studio interior corner built from the same Medieval modules.

python3 tools/render_style_study_interior.py SOURCES DIRECTION OUT.png [samples]
"""
import sys
import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
direction, out = ARGS[1], ARGS[2]
samples = int(ARGS[3]) if len(ARGS) > 3 else 64

from pathlib import Path
SRC = Path(ARGS[0]) / 'assests'
PACKS = {'M': 'Medieval Village MegaKit[Standard]', 'N': 'Stylized Nature MegaKit[Standard]'}
_cache = {}

def load(kind, name):
    """Import a glTF once; return a hidden template collection reused via linked duplicates."""
    key = (kind, name)
    if key not in _cache:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(SRC/PACKS[kind]/'glTF'/f'{name}.gltf'))
        objs = [o for o in bpy.data.objects if o not in before]
        coll = bpy.data.collections.new(f'T/{name}')
        for o in objs:
            for c in list(o.users_collection): c.objects.unlink(o)
            coll.objects.link(o)
        _cache[key] = coll
    return _cache[key]

def place(kind, name, loc=(0,0,0), rot=0, scale=1, parent=None):
    inst = bpy.data.objects.new(f'{name}', None)
    inst.instance_type = 'COLLECTION'
    inst.instance_collection = load(kind, name)
    bpy.context.scene.collection.objects.link(inst)
    inst.location = loc; inst.rotation_euler.z = rot; inst.scale = (scale,)*3
    if parent: inst.parent = parent
    return inst

def empty(name, loc=(0,0,0), rot=0, scale=1):
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e)
    e.location = loc; e.rotation_euler.z = rot; e.scale = (scale,)*3
    return e

L = {'storybook': dict(sun=(1, .9, .78), e=4.0, rot=(math.radians(52), 0, math.radians(-150)), sky=(.62, .74, .92), sky_e=.7, lamp=0, look='AgX - Punchy', sat=.88),
     'toybox': dict(sun=(1, .98, .95), e=3.2, rot=(math.radians(40), 0, math.radians(-150)), sky=(.85, .88, .95), sky_e=1.2, lamp=0, look='AgX - Base Contrast', sat=.8),
     'lantern': dict(sun=(1, .62, .38), e=2.6, rot=(math.radians(72), 0, math.radians(-160)), sky=(.3, .32, .55), sky_e=.5, lamp=120, look='AgX - Medium High Contrast', sat=.95)}[direction]


def srgb(h):
    v = [int(h.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(c/12.92 if c < .04045 else ((c+.055)/1.055)**2.4 for c in v) + (1,)


def box(loc, dims, mat, bevel=.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object
    o.dimensions = dims; bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('b', 'BEVEL'); b.width, b.segments = bevel, 2
    return o


# Floor of original wood planks, two walls with the original windows and timber grid.
for x in (-2, 0, 2):
    for y in (-2, 0, 2):
        place('M', 'Floor_WoodLight', (x, y, 0))
for x in (-2, 0, 2):
    place('M', 'Wall_Plaster_Window_Wide_Round' if x != 0 else 'Wall_Plaster_WoodGrid', (x, 3, 0), math.pi)
    if x != 0:
        place('M', 'Window_Wide_Round1', (x, 3.05, 0), math.pi)
for y in (-2, 0, 2):
    place('M', 'Wall_Plaster_Straight' if y != 0 else 'Wall_Plaster_Window_Wide_Round', (-3, y, 0), -math.pi/2)
    if y == 0:
        place('M', 'Window_Wide_Round1', (-3.05, y, 0), -math.pi/2)
place('M', 'Corner_Exterior_Wood', (-3, 3, 0))

# Reuse the pack's own wood material for furniture so the room matches the exterior trim.
load('M', 'Prop_Crate')
wood = next(m for m in bpy.data.materials if 'WoodTrim' in m.name)
paper = bpy.data.materials.new('blueprint'); paper.use_nodes = True
nt = paper.node_tree; p = nt.nodes['Principled BSDF']
g = nt.nodes.new('ShaderNodeTexBrick'); g.inputs['Scale'].default_value = 14; g.inputs['Mortar Size'].default_value = .03
g.offset = 0; g.inputs['Color1'].default_value = srgb('#2f5f93'); g.inputs['Color2'].default_value = srgb('#2f5f93')
g.inputs['Mortar'].default_value = srgb('#9cc0e4'); g.inputs['Brick Width'].default_value = .5; g.inputs['Row Height'].default_value = .5
nt.links.new(g.outputs['Color'], p.inputs['Base Color'])
cream = bpy.data.materials.new('cream'); cream.use_nodes = True
cream.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = srgb('#f4ead2')
clay = bpy.data.materials.new('clay'); clay.use_nodes = True
clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = srgb('#d2735a')

# Workbench with blueprint (hotspot 1).
box((-.4, 1.6, .92), (2.6, 1.3, .12), wood)
for dx in (-1.55, .75):
    for dy in (1.1, 2.1):
        box((dx, dy, .45), (.14, .14, .9), wood, .01)
box((-.5, 1.55, .99), (1.5, .95, .015), paper, 0)
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=.07, depth=1.0, location=(.45, 1.55, 1.04)); bpy.context.object.rotation_euler.x = math.pi/2
bpy.context.object.data.materials.append(cream)
# Prototype table with small models (hotspot 2).
box((1.6, -.9, .7), (1.4, 1.1, .1), wood)
for dx in (1.05, 2.15):
    for dy in (-1.35, -.45):
        box((dx, dy, .33), (.12, .12, .66), wood, .01)
for i, (dx, dy, h) in enumerate([(1.3, -.8, .35), (1.65, -1.1, .22), (1.95, -.7, .45)]):
    box((dx, dy, .75 + h/2), (.25, .25, h), clay if i != 1 else cream, .04)
# Shelf of project files against the left wall (hotspot 3).
for z in (.5, 1.3, 2.1):
    box((-2.7, -1.0, z), (.45, 1.8, .07), wood, .01)
for i in range(9):
    z = (.5, 1.3, 2.1)[i // 3]
    box((-2.7, -1.6 + (i % 3)*.5 + (i % 2)*.08, z + .3), (.32, .14 + .04*(i % 2), .5), clay if i % 3 == 0 else cream if i % 3 == 1 else paper, .01)
for y in (-1.9, -.1):
    box((-2.7, y, 1.2), (.45, .07, 2.4), wood, .01)
place('M', 'Prop_Crate', (1.8, 2.1, 0), .3, .7)
place('N', 'Plant_1', (2.55, 1.0, .26), 0, .4)
bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=.2, depth=.26, location=(2.55, 1.0, .13))
bpy.context.object.data.materials.append(clay)

for m in bpy.data.materials:
    if m.use_nodes and not m.get('styled'):
        pr = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if pr and pr.inputs['Base Color'].links:
            src = pr.inputs['Base Color'].links[0].from_socket
            hsv = m.node_tree.nodes.new('ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = L['sat']; hsv.inputs['Value'].default_value = 1.15 if 'Plaster' in m.name else 1.0
            m.node_tree.links.new(src, hsv.inputs['Color']); m.node_tree.links.new(hsv.outputs['Color'], pr.inputs['Base Color'])
        m['styled'] = 1

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8; sc.cycles.transparent_max_bounces = 24
sc.render.resolution_x, sc.render.resolution_y = 1200, 900
sc.render.film_transparent = True
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = L['look']
w = bpy.data.worlds.new('sky'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = L['sky'] + (1,); w.node_tree.nodes['Background'].inputs[1].default_value = L['sky_e']
bpy.ops.object.light_add(type='SUN'); s = bpy.context.object
s.rotation_euler = L['rot']; s.data.energy = L['e']; s.data.color = L['sun']; s.data.angle = math.radians(3)
bpy.ops.object.light_add(type='AREA', location=(14, -18, 16)); fill = bpy.context.object
fill.data.size = 14; fill.data.energy = {'storybook': 9000, 'toybox': 14000, 'lantern': 3500}[direction]
fill.data.color = (.85, .9, 1) if direction != 'lantern' else (.6, .6, .9)
fill.rotation_euler = (Vector((0, 0, 1)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
if L['lamp']:
    bpy.ops.object.light_add(type='POINT', location=(-.3, 1.2, 2.2)); lp = bpy.context.object
    lp.data.energy = L['lamp']; lp.data.color = (1, .7, .4); lp.data.shadow_soft_size = .3
bpy.ops.object.camera_add(); cam = bpy.context.object
t = Vector((-.2, .2, 1.5)); cam.location = t + Vector((20, -30, 26))
cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type, cam.data.ortho_scale = 'ORTHO', 11
sc.camera = cam
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
