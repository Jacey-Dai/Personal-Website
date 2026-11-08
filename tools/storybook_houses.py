"""Hand-modelled storybook houses for the island, one silhouette per destination.

Each builder returns an empty tagged with `place`, holding chunky, softly bevelled parts:
stepped shingle roofs, trimmed windows with sills and flower boxes, and a signature
feature per building (studio north-light roof, museum portico and dome, round welcome
cottage, striped kiosk awning, barrel-vaulted greenhouse). Local units are metres,
+Z up, front facing -Y (towards the camera), ground at local z = 0.
Glass materials keep `WindowGlass` / `glass` in their names, which the visited window
light (export_building_layers.py, src/island3d.js) looks for.
"""
import math
import random
import bmesh
import bpy
from mathutils import Matrix, Vector
from quaternius_kit import flat, srgb

_mats = {}
PALETTE = {
    # name: (base, variation, roughness)
    'plaster cream': ('#f4e6c9', '#ecd8b3', .9),
    'plaster peach': ('#f3cba6', '#eebb93', .9),
    'stone white': ('#efe7d8', '#e0d4bf', .85),
    'kiosk cream': ('#f8efdc', None, .85),
    'plinth stone': ('#bdae98', '#a89880', .95),
    'timber': ('#7c5236', '#8d6040', .8),
    'trim cream': ('#fbf6ea', None, .6),
    'roof coral': ('#c95f48', '#d8775a', .75),
    'roof coral light': ('#d6745a', '#e08a6b', .75),
    'roof slate': ('#536f91', '#6582a4', .7),
    'roof slate light': ('#6280a2', '#7592b2', .7),
    'roof sage': ('#5a9682', '#6fae96', .75),
    'roof sage light': ('#6aa892', '#80bba3', .75),
    'copper': ('#6aa697', '#82b8a8', .5),
    'stripe mustard': ('#e0a73f', None, .7),
    'stripe cream': ('#f9f1df', None, .7),
    'door teal': ('#3d7d86', None, .6),
    'door coral': ('#b9543f', None, .6),
    'door slate': ('#455f80', None, .6),
    'post teal': ('#3f7f88', None, .6),
    'brass': ('#d9a84a', None, .35),
    'brick': ('#b4644a', '#c2785b', .9),
    'chimney cap': ('#5b5552', None, .8),
    'leaf': ('#5f9443', '#7cb052', .8),
    'flower red': ('#e0604f', None, .6),
    'flower yellow': ('#f2c64b', None, .6),
    'flower pink': ('#ee9bb0', None, .6),
    'flower white': ('#fbf4ea', None, .6),
    'banner coral': ('#d46a52', None, .7),
    'banner mustard': ('#dca743', None, .7),
    'banner teal': ('#3f8f99', None, .7),
    'canvas': ('#fbf7ee', None, .8),
    'paint blue': ('#4f86b8', None, .6),
    'lantern': ('#3e3a38', None, .5),
    'terracotta': ('#c9744f', '#d98c64', .8),
}


def mat(name):
    if name not in _mats:
        if name == 'glass':
            m = flat('WindowGlass storybook', '#b6dbe0', .1)
        elif name == 'greenhouse glass':
            m = bpy.data.materials.new('glass greenhouse')
            m.use_nodes = True
            p = m.node_tree.nodes['Principled BSDF']
            p.inputs['Base Color'].default_value, p.inputs['Roughness'].default_value = srgb('#d7eeee'), .12
            p.inputs['Alpha'].default_value = .38
        elif name == 'lamp glass':
            m = flat('WindowGlass lantern', '#ffe3a6', .2)
        else:
            base, vary, rough = PALETTE[name]
            m = flat(name, base, rough, vary, 6)
        _mats[name] = m
    return _mats[name]


