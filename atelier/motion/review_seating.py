import bpy,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
for d in (HERE,HERE.parent/'mantle',HERE.parent/'head',HERE.parent/'pedal'): sys.path.insert(0,str(d))
from cranial import apply_head
from pedal import apply_pedal
from mantle import apply_mantle
from first_choice import apply_motion
apply_head()
apply_mantle()
apply_pedal()
apply_motion()
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=4
sc.cycles.use_denoising=True
sc.cycles.device='CPU'
sc.render.resolution_percentage=100
sc.render.resolution_x=600
sc.render.resolution_y=660
cam=sc.camera
cam.data.type='ORTHO'
for nm,f,p,target,size in [
 ('mounted',0,(-3.65,-2.30,1.60),(0,-.12,.92),2.00),
 ('inspect',155,(-3.65,-2.30,1.60),(0,-.12,.92),2.00),
 ('bearing',0,(-3.65,-1.6,1.35),(0,-.373,.78),.76),
 ('bearing-dipped',155,(-3.65,-1.6,1.35),(0,-.373,.78),.76),
]:
 sc.frame_set(f)
 cam.location=p;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.ortho_scale=size
 sc.render.filepath=str(HERE/(nm+'.jpg'));sc.render.image_settings.file_format='JPEG'
 bpy.ops.render.render(write_still=True)
