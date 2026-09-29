import bpy, json, hashlib
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
BASE=R/'assets/models/whole-character-v34/attempt-form01/murderbird-whole-character-v34.blend'
NEW=R/'assets/models/whole-character-v35/regional-studies/joint-housings/attempt02/murderbird-whole-character-v35-joint-housings.blend'
POSE_PATH=R/'assets/audit/whole-character-v34/attempt-form01/leg-composition-screen/pose-matrices.json'
OUT=R/'assets/audit/whole-character-v35/regional-studies/joint-housings/attempt02/fit-screen.json'
POSE_DATA=json.loads(POSE_PATH.read_text()); C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inside(p,tri):
 x,y,z=tri;v0=y-x;v1=z-x;v2=p-x;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);den=d00*d11-d01*d01
 if abs(den)<1e-18:return False
 u=(d11*v2.dot(v0)-d01*v2.dot(v1))/den;v=(d00*v2.dot(v1)-d01*v2.dot(v0))/den
 return min(u,v,1-u-v)>1e-6
def edge(p,q,tri):
 n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
 if n.length<1e-12:return False
 n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 direction=q-p;hit=intersect_ray_tri(*tri,direction,p,True)
 if hit is None:return False
 t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
 return 1e-6<t<1-1e-6 and inside(hit,tri)
def screen(path,pose):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 if pose['id']!='exported-rest':
  transforms={row['name']:C.inverted()@Matrix([row['worldMatrix'][i::4] for i in range(4)])@C for row in pose['transforms']}
  nodes=[o for o in bpy.data.objects if o.type=='EMPTY' and not o.get('authoringGuide')]
  def depth(o):
   i=0
   while o.parent:i+=1;o=o.parent
   return i
  for o in sorted(nodes,key=depth): o.matrix_world=transforms[o.name]
  bpy.context.view_layer.update()
  error=max(abs(o.matrix_world[i][j]-transforms[o.name][i][j]) for o in nodes for i in range(4) for j in range(4))
  assert error<1e-6,error
 else:error=0
 dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.get('authoringGuide') is True:continue
  if 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];tri=[tuple(f.vertices) for f in m.loop_triangles];ev.to_mesh_clear()
  if not v:continue
  scope=o.parent.name in ('left-thigh','left-shin','right-thigh','right-shin')
  bounds=[[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]]
  items.append((o.name,o.parent.name,scope,v,tri,bounds,BVHTree.FromPolygons(v,tri,all_triangles=True)))
 pairs=set()
 for i,x in enumerate(items):
  for y in items[i+1:]:
   if x[1]==y[1] or not(x[2] or y[2]) or any(x[5][1][k]<y[5][0][k] or y[5][1][k]<x[5][0][k] for k in range(3)):continue
   for ix,iy in x[6].overlap(y[6]):
    tx=[x[3][j] for j in x[4][ix]];ty=[y[3][j] for j in y[4][iy]]
    if any(edge(tx[k],tx[(k+1)%3],ty) or edge(ty[k],ty[(k+1)%3],tx) for k in range(3)):
     pairs.add(tuple(sorted((x[0],y[0]))));break
 return {'pose':pose['id'],'poseInstallMaxMatrixError':error,'pairCount':len(pairs),'pairs':[list(p) for p in sorted(pairs)]}
report={'status':'strict discrete cross-owner screen only','method':'V34 edge-through-face triangle method; 1e-7m plane and 1e-6 barycentric/edge thresholds; no pair exemptions; not continuous clearance or physics','sourcePoseFileSHA256':sha(POSE_PATH),'baselineNativeSHA256':sha(BASE),'candidateNativeSHA256':sha(NEW),'poses':[]}
for pose in POSE_DATA['poses']:
 before=screen(BASE,pose);after=screen(NEW,pose)
 b={tuple(x) for x in before['pairs']};c={tuple(x) for x in after['pairs']}
 result={'pose':pose['id'],'baselinePairCount':len(b),'candidatePairCount':len(c),'introducedCount':len(c-b),'resolvedCount':len(b-c),'retainedCount':len(b&c),'introduced':[list(x) for x in sorted(c-b)],'resolved':[list(x) for x in sorted(b-c)],'retained':[list(x) for x in sorted(c&b)]}
 report['poses'].append(result);OUT.write_text(json.dumps(report,indent=2)+'\n')
 print(pose['id'], 'base',len(b),'candidate',len(c),'introduced',len(c-b),'resolved',len(b-c),flush=True)
print(json.dumps({'status':report['status'],'poses':[{k:v for k,v in x.items() if k not in ('introduced','resolved','retained')} for x in report['poses']]}))