# ---------- primitives (all parented, local coordinates) ----------
def _object(name, bm, materials, parent, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0, segments=2, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    for m in materials:
        me.materials.append(m)
    o.location, o.rotation_euler = loc, rot
    o.parent = parent
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if bevel:
        b = o.modifiers.new('Soft edges', 'BEVEL')
        b.width, b.segments, b.limit_method = bevel, segments, 'ANGLE'
    return o


def empty(name, parent, loc=(0, 0, 0), rot=0):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location, e.rotation_euler.z, e.parent = loc, rot, parent
    return e


def box(name, parent, center, size, material, bevel=.025, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    return _object(name, bm, [mat(material)], parent, center, rot, bevel)


def slab(name, parent, origin, size, material, rot=(0, 0, 0), bevel=.02):
    """A box whose local origin is its top-back edge: x centred, y in [0, depth], z in [0, height]."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, size[1]/2, size[2]/2), verts=bm.verts)
    return _object(name, bm, [mat(material)], parent, origin, rot, bevel)


def cyl(name, parent, center, r, h, material, segments=24, r2=None, rot=(0, 0, 0), bevel=0, smooth=True, spin=0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=r, radius2=r if r2 is None else r2, depth=h)
    if spin:
        bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(spin, 3, 'Z'))
    o = _object(name, bm, [mat(material)], parent, center, rot, bevel, smooth=smooth)
    if smooth:
        o.data.set_sharp_from_angle(angle=math.radians(40))
    return o


def ball(name, parent, center, r, material, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    return _object(name, bm, [mat(material)], parent, center, smooth=True)


def solid(name, parent, verts, faces, material, loc=(0, 0, 0), bevel=0):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in verts]
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _object(name, bm, [mat(material)], parent, loc, bevel=bevel)


def prism(name, parent, width, length, z0, rise, material, y0=None):
    """Gable infill: a triangle in XZ (width, rise) extruded along Y."""
    y0 = -length/2 if y0 is None else y0
    y1 = y0 + length
    w = width/2
    v = [(-w, y0, z0), (w, y0, z0), (0, y0, z0 + rise), (-w, y1, z0), (w, y1, z0), (0, y1, z0 + rise)]
    return solid(name, parent, v, [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], material)


def tube(name, parent, points, material, width=.04):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions, data.bevel_depth, data.bevel_resolution = '3D', width, 2
    spline = data.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for target, xyz in zip(spline.points, points):
        target.co = (*xyz, 1)
    o = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat(material))
    o.parent = parent
    return o


# ---------- roofs ----------
def shingles(name, parent, top, bottom, width, rows, materials, thick=.1, jitter=.012):
    """Overlapping shingle courses on one roof plane.

    The plane slopes in local YZ from `top` (y, z) down to `bottom` and spans `width` in X.
    Each course pivots on its upper edge and lifts its lower edge by its thickness,
    which gives the stepped, hand-laid look.
    """
    d = Vector((bottom[0] - top[0], bottom[1] - top[1]))
    length = d.length
    fall = math.atan2(-d.y, d.x)
    course = length / rows
    for k in range(rows):
        s = k * course
        y, z = top[0] + d.x/length*s, top[1] + d.y/length*s
        lift = math.atan2(thick*.9, course*1.25)
        tilt = fall - lift + random.uniform(-jitter, jitter)
        slab(f'{name} course', parent, (random.uniform(-.015, .015), y, z - thick*.25),
             (width + random.uniform(0, .04), course*1.25 + .02, thick), materials[k % len(materials)],
             rot=(-tilt, 0, 0))


def gable_roof(name, parent, width, length, z0, rise, materials, overhang=.22, rows=5, ridge='trim cream', y=0):
    """A ridge along Y over a width x length body whose walls end at z0; gables at both ends."""
    w = width/2 + overhang
    ridge_z = z0 + rise
    eave_drop = overhang * rise / (width/2)
    for side in (1, -1):
        e = empty(f'{name} side', parent, (0, y, 0), side*math.pi/2)
        shingles(name, e, (0, ridge_z + .03), (w, z0 - eave_drop), length + 2*overhang*.8, rows, materials)
    cyl(f'{name} ridge', parent, (0, y, ridge_z + .07), .07, length + 2*overhang*.8, ridge, 12,
        rot=(math.pi/2, 0, 0))


# ---------- facade details ----------
def window(parent, loc, rot, w=.55, h=.75, arch=False, shutters=None, flowers=None, frame='trim cream', panes=True):
    """A trimmed window facing local -Y: glass, frame, mullions, sill, optional shutters and flower box."""
    e = empty('Window', parent, loc, rot)
    t = .06
    box('Window glass', e, (0, .0, h/2), (w, .05, h), 'glass', 0)
    if arch:
        cyl('Window glass arch', e, (0, 0, h), w/2, .05, 'glass', 16, rot=(math.pi/2, 0, 0), smooth=False)
        tube('Window arch frame', e, [(w/2*math.cos(a*math.pi/12), -.04, h + w/2*math.sin(a*math.pi/12)) for a in range(13)],
             frame, .035)
    else:
        box('Window head', e, (0, -.03, h + t/2), (w + 2*t, .08, t), frame, .012)
    for x in (-1, 1):
        box('Window jamb', e, (x*(w/2 + t/2), -.03, h/2), (t, .08, h), frame, .012)
    if panes:
        box('Window mullion', e, (0, -.04, h/2), (.03, .03, h), frame, 0)
        box('Window transom', e, (0, -.04, h*.55), (w, .03, .03), frame, 0)
    box('Window sill', e, (0, -.07, -.03), (w + .2, .16, .06), frame, .015)
    if shutters:
        for x in (-1, 1):
            box('Shutter', e, (x*(w/2 + t + w*.26), -.04, h/2), (w*.48, .04, h*.98), shutters, .015)
    if flowers:
        box('Flower box', e, (0, -.13, -.13), (w + .1, .16, .16), flowers, .02)
        for i in range(5):
            x = -w/2 + (i + .5)*w/5
            ball('Flower box leaves', e, (x, -.13, -.03), .08, 'leaf', (1.1, .9, .8))
            ball('Flower', e, (x + random.uniform(-.03, .03), -.18, .03), .045,
                 ('flower red', 'flower pink', 'flower yellow', 'flower white')[(i + len(flowers)) % 4])
    return e


def door(parent, loc, rot, w=.6, h=1.1, colour='door teal', arch=True, frame='trim cream', double=False):
    e = empty('Door', parent, loc, rot)
    box('Door leaf', e, (0, -.02, h/2), (w, .07, h), colour, .012)
    if arch:
        cyl('Door arch', e, (0, -.02, h), w/2, .07, colour, 16, rot=(math.pi/2, 0, 0), smooth=False)
        ra = w/2 + .04
        tube('Door arch frame', e, [(ra*math.cos(a*math.pi/12), -.05, h + ra*math.sin(a*math.pi/12)) for a in range(13)],
             frame, .04)
    else:
        box('Door head', e, (0, -.05, h + .04), (w + .16, .09, .08), frame, .012)
    for x in (-1, 1):
        box('Door jamb', e, (x*(w/2 + .04), -.05, h/2), (.08, .09, h), frame, .012)
    if double:
        box('Door split', e, (0, -.065, h/2), (.025, .02, h*.98), frame, 0)
        for s in (-1, 1):
            box('Door brace', e, (s*w/4, -.07, h/2), (.05, .02, math.hypot(w/2, h)*.92), frame, 0,
                rot=(0, s*math.atan2(w/2, h), 0))
    ball('Door knob', e, (w*.3 if not double else .07, -.08, h*.48), .035, 'brass')
    box('Door step', e, (0, -.2, .03), (w + .3, .3, .06), 'plinth stone', .02)
    return e


def lantern(parent, loc, rot=0):
    e = empty('Lantern', parent, loc, rot)
    box('Lantern bracket', e, (0, -.1, .15), (.03, .2, .03), 'lantern', 0)
    box('Lantern glass', e, (0, -.2, .05), (.1, .1, .14), 'lamp glass', .01)
    cyl('Lantern cap', e, (0, -.2, .15), .08, .06, 'lantern', 4, r2=.01, spin=math.pi/4)
    return e


def potted_plant(parent, loc, scale=1, flower='flower red'):
    e = empty('Potted plant', parent, loc)
    cyl('Pot', e, (0, 0, .1*scale), .11*scale, .2*scale, 'terracotta', 16, r2=.14*scale)
    ball('Plant', e, (0, 0, .28*scale), .16*scale, 'leaf')
    for a in range(3):
        ball('Bloom', e, (.09*scale*math.cos(a*2.1), .09*scale*math.sin(a*2.1), .36*scale), .045*scale, flower)
    return e


# ---------- the five buildings ----------
def project_studio(loc):
    """Maker's studio: sawtooth north-light roof, barn doors, chimney, easel outside."""
    root = empty('Project Studio', None, loc)
    root['place'] = 'projects'
    box('Studio plinth', root, (0, 0, .12), (3.2, 4.0, .24), 'plinth stone', .04)
    box('Studio walls', root, (0, 0, .24 + 1.1), (3.0, 3.8, 2.2), 'plaster cream', .03)
    for x in (-1.5, 1.5):
        for y in (-1.9, 1.9):
            box('Studio corner post', root, (x, y, 1.34), (.16, .16, 2.22), 'timber', .02)
    box('Studio top beam', root, (0, 0, 2.48), (3.12, 3.92, .14), 'timber', .02)
    # Two north-light teeth: glazed faces look towards the town, roofs fall away behind them.
    z0, z1 = 2.55, 3.45
    for a, b in ((-1.9, 0), (0, 1.9)):
        solid('Studio tooth infill', root, [(-1.5, a, z0), (1.5, a, z0), (-1.5, b, z0), (1.5, b, z0),
                                             (-1.5, a + .05, z1), (1.5, a + .05, z1)],
              [(0, 1, 3, 2), (0, 4, 5, 1), (2, 3, 5, 4), (0, 2, 4), (1, 5, 3)], 'plaster cream')
        box('Studio north light', root, (0, a - .02, (z0 + z1)/2), (2.7, .05, z1 - z0 - .1), 'glass', 0)
        for x in (-1.35, -.68, 0, .68, 1.35):
            box('Studio light mullion', root, (x, a - .05, (z0 + z1)/2), (.06, .06, z1 - z0), 'trim cream', .01)
        box('Studio light sill', root, (0, a - .06, z0 + .02), (2.9, .12, .06), 'trim cream', .01)
        e = empty('Studio roof plane', root, (0, 0, 0))
        shingles('Studio roof', e, (a - .16, z1 + .1), (b + .22, z0 - .06), 3.5, 4, ['roof coral', 'roof coral light'], thick=.13)
        box('Studio roof fascia', root, (0, a - .2, z1 + .06), (3.6, .1, .2), 'timber', .02)
    # Chimney.
    box('Studio chimney', root, (1.0, 1.25, 3.25), (.42, .42, 1.5), 'brick', .03)
    box('Studio chimney cap', root, (1.0, 1.25, 4.03), (.54, .54, .1), 'chimney cap', .02)
    # Front: barn doors under a little awning, one window with a flower box.
    door(root, (-.45, -1.9, .24), 0, 1.15, 1.6, 'door teal', arch=False, double=True)
    shingles('Studio awning', empty('Awning', root, (-.45, -1.9, 0)), (0, 2.25), (-.6, 1.95), 1.7, 2,
             ['roof coral', 'roof coral light'], thick=.06)
    for x in (-1.2, .3):
        box('Awning bracket', root, (x, -2.15, 2.08), (.06, .5, .06), 'timber', .01, rot=(math.radians(-35), 0, 0))
    window(root, (.9, -1.9, 1.0), 0, .62, .8, shutters='door teal', flowers='timber')
    lantern(root, (.35, -1.9, 1.75))
    for y in (-.85, .85):
        window(root, (1.5, y, 1.0), math.pi/2, .6, .8, flowers='timber' if y < 0 else None)
        window(root, (-1.5, y, 1.0), -math.pi/2, .6, .8)
    window(root, (0, 1.9, 1.0), math.pi, .6, .8)
    # Easel with a painted canvas beside the door.
    easel = empty('Easel', root, (-2.05, -2.45, 0), math.radians(-25))
    for x, tilt in ((-.22, .12), (.22, -.12)):
        box('Easel leg', easel, (x, 0, .62), (.05, .05, 1.3), 'timber', 0, rot=(math.radians(-8), tilt, 0))
    box('Easel back leg', easel, (0, .25, .6), (.05, .05, 1.25), 'timber', 0, rot=(math.radians(20), 0, 0))
    box('Canvas', easel, (0, -.06, .95), (.6, .04, .5), 'canvas', .01)
    for (x, z), c in (((-.12, .98), 'paint blue'), ((.1, 1.05), 'flower yellow'), ((.05, .88), 'roof sage')):
        ball('Paint', easel, (x, -.09, z), .07, c, (1.3, .2, 1))
    box('Easel shelf', easel, (0, -.05, .68), (.7, .1, .04), 'timber', 0)
    potted_plant(root, (.25, -2.2, 0), 1.2, 'flower yellow')
    return root


def experience_museum(loc):
    """Little gallery: columned portico, pediment oculus, hanging banners, copper dome."""
    root = empty('Experience Museum', None, loc)
    root['place'] = 'experience'
    box('Museum plinth', root, (0, -.1, .17), (3.6, 5.0, .34), 'plinth stone', .04)
    for i, (d, h) in enumerate(((.3, .24), (.3, .12))):
        box('Museum step', root, (0, -2.6 - .15 - i*.3, h/2), (2.2 + .4*i, d, h), 'plinth stone', .02)
    box('Museum walls', root, (0, .3, .34 + 1.15), (3.2, 3.8, 2.3), 'stone white', .03)
    for x in (-1.6, 1.6):
        for y in (-1.6, 2.2):
            box('Museum pilaster', root, (x, y, 1.49), (.22, .22, 2.3), 'trim cream', .02)
    box('Museum cornice', root, (0, -.25, 2.74), (3.5, 5.0, .2), 'trim cream', .03)
    box('Museum frieze', root, (0, -.25, 2.9), (3.3, 4.85, .14), 'stone white', .02)
    prism('Museum pediment', root, 3.3, 4.85, 2.97, .85, 'stone white', y0=-2.675)
    gable_roof('Museum roof', root, 3.3, 4.85, 2.97, .85, ['roof slate', 'roof slate light'], .2, 5, y=-.25)
    # Portico columns.
    for x in (-1.3, -.45, .45, 1.3):
        cyl('Museum column', root, (x, -2.25, 1.52), .13, 2.1, 'trim cream', 16)
        box('Column base', root, (x, -2.25, .4), (.36, .36, .12), 'trim cream', .02)
        box('Column capital', root, (x, -2.25, 2.58), (.38, .38, .12), 'trim cream', .02)
    # Oculus in the pediment.
    cyl('Oculus', root, (0, -2.69, 3.3), .24, .04, 'glass', 20, rot=(math.pi/2, 0, 0), smooth=False)
    bpy.ops.mesh.primitive_torus_add(major_radius=.27, minor_radius=.04, location=(0, 0, 0))
    ring = bpy.context.object
    ring.name, ring.rotation_euler, ring.location, ring.parent = 'Oculus frame', (math.pi/2, 0, 0), (0, -2.72, 3.3), root
    ring.data.materials.append(mat('trim cream'))
    # Banners between the outer columns.
    for x, c in ((-.87, 'banner coral'), (.87, 'banner mustard')):
        box('Banner rod', root, (x, -2.25, 2.48), (.5, .04, .04), 'brass', 0)
        banner = empty('Banner', root, (x, -2.25, 2.46))
        cloth = solid('Banner cloth', banner, [(-.2, 0, 0), (.2, 0, 0), (.2, 0, -1.0), (0, 0, -.85), (-.2, 0, -1.0)],
              [(0, 1, 2, 3, 4)], c)
        cloth.modifiers.new('Cloth thickness', 'SOLIDIFY').thickness = .03
    door(root, (0, -1.6, .34), 0, .8, 1.45, 'door slate', frame='trim cream')
    for x in (-1.05, 1.05):
        window(root, (x, -1.6, .85), 0, .5, 1.05, arch=True)
    for y in (-.75, .55, 1.75):
        for side in (-1, 1):
            window(root, (side*1.6, y, .85), side*math.pi/2, .5, 1.05, arch=True)
    # Copper dome on a drum over the gallery.
    cyl('Museum drum', root, (0, .9, 3.75), .62, .7, 'stone white', 8, spin=math.pi/8, smooth=False, bevel=.02)
    for a in range(8):
        ang = a*math.pi/4
        window(root, (.6*math.sin(ang), .9 - .6*math.cos(ang), 3.55), ang, .2, .3, panes=False)
    cyl('Museum drum cornice', root, (0, .9, 4.13), .72, .1, 'trim cream', 8, spin=math.pi/8, smooth=False)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=.66)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -.01], context='VERTS')
    _object('Museum dome', bm, [mat('copper')], root, (0, .9, 4.17), smooth=True)
    cyl('Dome lantern', root, (0, .9, 4.92), .1, .2, 'trim cream', 12)
    ball('Dome finial', root, (0, .9, 5.1), .09, 'brass')
    for x in (-1.15, 1.15):
        potted_plant(root, (x, -2.95, 0), 1.3, 'flower pink')
    return root


