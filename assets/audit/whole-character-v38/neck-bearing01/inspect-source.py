import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/torso-support01/murderbird-v38-torso-support01.blend'));bpy.context.view_layer.update()
for n in ['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']+[f'V23 cervical 1 {part} {s}'for part in ['load link','distal race']for s in(-1,1)]+['V23 cervical 1 captive pin']+[f'V23 cervical {r} directional guard {g}'for r in(1,2)for g in range(1,6)]:
 o=bpy.data.objects.get(n)
 if not o:continue
 rec={'name':n,'parent':o.parent.name if o.parent else None,'worldOrigin':list(o.matrix_world.translation),'localRotation':list(o.rotation_euler),'extras':dict(o.items())}
 if o.type=='MESH':
  pts=[o.matrix_world@v.co for v in o.data.vertices];rec['bounds']=[[min(p[i]for p in pts),max(p[i]for p in pts)]for i in range(3)];rec['vertices']=len(pts)
  if 'race' in n or 'load link' in n:rec['faces']=[{'index':p.index,'indices':list(p.vertices),'world':[list(pts[i])for i in p.vertices]}for p in o.data.polygons]
 print('SOURCE',json.dumps(rec,default=lambda x:list(x)),flush=True)
for name in ['V23 cervical 1 directional guard 3','V23 cervical 2 directional guard 3']:
 o=bpy.data.objects[name];print('ROWS',name,[(r,list(o.matrix_world@o.data.vertices[r*19+9].co))for r in [0,4,8,12,16,20,24]],flush=True)
