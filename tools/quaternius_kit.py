"""Shared Blender helpers for the storybook island and interiors.

Imports the owner's Quaternius glTF models once, places linked copies, and
restyles their original textures instead of repainting them flat. Lighting
lives in LIGHTS so a later day/dusk switch only needs a second render.
"""
import math
from pathlib import Path
import bpy
from mathutils import Vector

PACKS = {'M': 'Medieval Village MegaKit[Standard]', 'N': 'Stylized Nature MegaKit[Standard]'}
SOURCE = None
_templates = {}

LIGHTS = {
    # Approved direction A: warm afternoon daylight.
    'day': dict(sun=(1, .9, .78), energy=4.2, rot=(math.radians(48), 0, math.radians(-38)), angle=3,
                sky=(.62, .74, .92), sky_energy=.9, look='AgX - Punchy', glass_glow=0),
    # Direction C, kept for the later day/night feature.
    'dusk': dict(sun=(1, .66, .42), energy=3.4, rot=(math.radians(74), 0, math.radians(-62)), angle=2,
                 sky=(.36, .38, .62), sky_energy=.75, look='AgX - Medium High Contrast', glass_glow=6),
}
SATURATION = .88
LEAFY = ('Leaves', 'Leaf', 'Grass', 'Flowers', 'Vine')


def set_source(path):
    global SOURCE
    SOURCE = Path(path) / 'assests'