def welcome_cottage(loc):
    """Round welcome cottage: layered sage roof, arched coral door, flower boxes and a bench."""
    root = empty('Welcome Center', None, loc)
    root['place'] = 'about'
    r = 1.0
    cyl('Cottage plinth', root, (0, 0, .1), r + .12, .2, 'plinth stone', 32, bevel=.03)
    cyl('Cottage walls', root, (0, 0, .2 + .8), r, 1.6, 'plaster peach', 32)
    cyl('Cottage band', root, (0, 0, 1.78), r + .05, .1, 'trim cream', 32)
    tiers = [(1.45, .92, 1.75, .5), (1.18, .6, 2.17, .52), (.86, .05, 2.6, 1.0)]
    for i, (r1, r2, z, h) in enumerate(tiers):
        colour = 'roof sage' if i % 2 == 0 else 'roof sage light'
        cyl('Cottage roof tier', root, (0, 0, z + h/2), r1, h, colour, 32, r2=r2, bevel=.03)
        cyl('Cottage roof lip', root, (0, 0, z + .04), r1 + .02, .12, colour, 32, bevel=.04)
    box('Cottage chimney', root, (.45, .35, 2.75), (.26, .26, .95), 'brick', .02)
    box('Cottage chimney cap', root, (.45, .35, 3.25), (.36, .36, .07), 'chimney cap', .01)
    ball('Cottage finial', root, (0, 0, 3.62), .09, 'brass')
    door(root, (0, -r + .02, .2), 0, .58, 1.05, 'door coral')
    # Porch hood above the door.
    hood = empty('Door hood', root, (0, -r, 0))
    shingles('Door hood', hood, (.02, 1.75), (-.42, 1.55), .95, 2, ['roof sage', 'roof sage light'], thick=.05)
    for a, flower in ((-55, 'timber'), (55, 'timber'), (125, None), (-125, None), (180, None)):
        ang = math.radians(a)
        window(root, (r*math.sin(ang)*1.01, -r*math.cos(ang)*1.01, .78), ang, .42, .6, arch=True,
               flowers=flower, shutters='door teal' if flower else None)
    lantern(root, (.42, -r + .03, 1.42))
    # Bench and pots welcome visitors.
    bench = empty('Bench', root, (-1.35, -.75, 0), math.radians(-35))
    box('Bench seat', bench, (0, 0, .32), (.8, .3, .06), 'timber', .015)
    box('Bench back', bench, (0, .14, .55), (.8, .05, .3), 'timber', .015)
    for x in (-.32, .32):
        box('Bench leg', bench, (x, 0, .16), (.06, .26, .32), 'timber', .01)
    potted_plant(root, (.5, -1.25, 0), 1.2, 'flower red')
    potted_plant(root, (-.5, -1.25, 0), 1.0, 'flower yellow')
    return root


