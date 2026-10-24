"""Render the five cutaway interiors from the same Quaternius modules as the island.

python3 tools/render_interiors.py SOURCES OUTPUT [day|dusk] [samples]
  (bpy 5.1 module; or: blender --background --python tools/render_interiors.py -- SOURCES OUTPUT)
Walls, windows, doors, floors, crates and plants are the owner's CC0 models with their
original textures; furniture is simple original geometry wearing the pack's own wood,
plaster and brick materials. Outputs PNGs and projected object hotspot coordinates.
"""
import json
import math
import random
import sys
from pathlib import Path
import bpy  # first: the bpy module provides mathutils
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
source, output = Path(args[0]), Path(args[1])
light = args[2] if len(args) > 2 else 'day'
samples = int(args[3]) if len(args) > 3 else 96
rooms_to_render = args[4].split(',') if len(args) > 4 else ['about', 'projects', 'experience', 'beyond', 'currently']
sys.path.insert(0, str(Path(__file__).resolve().parent))
import quaternius_kit as kit

output.mkdir(parents=True, exist_ok=True)
# The room is built in module units (walls 2 wide, 3.12 tall), then scaled to the old camera framing.
SCALE = 1.75


def box(name, loc, dims, material, bevel=.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name, o.dimensions = name, dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Soft edges', 'BEVEL')
        b.width, b.segments = bevel, 2
    o.parent = ROOT
    return o


def disk(name, loc, radius, depth, material, vertices=24, rot_x=0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name, o.rotation_euler.x = name, rot_x
    o.data.materials.append(material)
    for f in o.data.polygons:
        f.use_smooth = True
    o.parent = ROOT
    return o


def put(kind, name, loc, rot=0, scale=1):
    return kit.place(kind, name, loc, rot, scale, parent=ROOT)


def table(x, y, w, d, h, wood):
    box('Table top', (x, y, h), (w, d, .1), wood)
    for dx in (-w/2 + .12, w/2 - .12):
        for dy in (-d/2 + .12, d/2 - .12):
            box('Table leg', (x + dx, y + dy, h/2), (.12, .12, h), wood, .01)


def frame_on_back_wall(x, z, w, h, backing, wood):
    box('Frame', (x, 2.76, z), (w + .16, .08, h + .16), wood, .02)
    box('Frame backing', (x, 2.71, z), (w, .03, h), backing, .005)


def shell(walls='Wall_Plaster', floor='Floor_WoodLight', back=('Window', 'Straight', 'Straight', 'Window'), left=('Straight', 'Window', 'Straight')):
    """Back wall at y=3, left wall at x=-4; open towards the camera like a dollhouse."""
    for x in (-3, -1, 1, 3):
        for y in (-2, 0, 2):
            put('M', floor, (x, y, 0))
    for x, kind in zip((-3, -1, 1, 3), back):
        put('M', f'{walls}_Window_Wide_Round' if kind == 'Window' else f'{walls}_Straight', (x, 3, 0), math.pi)
        if kind == 'Window':
            put('M', 'Window_Wide_Round1', (x, 3.06, 0), math.pi)
    for y, kind in zip((-2, 0, 2), left):
        put('M', f'{walls}_Window_Wide_Round' if kind == 'Window' else f'{walls}_Straight', (-4, y, 0), -math.pi/2)
        if kind == 'Window':
            put('M', 'Window_Wide_Round1', (-4.06, y, 0), -math.pi/2)
    put('M', 'Corner_Exterior_Brick' if 'Brick' in walls else 'Corner_Exterior_Wood', (-4, 3, 0))


def plant_pot(x, y, z, model, size, clay):
    disk('Pot', (x, y, z + size*.35), size*.5, size*.7, clay, 20)
    put('N', model, (x, y, z + size*.62), random.uniform(0, 6), size*(1.0 if model == 'Plant_1' else 1.6))


def build(room):
    """Furnish one room; return hotspot points in room (module) coordinates."""
    for name in ('Floor_WoodLight', 'Wall_Plaster_Window_Wide_Round'):
        kit.template('M', name)  # makes the pack's wood, plaster and brick materials available
    wood = kit.pack_material('WoodTrim')
    plaster = kit.pack_material('Plaster')
    paper = kit.flat('paper', '#f7efdb', .9)
    clay = kit.flat('terracotta', '#c9744f', .8, '#d98c64', 8)
    coral, blue, sage, ink = (kit.flat(n, h, .7) for n, h in (('coral', '#c45c46'), ('blueprint', '#2f5f93'), ('sage', '#93ad7f'), ('ink', '#3b342c')))
    if room == 'projects':
        shell()
        table(-1.2, .9, 2.6, 1.3, .92, wood)
        box('Blueprint', (-1.3, .85, .99), (1.5, .95, .015), blue, 0)
        disk('Rolled blueprint', (-.25, .85, 1.04), .07, 1.0, paper, 16, math.pi/2)
        table(1.9, -1.0, 1.5, 1.1, .7, wood)
        for i, (dx, dy, h) in enumerate([(-.35, .1, .35), (0, -.2, .22), (.35, .15, .45)]):
            box('Prototype', (1.9 + dx, -1.0 + dy, .75 + h/2), (.25, .25, h), (coral, paper, coral)[i], .04)
        box('Project wall', (-.4, 2.76, 1.9), (2.6, .08, 1.4), kit.flat('cork', '#b98b5e', .9, '#a87b50', 9), .02)
        for x, z in ((-1.1, 2.1), (-.3, 1.75), (.5, 2.05)):
            box('Pinned sheet', (x, 2.71, z), (.6, .02, .45), blue if x < 0 else paper, .005)
        for z in (.5, 1.3, 2.1):
            box('Shelf', (-3.72, -.6, z), (.45, 1.8, .07), wood, .01)
        for i in range(9):
            box('Project file', (-3.72, -1.2 + (i % 3)*.5, (.5, 1.3, 2.1)[i // 3] + .3), (.32, .16, .5), (coral, paper, blue)[i % 3], .01)
        put('M', 'Prop_Crate', (2.9, 2.2, 0), .3, .7)
        plant_pot(3.3, .9, 0, 'Plant_1', .45, clay)
        box('Stool', (-1.2, -.3, .3), (.5, .5, .6), wood, .05)
        return {'project-01': (-1.3, .85, 1.05), 'project-02': (1.9, -1.0, 1.0), 'index': (-.4, 2.7, 1.9)}
    if room == 'about':
        shell(back=('Window', 'Straight', 'Straight', 'Window'), left=('Window', 'Straight', 'Window'))
        box('Rug', (-.6, -.6, .02), (3.6, 2.4, .02), kit.flat('rug', '#c98f6a', .95, '#b97a58', 12), 0)
        box('Reception desk', (-.6, -.1, .5), (2.8, 1.0, 1.0), plaster, .04)
        box('Desk top', (-.6, -.1, 1.04), (3.0, 1.15, .08), wood, .02)
        box('Guestbook left page', (-.85, -.15, 1.1), (.45, .6, .03), paper, .01)
        box('Guestbook right page', (-.38, -.15, 1.1), (.45, .6, .03), paper, .01)
        box('Guestbook cover', (-.62, -.15, 1.085), (1.0, .66, .02), coral, 0)
        frame_on_back_wall(-.1, 1.9, 2.4, 1.3, kit.flat('map sea', '#5fb3bf', .8), wood)
        for x, z, s in ((-.6, 1.95, .5), (.2, 1.8, .35), (.5, 2.15, .25)):
            disk('Map island', (x, 2.69, z), s, .01, sage, 20, math.pi/2)
        box('Brochure stand', (2.1, -.6, .45), (.8, .5, .9), wood, .02)
        for i in range(3):
            box('Resume brochure', (1.85 + i*.25, -.62, 1.08), (.18, .35, .4), paper, .01)
        box('Letterbox post', (2.9, -2.1, .5), (.12, .12, 1.0), wood, .01)
        box('Letterbox', (2.9, -2.1, 1.15), (.6, .45, .45), coral, .06)
        box('Letter slot', (2.9, -2.33, 1.22), (.34, .02, .05), ink, .005)
        plant_pot(-3.2, -2.0, 0, 'Plant_7', .5, clay)
        plant_pot(3.3, 2.2, 0, 'Plant_1', .5, clay)
        put('M', 'Prop_Crate', (-3.3, 2.2, 0), .2, .6)
        return {'story': (-.6, -.15, 1.15), 'resume': (2.1, -.6, 1.1), 'contact': (2.9, -2.1, 1.2)}
    if room == 'experience':
        shell(walls='Wall_UnevenBrick', floor='Floor_Brick', back=('Straight', 'Straight', 'Straight', 'Window'), left=('Straight', 'Straight', 'Window'))
        frame_on_back_wall(-2.0, 1.85, 1.6, 1.1, kit.flat('exhibit blue', '#5f7f9e', .8), wood)
        frame_on_back_wall(.6, 1.85, 1.6, 1.1, kit.flat('exhibit sage', '#8fa97c', .8), wood)
        for x in (-2.0, .6):
            box('Exhibit label', (x, 2.72, 1.05), (.7, .02, .22), paper, .005)
        box('Timeline rail', (-.7, 2.72, .75), (4.4, .04, .04), wood, 0)
        for x in (-2.6, -1.2, .2, 1.4):
            disk('Timeline marker', (x, 2.7, .75), .07, .04, coral, 12, math.pi/2)
        for x, y in ((-3.3, -2.3), (2.6, -1.9)):
            disk('Column', (x, y, 1.45), .2, 2.6, plaster, 20)
            disk('Column base', (x, y, .1), .3, .2, kit.pack_material('Brick'), 20)
            disk('Column capital', (x, y, 2.8), .3, .16, kit.pack_material('Brick'), 20)
        box('Archive cabinet', (-3.6, .7, .8), (.7, 1.5, 1.6), wood, .03)
        for z in (.35, .8, 1.25):
            box('Drawer', (-3.24, .7, z), (.03, 1.3, .36), paper, .01)
        disk('Plinth', (.1, -.6, .5), .45, 1.0, plaster, 24)
        box('Open record', (.1, -.6, 1.04), (.8, .55, .05), paper, .01)
        box('Gallery bench', (-.9, -2.0, .25), (1.8, .5, .5), wood, .03)
        return {'work': (-2.0, 2.7, 1.85), 'education': (.6, 2.7, 1.85), 'index': (-3.6, .7, 1.0)}
    if room == 'beyond':
        for x in (-3, -1, 1, 3):
            for y in (-2, 0, 2):
                put('M', 'Floor_UnevenBrick', (x, y, 0))
        glass = bpy.data.materials.new('glass room')
        glass.use_nodes = True
        gp = glass.node_tree.nodes['Principled BSDF']
        gp.inputs['Base Color'].default_value, gp.inputs['Alpha'].default_value, gp.inputs['Roughness'].default_value = kit.srgb('#d7eeee'), .35, .1
        frame = kit.flat('greenhouse frame', '#f3efe3', .6)
        box('Low wall', (0, 2.95, .3), (8, .2, .6), kit.pack_material('Brick'), .02)
        box('Low wall', (-3.95, 0, .3), (.2, 6, .6), kit.pack_material('Brick'), .02)
        box('Back glass', (0, 2.95, 1.95), (7.9, .03, 2.7), glass, 0)
        box('Left glass', (-3.95, 0, 1.95), (.03, 5.9, 2.7), glass, 0)
        for x in (-4, -2, 0, 2, 4):
            box('Upright', (x, 2.95, 1.65), (.08, .08, 3.3), frame, 0)
        for y in (-3, -1, 1, 3):
            box('Upright', (-3.95, y, 1.65), (.08, .08, 3.3), frame, 0)
        box('Top rail', (0, 2.95, 3.3), (8.1, .1, .1), frame, 0)
        box('Top rail', (-3.95, 0, 3.3), (.1, 6.1, .1), frame, 0)
        for x, kind in ((-2.0, 'community'), (.9, 'curiosities')):
            box('Planting bed', (x, .2, .3), (2.0, 1.8, .6), wood, .03)
            box('Soil', (x, .2, .61), (1.85, 1.65, .04), kit.flat('soil', '#6e5240', .95, '#7d5f4a', 6), 0)
            picks = ['Fern_1', 'Flower_4_Group', 'Bush_Common_Flowers'] if kind == 'community' else ['Plant_7', 'Flower_3_Group', 'Fern_1']
            for (dx, dy), model in zip(((-.5, -.4), (.45, -.3), (0, .45)), picks):
                put('N', model, (x + dx, .2 + dy, .62), random.uniform(0, 6), .4)
        table(2.7, 1.8, 1.8, .9, .9, wood)
        box('Garden journal', (2.6, 1.75, .97), (.6, .45, .05), kit.flat('journal', '#5f7f5a', .7), .01)
        box('Journal page', (2.6, 1.75, 1.0), (.55, .4, .01), paper, 0)
        # The owner likes succulents: a row of potted ones on the bench, without invented details.
        box('Succulent shelf', (-3.55, -1.6, .75), (.6, 2.4, .08), wood, .01)
        for y in (-2.5, -1.9, -1.3, -.7):
            plant_pot(-3.55, y, .79, 'Plant_1' if y != -1.9 else 'Plant_7', .32, clay)
        for x in (1.0, 2.4):
            plant_pot(x, -2.2, 0, 'Plant_1', .5, clay)
        return {'community': (-2.0, .2, .8), 'curiosities': (.9, .2, .8), 'index': (2.6, 1.75, 1.0)}
    # currently
    shell(back=('Straight', 'Straight', 'Straight', 'Window'), left=('Window', 'Straight', 'Straight'))
    box('Noticeboard', (-.6, 2.76, 1.85), (3.8, .08, 1.6), kit.flat('cork', '#b98b5e', .9, '#a87b50', 9), .02)
    box('Noticeboard frame', (-.6, 2.79, 1.85), (3.95, .05, 1.75), wood, .02)
    for x, color in ((-1.5, paper), (.3, kit.flat('note sage', '#dfe8cf', .9))):
        box('Pinned update', (x, 2.71, 1.85), (1.2, .02, .95), color, .005)
        disk('Pin', (x, 2.69, 2.25), .05, .04, coral, 12, math.pi/2)
        for i in range(3):
            box('Note line', (x - .1, 2.695, 1.95 - i*.18), (.8, .01, .03), blue, 0)
    box('Rug', (-1.2, -1.2, .02), (3.0, 2.4, .02), kit.flat('rug', '#7f9f8a', .95, '#6d8f7a', 12), 0)
    table(-1.3, -.9, 2.2, 1.1, .85, wood)
    for i in range(4):
        box('Update paper', (-1.4 + i*.06, -.9, .92 + i*.02), (.7, .5, .015), paper, 0)
    put('M', 'Prop_Crate', (2.3, -1.6, 0), .3, .65)
    disk('Paint brush', (2.3, -1.6, 1.0), .03, .9, coral, 10)
    box('Stool', (-1.3, -2.0, .3), (.5, .5, .6), wood, .05)
    plant_pot(3.2, 2.1, 0, 'Plant_1', .45, clay)
    return {'learning': (-1.5, 2.7, 1.85), 'making': (.3, 2.7, 1.85), 'index': (-1.3, -.9, .95)}


all_points = {}
layout_file = output/'interior-layout.json'
if layout_file.exists():
    all_points = json.loads(layout_file.read_text())
for room in rooms_to_render:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    kit._templates.clear()
    kit.set_source(source)
    random.seed(3)
    ROOT = kit.empty('Room', (0, 0, 0), 0, SCALE)
    points = build(room)
    kit.restyle(light)
    kit.soften_foliage()
    sun = kit.light_scene(light, (1600, 1100), samples)
    # Sun through the back/left windows; a soft fill from the open side keeps the room readable.
    sun.rotation_euler = (math.radians(52), 0, math.radians(-150))
    bpy.ops.object.light_add(type='AREA', location=(14, -18, 16))
    fill = bpy.context.object
    fill.data.size, fill.data.energy = 14, 13000 if light == 'day' else 3500
    fill.data.color = (.88, .9, 1) if light == 'day' else (.6, .6, .9)
    fill.rotation_euler = (Vector((0, 0, 1)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
    scene = bpy.context.scene
    bpy.ops.object.camera_add(location=(15, -23, 19))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0, 0, 1.7)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type, camera.data.ortho_scale = 'ORTHO', 22
    scene.camera = camera
    bpy.context.view_layer.update()
    all_points[room] = {}
    for key, xyz in points.items():
        p = world_to_camera_view(scene, camera, ROOT.matrix_world @ Vector(xyz))
        all_points[room][key] = {'x': round(p.x*100, 2), 'y': round((1 - p.y)*100, 2)}
    scene.render.filepath = str(output/f'{room}.png')
    bpy.ops.render.render(write_still=True)
layout_file.write_text(json.dumps(all_points, indent=2) + '\n')
