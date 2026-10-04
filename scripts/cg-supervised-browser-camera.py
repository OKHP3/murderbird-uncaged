import json,sys
from pathlib import Path
import bpy
from mathutils import Euler,Vector
args=sys.argv[sys.argv.index('--')+1:]
r=Path(args[0])
for attempt in args[1:]:
 j=json.loads((r/'assets/audit/cg-supervised01'/attempt/'builder/receipt.json').read_text())
 c=j['cameras']['canon-neutral']
 s=bpy.context.scene;s.render.resolution_x,s.render.resolution_y=c['resolution'];s.render.resolution_percentage=100
 d=bpy.data.cameras.new('camera projection probe');d.type=c['projection'];d.ortho_scale=c['ortho_scale'];d.shift_x,d.shift_y=c['shift']
 frames=d.view_frame(scene=s)
 rot=Euler(c['rotation_euler']).to_matrix();pos=Vector(c['location']);look=rot@Vector((0,0,-1));up=rot@Vector((0,1,0))
 cv=lambda v:[v.x,v.z,-v.y]
 out={'source_receipt':str((r/'assets/audit/cg-supervised01'/attempt/'builder/receipt.json').relative_to(r)),'registration':'estimated, not calibrated','coordinate_conversion':'Blender Z-up to glTF Y-up: x,z,-y','native_resolution':c['resolution'],'position':cv(pos),'target':cv(pos+look),'up':cv(up),'frustum':{'left':min(v.x for v in frames),'right':max(v.x for v in frames),'bottom':min(v.y for v in frames),'top':max(v.y for v in frames)},'renderer_pixel_equivalence':False}
 (r/'assets/audit/cg-supervised01'/attempt/'browser-camera.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out))