def notice_kiosk(loc):
    """Octagonal news kiosk with a striped awning, service hatch and posters."""
    root = empty('Noticeboard kiosk', None, loc)
    root['place'] = 'currently'
    r = .9
    apothem = r*math.cos(math.pi/8)
    cyl('Kiosk plinth', root, (0, 0, .09), r + .15, .18, 'plinth stone', 8, spin=math.pi/8, smooth=False, bevel=.02)
    cyl('Kiosk walls', root, (0, 0, .18 + .85), r, 1.7, 'kiosk cream', 8, spin=math.pi/8, smooth=False)
    cyl('Kiosk skirting', root, (0, 0, .3), r + .03, .22, 'post teal', 8, spin=math.pi/8, smooth=False)
    for k in range(8):
        a = math.pi/8 + k*math.pi/4
        box('Kiosk post', root, (r*math.sin(a), -r*math.cos(a), 1.03), (.09, .09, 1.72), 'post teal', .015, rot=(0, 0, a))
    # Service hatch at the front, posters on the other faces.
    e = empty('Hatch', root, (0, -apothem, 0))
    box('Kiosk hatch glass', e, (0, -.01, 1.25), (.6, .04, .55), 'glass', 0)
    box('Kiosk counter', e, (0, -.12, .95), (.72, .26, .05), 'post teal', .01)
    box('Kiosk hatch frame', e, (0, -.03, 1.55), (.72, .06, .06), 'trim cream', .01)
    for x in (-1, 1):
        box('Kiosk hatch frame', e, (x*.33, -.03, 1.25), (.06, .06, .6), 'trim cream', .01)
    posters = ['banner coral', 'flower yellow', 'paint blue', 'roof sage', 'banner mustard', 'flower pink', 'canvas']
    for k in range(1, 8):
        a = k*math.pi/4
        p = empty('Poster', root, (apothem*math.sin(a), -apothem*math.cos(a), 0), a)
        box('Poster', p, (random.uniform(-.06, .06), -.015, 1.15 + random.uniform(-.08, .08)), (.42, .02, .58),
            posters[k - 1], .005)
    # Striped awning cone and a scalloped valance.
    bm = bmesh.new()
    n, ra, z0, rise = 16, 1.3, 1.92, .95
    apex = bm.verts.new((0, 0, z0 + rise))
    ring = [bm.verts.new((ra*math.cos(i*math.tau/n), ra*math.sin(i*math.tau/n), z0)) for i in range(n)]
    for i in range(n):
        f = bm.faces.new((ring[i], ring[(i + 1) % n], apex))
        f.material_index = i % 2
    awning = _object('Kiosk awning', bm, [mat('stripe mustard'), mat('stripe cream')], root)
    awning.modifiers.new('Awning thickness', 'SOLIDIFY').thickness = .05
    chord = 2*ra*math.sin(math.pi/n)
    for i in range(n):
        a = (i + .5)*math.tau/n
        flap = empty('Valance flap', root, (ra*math.cos(math.pi/n)*math.cos(a), ra*math.cos(math.pi/n)*math.sin(a), z0),
                     a + math.pi/2)
        pts = [(chord/2*math.cos(math.pi*j/8), 0, -.2*math.sin(math.pi*j/8)) for j in range(9)]
        f = solid('Kiosk valance', flap, pts, [tuple(range(9))], 'stripe mustard' if i % 2 == 0 else 'stripe cream')
        f.modifiers.new('Flap thickness', 'SOLIDIFY').thickness = .03
    cyl('Kiosk ceiling', root, (0, 0, 1.9), r + .02, .06, 'post teal', 8, spin=math.pi/8, smooth=False)
    cyl('Kiosk spire', root, (0, 0, z0 + rise + .15), .03, .35, 'brass', 8)
    ball('Kiosk finial', root, (0, 0, z0 + rise + .34), .08, 'brass')
    return root


