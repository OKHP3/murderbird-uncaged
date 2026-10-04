"""Read-only eight-angle visual inspection of the saved final body study."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3];out=Path(__file__).parent/'attempt02';s=bpy.context.scene;cam=s.camera;s.cycles.samples=8;s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100
receipt={}
for i in range(8):
 a=math.radians(i*45);target=Vector((0,-.04,1));cam.location=target+Vector((6*math.sin(a),-6*math.cos(a),1.02));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.15;cam.data.shift_x=cam.data.shift_y=0
 name=f'turn-{i*45:03d}';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);receipt[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'resolution':[640,640]}
(out/'turntable-cameras.json').write_text(json.dumps({'samples':8,'engine':'CYCLES','nativeModified':False,'cameras':receipt},indent=2)+'\n')
