"""Export the saved island as a small web glTF for the draggable 3D view.

python3 tools/export_island_glb.py ISLAND.blend OUTPUT.glb [texture_px]
  (bpy module; ISLAND.blend from `tools/render_island.py SOURCES OUT day 0`)
The browser draws its own sea, foam, sky and light (src/island3d.js), so those are left out.
Cycles-only shader nodes are folded into glTF-friendly values; the hue/saturation/value tweaks
that restyle() and tinted() add are kept as material extras and reapplied in the browser.
"""
import sys
from pathlib import Path
import bpy

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
bpy.ops.wm.open_mainfile(filepath=args[0])
output = Path(args[1])
texture_px = int(args[2]) if len(args) > 2 else 512

for o in [o for o in bpy.data.objects if o.name in ('Sea', 'Foam') or o.type in ('CAMERA', 'LIGHT')]:
    bpy.data.objects.remove(o)

# Curves (paths, greenhouse ribs, the wheel) become meshes so the exporter keeps them.
bpy.ops.object.select_all(action='DESELECT')
curves = [o for o in bpy.context.scene.objects if o.type == 'CURVE']
for o in curves:
    o.select_set(True)
if curves:
    bpy.context.view_layer.objects.active = curves[0]
    bpy.ops.object.convert(target='MESH')


def node_color(node):
    """The colour a flat() ramp or plain input settles on, as linear RGBA."""
    if node.type == 'VALTORGB':
        a, b = node.color_ramp.elements[0].color, node.color_ramp.elements[-1].color
        return [(a[i] + b[i]) / 2 for i in range(3)] + [1]
    return None


for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    nt = m.node_tree
    p = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if not p or not out:
        continue
    base = p.inputs['Base Color']
    if base.links:
        src = base.links[0].from_node
        if src.type == 'HUE_SAT':
            m['hsv'] = [src.inputs['Hue'].default_value, src.inputs['Saturation'].default_value,
                        src.inputs['Value'].default_value]
            upstream = src.inputs['Color'].links[0].from_socket
            nt.links.new(upstream, base)
            src = base.links[0].from_node
            if src.type == 'HUE_SAT':  # tinted() over restyle()
                upstream = src.inputs['Color'].links[0].from_socket
                nt.links.new(upstream, base)
        color = node_color(base.links[0].from_node)
        if color:
            nt.links.remove(base.links[0])
            base.default_value = color
    # Leaf translucency and alpha-cut mixes: the plain BSDF carries the alpha texture already.
    nt.links.new(p.outputs[0], out.inputs['Surface'])
    for name in ('Normal', 'Roughness', 'Metallic'):
        for link in list(p.inputs[name].links):
            nt.links.remove(link)
    if p.inputs['Alpha'].default_value < 1 and not p.inputs['Alpha'].links:
        m['glass'] = 1
    if any(k in m.name for k in ('WindowGlass', 'glass')):
        m['glass'] = 1

for img in bpy.data.images:
    if img.size[0] > texture_px:
        img.scale(texture_px, round(img.size[1] * texture_px / img.size[0]))

bpy.ops.export_scene.gltf(
    filepath=str(output), export_format='GLB', export_apply=True, export_extras=True,
    export_image_format='WEBP', export_image_quality=82, export_cameras=False, export_lights=False,
    export_animations=False, export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=7)
print(f'{output}: {output.stat().st_size / 1e6:.2f} MB')
