"""Render a local art-direction sample from the owner's selected CC0 models.

blender --background --threads 4 --python tools/render_art_sample.py -- SOURCES OUTPUT_DIR
The browser consumes renders, not Blender or live 3D. No downloaded code is executed.
"""
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

source, output = [Path(p) for p in sys.argv[sys.argv.index("--") + 1:]]
output.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


def rgb(value):
    value = value.lstrip("#")
    c = [int(value[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(v/12.92 if v < .04045 else ((v+.055)/1.055)**2.4 for v in c) + (1,)


def material(name, color, roughness=.7):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = rgb(color)
    p.inputs["Roughness"].default_value = roughness
    m.diffuse_color = rgb(color)
    return m


palette = {
    "wall": material("Sample / sunny walls", "#ffca43"),
    "roof": material("Sample / coral tiles", "#f24c55"),
    "trim": material("Sample / blue timber", "#324eb8"),
    "glass": material("Sample / warm windows", "#fff1af", .3),
    "stone": material("Sample / lilac stone", "#b3a5d6"),
    "wood": material("Sample / golden pier", "#e9a45b"),
    "grass": material("Sample / lime meadow", "#a9d84d"),
    "sand": material("Sample / warm sand", "#ffe6a3"),
    "earth": material("Sample / lavender island edge", "#8d70b4"),
    "water": material("Sample / turquoise sea", "#22bfd4", .34),
    "wateredge": material("Sample / cobalt sea edge", "#297ac9"),
    "foam": material("Sample / foam", "#c9fff0"),
    "pink": material("Sample / pink accents", "#ff80be"),
}


def cube(name, loc, scale, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new("Soft toy edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return o


def cylinder(name, loc, radius, depth, mat, scale=(1,1,1), vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(mat)
    return o


def imported(pack, model, loc, scale=1, rotation=0, nature_tint=None):
    path = source / "assests" / pack / "glTF" / f"{model}.gltf"
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objs = set(bpy.context.scene.objects) - before
    parent = bpy.data.objects.new(f"Asset / {model}", None)
    bpy.context.collection.objects.link(parent)
    for o in objs:
        if o.parent not in objs:
            o.parent = parent
        if o.type != "MESH":
            continue
        for i, m in enumerate(o.data.materials):
            name = m.name.lower()
            if pack.startswith("Medieval"):
                key = "wall" if "plaster" in name else "roof" if "roundtiles" in name else "glass" if "glass" in name else "stone" if "brick" in name or "rock" in name else "trim"
                if model in {"Floor_WoodLight", "Prop_Crate", "Prop_WoodenFence_Single", "Balcony_Simple_Straight"}:
                    key = "wood"
                o.data.materials[i] = palette[key]
            elif "rock" in name:
                o.data.materials[i] = palette["stone"]
            elif "bark" in name:
                o.data.materials[i] = palette["wood"]
            elif "leaves" in name or "flowers" in name:
                # Keep the authored alpha mask, but use a bright flat color.
                # The free pack lacks the SOURCE edition's foliage shader.
                clone = m.copy()
                nodes = clone.node_tree.nodes
                p = nodes.get("Principled BSDF")
                socket = p.inputs["Base Color"]
                for link in list(socket.links):
                    clone.node_tree.links.remove(link)
                color = "#ff82bd" if "flowers" in name else "#ffad38" if nature_tint else "#72bf41" if "pine" not in name else "#3c9e79"
                socket.default_value = rgb(color)
                p.inputs["Roughness"].default_value = .85
                o.data.materials[i] = clone
    parent.location = loc
    parent.scale = (scale,)*3
    parent.rotation_euler.z = rotation
    return parent


def curve(name, points, mat, thickness=.035):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = thickness
    data.bevel_resolution = 2
    poly = data.splines.new("POLY")
    poly.points.add(len(points)-1)
    for p, co in zip(poly.points, points):
        p.co = (*co,1)
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


# An intentionally small slice of the future world, not a replacement full map.
cylinder("Floating patch of sea", (0,-1,-1.1), 13.6, .5, palette["wateredge"], (1,.86,1), 96)
cylinder("Sea surface", (0,-1,-.83), 13.6, .07, palette["water"], (1,.86,1), 96)
cylinder("Island soil", (0,.5,-.04), 8.4, 1.45, palette["earth"], (1,.73,1), 20)
cylinder("Sandy shore", (0,.5,.72), 8.5, .18, palette["sand"], (1,.73,1), 40)
cylinder("Meadow", (0,.8,.85), 7.85, .14, palette["grass"], (1,.72,1), 40)

medieval = "Medieval Village MegaKit[Standard]"
nature = "Stylized Nature MegaKit[Standard]"
bx, by, z = -1.4, 1.6, .93
# Two 2m modules across, three along each side. The glTF kit is in meters.
for x in (-1,1):
    imported(medieval, "Wall_Plaster_Door_Round" if x == 1 else "Wall_Plaster_Window_Wide_Round", (bx+x,by-3,z))
    imported(medieval, "Wall_Plaster_Straight", (bx+x,by+3,z), rotation=math.pi)
    if x == -1:
        imported(medieval, "Window_Wide_Round1", (bx+x,by-3.1,z))
imported(medieval, "Door_1_Round", (bx+.49,by-3.05,z))
for y in (-2,0,2):
    for side in (-1,1):
        imported(medieval, "Wall_Plaster_Window_Wide_Round", (bx+side*2,by+y,z), rotation=-side*math.pi/2)
        imported(medieval, "Window_Wide_Round1", (bx+side*2.06,by+y,z), rotation=-side*math.pi/2)
roofz = z+3.12
imported(medieval, "Roof_RoundTiles_4x6", (bx,by,roofz))
for y in (-3,3):
    mesh = bpy.data.meshes.new("Gable face")
    mesh.from_pydata([(bx-2.05,by+y,roofz), (bx+2.05,by+y,roofz), (bx,by+y,roofz+3.2)], [], [(0,1,2)])
    obj = bpy.data.objects.new("Original / gable infill", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(palette["wall"])
imported(medieval, "Prop_Chimney", (bx-1.25,by+1.5,roofz+1.4), .65)
cube("Studio front step", (bx+.9,by-3.35,z+.03), (1.5,.65,.18), palette["stone"], .07)

# Pier assembled from the supplied floor module, with original support posts.
for y in (-4.1,-6.1,-8.1):
    imported(medieval, "Floor_WoodLight", (2.4,y,.42))
for x in (1.45,3.35):
    for y in (-4.5,-6.5,-8.8):
        cylinder("Original / pier post", (x,y,-.1), .105, 1.6, palette["wood"], vertices=12)
        cylinder("Original / pier cap", (x,y,.76), .14, .12, palette["wall"], vertices=12)
imported(medieval, "Prop_Crate", (4,-4.3,.9), .6, rotation=.2)
imported(medieval, "Prop_Crate", (4.6,-3.7,.9), .45, rotation=-.2)
imported(medieval, "Balcony_Simple_Straight", (2.4,-6.1,.43), rotation=math.pi/2)

# Vegetation remains sparse enough to preserve architecture and paths.
imported(nature, "CommonTree_1", (-5.1,3.2,.95), .83)
imported(nature, "CommonTree_3", (3.7,3.4,.95), .66, nature_tint=(1.65,.68,.35))
imported(nature, "Pine_5", (-5.8,-.1,.95), .51)
imported(nature, "Bush_Common_Flowers", (4.7,.5,.95), .8)
imported(nature, "Bush_Common_Flowers", (-3.7,-2,.95), .65)
imported(nature, "Flower_3_Group", (4.8,-1.3,.95), .45)
for i, (x,y,s) in enumerate([(-6.9,-2.5,.65),(6.8,.1,.7),(5.3,-4,.6),(-7,1.2,.45)]):
    imported(nature, "Rock_Medium_1" if i%2 else "Rock_Medium_2", (x,y,.55), s, rotation=i)

# Short stepping-stone trail connects the studio and pier.
for i,(x,y) in enumerate([(.5,-2.3),(.9,-2.9),(1.3,-3.5)]):
    o=cylinder("Original / stepping stone", (x,y,.99), .42,.09,palette["sand"],(1,.7,1),8)
    o.rotation_euler.z=i*.4

# Original toy sailboat, kept separate from CC0 kit provenance.
boatroot = bpy.data.objects.new("Original / toy sailboat", None)
bpy.context.collection.objects.link(boatroot)
hull = cylinder("Original / boat hull", (5.7,-7.2,-.45), .65,.38,palette["roof"],(.75,1.8,1),8)
cube("Original / boat seat", (5.7,-7.2,-.21),(.85,.19,.12),palette["wall"],.03)
cylinder("Original / mast", (5.7,-7.3,.72), .045, 2.05, palette["wood"], vertices=12)
mesh=bpy.data.meshes.new("Original / sail")
mesh.from_pydata([(5.7,-7.3,1.73),(5.7,-7.3,.08),(5.7,-6.05,.08)], [], [(0,1,2)])
o=bpy.data.objects.new("Original / triangular sail",mesh)
bpy.context.collection.objects.link(o)
o.data.materials.append(palette["sand"])

# A small violet sign and flag suggest a personal studio rather than a historic village.
cylinder("Original / sign post", (3.3,-1.8,1.65),.06,1.5,palette["trim"],vertices=12)
cube("Original / studio sign", (3.3,-1.85,2.22),(1.65,.14,.65),palette["trim"],.08)
for x in (2.88,3.3,3.72):
    cylinder("Original / sign dot",(x,-1.94,2.23),.08,.03,palette["sand"],vertices=16).rotation_euler.x=math.pi/2

for x,y,length in [(-9,-3,1.5),(-7,-6,1.3),(-2,-8.4,1.5),(0,-10.5,1.8),(8,-6,1.1),(10,-1,1.2),(8.8,3.5,1.4),(-9,3,1.1),(-4,7,1.2)]:
    curve("Original / ripple", [(x+t*length,y+math.sin(t*math.pi)*.12,-.76) for t in [i/12 for i in range(13)]],palette["foam"],.035)

# CPU Cycles is repeatable in the cloud and handles alpha leaf cards reliably.
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=48
# Cloud Blender build has no OpenImageDenoise; sample directly instead.
scene.cycles.use_denoising=False
scene.cycles.max_bounces=5
scene.render.resolution_x=1600
scene.render.resolution_y=1200
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGBA"
scene.render.film_transparent=True
scene.view_settings.view_transform="Standard"
scene.world.color=(.5,.5,.5)
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(.65,.78,1,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=.7

bpy.ops.object.light_add(type="AREA", location=(-8,-10,20))
light=bpy.context.object
light.name="Large soft key"
light.data.energy=2300
light.data.shape="DISK"
light.data.size=9
light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(location=(19,-26,22))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,-.7,1))-camera.location).to_track_quat("-Z","Y").to_euler()
camera.data.type="ORTHO"
camera.data.ortho_scale=33
scene.camera=camera

scene.render.filepath=str(output / "coral-coast.png")
bpy.ops.wm.save_as_mainfile(filepath=str(output / "coastal-sample.blend"))
bpy.ops.render.render(write_still=True)

# Same geometry, light and camera; only five swatches change for a fair comparison.
for key,color in {"wall":"#e5c4ff", "roof":"#7143dc", "trim":"#164795", "water":"#218fe0", "grass":"#b7e54e"}.items():
    m=palette[key]
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=rgb(color)
    m.diffuse_color=rgb(color)
scene.render.filepath=str(output / "violet-coast.png")
bpy.ops.render.render(write_still=True)
