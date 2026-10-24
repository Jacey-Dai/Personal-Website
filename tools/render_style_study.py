"""Style study 02: coastal sample in three art directions, using the original Quaternius textures.

python3 tools/render_style_study.py SOURCES DIRECTION OUT.png [samples]
  (needs the `bpy` module, e.g. `pip install bpy==5.1.2` with Python 3.13; Blender 5.1 also works:
   blender --background --python tools/render_style_study.py -- SOURCES DIRECTION OUT.png)
SOURCES is the folder written by `git archive origin/assets/source-packs assests | tar -x -C SOURCES`.
DIRECTION: storybook | toybox | lantern
"""
import sys
import bpy, bmesh, math, random
from mathutils import Vector, noise
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

random.seed(7)

def srgb(h):
    v = [int(h.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(c/12.92 if c < .04045 else ((c+.055)/1.055)**2.4 for c in v) + (1,)

STYLE = {
    'storybook': dict(sun=(1, .9, .78), sun_e=4.2, sun_rot=(math.radians(48), 0, math.radians(-38)), sun_angle=3,
                      sky=(.62, .74, .92), sky_e=.9, sat=.88, val=1.0,
                      grass=('#7fae4f', '#a9c45e'), sand='#ead6a6', cliff=('#b58a6a', '#8f6d5c'),
                      sea=('#6fd0c4', '#2e98ad', '#1f5f8c'), foam='#f6f3e6', glow=0),
    'toybox':    dict(sun=(1, .98, .95), sun_e=3.6, sun_rot=(math.radians(35), 0, math.radians(-30)), sun_angle=12,
                      sky=(.85, .88, .95), sky_e=1.1, sat=.8, val=1.05,
                      grass=('#86c25a', '#a8d46a'), sand='#f6e0a8', cliff=('#e3a87f', '#c78d77'),
                      sea=('#7fe0d4', '#38b6c8', '#2a7fc0'), foam='#ffffff', glow=0),
    'lantern':   dict(sun=(1, .66, .42), sun_e=3.4, sun_rot=(math.radians(74), 0, math.radians(-62)), sun_angle=2,
                      sky=(.36, .38, .62), sky_e=.75, sat=.95, val=.95,
                      grass=('#6f9a5e', '#9aa95d'), sand='#e2c08e', cliff=('#9a6c5c', '#6e5160'),
                      sea=('#5fb5bf', '#2f7d9c', '#22416f'), foam='#ffe9cc', glow=6),
}[direction]
# Flat palette used only by the toybox direction (texture kept as subtle detail).
TOY = {'Plaster': '#fbf1dc', 'RoundTiles': '#3e9a9a', 'WoodTrim': '#e3a35d', 'Brick': '#d9d2c4',
       'UnevenBrick': '#d9d2c4', 'WindowGlass': '#bfe6ee', 'Vine': '#7fbf6a'}


def mat_flat(name, base, rough=.85, noise_hex=None, noise_scale=3.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    p.inputs['Roughness'].default_value = rough
    if noise_hex:
        tex = nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = noise_scale
        tex.inputs['Detail'].default_value = 3
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[1].position = .35, .7
        ramp.color_ramp.elements[0].color, ramp.color_ramp.elements[1].color = srgb(base), srgb(noise_hex)
        nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    else:
        p.inputs['Base Color'].default_value = srgb(base)
    return m


def restyle_imported():
    """Adjust the original Quaternius materials rather than replacing them with flat paint."""
    for m in bpy.data.materials:
        if not m.use_nodes or m.get('styled'):
            continue
        nt = m.node_tree; p = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not p:
            continue
        m['styled'] = 1
        leafy = any(k in m.name for k in ('Leaves', 'Leaf', 'Grass', 'Flowers', 'Vine'))
        links = p.inputs['Base Color'].links
        if links:
            src = links[0].from_socket
            hsv = nt.nodes.new('ShaderNodeHueSaturation')
            hsv.inputs['Saturation'].default_value = STYLE['sat'] * (1.08 if leafy else 1)
            hsv.inputs['Value'].default_value = STYLE['val'] * (1.6 if leafy else 1)
            nt.links.new(src, hsv.inputs['Color'])
            out_sock = hsv.outputs['Color']
            if direction == 'toybox' and not leafy:
                key = next((k for k in TOY if k in m.name), None)
                if key:
                    # Keep 30% of the painted texture as value detail over a clean toy colour.
                    bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(src, bw.inputs['Color'])
                    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
                    mix.inputs['Factor'].default_value = .35
                    mix.inputs['A'].default_value = srgb(TOY[key])
                    lift = nt.nodes.new('ShaderNodeMath'); lift.operation = 'MULTIPLY_ADD'
                    lift.inputs[1].default_value = .9; lift.inputs[2].default_value = .55
                    nt.links.new(bw.outputs['Val'], lift.inputs[0])
                    comb = nt.nodes.new('ShaderNodeCombineColor')
                    for i in range(3): nt.links.new(lift.outputs[0], comb.inputs[i])
                    nt.links.new(comb.outputs['Color'], mix.inputs['B'])
                    out_sock = mix.outputs['Result']
            nt.links.new(out_sock, p.inputs['Base Color'])
            if leafy:
                # Soft translucency stands in for the paid pack's stylised foliage shader.
                tr = nt.nodes.new('ShaderNodeBsdfTranslucent'); nt.links.new(out_sock, tr.inputs['Color'])
                outn = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
                bsdf_link = outn.inputs['Surface'].links[0].from_socket
                mixs = nt.nodes.new('ShaderNodeMixShader'); mixs.inputs['Fac'].default_value = .35
                nt.links.new(bsdf_link, mixs.inputs[1]); nt.links.new(tr.outputs[0], mixs.inputs[2])
                # Preserve the alpha cut-out: mix with transparency by the original alpha.
                alpha_links = p.inputs['Alpha'].links
                if alpha_links:
                    tp = nt.nodes.new('ShaderNodeBsdfTransparent'); mix2 = nt.nodes.new('ShaderNodeMixShader')
                    nt.links.new(alpha_links[0].from_socket, mix2.inputs['Fac'])
                    nt.links.new(tp.outputs[0], mix2.inputs[1]); nt.links.new(mixs.outputs[0], mix2.inputs[2])
                    nt.links.new(mix2.outputs[0], outn.inputs['Surface'])
                else:
                    nt.links.new(mixs.outputs[0], outn.inputs['Surface'])
        if 'WindowGlass' in m.name and STYLE['glow']:
            p.inputs['Emission Color'].default_value = (1, .62, .3, 1)
            p.inputs['Emission Strength'].default_value = STYLE['glow']


def soften_foliage():
    """Spherical normals on leaf faces so crowns read as soft volumes, not black clumps."""
    for coll in [c for c in bpy.data.collections if c.name.startswith('T/')]:
        for o in coll.objects:
            if o.type != 'MESH' or o.data.get('soft'):
                continue
            me = o.data
            leaf_ids = {i for i, m in enumerate(me.materials) if m and any(k in m.name for k in ('Leaves', 'Leaf'))}
            if not leaf_ids:
                continue
            me['soft'] = 1
            leaf_verts = {v for p in me.polygons if p.material_index in leaf_ids for v in p.vertices}
            if not leaf_verts:
                continue
            c = sum((me.vertices[i].co for i in leaf_verts), Vector()) / len(leaf_verts)
            c.z -= .15 * (max(me.vertices[i].co.z for i in leaf_verts) - c.z)
            normals = [((v.co - c).normalized() if v.index in leaf_verts else v.normal.copy()) for v in me.vertices]
            me.normals_split_custom_set_from_vertices(normals)


# ---------- Island ----------
OUT = []
for i in range(72):
    a = i * math.tau / 72
    r = 1 + .06*math.sin(3*a+.4) + .035*math.cos(5*a) + .02*math.sin(9*a)
    OUT.append((9.2*r*math.cos(a), 7.0*r*math.sin(a)))


def slab(name, scale, z0, z1, mat, bevel=0, taper=1.0, segs=4):
    bm = bmesh.new()
    top = [bm.verts.new((x*scale, y*scale, z1)) for x, y in OUT]
    bot = [bm.verts.new((x*scale*taper, y*scale*taper, z0)) for x, y in OUT]
    bm.faces.new(top); bm.faces.new(list(reversed(bot)))
    n = len(OUT)
    for i in range(n):
        bm.faces.new((bot[i], bot[(i+1) % n], top[(i+1) % n], top[i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    me.materials.append(mat)
    if bevel:
        b = o.modifiers.new('round', 'BEVEL'); b.width, b.segments, b.limit_method = bevel, segs, 'ANGLE'
    for p in me.polygons: p.use_smooth = True
    return o


m_grass = mat_flat('grass', STYLE['grass'][0], .9, STYLE['grass'][1], .9)
m_sand = mat_flat('sand', STYLE['sand'], .95, '#f3e3bd', 6)
m_cliff = mat_flat('cliff', STYLE['cliff'][0], .9, STYLE['cliff'][1], 2.5)
m_cliff2 = mat_flat('cliff2', STYLE['cliff'][1], .9, STYLE['cliff'][0], 4)
slab('meadow', .95, .55, 1.0, m_grass, bevel=.35, segs=5)
slab('beach', 1.03, .05, .62, m_sand, bevel=.3, segs=4)
slab('cliff upper', .99, -1.4, .1, m_cliff, taper=.93)
slab('cliff lower', .9, -3.2, -1.35, m_cliff2, taper=.62, bevel=.4)

# ---------- Sea, with depth gradient, glints and a soft edge instead of a plate rim ----------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, .18)); sea = bpy.context.object
sea.scale = (70, 56, 1)
ms = bpy.data.materials.new('sea'); ms.use_nodes = True; nt = ms.node_tree
p = nt.nodes['Principled BSDF']; p.inputs['Roughness'].default_value = .32; p.inputs['Specular IOR Level'].default_value = .25
tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
mp.inputs['Scale'].default_value = (70/9.6, 56/7.4, 1)
nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; nt.links.new(mp.outputs['Vector'], ln.inputs[0])
ns = nt.nodes.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = 3; nt.links.new(mp.outputs['Vector'], ns.inputs['Vector'])
wob = nt.nodes.new('ShaderNodeMath'); wob.operation = 'MULTIPLY_ADD'; wob.inputs[1].default_value = .12
nt.links.new(ns.outputs['Fac'], wob.inputs[0]); nt.links.new(ln.outputs['Value'], wob.inputs[2])
ramp = nt.nodes.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
cr.elements[0].position, cr.elements[0].color = 1.04/3, srgb(STYLE['sea'][0])
cr.elements[1].position, cr.elements[1].color = 1.9/3, srgb(STYLE['sea'][2])
e = cr.elements.new(1.3/3); e.color = srgb(STYLE['sea'][1])
# Ramp input expected 0..1; normalise.
nrm = nt.nodes.new('ShaderNodeMath'); nrm.operation = 'DIVIDE'; nrm.inputs[1].default_value = 3
nt.links.new(wob.outputs[0], nrm.inputs[0]); nt.links.new(nrm.outputs[0], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
wave = nt.nodes.new('ShaderNodeTexWave'); wave.inputs['Scale'].default_value = 1.6; wave.inputs['Distortion'].default_value = 6
bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .08
nt.links.new(tc.outputs['Object'], wave.inputs['Vector']); nt.links.new(wave.outputs['Fac'], bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
# Fade to transparent towards the page.
fade = nt.nodes.new('ShaderNodeMapRange'); fade.inputs['From Min'].default_value = 1.3; fade.inputs['From Max'].default_value = 1.75
nt.links.new(ln.outputs['Value'], fade.inputs['Value'])
tp = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader')
outn = nt.nodes['Material Output']
nt.links.new(fade.outputs['Result'], mx.inputs['Fac']); nt.links.new(p.outputs[0], mx.inputs[1]); nt.links.new(tp.outputs[0], mx.inputs[2])
nt.links.new(mx.outputs[0], outn.inputs['Surface'])
sea.data.materials.append(ms)

# Foam: a soft, broken band hugging the beach (alpha falls off across its width).
m_foam = mat_flat('foam', STYLE['foam'], .6)
fm = bpy.data.materials.new('foam band'); fm.use_nodes = True; fnt = fm.node_tree
fp = fnt.nodes['Principled BSDF']; fp.inputs['Base Color'].default_value = srgb(STYLE['foam']); fp.inputs['Roughness'].default_value = .7
attr = fnt.nodes.new('ShaderNodeAttribute'); attr.attribute_name = 'edge'
fn = fnt.nodes.new('ShaderNodeTexNoise'); fn.inputs['Scale'].default_value = 1.4; fn.inputs['Detail'].default_value = 4
fr = fnt.nodes.new('ShaderNodeMath'); fr.operation = 'MULTIPLY'
cut = fnt.nodes.new('ShaderNodeMapRange'); cut.inputs['From Min'].default_value = .42; cut.inputs['From Max'].default_value = .6
fnt.links.new(fn.outputs['Fac'], cut.inputs['Value'])
fnt.links.new(attr.outputs['Fac'], fr.inputs[0]); fnt.links.new(cut.outputs['Result'], fr.inputs[1])
fnt.links.new(fr.outputs[0], fp.inputs['Alpha'])
bm = bmesh.new(); n = len(OUT); rows = []
for k, (s_, a_) in enumerate(((1.035, 0.), (1.06, 1.), (1.12, 0.))):
    rows.append([bm.verts.new((x*s_, y*s_, .2)) for x, y in OUT])
for r in range(2):
    for i in range(n):
        bm.faces.new((rows[r][i], rows[r+1][i], rows[r+1][(i+1) % n], rows[r][(i+1) % n]))
me = bpy.data.meshes.new('foam'); bm.to_mesh(me); bm.free()
at = me.attributes.new('edge', 'FLOAT', 'POINT')
for v in me.vertices:
    at.data[v.index].value = (0., 1., 0.)[v.index // n]
fo = bpy.data.objects.new('foam', me); bpy.context.scene.collection.objects.link(fo); me.materials.append(fm)

# ---------- Project Studio from the uploaded Medieval modules ----------
Z = 1.0
st = empty('Project Studio', (-2.2, .8, Z), math.radians(8), .78)
for xx in (-1, 1):
    place('M', 'Wall_Plaster_Door_Round' if xx == 1 else 'Wall_Plaster_Window_Wide_Round', (xx, -3, 0), parent=st)
    place('M', 'Wall_Plaster_WoodGrid', (xx, 3, 0), math.pi, parent=st)
for yy in (-2, 0, 2):
    for s in (-1, 1):
        place('M', 'Wall_Plaster_Window_Wide_Round' if yy != 0 else 'Wall_Plaster_WoodGrid', (s*2, yy, 0), -s*math.pi/2, parent=st)
        if yy != 0:
            place('M', 'Window_Wide_Round1', (s*2.06, yy, 0), -s*math.pi/2, parent=st)
for cx, cy in ((-2, -3), (2, -3), (-2, 3), (2, 3)):
    place('M', 'Corner_Exterior_Wood', (cx, cy, 0), parent=st)
place('M', 'Roof_RoundTiles_4x6', (0, 0, 3.12), parent=st)
place('M', 'Roof_Front_Brick4', (0, -3, 3.12), parent=st)
place('M', 'Roof_Front_Brick4', (0, 3, 3.12), math.pi, parent=st)
place('M', 'Door_1_Round', (.49, -3.06, 0), parent=st)
place('M', 'Window_Wide_Round1', (-1, -3.08, 0), parent=st)
place('M', 'WindowShutters_Wide_Round_Open', (-1, -3.05, 0), parent=st)
place('M', 'Prop_Chimney', (1.1, 1.6, 4.1), parent=st)
place('M', 'Prop_Vine2', (-2.1, -2.6, 3.0), -math.pi/2, parent=st)
place('M', 'Prop_Crate', (2.9, -3.4, 0), .4, .8, parent=st)
place('M', 'Prop_Crate', (3.0, -2.5, 0), -.2, .6, parent=st)
# Workbench signal outside the studio: a wagon with the day's materials.
place('M', 'Prop_Wagon', (3.6, 1.0, 0), math.radians(-70), .75, parent=st)

# Fence along the back meadow.
for i in range(4):
    place('M', 'Prop_WoodenFence_Single', (-7.2 + i*2.05, 4.4 - i*.15, Z), math.radians(-4), .9)

# ---------- Path of pressed stones: studio door -> pier ----------
pts = [(-1.5, -2.0), (-.6, -3.2), (.6, -4.3), (1.6, -5.4), (2.3, -6.3)]
for i, (x, y) in enumerate(pts):
    place('N', 'RockPath_Round_Wide' if i % 2 == 0 else 'RockPath_Round_Thin', (x, y, Z - .04), random.uniform(0, 6), .62)

# ---------- Trees, shrubs, flowers ----------
for name, x, y, s in [('CommonTree_1', -6.6, 2.2, .5), ('CommonTree_3', -7.6, -.8, .38), ('CommonTree_1', 4.8, 4.0, .42),
                      ('Pine_3', -5.0, 4.4, .45), ('CommonTree_3', 6.6, 2.2, .34)]:
    place('N', name, (x, y, Z - .05), random.uniform(0, 6), s)
for x, y in [(-4.6, -2.6), (4.6, -1.6), (-6.5, -3.4), (5.8, -3.2)]:
    place('N', 'Bush_Common_Flowers', (x, y, Z - .05), random.uniform(0, 6), .55)
for x, y in [(-3.4, -4.2), (3.6, -3.8), (-7.3, 1.0), (2.8, 3.8), (-.8, 4.2)]:
    place('N', 'Flower_4_Group', (x, y, Z - .05), random.uniform(0, 6), .4)
for _ in range(70):
    a = random.uniform(0, math.tau); r = random.uniform(.25, .88)
    x, y = 9.2*r*math.cos(a), 7*r*math.sin(a)
    if -5 < x < 1.5 and -3.5 < y < 4.5:
        continue
    place('N', random.choice(['Grass_Common_Short', 'Grass_Wispy_Short', 'Clover_1', 'Fern_1']), (x, y, Z - .05), random.uniform(0, 6), random.uniform(.35, .55))
for x, y, s in [(-8.6, -3.9, .5), (8.4, -2.4, .42), (7.9, 3.4, .55), (-2.0, -7.1, .36), (-8.9, 2.9, .4)]:
    place('N', 'Rock_Medium_2' if s > .4 else 'Rock_Medium_1', (x, y, .1), random.uniform(0, 6), s)

# ---------- Succulent shelf: real preference, no invented collection ----------
m_pot = mat_flat('terracotta', '#c9744f', .8, '#d98c64', 8)
bench = empty('succulent bench', (2.4, -1.1, Z), math.radians(-20))
place('M', 'Prop_Crate', (0, 0, 0), 0, .55, parent=bench)
for i, (dx, dy, dz, s) in enumerate([(-.95, .1, 0, .3), (0, 0, .55, .26), (.9, -.05, 0, .32)]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=s, depth=s*1.1, location=(dx, dy, dz + s*.55))
    pot = bpy.context.object; pot.parent = bench; pot.data.materials.append(m_pot)
    b = pot.modifiers.new('b', 'BEVEL'); b.width, b.segments = .04, 3
    for f in pot.data.polygons: f.use_smooth = True
    place('N', 'Plant_1' if i != 1 else 'Plant_7', (dx, dy, dz + s*1.05), random.uniform(0, 6), s*1.3 if i != 1 else s*1.6, parent=bench)

# ---------- Pier and sailing boat ----------
m_wood = mat_flat('pier wood', '#9a6a48', .8, '#b8845a', 5)
for j in range(3):
    place('M', 'Floor_WoodLight', (2.6 + j*0.0, -7.0 - j*2, .62), 0, 1)
for px in (1.65, 3.55):
    for py in (-6.2, -8.2, -11.8):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=.11, depth=1.6, location=(px, py, -.1))
        bpy.context.object.data.materials.append(m_wood)
m_hull = mat_flat('hull', '#d4685a' if direction != 'toybox' else '#f0b54a', .5)
m_sail = mat_flat('sail', '#fbf3e3', .7)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(6.2, -9.6, .62))
hull = bpy.context.object; hull.scale = (.55, 1.35, .42); hull.rotation_euler.z = math.radians(18)
bpy.ops.object.mode_set(mode='EDIT'); bm = bmesh.from_edit_mesh(hull.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > .25], context='VERTS'); bmesh.update_edit_mesh(hull.data)
bpy.ops.object.mode_set(mode='OBJECT'); hull.data.materials.append(m_hull)
sol = hull.modifiers.new('s', 'SOLIDIFY'); sol.thickness = .08
for f in hull.data.polygons: f.use_smooth = True
bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=.05, depth=2.6, location=(6.2, -9.6, 1.5)); bpy.context.object.data.materials.append(m_wood)
sm = bpy.data.meshes.new('sail'); sm.from_pydata([(6.2, -9.55, 2.7), (6.2, -9.55, .55), (6.55, -8.5, .55)], [], [(0, 1, 2)])
so = bpy.data.objects.new('sail', sm); bpy.context.scene.collection.objects.link(so); sm.materials.append(m_sail)
so.rotation_euler.z = 0
# Little wake ring around the boat.
bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=.025, location=(6.2, -9.6, .2)); w = bpy.context.object
w.scale = (.6, 1.1, .2); w.rotation_euler.z = math.radians(18); w.data.materials.append(m_foam)

# ---------- Materials, light, camera ----------
restyle_imported(); soften_foliage()
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
try:
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception:
    pass
sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 32
sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
sc.render.film_transparent = True
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = {'storybook': 'AgX - Punchy', 'toybox': 'AgX - Base Contrast', 'lantern': 'AgX - Medium High Contrast'}[direction]
world = bpy.data.worlds.new('sky'); sc.world = world; world.use_nodes = True
bg = world.node_tree.nodes['Background']; bg.inputs[0].default_value = STYLE['sky'] + (1,); bg.inputs[1].default_value = STYLE['sky_e']
bpy.ops.object.light_add(type='SUN'); sun = bpy.context.object
sun.rotation_euler = STYLE['sun_rot']; sun.data.energy = STYLE['sun_e']; sun.data.color = STYLE['sun']
sun.data.angle = math.radians(STYLE['sun_angle'])
bpy.ops.object.camera_add(location=(20, -30, 31)); cam = bpy.context.object
target = Vector((0, -1.2, 0))
cam.location = target + Vector((20, -30, 31))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type, cam.data.ortho_scale = 'ORTHO', 27
sc.camera = cam
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
