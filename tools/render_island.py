"""Build the storybook island from the owner's CC0 Quaternius models, keeping their textures.

python3 tools/render_island.py SOURCES OUTPUT [day|dusk] [samples]
  (bpy 5.1 module; or: blender --background --python tools/render_island.py -- SOURCES OUTPUT)
SOURCES holds `assests/` from the assets/source-packs branch (see docs/framework.md).
OUTPUT receives island.png, island.blend and map-layout.json. Then run
tools/export_building_layers.py on island.blend for hit shapes, window lights and flags.
`dusk` keeps geometry and camera identical, for a later day/night switch.
"""
import json
import math
import random
import sys
from pathlib import Path
import bpy  # first: the bpy module provides bmesh and mathutils
import bmesh
from mathutils import Vector, noise
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
source, output = Path(args[0]), Path(args[1])
light = args[2] if len(args) > 2 else 'day'
samples = int(args[3]) if len(args) > 3 else 96
preview = int(args[4]) if len(args) > 4 else 100
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quaternius_kit import (empty, flat, light_scene, make_real, pack_material, place, restyle, retint,
                            set_source, soften_foliage, srgb, tinted)

output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
set_source(source)
random.seed(11)
GROUND = 1.0

# ---------- Island: meadow, beach and a cliff that disappears into the sea ----------
OUTLINE = []
for i in range(96):
    a = i * math.tau / 96
    r = 1 + .045*math.sin(3*a) + .03*math.cos(5*a) + .015*math.sin(11*a)
    OUTLINE.append((12.6*r*math.cos(a), 9.8*r*math.sin(a)))


def slab(name, scale, z0, z1, material, bevel=0, taper=1.0, segments=4):
    bm = bmesh.new()
    top = [bm.verts.new((x*scale, y*scale, z1)) for x, y in OUTLINE]
    bottom = [bm.verts.new((x*scale*taper, y*scale*taper, z0)) for x, y in OUTLINE]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bottom)))
    n = len(OUTLINE)
    for i in range(n):
        bm.faces.new((bottom[i], bottom[(i+1) % n], top[(i+1) % n], top[i]))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(o)
    mesh.materials.append(material)
    if bevel:
        b = o.modifiers.new('Rounded edge', 'BEVEL')
        b.width, b.segments, b.limit_method = bevel, segments, 'ANGLE'
    for p in mesh.polygons:
        p.use_smooth = True
    return o


slab('Meadow', .95, .55, GROUND, flat('grass', '#7fae4f', .9, '#a9c45e', .55), bevel=.4, segments=5)
slab('Beach', 1.03, .05, .62, flat('sand', '#ead6a6', .95, '#f3e3bd', 6), bevel=.3)
slab('Cliff', .99, -1.6, .1, flat('cliff', '#b58a6a', .9, '#8f6d5c', 2.5), taper=.92)

