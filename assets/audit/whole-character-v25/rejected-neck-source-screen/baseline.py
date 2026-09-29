from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Quaternion,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');BASE=ROOT/'assets/models/whole-character-v25/attempt-mass01/murderbird-whole-character-v25.blend';assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='bef1ff579680f7f5a95bdf7c87bde74f1a62cb68b19a7725a52ab8ce61b0aeff'
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper'];OWNERS=CHAIN+['head','jaw'];STATES=[('rest',0,0,0,0),('maker-neck-jaw',-.14,-.45,0,.32),('attention',.08,.288,.02,0),('contact-neck',.65,0,-.731,.10),('thrust-neck',-.07,0,-.035,0),('yaw-minus',0,-.45,0,0),('yaw-plus',0,.45,0,0)]
def configure():
 global REST
 bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update();REST={n:bpy.data.objects[n].matrix_local.copy() for n in OWNERS}
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
 for n in OWNERS:bpy.data.objects[n].rotation_mode='QUATERNION'
def pose(state):
 label,q,y,h,j=state
 for i,n in enumerate(CHAIN):
  o=bpy.data.objects[n];d=Quaternion((1,0,0),q*.25)
  if i==0:d=d@Quaternion((0,0,1),y)
  o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@d
 for n,v in [('head',h),('jaw',j)]:
  o=bpy.data.objects[n];o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@Quaternion((1,0,0),v)
 bpy.context.view_layer.update()
def bounds(v):return [[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]]
def straddle(A,B):
 n=(A[1]-A[0]).cross(A[2]-A[0]);n.normalize();d=[n.dot(p-A[0]) for p in B];return min(d)<-1e-7 and max(d)>1e-7
def screen(state):
 pose(state);dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent:continue
  guard=o.name.startswith('V23 cervical ') and 'directional guard' in o.name
  neighbor=o.parent.name in OWNERS+['upper-bill','cranial-cover','builder-optics','body','breastplate'] and o.get('surfaceRole') in ('plate','shell','guard','recess','frame','edge','bearing')
  if not guard and not neighbor:continue
  if 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];t=[tuple(x.vertices) for x in m.loop_triangles];ev.to_mesh_clear()
  if not v:continue
  items.append((o.name,o.parent.name,guard,bounds(v),v,t,BVHTree.FromPolygons(v,t,all_triangles=True)))
 pairs=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if a[1]==b[1] or not(a[2] or b[2]) or any(a[3][1][k]<b[3][0][k] or b[3][1][k]<a[3][0][k] for k in range(3)):continue
   hits=a[6].overlap(b[6]);strict=[]
   for x,y in hits:
    A=[a[4][n] for n in a[5][x]];B=[b[4][n] for n in b[5][y]]
    if straddle(A,B) and straddle(B,A):strict.append((x,y))
   if strict:pairs.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'strictTriangleWitnesses':len(strict)})
 return {'pose':state[0],'angles':list(state[1:]),'pairCount':len(pairs),'pairs':pairs}
if __name__=='__main__':
 configure();r={'baseSha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'method':'evaluated loop triangles; mutual plane-straddle epsilon1e-7m; interowner neck guard vs adjacent head/bill/jaw/breast/body/frame/bearings','poses':[screen(s) for s in STATES]};Path('/tmp/v25-neck-laps/baseline.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
