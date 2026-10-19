"""Render five cutaway interiors in the island's material/camera language.

blender --background --threads 4 --python tools/render_interiors.py -- OUTPUT
Original geometry only. Outputs PNGs and projected object hotspot coordinates.
"""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

output=Path(sys.argv[sys.argv.index('--')+1])
output.mkdir(parents=True,exist_ok=True)
swatches={'cream':'#f0e4c9','paper':'#fff5d8','wood':'#ba987b','darkwood':'#96745c','coral':'#c78578','blue':'#687f94','green':'#7f9d86','sage':'#b5c7a7','pink':'#cba2aa','glass':'#c5dedb','stone':'#b6afbc','ink':'#465765','water':'#96c8cf','soil':'#a39379','leaf':'#789768','yellow':'#dcc58d'}


def rgba(hex):
    a=[int(hex.lstrip('#')[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)


def cube(name,xyz,dims,key,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    o=bpy.context.object
    o.name=name
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mats[key])
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL');b.width=bevel;b.segments=2
        o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o


def disk(name,xyz,r,depth,key):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=xyz)
    o=bpy.context.object;o.name=name;o.data.materials.append(mats[key]);return o


def rod(name,a,b,r,key):
    a,b=Vector(a),Vector(b)
    o=disk(name,(a+b)/2,r,(a-b).length,key)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o


def text(label,xyz,size,key='ink'):
    c=bpy.data.curves.new(label,'FONT');c.body=label;c.size=size;c.extrude=.003
    o=bpy.data.objects.new(label,c);bpy.context.collection.objects.link(o)
    o.location=xyz;o.rotation_euler=(math.pi/2,0,0);c.materials.append(mats[key]);return o


def table(x,y,w=4,d=2.3,key='wood',height=1.5):
    cube('Work surface',(x,y,height),(w,d,.18),key)
    for xx in (-w/2+.2,w/2-.2):
        for yy in (-d/2+.2,d/2-.2):cube('Table leg',(x+xx,y+yy,height/2),(.15,.15,height),'darkwood')


def paper(x,y,z,w=1.4,d=1,key='paper'):
    return cube('Paper',(x,y,z),(w,d,.035),key,.01)


def frame(x,z,w=2.5,h=1.8,key='blue',y=4.25):
    cube('Exhibit frame',(x,y,z),(w+.2,.16,h+.2),'wood')
    cube('Exhibit backing',(x,y-.1,z),(w,.035,h),key,.01)
    for i in range(3):cube('Label line',(x-.25,y-.13,z-.2-i*.18),(w*.55,.025,.03),'paper',.005)


def plant(x,y,s=1,key='leaf'):
    disk('Terracotta pot',(x,y,.28*s),.4*s,.55*s,'coral')
    disk('Pot soil',(x,y,.565*s),.36*s,.02*s,'soil')
    rod('Plant stem',(x,y,.55*s),(x,y,1.5*s),.025*s,'green')
    for i in range(5):
        a=i*2.4
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=(x+.25*s*math.cos(a),y+.25*s*math.sin(a),(.8+i*.13)*s))
        o=bpy.context.object;o.name='Stylized leaf';o.scale=(.42*s,.15*s,.12*s);o.rotation_euler.z=a;o.data.materials.append(mats[key])


def shelf(x,y):
    for z in (.35,1.2,2.1,3):cube('Shelf',(x,y,z),(2.4,.65,.12),'wood')
    for xx in (-1.15,1.15):cube('Shelf upright',(x+xx,y,1.65),(.12,.65,3.3),'darkwood')
    for z in (.65,1.5,2.4):
        for i in range(6):cube('Book',(x-.9+i*.32,y-.08,z),(.19,.4,.5),['coral','blue','green','pink'][i%4])


def window(x,z=3,w=2.4,h=2):
    cube('Window frame',(x,4.19,z),(w+.22,.18,h+.22),'wood')
    cube('Sea through window',(x,4.08,z),(w,.05,h),'water')
    cube('Window mullion',(x,4.01,z),(.09,.1,h),'paper')
    cube('Window mullion',(x,4.01,z),(w,.1,.09),'paper')