def srgb(h):
    v = [int(h.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(c/12.92 if c < .04045 else ((c+.055)/1.055)**2.4 for c in v) + (1,)


def template(kind, name):
    """Import a model once into a hidden collection reused by every placement."""
    key = (kind, name)
    if key not in _templates:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(SOURCE/PACKS[kind]/'glTF'/f'{name}.gltf'))
        coll = bpy.data.collections.new(f'Template / {name}')
        for o in [o for o in bpy.data.objects if o not in before]:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            coll.objects.link(o)
        _templates[key] = coll
    return _templates[key]


def place(kind, name, loc=(0, 0, 0), rot=0, scale=1, parent=None):
    inst = bpy.data.objects.new(name, None)
    inst.instance_type = 'COLLECTION'
    inst.instance_collection = template(kind, name)
    bpy.context.scene.collection.objects.link(inst)
    inst.location, inst.rotation_euler.z = loc, rot
    inst.scale = (scale,)*3 if isinstance(scale, (int, float)) else scale
    if parent:
        inst.parent = parent
    return inst


def empty(name, loc=(0, 0, 0), rot=0, scale=1):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location, e.rotation_euler.z, e.scale = loc, rot, (scale,)*3
    return e


def pack_material(fragment):
    """An original pack material (e.g. 'WoodTrim', 'Plaster') for original geometry."""
    return next(m for m in bpy.data.materials if fragment in m.name and m.use_nodes)


def flat(name, base, rough=.85, vary=None, scale=3.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Roughness'].default_value = rough
    if vary:
        tex = nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value, tex.inputs['Detail'].default_value = scale, 3
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[1].position = .35, .7
        ramp.color_ramp.elements[0].color, ramp.color_ramp.elements[1].color = srgb(base), srgb(vary)
        nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    else:
        p.inputs['Base Color'].default_value = srgb(base)
    return m


def tinted(fragment, name, hue=.5, saturation=1, value=1):
    """Copy an original textured material and shift its hue, keeping all texture detail."""
    m = pack_material(fragment).copy()
    m.name = name
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    src = p.inputs['Base Color'].links[0].from_socket
    hsv = nt.nodes.new('ShaderNodeHueSaturation')
    hsv.inputs['Hue'].default_value, hsv.inputs['Saturation'].default_value, hsv.inputs['Value'].default_value = hue, saturation, value
    nt.links.new(src, hsv.inputs['Color'])
    nt.links.new(hsv.outputs['Color'], p.inputs['Base Color'])
    m['styled'] = 1
    return m


def retint(root, fragment, material):
    """After make_real(): swap one original material for a tinted copy under root."""
    for o in root.children_recursive:
        if o.type == 'MESH':
            for slot in o.material_slots:
                if slot.material and fragment in slot.material.name:
                    slot.link = 'OBJECT'
                    slot.material = material


def restyle(light):
    """Gently desaturate the painted textures; give foliage translucency."""
    for m in bpy.data.materials:
        if not m.use_nodes or m.get('styled'):
            continue
        nt = m.node_tree
        p = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not p:
            continue
        m['styled'] = 1
        leafy = any(k in m.name for k in LEAFY)
        if p.inputs['Base Color'].links:
            src = p.inputs['Base Color'].links[0].from_socket
            hsv = nt.nodes.new('ShaderNodeHueSaturation')
            hsv.inputs['Saturation'].default_value = SATURATION * (1.08 if leafy else 1)
            hsv.inputs['Value'].default_value = 1.6 if leafy else 1.08 if 'Plaster' in m.name else 1
            nt.links.new(src, hsv.inputs['Color'])
            nt.links.new(hsv.outputs['Color'], p.inputs['Base Color'])
            if leafy:
                out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
                bsdf = out.inputs['Surface'].links[0].from_socket
                tr = nt.nodes.new('ShaderNodeBsdfTranslucent')
                nt.links.new(hsv.outputs['Color'], tr.inputs['Color'])
                mix = nt.nodes.new('ShaderNodeMixShader')
                mix.inputs['Fac'].default_value = .35
                nt.links.new(bsdf, mix.inputs[1])
                nt.links.new(tr.outputs[0], mix.inputs[2])
                surface = mix.outputs[0]
                if p.inputs['Alpha'].links:
                    cut = nt.nodes.new('ShaderNodeMixShader')
                    nt.links.new(p.inputs['Alpha'].links[0].from_socket, cut.inputs['Fac'])
                    nt.links.new(nt.nodes.new('ShaderNodeBsdfTransparent').outputs[0], cut.inputs[1])
                    nt.links.new(mix.outputs[0], cut.inputs[2])
                    surface = cut.outputs[0]
                nt.links.new(surface, out.inputs['Surface'])
        if 'WindowGlass' in m.name and LIGHTS[light]['glass_glow']:
            p.inputs['Emission Color'].default_value = (1, .62, .3, 1)
            p.inputs['Emission Strength'].default_value = LIGHTS[light]['glass_glow']


def soften_foliage():
    """Spherical normals on leaf cards so crowns read as soft volumes, not black clumps."""
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.data.get('soft'):
            continue
        me = o.data
        leaves = {i for i, m in enumerate(me.materials) if m and ('Leaves' in m.name or 'Leaf' in m.name)}
        verts = {v for p in me.polygons if p.material_index in leaves for v in p.vertices}
        if not verts:
            continue
        me['soft'] = 1
        c = sum((me.vertices[i].co for i in verts), Vector()) / len(verts)
        c.z -= .15 * (max(me.vertices[i].co.z for i in verts) - c.z)
        me.normals_split_custom_set_from_vertices(
            [(v.co - c).normalized() if v.index in verts else v.normal.copy() for v in me.vertices])


def light_scene(light, resolution, samples):
    s = LIGHTS[light]
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples, sc.cycles.use_denoising = samples, True
    sc.cycles.max_bounces, sc.cycles.transparent_max_bounces = 6, 32
    sc.render.resolution_x, sc.render.resolution_y = resolution
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format, sc.render.image_settings.color_mode = 'PNG', 'RGBA'
    sc.view_settings.view_transform, sc.view_settings.look = 'AgX', s['look']
    world = bpy.data.worlds.new('Sky')
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value, bg.inputs[1].default_value = s['sky'] + (1,), s['sky_energy']
    bpy.ops.object.light_add(type='SUN')
    sun = bpy.context.object
    sun.rotation_euler, sun.data.energy, sun.data.color = s['rot'], s['energy'], s['sun']
    sun.data.angle = math.radians(s['angle'])
    return sun


def make_real():
    """Turn linked placements into real objects so geometry can be exported per building."""
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.instance_type == 'COLLECTION':
            o.select_set(True)
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)
