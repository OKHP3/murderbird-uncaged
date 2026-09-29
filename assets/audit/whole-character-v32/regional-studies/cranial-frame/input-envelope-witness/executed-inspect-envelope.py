from pathlib import Path
import bpy,json,hashlib
from mathutils import Quaternion
N=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v31/attempt-form02/murderbird-whole-character-v31.blend')
assert hashlib.sha256(N.read_bytes()).hexdigest()=='81280c2a7103bc3b85603a5fd108daab5e337842f6a7f7c8e298be5049e07e2a'
bpy.ops.wm.open_mainfile(filepath=str(N));bpy.context.view_layer.update()
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper'];OWNERS=CHAIN+['head','jaw'];REST={n:bpy.data.objects[n].matrix_local.copy() for n in OWNERS}
STATES=[('rest',0,0,0,0),('maker-neck-jaw',-.14,-.45,0,.32),('attention',.08,.288,.02,0),('contact-neck',.65,0,-.731,.10),('thrust-neck',-.07,0,-.035,0),('yaw-minus',0,-.45,0,0),('yaw-plus',0,.45,0,0)]
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
for n in OWNERS:bpy.data.objects[n].rotation_mode='QUATERNION'
rows=[]
for label,q,y,h,j in STATES:
 for i,n in enumerate(CHAIN):
  o=bpy.data.objects[n];d=Quaternion((1,0,0),q*.25)
  if i==0:d=d@Quaternion((0,0,1),y)
  o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@d
 for n,v in [('head',h),('jaw',j)]:
  o=bpy.data.objects[n];o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@Quaternion((1,0,0),v)
 bpy.context.view_layer.update();inv=bpy.data.objects['head'].matrix_world.inverted();dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not (o.name.startswith('V23 cervical 4 ') or o.name.startswith('V31 passive cranial load bow') or o.name.startswith('V31 cranial load bow shaft seat') or o.name=='V21 head captive shaft'):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();v=[inv@ev.matrix_world@pt.co for pt in m.vertices];items.append({'name':o.name,'bounds':[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)],'vertices':[list(p) for p in v]});ev.to_mesh_clear()
 rows.append({'pose':label,'items':items})
Path('/tmp/v32-cranial-frame/envelope-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
for row in rows:
 print(row['pose'],[(i['name'],i['bounds']) for i in row['items'] if 'directional guard 7' in i['name'] or 'directional guard 8' in i['name'] or 'captive shaft' in i['name']],flush=True)
