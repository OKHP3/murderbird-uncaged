import bpy, json, sys
from mathutils import Vector
from pathlib import Path
folder=Path(__file__).resolve().parent
sys.path.insert(0,str(folder))
from mantle import apply_mantle
scene=bpy.context.scene
params=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=params[0] if params else 'after'
if mode=='after':
    print(apply_mantle())
scene.render.engine='CYCLES'
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='METAL'
    prefs.refresh_devices()
    for d in prefs.devices:d.use=d.type=='METAL'
    scene.cycles.device='GPU' if any(d.use for d in prefs.devices) and 'cpu' not in params else 'CPU'
except Exception as e:print(e)
scene.cycles.samples=6
scene.cycles.use_denoising=True
scene.cycles.use_adaptive_sampling=True
scene.render.resolution_x=640
scene.render.resolution_y=680
scene.render.resolution_percentage=100
cam=scene.camera
cam.data.type='ORTHO'
cam.data.ortho_scale=1.57
world_t=Vector((0,-.025,1.07))
for angle,position in [('left',(-3.6,-2.15,1.66)),('right',(3.6,-2.15,1.66))]:
    cam.location=Vector(position)
    cam.rotation_euler=(world_t-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(folder / f'{mode}-{angle}.png')
    bpy.ops.render.render(write_still=True)
