"""Export precise building silhouettes and lit-window geometry from the saved island.

blender --background /tmp/soft-island/island.blend --python tools/export_building_layers.py -- OUTPUT
No new render is needed; the SVG coordinates use the original camera and resolution.
"""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

output=Path(sys.argv[sys.argv.index('--')+1])
scene=bpy.context.scene
camera=scene.camera
width,height=1800,1400
definitions={
    'about':('Welcome kiosk',(.1,1,1.02+6.32*.36)),
    'projects':('Project Studio',(-6.7,-2.7,1.02+6.32*.71)),
    'experience':('Experience Museum',(-4.3,4,1.02+6.32*.70)),
    'beyond':(None,(6.2,-2,4.65)),
    'currently':('Currently kiosk',(5.2,4.5,1.02+6.32*.38)),
}


def project(point):
    p=world_to_camera_view(scene,camera,point)
    return (round(p.x*width,2),round((1-p.y)*height,2))


def hull(points):
    points=sorted(set(points))
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[]
    for p in points:
        while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0: lower.pop()
        lower.append(p)
    upper=[]
    for p in reversed(points):
        while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0: upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]


data={}
depsgraph=bpy.context.evaluated_depsgraph_get()
view_direction=(camera.matrix_world.to_quaternion()@Vector((0,0,1))).normalized()
for key,(root_name,roof) in definitions.items():
    objects=list(bpy.data.objects[root_name].children_recursive) if root_name else [o for o in scene.objects if o.name.startswith('Greenhouse')]
    objects=[o for o in objects if o.type=='MESH']
    points=[project(o.matrix_world@v.co) for o in objects for v in o.data.vertices]
    outline=hull(points)
    minx,miny=min(p[0] for p in outline),min(p[1] for p in outline)
    maxx,maxy=max(p[0] for p in outline),max(p[1] for p in outline)
    polygons=[]
    for o in objects:
        for poly in o.data.polygons:
            material=o.material_slots[poly.material_index].material
            if material and material.name.startswith('glass'):
                normal=o.matrix_world.to_3x3()@poly.normal
                if normal.dot(camera.location-(o.matrix_world@poly.center))<0: continue
                # Reject windows hidden behind roofs/walls. Facing the camera
                # alone is insufficient for a projected light overlay.
                center=o.matrix_world@poly.center
                hit=scene.ray_cast(depsgraph,center+view_direction*100,-view_direction,distance=100.01)
                if not hit[0] or hit[4].original!=o: continue
                coords=[project(o.matrix_world@o.data.vertices[i].co) for i in poly.vertices]
                polygons.append('M'+' L'.join(f'{x},{y}' for x,y in coords)+' Z')
    # The greenhouse glass is intentionally a warm, low-opacity interior light.
    data[key]={
        'left':round(minx/width*100,3),'top':round(miny/height*100,3),
        'width':round((maxx-minx)/width*100,3),'height':round((maxy-miny)/height*100,3),
        'clip':'polygon('+','.join(f'{(x-minx)/(maxx-minx)*100:.2f}% {(y-miny)/(maxy-miny)*100:.2f}%' for x,y in outline)+')',
        'roof':project(Vector(roof)),
        'lights':' '.join(polygons),
    }
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(data,indent=2)+'\n')
print('Exported silhouettes, roof flags and window geometry for',len(data),'buildings')
