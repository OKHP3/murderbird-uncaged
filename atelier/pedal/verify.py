"""Render a fixed-camera pedal comparison and measure the candidate contact patches."""
import bpy, json, sys, hashlib
from pathlib import Path
from mathutils import Vector

base=Path(__file__).resolve().parent
sys.path.insert(0,str(base))
from pedal import apply_pedal, FLOOR
scene = bpy.context.scene
for o in list(scene.objects):
    if o.type=='LIGHT':
        o.hide_render=True
    elif o.type=='MESH' and o.get('cg1cRegion') not in ('leg','foot'):
        o.hide_render=True
scene.render.engine='CYCLES'
scene.cycles.samples=20
scene.cycles.use_denoising=True
scene.camera.data.type='ORTHO'
scene.camera.data.ortho_scale=1.27
scene.camera.location=(-1.36,-2.18,.92)
scene.camera.rotation_euler=(Vector((0,-.065,.305))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0))
floor=bpy.context.object
ground=bpy.data.materials.new("Review floor")
ground.use_nodes=True
ground.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.065,.057,.044,1)
ground.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.84
floor.data.materials.append(ground)
world = bpy.data.worlds.new("Review studio")
scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.45,.50,.54,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.38
def light(name, position, size, power, col):
    bpy.ops.object.light_add(type="AREA",location=position)
    obj=bpy.context.object
    obj.name=name
    obj.data.energy=power; obj.data.shape='DISK'; obj.data.size=size; obj.data.color=col
    obj.rotation_euler=(Vector((0,0,.25))-obj.location).to_track_quat('-Z','Y').to_euler()
light('Pedal softbox',(-1.2,-1.1,2.3),1.9,180,(1,.92,.79))
light('Upper contour',(.8,.75,2.1),1.3,155,(.78,.86,1.0))
light('Warm fill',(1.65,-.5,.67),1.3,78,(1,.74,.54))
scene.render.resolution_x=1024
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
def render(name):
    scene.render.filepath=str(base/name)
    bpy.ops.render.render(write_still=True)
if '--baseline' in sys.argv:
    render('baseline-foot-detail.png')
else:
    objects=apply_pedal()
    render('first-choice-foot-detail.png')
    report = []
    for ob in objects:
        data=ob.data
        verts=[ob.matrix_world@v.co for v in data.vertices]
        low=min(p.z for p in verts)
        if ob['surfaceRole'] in ['sole','talon']:
            assert abs(low-FLOOR)<.000001, (ob.name,low)
        data.calc_loop_triangles()
        report.append(dict(name=ob.name,vertices=len(verts),triangles=len(data.loop_triangles),
                           min_z=round(low,6),contact_vertices=sum(abs(p.z-FLOOR)<.000001 for p in verts),
                           bounds=[[round(f(v[i] for v in verts),5) for i in range(3)] for f in (min,max)]))
    result={'source_blob':'9de7c4d1c9ac158135f9f846af61683528e00340a708820b2cfe1d942acc54d5',
            'script_sha256':hashlib.sha256((base/'pedal.py').read_bytes()).hexdigest(),
            'floor_z':0,'sole_and_talon_contact_height':FLOOR,
            'superseded_visible_originals':sum(bool(o.get('fc_superseded')) for o in scene.objects),
            'new_objects':report,'blender':bpy.app.version_string}
    (base/'contact-check.json').write_text(json.dumps(result,indent=2)+'\n')