# Sea: shallow turquoise near the beach, deeper blue further out, fading into the page.
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, .18))
sea = bpy.context.object
sea.name, sea.scale = 'Sea', (90, 74, 1)
m = bpy.data.materials.new('sea')
m.use_nodes = True
nt = m.node_tree
p = nt.nodes['Principled BSDF']
p.inputs['Roughness'].default_value, p.inputs['Specular IOR Level'].default_value = .32, .25
coords = nt.nodes.new('ShaderNodeTexCoord')
mapping = nt.nodes.new('ShaderNodeMapping')
mapping.inputs['Scale'].default_value = (90/13.1, 74/10.2, 1)
nt.links.new(coords.outputs['Object'], mapping.inputs['Vector'])
dist = nt.nodes.new('ShaderNodeVectorMath')
dist.operation = 'LENGTH'
nt.links.new(mapping.outputs['Vector'], dist.inputs[0])
wobble_tex = nt.nodes.new('ShaderNodeTexNoise')
wobble_tex.inputs['Scale'].default_value = 3
nt.links.new(mapping.outputs['Vector'], wobble_tex.inputs['Vector'])
wobble = nt.nodes.new('ShaderNodeMath')
wobble.operation = 'MULTIPLY_ADD'
wobble.inputs[1].default_value = .1
nt.links.new(wobble_tex.outputs['Fac'], wobble.inputs[0])
nt.links.new(dist.outputs['Value'], wobble.inputs[2])
normalise = nt.nodes.new('ShaderNodeMath')
normalise.operation, normalise.inputs[1].default_value = 'DIVIDE', 3
nt.links.new(wobble.outputs[0], normalise.inputs[0])
ramp = nt.nodes.new('ShaderNodeValToRGB')
cr = ramp.color_ramp
cr.elements[0].position, cr.elements[0].color = 1.04/3, srgb('#6fd0c4')
cr.elements[1].position, cr.elements[1].color = 1.6/3, srgb('#2a6f9a')
cr.elements.new(1.25/3).color = srgb('#2e98ad')
nt.links.new(normalise.outputs[0], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
wave = nt.nodes.new('ShaderNodeTexWave')
wave.inputs['Scale'].default_value, wave.inputs['Distortion'].default_value = 1.2, 6
bump = nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .08
nt.links.new(coords.outputs['Object'], wave.inputs['Vector'])
nt.links.new(wave.outputs['Fac'], bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
fade = nt.nodes.new('ShaderNodeMapRange')
fade.inputs['From Min'].default_value, fade.inputs['From Max'].default_value = 1.22, 1.55
nt.links.new(dist.outputs['Value'], fade.inputs['Value'])
mix = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(fade.outputs['Result'], mix.inputs['Fac'])
nt.links.new(p.outputs[0], mix.inputs[1])
nt.links.new(nt.nodes.new('ShaderNodeBsdfTransparent').outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
sea.data.materials.append(m)

# Foam: a broken band hugging the beach, alpha falling off across its width.
foam = bpy.data.materials.new('foam')
foam.use_nodes = True
nt = foam.node_tree
p = nt.nodes['Principled BSDF']
p.inputs['Base Color'].default_value, p.inputs['Roughness'].default_value = srgb('#f6f3e6'), .7
edge = nt.nodes.new('ShaderNodeAttribute')
edge.attribute_name = 'edge'
breakup = nt.nodes.new('ShaderNodeTexNoise')
breakup.inputs['Scale'].default_value, breakup.inputs['Detail'].default_value = 1.2, 4
cut = nt.nodes.new('ShaderNodeMapRange')
cut.inputs['From Min'].default_value, cut.inputs['From Max'].default_value = .42, .6
nt.links.new(breakup.outputs['Fac'], cut.inputs['Value'])
alpha = nt.nodes.new('ShaderNodeMath')
alpha.operation = 'MULTIPLY'
nt.links.new(edge.outputs['Fac'], alpha.inputs[0])
nt.links.new(cut.outputs['Result'], alpha.inputs[1])
nt.links.new(alpha.outputs[0], p.inputs['Alpha'])
bm = bmesh.new()
n = len(OUTLINE)
rows = [[bm.verts.new((x*s, y*s, .2)) for x, y in OUTLINE] for s in (1.035, 1.055, 1.1)]
for r in range(2):
    for i in range(n):
        bm.faces.new((rows[r][i], rows[r+1][i], rows[r+1][(i+1) % n], rows[r][(i+1) % n]))
mesh = bpy.data.meshes.new('Foam')
bm.to_mesh(mesh)
bm.free()
attr = mesh.attributes.new('edge', 'FLOAT', 'POINT')
for v in mesh.vertices:
    attr.data[v.index].value = (0., 1., 0.)[v.index // n]
o = bpy.data.objects.new('Foam', mesh)
bpy.context.scene.collection.objects.link(o)
mesh.materials.append(foam)


# ---------- Buildings from the Medieval modules ----------
def building(name, key, loc, scale, width=4, depth=6, stone=False, rot=0, grid_back=True):
    """A module-built house: walls on a 2-unit grid, original windows, door, roof and gables."""
    root = empty(name, (loc[0], loc[1], GROUND), rot, scale)
    root['place'] = key
    wall = 'Wall_UnevenBrick' if stone else 'Wall_Plaster'
    hx, hy = width/2, depth/2
    xs = [-hx + 1 + 2*i for i in range(width//2)]
    ys = [-hy + 1 + 2*i for i in range(depth//2)]
    door_x = xs[len(xs)//2]
    for x in xs:
        front = f'{wall}_Door_Round' if x == door_x else f'{wall}_Window_Wide_Round'
        place('M', front, (x, -hy, 0), parent=root)
        if x == door_x:
            place('M', 'Door_1_Round', (x - .51, -hy - .06, 0), parent=root)
        else:
            place('M', 'Window_Wide_Round1', (x, -hy - .08, 0), parent=root)
        back = 'Wall_Plaster_WoodGrid' if grid_back and not stone else f'{wall}_Straight'
        place('M', back, (x, hy, 0), math.pi, parent=root)
    for y in ys:
        for side in (-1, 1):
            windowed = (ys.index(y) % 2 == 0) or len(ys) < 3
            place('M', f'{wall}_Window_Wide_Round' if windowed else f'{wall}_Straight', (side*hx, y, 0), -side*math.pi/2, parent=root)
            if windowed:
                place('M', 'Window_Wide_Round1', (side*(hx + .06), y, 0), -side*math.pi/2, parent=root)
    corner = 'Corner_Exterior_Brick' if stone else 'Corner_Exterior_Wood'
    for cx in (-hx, hx):
        for cy in (-hy, hy):
            place('M', corner, (cx, cy, 0), parent=root)
    place('M', f'Roof_RoundTiles_{width}x{depth}', (0, 0, 3.12), parent=root)
    place('M', f'Roof_Front_Brick{width}', (0, -hy, 3.12), parent=root)
    place('M', f'Roof_Front_Brick{width}', (0, hy, 3.12), math.pi, parent=root)
    return root


def cube(name, loc, dims, material, bevel=.04, parent=None, local=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name, o.dimensions = name, dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Soft edges', 'BEVEL')
        b.width, b.segments = bevel, 2
    attach(o, parent, local)
    return o


def attach(o, parent, local=False):
    """Parent keeping world position, or (local=True) treating the location as parent space."""
    if parent:
        o.parent = parent
        if not local:
            o.matrix_parent_inverse = parent.matrix_world.inverted()


def cylinder(name, loc, radius, depth, material, vertices=24, scale=(1, 1, 1), parent=None, local=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name, o.scale = name, scale
    o.data.materials.append(material)
    for f in o.data.polygons:
        f.use_smooth = True
    attach(o, parent, local)
    return o


def line(name, points, material, width=.05):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions, data.bevel_depth, data.bevel_resolution = '3D', width, 3
    spline = data.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for target, xyz in zip(spline.points, points):
        target.co = (*xyz, 1)
    o = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(material)
    return o


studio = building('Project Studio', 'projects', (-6.7, -2.7), .71)
place('M', 'Prop_Chimney', (1.1, 1.6, 4.1), parent=studio)
place('M', 'Prop_Vine2', (-2.1, -2.6, 3.0), -math.pi/2, parent=studio)
place('M', 'Prop_Wagon', (-3.6, -.6, GROUND), math.radians(-60), .55)
place('M', 'Prop_Crate', (-4.4, -5.4, GROUND), .4, .55)
place('M', 'Prop_Crate', (-4.0, -4.9, GROUND), -.3, .42)

museum = building('Experience Museum', 'experience', (-4.3, 4.2), .58, width=6, depth=8, stone=True)
for x in (-2.4, -.8, .8, 2.4):
    cylinder('Museum column', (x, -4.9, 1.5), .22, 3.0, pack_material('Plaster'), 20, parent=museum, local=True)
    cylinder('Column base', (x, -4.9, .1), .32, .2, pack_material('Brick'), 20, parent=museum, local=True)
cube('Museum portico roof', (0, -4.95, 3.12), (6.0, 1.3, .3), pack_material('WoodTrim'), parent=museum, local=True)
cube('Museum steps', (0, -4.7, .06), (5.4, 1.6, .14), pack_material('Brick'), .02, parent=museum, local=True)

welcome = building('Welcome Center', 'about', (.1, 1.4), .44, width=4, depth=4)
place('M', 'WindowShutters_Wide_Round_Open', (-1, -2.05, 0), parent=welcome)

kiosk = building('Noticeboard kiosk', 'currently', (5.4, 4.6), .4, width=4, depth=4)
board = empty('The Noticeboard', (5.2, 2.55, GROUND))
board.parent = kiosk
board.matrix_parent_inverse = kiosk.matrix_world.inverted()
wood = pack_material('WoodTrim')
paper = flat('noticeboard paper', '#f8efd8', .9)
pins = {k: flat(f'pin {k}', h, .5) for k, h in (('red', '#c75a45'), ('blue', '#4f7fae'), ('gold', '#d9a441'))}
for x in (-1, 1):
    cube('Noticeboard post', (5.2 + x, 2.6, GROUND + .9), (.14, .16, 1.8), wood, .02)
cube('Noticeboard panel', (5.2, 2.6, GROUND + 1.45), (2.3, .16, 1.1), wood, .03)
cube('Noticeboard cap', (5.2, 2.6, GROUND + 2.05), (2.6, .45, .12), wood, .03)
for (x, z), pin in zip([(4.62, 1.5), (5.2, 1.6), (5.78, 1.42)], pins.values()):
    cube('Note', (x, 2.5, GROUND + z), (.48, .03, .6), paper, .005)
    cylinder('Pin', (x, 2.48, GROUND + z + .25), .05, .05, pin, 10)
for o in [o for o in bpy.data.objects if o.name.startswith(('Noticeboard', 'Note', 'Pin'))]:
    o.parent = board
    o.matrix_parent_inverse = board.matrix_world.inverted()

# Greenhouse (original frame and glass; the visible glass is what lights up after a visit).
gx, gy = 6.2, -2.0
greenhouse = empty('Curiosity Greenhouse', (gx, gy, GROUND))
greenhouse['place'] = 'beyond'
glass = bpy.data.materials.new('glass greenhouse')
glass.use_nodes = True
gp = glass.node_tree.nodes['Principled BSDF']
gp.inputs['Base Color'].default_value, gp.inputs['Roughness'].default_value = srgb('#d7eeee'), .15
gp.inputs['Alpha'].default_value = .42
frame = flat('greenhouse frame', '#f3efe3', .6)
cube('Greenhouse base', (gx, gy, GROUND + .12), (4.6, 3.3, .26), pack_material('Brick'), .03, greenhouse)
cube('Greenhouse glass', (gx, gy, GROUND + 1.38), (4.2, 2.9, 2.26), glass, .0, greenhouse)
for xx in (-2.1, -1.05, 0, 1.05, 2.1):
    for yy in (-1.46, 1.46):
        cube('Greenhouse post', (gx + xx, gy + yy, GROUND + 1.4), (.08, .08, 2.4), frame, 0, greenhouse)
    rib = line('Greenhouse roof rib', [(gx + xx, gy - 1.46, GROUND + 2.55), (gx + xx, gy, GROUND + 3.6), (gx + xx, gy + 1.46, GROUND + 2.55)], frame, .055)
    rib.parent = greenhouse
    rib.matrix_parent_inverse = greenhouse.matrix_world.inverted()
for yy, zz in ((-1.46, 2.55), (0, 3.6), (1.46, 2.55)):
    rail = line('Greenhouse roof rail', [(gx - 2.15, gy + yy, GROUND + zz), (gx + 2.15, gy + yy, GROUND + zz)], frame, .055)
    rail.parent = greenhouse
    rail.matrix_parent_inverse = greenhouse.matrix_world.inverted()
for side in (-1, 1):
    m = bpy.data.meshes.new('Greenhouse roof glass')
    m.from_pydata([(gx - 2.1, gy + side*1.46, GROUND + 2.55), (gx + 2.1, gy + side*1.46, GROUND + 2.55),
                   (gx + 2.1, gy, GROUND + 3.6), (gx - 2.1, gy, GROUND + 3.6)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new('Greenhouse roof glass', m)
    bpy.context.scene.collection.objects.link(o)
    m.materials.append(glass)
    o.parent = greenhouse
    o.matrix_parent_inverse = greenhouse.matrix_world.inverted()
# Succulents on a bench inside and in pots by the door: the owner's real interest, nothing invented.
terracotta = flat('terracotta', '#c9744f', .8, '#d98c64', 8)
cube('Greenhouse bench', (gx, gy + .6, GROUND + .75), (3.4, .9, .1), wood, .02)
for i, x in enumerate((-1.3, -.45, .4, 1.25)):
    cylinder('Succulent pot', (gx + x, gy + .6, GROUND + .95), .22, .3, terracotta)
    place('N', 'Plant_1' if i % 2 == 0 else 'Plant_7', (gx + x, gy + .6, GROUND + 1.08), random.uniform(0, 6), .32 if i % 2 == 0 else .55)
for x in (-1.5, -.6, 1.4):
    cylinder('Succulent pot', (gx + x, gy - 2.15, GROUND + .2), .3, .4, terracotta)
    place('N', 'Plant_1', (gx + x, gy - 2.15, GROUND + .38), random.uniform(0, 6), .42)

# ---------- Central plaza and fountain ----------
cylinder('Plaza', (0, -.9, GROUND - .02), 2.8, .08, flat('plaza sand', '#e6d3a8', .95, '#d9c597', 5), 64, (1, .8, 1))
for i in range(30):
    a, r = random.uniform(0, math.tau), math.sqrt(random.uniform(.16, 1)) * 2.45
    x, y = r*math.cos(a), -.9 + .8*r*math.sin(a)
    if math.hypot(x, (y + .7)/.9) > 1.15:
        place('N', 'RockPath_Square_Small_1' if i % 3 else 'RockPath_Square_Small_2', (x, y, GROUND), random.uniform(0, 6), .55)
brick = pack_material('Brick')
cylinder('Fountain basin', (0, -.7, GROUND + .18), .85, .36, brick, 32)
cylinder('Fountain water', (0, -.7, GROUND + .33), .72, .06, flat('fountain water', '#5fc1c4', .15), 32)
cylinder('Fountain column', (0, -.7, GROUND + .7), .14, .8, pack_material('Plaster'), 16)
cylinder('Fountain bowl', (0, -.7, GROUND + 1.08), .36, .12, brick, 24)

# ---------- Stone paths, pressed into the meadow ----------
dirt = flat('path dirt', '#b9a57a', .95, '#a99467', 4)
ROUTES = [
    [(-1.9, -1.5), (-3.6, -2.6), (-5.2, -4.3), (-6.5, -5.2)],  # studio door
    [(-1.4, .3), (-2.6, .5), (-4.0, .4)],                       # museum steps
    [(1.9, -1.8), (3.4, -3.0), (5.0, -4.4)],                    # greenhouse door
    [(2.2, -.2), (3.6, .9), (4.9, 1.9)],                        # noticeboard
    [(.1, -3.0), (.2, -5.5), (.7, -8.2)],                       # pier
]
for route in ROUTES:
    pts = [Vector((x, y, 0)) for x, y in route]
    underlay = line('Path underlay', [(p.x, p.y, GROUND - .03) for p in pts], dirt, .48)
    underlay.scale.z = .08
    underlay.location.z = GROUND * .92
    for a, b in zip(pts, pts[1:]):
        steps = max(1, int((b - a).length / .85))
        for k in range(steps):
            p = a.lerp(b, (k + .5) / steps)
            side = (b - a).normalized().cross(Vector((0, 0, 1)))
            p += side * random.uniform(-.12, .12)
            place('N', random.choice(['RockPath_Round_Small_1', 'RockPath_Round_Small_2', 'RockPath_Round_Small_3']),
                  (p.x, p.y, GROUND - .02), random.uniform(0, 6), random.uniform(.6, .75))

# ---------- Pier, boat, short bridge, observation wheel ----------
pier_wood = flat('pier wood', '#9a6a48', .8, '#b8845a', 5)
for j in range(3):
    place('M', 'Floor_WoodLight', (1, -9 - j*2, .62))
for px in (.08, 1.92):
    for py in (-8.6, -10.6, -12.8):
        cylinder('Pier post', (px, py, -.1), .1, 1.7, pier_wood, 10)
place('M', 'Prop_Crate', (1.6, -9.2, .64), .3, .45)
hull_mat = flat('boat hull', '#d4685a', .5)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(4.8, -12.0, .62))
hull = bpy.context.object
hull.name, hull.scale, hull.rotation_euler.z = 'Boat hull', (.6, 1.45, .45), math.radians(18)
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(hull.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > .25], context='VERTS')
bmesh.update_edit_mesh(hull.data)
bpy.ops.object.mode_set(mode='OBJECT')
hull.data.materials.append(hull_mat)
hull.modifiers.new('Hull thickness', 'SOLIDIFY').thickness = .08
for f in hull.data.polygons:
    f.use_smooth = True
cylinder('Boat mast', (4.8, -12.0, 1.6), .05, 2.8, pier_wood, 10)
sail = bpy.data.meshes.new('Sail')
sail.from_pydata([(4.8, -11.95, 2.9), (4.8, -11.95, .6), (5.18, -10.8, .6)], [], [(0, 1, 2)])
o = bpy.data.objects.new('Sail', sail)
bpy.context.scene.collection.objects.link(o)
sail.materials.append(flat('sail', '#fbf3e3', .7))
bpy.ops.mesh.primitive_torus_add(major_radius=1.55, minor_radius=.025, location=(4.8, -12.0, .2))
wake = bpy.context.object
wake.scale, wake.rotation_euler.z = (.6, 1.1, .2), math.radians(18)
wake.data.materials.append(flat('wake', '#f6f3e6', .6))

for i in range(8):
    cube('Short bridge plank', (12.0 + i*.42, -1.7, .7 + .22*math.sin(i*math.pi/7)), (.44, 1.3, .14), wood, .02)
for x in (12.0, 14.95):
    for y in (-2.3, -1.1):
        cylinder('Bridge post', (x, y, .5), .07, 1.1, pier_wood, 10)
place('N', 'Rock_Medium_2', (15.6, -1.6, -.3), 1.2, .75)

wx, wy, wz = -.6, 6.6, GROUND + 2.6
cream = flat('wheel cream', '#f6ecd6', .6)
cabins = [flat('cabin coral', '#d4796a', .6), flat('cabin teal', '#3f8f99', .6)]
line('Observation wheel rim', [(wx + 1.55*math.cos(i*math.tau/64), wy, wz + 1.55*math.sin(i*math.tau/64)) for i in range(65)], cream, .07)
for i in range(8):
    a = i * math.tau / 8
    x, z = wx + 1.55*math.cos(a), wz + 1.55*math.sin(a)
    line('Wheel spoke', [(wx, wy, wz), (x, wy, z)], cream, .035)
    cube('Wheel cabin', (x, wy, z - .25), (.42, .5, .42), cabins[i % 2], .06)
line('Wheel frame', [(wx - 1, wy, GROUND), (wx, wy, wz), (wx + 1, wy, GROUND)], wood, .09)

# ---------- Trees, rocks, flowers, fence ----------
for name, x, y, s in [('CommonTree_1', -9.6, 2.6, .52), ('CommonTree_3', -10.4, -1.2, .4), ('Pine_3', -8.6, 6.2, .5),
                      ('CommonTree_1', 3.2, 7.6, .46), ('CommonTree_3', 9.6, 4.0, .38), ('CommonTree_1', 10.4, 1.0, .4),
                      ('Pine_3', -1.2, 8.6, .42), ('CommonTree_3', -10.2, -4.6, .34), ('CommonTree_1', 9.2, -5.6, .36)]:
    place('N', name, (x, y, GROUND - .05), random.uniform(0, 6), s)
for x, y in [(-3.0, -4.6), (-8.4, -5.8), (3.6, -6.2), (8.6, -.6), (7.2, 2.4), (-1.8, 4.2), (2.4, 4.6)]:
    place('N', 'Bush_Common_Flowers', (x, y, GROUND - .05), random.uniform(0, 6), .5)
for x, y, s in [(-11.8, -3.2, .55), (-6.2, -8.4, .45), (9.6, -6.8, .5), (11.6, 2.6, .42), (-9.6, 6.6, .55), (5.6, 8.6, .4)]:
    place('N', 'Rock_Medium_2' if s > .45 else 'Rock_Medium_1', (x, y, .1), random.uniform(0, 6), s)
for i in range(5):
    place('M', 'Prop_WoodenFence_Single', (-8.4 + i*2.05, 7.9 - i*.25, GROUND), math.radians(-7), .85)

BLOCKED = [(-8.5, -5.6, -4.8, .2), (-6.9, -.6, -1.4, 7.4), (-3.0, -3.2, 3.0, 2.8), (3.6, -4.8, 8.8, .2),
           (3.8, 1.8, 7.0, 6.2), (-2.4, 5.2, 1.2, 7.0)]
for _ in range(160):
    a, r = random.uniform(0, math.tau), random.uniform(.2, .9)
    x, y = 12.6*r*math.cos(a), 9.8*r*math.sin(a)
    if any(x0 < x < x1 and y0 < y < y1 for x0, y0, x1, y1 in BLOCKED):
        continue
    if any(min((Vector((x, y)) - Vector(p)).length for p in route) < .9 for route in ROUTES):
        continue
    kind = random.choices(['Grass_Common_Short', 'Grass_Wispy_Short', 'Clover_1', 'Fern_1', 'Flower_4_Group', 'Flower_3_Group'],
                          [5, 3, 2, 2, 1, 1])[0]
    place('N', kind, (x, y, GROUND - .05), random.uniform(0, 6), random.uniform(.35, .5))

# ---------- Materials, real geometry, light, camera ----------
restyle(light)
soften_foliage()
make_real()
retint(museum, 'RoundTiles', tinted('RoundTiles', 'tiles slate', hue=.07, saturation=.45, value=.95))
retint(welcome, 'RoundTiles', tinted('RoundTiles', 'tiles sage', hue=.77, saturation=.55, value=1.05))
retint(kiosk, 'RoundTiles', tinted('RoundTiles', 'tiles mustard', hue=.59, saturation=.95, value=1.1))

light_scene(light, (1800, 1400), samples)
scene = bpy.context.scene
scene.render.resolution_percentage = preview
bpy.ops.object.camera_add(location=(20, -30, 31))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, -1, 1)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type, camera.data.ortho_scale = 'ORTHO', 43
scene.camera = camera
bpy.context.view_layer.update()
anchors = {'about': (.1, -.4, 1.6), 'projects': (-6.7, -4.8, 1.2), 'experience': (-4.3, 1.4, 2.8),
           'beyond': (6.2, -4, 1.3), 'currently': (5.2, 2.6, 2.5)}
layout = {}
for key, point in anchors.items():
    p = world_to_camera_view(scene, camera, Vector(point))
    layout[key] = {'x': round(p.x*100, 2), 'y': round((1 - p.y)*100, 2)}
(output/'map-layout.json').write_text(json.dumps(layout, indent=2) + '\n')
scene.render.filepath = str(output/f'island-{light}.png')
bpy.ops.wm.save_as_mainfile(filepath=str(output/'island.blend'))
bpy.ops.render.render(write_still=True)