def curiosity_greenhouse(loc):
    """Barrel-vaulted glasshouse with an entrance bay, ridge cresting and potted succulents."""
    root = empty('Curiosity Greenhouse', None, loc)
    root['place'] = 'beyond'
    L, W, wall, vault = 4.4, 3.0, 1.3, 1.0
    base = .36
    box('Greenhouse plinth', root, (0, 0, base/2), (L + .2, W + .2, base), 'brick', .03)
    box('Greenhouse glass walls', root, (0, 0, base + wall/2), (L, W, wall), 'greenhouse glass', 0)
    top = base + wall
    profile = [(W/2*math.cos(i*math.pi/12), top + vault*math.sin(i*math.pi/12)) for i in range(13)]
    # Glass vault (single-sided panes, like the old greenhouse roof).
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y, z)) for y, z in profile] for x in (-L/2, L/2)]
    for i in range(12):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    _object('Greenhouse vault glass', bm, [mat('greenhouse glass')], root)
    for x in (-L/2, L/2):
        bm = bmesh.new()
        vs = [bm.verts.new((x, y, z)) for y, z in profile]
        bm.faces.new(vs)
        _object('Greenhouse vault end', bm, [mat('greenhouse glass')], root)
    for i in range(9):
        x = -L/2 + i*L/8
        tube('Greenhouse rib', root, [(x, y, z) for y, z in profile], 'trim cream', .04)
        for y in (-W/2, W/2):
            box('Greenhouse post', root, (x, y, base + wall/2), (.07, .07, wall), 'trim cream', 0)
    for y in (-W/2, W/2):
        for z in (base + .02, base + wall*.55, top):
            box('Greenhouse rail', root, (0, y, z), (L + .05, .07, .07), 'trim cream', 0)
    for x in (-L/2, L/2):
        for y in (-W/4, 0, W/4):
            box('Greenhouse end post', root, (x, y, base + wall/2), (.07, .07, wall), 'trim cream', 0)
        box('Greenhouse end rail', root, (x, 0, top), (.07, W, .07), 'trim cream', 0)
    for i in (3, 6, 9):
        y, z = profile[i]
        tube('Greenhouse purlin', root, [(-L/2, y, z), (L/2, y, z)], 'trim cream', .035)
    # Ridge vent and cresting.
    box('Greenhouse ridge vent', root, (0, 0, top + vault + .08), (L*.7, .4, .14), 'trim cream', .02)
    for i in range(15):
        x = -L*.33 + i*L*.66/14
        ball('Cresting', root, (x, 0, top + vault + .2), .045, 'roof sage')
    for x in (-L/2 - .02, L/2 + .02):
        ball('Greenhouse finial', root, (x, 0, top + vault + .1), .1, 'brass')
    # Entrance bay with its own small vault and sage door.
    bay = empty('Greenhouse entrance', root, (0, -W/2, 0))
    box('Entrance glass', bay, (0, -.3, base + .75), (1.1, .6, 1.5), 'greenhouse glass', 0)
    prof = [(.6*math.cos(i*math.pi/8), base + 1.5 + .45*math.sin(i*math.pi/8)) for i in range(9)]
    tube('Entrance arch', bay, [(x, -.62, z) for x, z in prof], 'trim cream', .045)
    tube('Entrance arch back', bay, [(x, 0, z) for x, z in prof], 'trim cream', .04)
    bm = bmesh.new()
    rr = [[bm.verts.new((x, y, z)) for x, z in prof] for y in (-.62, 0)]
    for i in range(8):
        bm.faces.new((rr[0][i], rr[0][i + 1], rr[1][i + 1], rr[1][i]))
    _object('Entrance vault glass', bm, [mat('greenhouse glass')], bay)
    bm = bmesh.new()
    bm.faces.new([bm.verts.new((x, -.62, z)) for x, z in prof])
    _object('Entrance fan glass', bm, [mat('greenhouse glass')], bay)
    for x in (-.55, .55):
        box('Entrance post', bay, (x, -.6, base + .75), (.08, .08, 1.5), 'trim cream', 0)
    door(bay, (0, -.62, base), 0, .7, 1.25, 'roof sage', arch=False)
    ball('Entrance finial', bay, (0, -.62, base + 2.0), .08, 'brass')
    # Benches of succulents inside, pots by the door.
    for y in (-.75, .75):
        box('Greenhouse bench', root, (0, y, base + .55), (L - .5, .6, .08), 'timber', .015)
        for i in range(5):
            x = -1.6 + i*.8
            cyl('Succulent pot', root, (x, y, base + .7), .15, .2, 'terracotta', 16, r2=.18)
            ball('Succulent', root, (x, y, base + .85), .16, 'roof sage' if i % 2 else 'leaf', (1, 1, .7))
    for x, flower in ((-1.2, 'flower pink'), (1.1, 'flower red'), (1.6, 'flower yellow')):
        potted_plant(root, (x, -W/2 - .45, 0), 1.4, flower)
    return root
