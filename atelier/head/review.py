"""Render the cranial checkpoint on the retained scene at the same camera and light."""
from pathlib import Path
import sys, bpy, json
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here))
from cranial import apply_head
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode='before' if 'before' in args else 'after'
if mode=='after':
    result=apply_head()
    (here/'result.json').write_text(json.dumps(result,indent=2))
if 'finish' in args:
    sys.path.insert(0,str(here.parent/'finish'))
    from metal import apply_finish
    apply_finish([o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and not o.hide_viewport and o.visible_get()])
    mode+='-finish'
scene=bpy.context.scene
scene.render.engine='CYCLES'
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL'
prefs.refresh_devices()
for d in prefs.devices:
    d.use=d.type=='METAL'
print('Render device:',[(d.type,d.name,d.use) for d in prefs.devices])
scene.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
scene.cycles.samples=12
scene.cycles.use_denoising=True
scene.cycles.use_adaptive_sampling=True
scene.render.resolution_x=920
scene.render.resolution_y=740
scene.render.resolution_percentage=100
cam=scene.camera
cam.data.type='ORTHO'
for name,loc,subject,size in (
    ('three-quarter',(-3.2,-1.65,2.02),(0,-.17,1.616),.90),
    ('profile',(-3.2,-.17,1.62),(0,-.17,1.616),.90),
    ('reverse',(2.8,1.08,2.0),(0,-.17,1.616),.90),
    ('body',(-3,-2.3,1.83),(0,-.06,.98),2.46)):
    cam.data.ortho_scale=size
    cam.location=Vector(loc)
    cam.rotation_euler=(Vector(subject)-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(here/(mode+'-'+name+'.jpg'))
    scene.render.image_settings.file_format='JPEG'
    scene.render.image_settings.quality=94
    bpy.ops.render.render(write_still=True)
