"""Build the complete soft-color island from the selected CC0 models.

blender --background --threads 4 --python tools/render_island.py -- SOURCES OUTPUT
OUTPUT receives island.png and map-layout.json. No live 3D is required on the site.
"""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

source, output = map(Path, sys.argv[sys.argv.index('--') + 1:])
output.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


def color(hex):
    values = [int(hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(v/12.92 if v < .04045 else ((v+.055)/1.055)**2.4 for v in values)+(1,)


def mat(name, hex):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = color(hex)
    p.inputs['Roughness'].default_value = .8
    return m


swatches = {
    'wall': '#f0d6a3', 'roof': '#cc7d73', 'trim': '#576c88',
    'glass': '#d6e8d8', 'stone': '#b2acbd', 'wood': '#b99170',
    'grass': '#afc58a', 'sand': '#f2dfb4', 'earth': '#a39bb1',
    'water': '#91cbd0', 'edge': '#74aebd', 'foam': '#d9eeea',
    'green': '#789b83', 'pink': '#d8a4ac', 'cream': '#fff4d8',
}
materials = {name: mat(name, hex) for name, hex in swatches.items()}


def cube(name, loc, dims, material, bevel=.05):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(materials[material])
    if bevel:
        b = o.modifiers.new('Soft edges', 'BEVEL')
        b.width, b.segments = bevel, 2
        o.modifiers.new('Normals', 'WEIGHTED_NORMAL')
    return o


def disk(name, loc, radius, depth, material, scale=(1,1,1), vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name, o.scale = name, scale
    o.data.materials.append(materials[material])
    return o


def line(name, points, material, width=.04):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions, data.bevel_depth, data.bevel_resolution = '3D', width, 2
    p = data.splines.new('POLY')
    p.points.add(len(points)-1)
    for target, xyz in zip(p.points, points):
        target.co = (*xyz,1)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(materials[material])
    if name == 'Walking path':
        # Flatten the bevel vertically into a path, rather than a raised tube.
        obj.scale.z = .05
        obj.location.z = 1.035 * .95
        data.use_fill_caps = True
    return obj


def model(name, loc, scale=1, rot=0, nature=False, orange=False):
    pack = 'Stylized Nature MegaKit[Standard]' if nature else 'Medieval Village MegaKit[Standard]'
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(source/'assests'/pack/'glTF'/f'{name}.gltf'))
    objs = set(bpy.context.scene.objects)-before
    parent = bpy.data.objects.new(f'Quaternius / {name}', None)
    bpy.context.collection.objects.link(parent)
    for o in objs:
        if o.parent not in objs:
            o.parent = parent
        if o.type != 'MESH':
            continue
        for i, material in enumerate(o.data.materials):
            n = material.name.lower()
            if nature and ('leaves' in n or 'flowers' in n):
                m = material.copy()
                p = m.node_tree.nodes.get('Principled BSDF')
                for link in list(p.inputs['Base Color'].links):
                    m.node_tree.links.remove(link)
                hex = '#d8a4ac' if 'flowers' in n else '#d6a36a' if orange else '#769f78'
                p.inputs['Base Color'].default_value = color(hex)
                p.inputs['Emission Color'].default_value = color(hex)
                p.inputs['Emission Strength'].default_value = .22
                o.data.materials[i] = m
            else:
                key = 'wood' if nature else 'wall' if 'plaster' in n else 'roof' if 'roundtiles' in n else 'glass' if 'glass' in n else 'stone' if 'brick' in n or 'rock' in n else 'trim'
                if nature and 'rock' in n:
                    key = 'stone'
                if name in ('Floor_WoodLight','Prop_Crate','Balcony_Simple_Straight'):
                    key = 'wood'
                o.data.materials[i] = materials[key]
    parent.location, parent.scale = loc, (scale,)*3
    parent.rotation_euler.z = rot
    return parent


def house(name, x, y, s=1, tint=None):
    z = 1.02
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    before = set(bpy.context.scene.objects)
    for xx in (-1,1):
        model('Wall_Plaster_Door_Round' if xx == 1 else 'Wall_Plaster_Window_Wide_Round', (xx,-3,0))
        model('Wall_Plaster_Straight', (xx,3,0), rot=math.pi)
    model('Door_1_Round', (.49,-3.06,0))
    model('Window_Wide_Round1', (-1,-3.1,0))
    for yy in (-2,0,2):
        for side in (-1,1):
            model('Wall_Plaster_Window_Wide_Round', (side*2,yy,0), rot=-side*math.pi/2)
            model('Window_Wide_Round1', (side*2.08,yy,0), rot=-side*math.pi/2)
    model('Roof_RoundTiles_4x6', (0,0,3.12))
    for yy in (-3,3):
        mesh = bpy.data.meshes.new('Gable')
        mesh.from_pydata([(-2.05,yy,3.12),(2.05,yy,3.12),(0,yy,6.32)],[],[(0,1,2)])
        o = bpy.data.objects.new('Original / gable',mesh)
        bpy.context.collection.objects.link(o)
        o.data.materials.append(materials['wall'])
    for obj in set(bpy.context.scene.objects)-before:
        if obj.parent is None:
            obj.parent = root
    root.location, root.scale = (x,y,z), (s,)*3
    if tint:
        for obj in set(bpy.context.scene.objects)-before:
            if obj.type == 'MESH':
                for i,m in enumerate(obj.data.materials):
                    if m == materials['roof']:
                        obj.data.materials[i] = materials[tint]
    return root


# Soft, low-sided floating sea, with an irregular island contour inside it.
disk('Floating sea', (0,0,-1), 19,.36,'edge',(1,.82,1),96)
disk('Sea surface', (0,0,-.79),19,.08,'water',(1,.82,1),96)
outline = []
for i in range(48):
    a = i*math.tau/48
    r = 1+.045*math.sin(3*a)+.03*math.cos(5*a)
    outline.append((12.6*r*math.cos(a),9.8*r*math.sin(a)))


def island_layer(name,z,depth,scale,material):
    verts=[(x*scale,y*scale,z+zz) for zz in (-depth/2,depth/2) for x,y in outline]
    n=len(outline)
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(materials[material])


island_layer('Island underside',-.04,1.65,.98,'earth')
island_layer('Sandy coastline',.82,.15,1.015,'sand')
island_layer('Garden meadow',.94,.12,.94,'grass')

# Five distinct destinations around the central plaza.
house('Project Studio',-6.7,-2.7,.71)
house('Experience Museum',-4.3,4,.70,tint='trim')
# Museum entry columns distinguish its silhouette from the studio.
for x in (-5.6,-4.7,-3.8,-2.9):
    disk('Museum column',(x,1.7,2.05),.13,2,'cream',vertices=16)
cube('Museum portico',(-4.3,1.7,3.15),(3.5,.7,.22),'sand')

disk('Welcome plaza',(0,-.9,1.03),2.7,.08,'sand',(1,.8,1))
disk('Welcome fountain',(0,-.7,1.18),.80,.25,'stone')
disk('Fountain water',(0,-.7,1.32),.68,.04,'water')
disk('Fountain center',(0,-.7,1.6),.16,.55,'cream',vertices=16)
house('Welcome kiosk',.1,1,.36,tint='green')

# Original greenhouse with simple opaque glass panels: readable at map scale.
gx,gy=6.2,-2
cube('Greenhouse base',(gx,gy,1.13),(4.5,3.2,.25),'stone')
cube('Greenhouse interior',(gx,gy,2.35),(4.2,2.9,2.3),'glass',.02)
for xx in (-2.1,-1.05,0,1.05,2.1):
    for yy in (-1.48,1.48):
        cube('Greenhouse frame',(gx+xx,gy+yy,2.35),(.07,.07,2.5),'green',0)
    line('Greenhouse roof rib',[(gx+xx,gy-1.48,3.6),(gx+xx,gy,4.65),(gx+xx,gy+1.48,3.6)],'green',.055)
for yy in (-1.48,0,1.48):
    line('Greenhouse roof rail',[(gx-2.15,gy+yy,4.65 if yy==0 else 3.6),(gx+2.15,gy+yy,4.65 if yy==0 else 3.6)],'green',.055)
for xx in (-1.4,0,1.4):
    disk('Garden planter',(gx+xx,gy-2.1,1.25),.42,.5,'roof',vertices=16)
    model('Bush_Common_Flowers',(gx+xx,gy-2.1,1.45),.45,nature=True)

house('Currently kiosk',5.2,4.5,.38,tint='pink')
for xx in (4.2,6.2):
    cube('Noticeboard post',(xx,2.65,1.9),(.1,.13,1.8),'wood')
cube('Noticeboard',(5.2,2.6,2.4),(2.3,.18,1.3),'wood')
for xx,zz in [(4.55,2.45),(5.2,2.6),(5.82,2.35)]:
    cube('Paper on noticeboard',(xx,2.49,zz),(.45,.03,.65),'cream',.01)

# Paths explain relationships without covering the whole meadow.
for points in [[(-1.5,-1,1.035),(-4,-2,1.035),(-5.8,-4.9,1.035)],[(0,-.5,1.035),(-2,1,1.035),(-4,1.6,1.035)],[(1,-1,1.035),(3,-3,1.035),(5.7,-4.4,1.035)],[(1.2,0,1.035),(3,1,1.035),(5,2,1.035)],[(0,-2,1.035),(0,-5,1.035),(1,-8,1.035)]]:
    line('Walking path',points,'sand',.40)

# Pier, boat, a tiny bridge, and observation wheel preserve the amusement layer.
for yy in (-9,-11,-13):
    model('Floor_WoodLight',(1,yy,.43))
for xx in (.08,1.92):
    for yy in (-8.6,-10.6,-13.7):
        disk('Pier post',(xx,yy,-.1),.09,1.8,'wood',vertices=12)
        disk('Pier cap',(xx,yy,.85),.13,.12,'cream',vertices=12)
model('Prop_Crate',(2.9,-8,.95),.5)
for i in range(7):
    cube('Short bridge plank',(11+i*.42,-1.7,1.05+.24*math.sin(i*math.pi/6)),(.46,1.25,.15),'wood')
disk('Near-shore rock',(14,-1.7,-.08),1.2,1.5,'stone',(1,.8,1),7)

bx,by=4.6,-12.2
disk('Boat hull',(bx,by,-.42),.65,.4,'roof',(.75,1.65,1),8)
disk('Boat mast',(bx,by,.65),.04,2,'wood',vertices=12)
mesh=bpy.data.meshes.new('Boat sail')
mesh.from_pydata([(bx,by,1.7),(bx,by,.1),(bx,by+1.1,.1)],[],[(0,1,2)])
o=bpy.data.objects.new('Sail',mesh)
bpy.context.collection.objects.link(o)
o.data.materials.append(materials['cream'])

wx,wy=-.3,6.4
line('Observation wheel rim',[(wx+1.55*math.cos(i*math.tau/64),wy,3.4+1.55*math.sin(i*math.tau/64)) for i in range(65)],'cream',.07)
for i in range(8):
    a=i*math.tau/8
    x,z=wx+1.55*math.cos(a),3.4+1.55*math.sin(a)
    line('Wheel spoke',[(wx,wy,3.4),(x,wy,z)],'cream',.035)
    cube('Wheel cabin',(x,wy,z-.22),(.44,.5,.4),'roof' if i%2 else 'trim')
line('Wheel frame',[(wx-1,wy,1.05),(wx,wy,3.4),(wx+1,wy,1.05)],'wood',.09)

for name,x,y,s,orange in [('CommonTree_1',-8.8,3.2,.65,False),('CommonTree_3',8.7,4,.5,True),('Pine_5',-9,-.2,.42,False),('CommonTree_1',3.6,7.1,.5,False)]:
    model(name,(x,y,1),s,nature=True,orange=orange)
for x,y,s in [(-10,-3,.6),(-6,-7.5,.5),(9,-6,.6),(10,2,.45),(-8,6,.6)]:
    model('Rock_Medium_1',(x,y,.6),s,nature=True)
for x,y in [(-4,-5.3),(-7,-5.7),(4,-5.5),(8,-.3),(6.8,2.2)]:
    model('Bush_Common_Flowers',(x,y,1.02),.45,nature=True)
for x,y in [(-14,-4),(-12,-8),(-8,-11),(-3,-13),(2,-15),(8,-11),(12,-7),(15,1),(13,7),(-11,9)]:
    line('Sea ripple',[(x+i*.14,y+.1*math.sin(i*math.pi/12),-.735) for i in range(13)],'foam',.035)

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=40
scene.cycles.use_denoising=False
scene.cycles.max_bounces=5
scene.cycles.transparent_max_bounces=24
scene.render.resolution_x,scene.render.resolution_y=1800,1400
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
scene.view_settings.view_transform='Standard'
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,1,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
bpy.ops.object.light_add(type='AREA',location=(-12,-15,25))
light=bpy.context.object
light.data.energy,light.data.size=3000,12
light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(20,-30,31))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,-1,1))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type,camera.data.ortho_scale='ORTHO',43
scene.camera=camera
bpy.context.view_layer.update()
anchors={'about':(0,-1,1.5),'projects':(-6.7,-4.8,1.2),'experience':(-4.3,1.5,3.3),'beyond':(6.2,-4,1.3),'currently':(5.2,2.6,2.5)}
layout={}
for key,point in anchors.items():
    p=world_to_camera_view(scene,camera,Vector(point))
    layout[key]={'x':round(p.x*100,2),'y':round((1-p.y)*100,2)}
(output/'map-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
scene.render.filepath=str(output/'island.png')
bpy.ops.wm.save_as_mainfile(filepath=str(output/'island.blend'))
bpy.ops.render.render(write_still=True)