all_points={}
for room in ['about','projects','experience','beyond','currently']:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    mats={}
    for key,hex in swatches.items():
        m=bpy.data.materials.new(room+'/'+key);m.use_nodes=True
        p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba(hex);p.inputs['Roughness'].default_value=.8
        mats[key]=m
    accent={'about':'green','projects':'coral','experience':'blue','beyond':'green','currently':'pink'}[room]
    cube('Diorama floor',(0,0,-.2),(14,10,.4),'wood',.12)
    for x in range(-6,7):cube('Floorboard seam',(x,0,.01),(.012,9.7,.009),'darkwood',0)
    cube('Back wall',(0,4.5,2.6),(14,.3,5.6),'cream')
    cube('Left wall',(-7,0,2.6),(.3,9,5.6),'cream')
    cube('Back skirting',(0,4.3,.25),(14,.13,.5),accent)
    cube('Wall top trim',(0,4.5,5.43),(14,.4,.22),accent)
    cube('Side top trim',(-7,0,5.43),(.4,9,.22),accent)
    for x in (-6.7,0,6.7):cube('Structural timber',(x,4.22,2.7),(.14,.13,5.2),accent)
    points={}
    if room=='projects':
        text('PROJECT STUDIO',(-5.8,4.24,4.55),.48)
        frame(-3.9,3.1,3.1,1.7,'blue');frame(.1,3.1,2.5,1.7,'sage')
        for x in (-5,-4.4,-3.8):cube('Tool peg',(x,4.02,1.8),(.08,.12,.5),'darkwood')
        shelf(5.3,3.7)
        table(-2.8,-1,4.5,2.9)
        paper(-2.8,-1,1.61,3.2,2,'blue')
        for y in (-1.4,-.9,-.4):cube('Blueprint line',(-3,y,1.65),(1.5,.025,.012),'paper',0)
        for x in (-4.2,-1.3):cube('Rolled blueprint',(x,-1,1.7),(.18,2.1,.18),'paper',.08)
        table(3.1,-1.7,3.6,2.5,'darkwood')
        paper(3.1,-1.7,1.61,2.6,1.8,'sage')
        for x in (2.7,3.2,3.7):cube('Prototype block',(x,-1.6,1.9),(.35,.5,.5),accent)
        cube('Desk stool',(-2.8,-3.4,.65),(1,1,1.3),'blue',.12)
        points={'project-01':(-2.8,-1,1.7),'project-02':(3.1,-1.7,1.8),'index':(-3.9,4.05,3.1)}
    elif room=='experience':
        text('EXPERIENCE MUSEUM',(-5.9,4.22,4.65),.40)
        frame(-3.5,3.05,3.3,2.1,'blue');frame(1.2,3.05,3.3,2.1,'sage')
        rod('Timeline rail',(-5.8,3.95,1.45),(3.5,3.95,1.45),.035,'wood')
        for x in (-5,-2,1,3):disk('Timeline node',(x,3.94,1.45),.08,.1,'coral').rotation_euler.x=math.pi/2
        for x in (-5.7,5.7):
            disk('Column',(x,1.1,2),.3,4,'paper');disk('Column base',(x,1.1,.18),.48,.35,'stone');disk('Column capital',(x,1.1,4.05),.48,.25,'paper')
        cube('Archive cabinet',(4.5,1.2,1.25),(2.2,1.3,2.5),'wood')
        for z in (.45,1.2,1.95):
            cube('Archive drawer',(4.5,.49,z),(2,.09,.6),'cream');cube('Drawer handle',(4.5,.39,z),(.4,.1,.05),'darkwood')
        disk('Exhibit plinth',(-2.2,-1.9,.75),.85,1.5,'stone')
        cube('Open archive on plinth',(-2.2,-1.9,1.55),(1.6,1,.12),'paper')
        cube('Gallery bench',(.8,-2.6,.65),(3.8,1,1.3),'blue',.08)
        points={'work':(-3.5,4,3.05),'education':(1.2,4,3.05),'index':(4.5,.4,1.5)}
    elif room=='beyond':
        # Open greenhouse: glass back panels, roof ribs, planting beds and a potting bench.
        for x in (-5,-2.5,0,2.5,5):
            cube('Greenhouse glass',(x,4.28,2.85),(2.3,.06,4.6),'glass')
            cube('Greenhouse upright',(x-1.2,4.14,2.85),(.07,.07,4.8),'green')
            rod('Glasshouse roof rib',(x,-4.4,4.4),(x,0,6.4),.06,'green')
            rod('Glasshouse roof rib',(x,0,6.4),(x,4.4,5.4),.06,'green')
        rod('Greenhouse ridge',(-6.5,0,6.4),(6.5,0,6.4),.07,'green')
        text('CURIOSITY GARDEN',(-5.8,4.0,4.55),.4)
        for x in (-3.8,.1):
            cube('Raised planting bed',(x,.4,.35),(2.9,2.8,.7),'wood')
            cube('Garden soil',(x,.4,.73),(2.65,2.55,.07),'soil')
            for dx,dy in [(-.7,-.6),(.65,-.3),(-.3,.7)]:
                plant(x+dx,.4+dy,.68)
        table(4.5,1.5,2.8,2,'wood',1.5)
        paper(4.5,1.5,1.62,1.8,1.4)
        for x in (-4.9,-1.5,2):plant(x,-3,1.15,'leaf')
        cube('Garden bench',(3.2,-2.8,.7),(3.8,1.2,1.4),'green')
        points={'community':(-3.8,.4,1.3),'curiosities':(.1,.4,1.3),'index':(4.5,1.5,1.65)}
    elif room=='currently':
        text('THE NOTICEBOARD',(-5.8,4.22,4.6),.45)
        cube('Corkboard',(0,4.12,2.85),(9,.22,2.7),'wood')
        for x,key in [(-2.2,'paper'),(1.7,'sage')]:
            cube('Pinned update',(x,3.96,2.85),(2.7,.04,1.8),key,.02)
            disk('Drawing pin',(x,3.91,3.64),.07,.06,'coral').rotation_euler.x=math.pi/2
            for z in (3.1,2.8,2.5):cube('Note line',(x-.15,3.92,z),(1.6,.02,.025),'blue',0)
        window(5.7,2.7,1.3,2.5)
        table(-3,-1.1,4,2.5)
        for i in range(4):paper(-3+i*.16,-1.1,1.6+i*.04,1.8,1.2)
        cube('Supply crate',(3,-1.8,.55),(1.8,1.6,1.1),'wood')
        rod('Paint brush',(3,-1.8,1),(3.4,-1.7,2.4),.06,'coral')
        cube('Small seat',(0,-2.8,.7),(1.1,1.1,1.4),'pink',.12)
        points={'learning':(-2.2,3.9,2.85),'making':(1.7,3.9,2.85),'index':(-3,-1.1,1.65)}
    else:
        text('WELCOME CENTER',(-5.9,4.22,4.65),.45)
        cube('Island map board',(-3.2,4.11,2.9),(4.7,.22,2.5),'blue')
        cube('Map paper',(-3.2,3.97,2.9),(4.45,.03,2.25),'paper')
        for x,z in [(-4.2,3.1),(-2.4,3.3),(-3.3,2.5)]:cube('Mini island on board',(x,3.93,z),(.65,.03,.4),'sage',.12)
        window(2.2,3,2.5,2.2)
        shelf(5.3,3.7)
        cube('Reception desk',(-1.7,-.5,.9),(5,2.3,1.8),'green',.10)
        cube('Reception desktop',(-1.7,-.5,1.85),(5.25,2.5,.16),'wood')
        paper(-1.7,-.5,1.96,2,1.5)
        cube('Brochure stand',(3.6,-.8,.8),(1.5,1.2,1.6),'wood')
        for i in range(3):cube('Resume brochure',(3.2+i*.32,-.8,1.8),(.23,.8,.8),'paper')
        cube('Contact mailbox',(4.2,-3.1,1.2),(1.4,1.15,1.8),'coral',.12)
        cube('Mailbox slot',(4.2,-3.69,1.5),(.85,.03,.07),'ink',.015)
        plant(-5.3,-2.8,1.3)
        points={'story':(-1.7,-.5,2),'resume':(3.6,-.8,1.8),'contact':(4.2,-3.1,1.7)}
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
    scene.render.resolution_x,scene.render.resolution_y=1600,1100
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
    scene.view_settings.view_transform='Standard';scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,1,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
    bpy.ops.object.light_add(type='AREA',location=(-3,-8,14))
    light=bpy.context.object;light.data.energy=1900;light.data.size=9
    light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(15,-23,19))
    camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,1.7))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=22;scene.camera=camera
    bpy.context.view_layer.update()
    all_points[room]={}
    for key,xyz in points.items():
        p=world_to_camera_view(scene,camera,Vector(xyz))
        all_points[room][key]={'x':round(p.x*100,2),'y':round((1-p.y)*100,2)}
    scene.render.filepath=str(output/f'{room}.png')
    bpy.ops.render.render(write_still=True)
(output/'interior-layout.json').write_text(json.dumps(all_points,indent=2)+'\n')
