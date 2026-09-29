from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
N=ROOT/'assets/models/whole-character-v23/attempt-form03/murderbird-whole-character-v23.blend'
assert hashlib.sha256(N.read_bytes()).hexdigest()=='66b6ff8c17e468c0e1ab7874728a3aea889a5630fd25dafc3392d954a1343e62'
bpy.ops.wm.open_mainfile(filepath=str(N))
chain=['neck','cervical-mid-a','cervical-mid-b','cervical-upper'];owners=chain+['head','jaw']
rest={n:bpy.data.objects[n].matrix_local.copy() for n in owners}
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
for n in owners:bpy.data.objects[n].rotation_mode='QUATERNION'
pairs=[('V23 cervical 1 directional guard 3','V23 recessed breast door'),('V23 cervical 1 directional guard 3','V23 breast formed course 01 plate 03'),('V23 cervical 1 directional guard 3','V23 cervical 2 directional guard 3'),('V23 cervical 3 directional guard 10','V23 cervical 4 directional guard 10')]
def evaluated(name):
 o=bpy.data.objects[name];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];tris=[tuple(t.vertices) for t in m.loop_triangles];ev.to_mesh_clear();return v,tris,BVHTree.FromPolygons(v,tris,all_triangles=True)
def bounds(v):return [[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]]
def straddles(A,B):
 n=(A[1]-A[0]).cross(A[2]-A[0]);n.normalize();d=[n.dot(p-A[0]) for p in B];return min(d)<-1e-7 and max(d)>1e-7
out={'nativeSha256':hashlib.sha256(N.read_bytes()).hexdigest(),'method':'Explicit evaluated triangles; BVH candidates filtered by mutual noncoplanar plane straddle epsilon 1e-7m. Nearest-normal depth is approximate local intrusion witness, not full solid containment.','sourceHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'scripts/render-v23-neck-study.py',ROOT/'scripts/regions/whole-character-v23-body.py',ROOT/'scripts/regions/whole-character-v21-envelope.py']},'poses':[],'rawRestSamples':{}}
for label,q,y,h,j in [('rest',0,0,0,0),('maker',-.14,-.45,0,.32),('contact',.65,0,-.731,.10)]:
 for i,n in enumerate(chain):
  o=bpy.data.objects[n];d=Quaternion((1,0,0),q*.25)
  if i==0:d=d@Quaternion((0,0,1),y)
  o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@rest[n].to_quaternion()@d
 for n,val in [('head',h),('jaw',j)]:
  o=bpy.data.objects[n];o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@rest[n].to_quaternion()@Quaternion((1,0,0),val)
 bpy.context.view_layer.update();result={'name':label,'pitch':q,'yaw':y,'head':h,'pairs':[]}
 for a,b in pairs:
  va,ta,ba=evaluated(a);vb,tb,bb=evaluated(b);hits=ba.overlap(bb);strict=[];witness=[]
  for i,k in hits:
   A=[va[n] for n in ta[i]];B=[vb[n] for n in tb[k]]
   if straddles(A,B) and straddles(B,A):strict.append((i,k));witness.extend(A+B)
  depths=[]
  for v in va:
   p,n,idx,d=bb.find_nearest(v)
   if p is not None and (v-p).dot(n)<-1e-7 and d<.020:depths.append(d)
  result['pairs'].append({'a':a,'b':b,'owners':[bpy.data.objects[a].parent.name,bpy.data.objects[b].parent.name],'boundsA':bounds(va),'boundsB':bounds(vb),'triangleCandidateCount':len(hits),'mutualStraddleCount':len(strict),'crossingRegionBounds':bounds(witness) if witness else None,'crossingTrianglesCentroid':list(sum(witness,Vector())/len(witness)) if witness else None,'nearestNormalIntrusionMaxBelow20mm':max(depths) if depths else 0})
 if label=='rest':
  for idx in range(1,5):
   for k in (3,10):
    o=bpy.data.objects[f'V23 cervical {idx} directional guard {k}'];pivot=bpy.data.objects[chain[min(idx,3)]].matrix_world.translation
    samples=[]
    for row in (0,16,32):
     p=o.matrix_world@o.data.vertices[row*25+12].co
     samples.append({'row':row,'world':list(p),'radiusFromDistalXAxis':math.hypot(p.y-pivot.y,p.z-pivot.z)})
    out['rawRestSamples'][o.name]={'owner':o.parent.name,'distalAxisCentre':list(pivot),'wall':o.modifiers[0].thickness,'samples':samples}
 result['jointWorldCentres']={n:list(bpy.data.objects[n].matrix_world.translation) for n in chain};out['poses'].append(result)
Path('/tmp/v24-neck-diagnosis/result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
