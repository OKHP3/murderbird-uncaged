"""Bounded actual finite triangle surfaces, strict crossing counts and first witnesses."""
import bpy,json,hashlib,bmesh
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
SCOPE=json.loads((OUT/'scope.json').read_text());CHANGED=SCOPE['changed']+list(SCOPE['added'])+SCOPE['removed'];CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper'];OWNERS=CHAIN+['cervical-skull-cover','head','jaw','upper-bill','cranial-cover','builder-optics','body','breastplate']
POSES=['neutral','capturedContact','makerDip','maximumPitch','openExploded']

def inside(p,t):
 x,y,z=t;a=y-x;b=z-x;c=p-x;aa=a.dot(a);ab=a.dot(b);bb=b.dot(b);den=aa*bb-ab*ab
 if abs(den)<1e-18:return False
 u=(bb*c.dot(a)-ab*c.dot(b))/den;v=(aa*c.dot(b)-ab*c.dot(a))/den;return min(u,v,1-u-v)>1e-6
 def_unused=0

def edge(p,q,t):
 n=(t[1]-t[0]).cross(t[2]-t[0]);length=n.length
 if length<1e-12:return False
 n/=length;d0=n.dot(p-t[0]);d1=n.dot(q-t[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 d=q-p;hit=intersect_ray_tri(*t,d,p,True)
 if hit is None:return False
 u=(hit-p).dot(d)/max(d.length_squared,1e-30);return 1e-6<u<1-1e-6 and inside(hit,t)
def load(path,pose):
 bpy.ops.wm.open_mainfile(filepath=str(path));label=pose
 if pose=='openExploded':
  o=bpy.data.objects['breastplate'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(o['inspectionOpenRadians'],4,'X');bpy.data.objects['cranial-cover'].location.z+=.08
  offsets={'breastplate':(-.70,-.18,-.12),'left-mantle':(.39,0,.09),'right-mantle':(-.39,0,.09),'left-wing-shield':(.11,-.12,-.04),'right-wing-shield':(-.11,-.12,-.04),'winding-drive':(-.45,-.22,-.10),'power-core':(.32,-.28,-.05),'processing':(.28,0,.20),'cranial-cover':(0,0,.14)}
  for n,p in offsets.items():bpy.data.objects[n].location+=Vector(p)
 if pose=='capturedContact':
  for n in CHAIN:o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Matrix.Rotation(.10675220489501955,4,'X')
  o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(-.5090505059024657,4,'X');o=bpy.data.objects['jaw'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(.025392792943327247,4,'X')
 if pose in ('maximumPitch','makerDip','attentionYaw'):
  from mathutils import Euler
  pitch=.1625 if pose=='maximumPitch'else(-.034764171855032014 if pose=='makerDip'else 0)
  yaw=-.44696792385041154 if pose=='makerDip'else(.312 if pose=='attentionYaw'else 0)
  for n in CHAIN:
   o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Euler((pitch,0,yaw if n=='neck'else 0),'XYZ').to_matrix().to_4x4()
  if pose=='maximumPitch':
   o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(-.5090505059024657,4,'X')
 if pose=='recordedThrustWing':
  for n,a in {'right-mantle':-.3143086,'right-wing-shield':.3535971,'left-mantle':.0343775,'left-wing-shield':.0883993}.items():o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Matrix.Rotation(a,4,'X')
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items={};stocks=[]
 for o in bpy.data.objects:
  if o.type!='MESH'or o.get('authoringGuide')is True:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles]
  if v:items[o.name]={'v':v,'f':f,'bvh':BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0),'bounds':[(min(p[i]for p in v),max(p[i]for p in v))for i in range(3)],'owner':o.parent.name if o.parent else None,'eras':str(o.get('exteriorEras','maker,mechanic,builder')).split(',')}
  if label=='neutral'and o.name in CHANGED:
   bm=bmesh.new();bm.from_mesh(m);rec={'name':o.name,'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)};bm.free()
   if 'directional guard' in o.name or 'tapered throat cheek plate' in o.name:
    half=len(v)//2;wall=[(v[i]-v[i+half]).length for i in range(half)];rec['pairedStockVectorLengthM']={'min':min(wall),'max':max(wall),'qualification':'Paired radial vector lengths, not normal wall certification.'}
   adjacency={i:set()for i in range(len(v))}
   for tri in f:
    for j in range(3):adjacency[tri[j]].add(tri[(j+1)%3]);adjacency[tri[(j+1)%3]].add(tri[j])
   seen=set();counts=[]
   for i in adjacency:
    if i in seen:continue
    todo=[i];seen.add(i);count=0
    while todo:
     j=todo.pop();count+=1
     for k in adjacency[j]:
      if k not in seen:seen.add(k);todo.append(k)
    counts.append(count)
   rec['connectedComponentVertexCounts']=counts
   if o.name in CHANGED:
    bvh=BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0);cross=set()
    for ia,ib in bvh.overlap(bvh):
     if ia>=ib or set(f[ia])&set(f[ib]):continue
     ta=[v[j]for j in f[ia]];tb=[v[j]for j in f[ib]]
     if any(edge(ta[k],ta[(k+1)%3],tb)or edge(tb[k],tb[(k+1)%3],ta)for k in range(3)):cross.add((ia,ib))
    rec['nonAdjacentSelfStrictTrianglePairs']=len(cross)
   stocks.append(rec)
  ev.to_mesh_clear()
 pairs=[]
 for a in CHANGED:
  if a not in items:continue
  x=items[a]
  for b,y in items.items():
   if a==b or(b in CHANGED and a>b)or not(set(x['eras'])&set(y['eras'])):continue
   if any(x['bounds'][i][1]<y['bounds'][i][0]or y['bounds'][i][1]<x['bounds'][i][0]for i in range(3)):continue
   raw=x['bvh'].overlap(y['bvh']);strict=[];witness=None
   for ia,ib in raw:
    tx=[x['v'][j]for j in x['f'][ia]];ty=[y['v'][j]for j in y['f'][ib]]
    if any(edge(tx[k],tx[(k+1)%3],ty)or edge(ty[k],ty[(k+1)%3],tx)for k in range(3)):
     strict.append((ia,ib))
   if strict:pairs.append({'changed':a,'other':b,'owners':[x['owner'],y['owner']],'sameOwner':x['owner']==y['owner'],'eraIntersection':sorted(set(x['eras'])&set(y['eras'])),'strictTrianglePairs':len(strict),'changedTriangles':len({p[0]for p in strict}),'otherTriangles':len({p[1]for p in strict})})
 print(label,len(pairs),flush=True);return {'pairs':pairs,'stocks':stocks,'screenedMeshCount':len(items),'pose':pose}
source=ROOT/'assets/models/whole-character-v38/neck-envelope01/murderbird-v38-neck-envelope01.blend';candidate=ROOT/'assets/models/whole-character-v38/neck-envelope01/attempt02/murderbird-v38-neck-envelope01-attempt02.blend';out={'method':'Evaluated finite world triangles with strict edge-through-face crossings;1e-7m signed-plane epsilon,1e-6 interior barycentric/edge margin. Same-owner and era-common surfaces INCLUDED; not containment, depth, swept fit or intended seat recognition.','unusedDiagnosticBranches':'Not executed:  Neutral plus declared breast+1.1 nativeX opening and all9 runtime glTF→native exploded offsets including rightwingY-.120; captured four neck+.10675220489501955/head-.5090505059024657; Recorded achievable thrustwing sample from root runtime (Lshoulder.0343775/elbow.0883993,Rshoulder-.3143086/elbow.3535971) applied at bodyrest to bound wing/torso interface; not complete capturedthrust pose or maximum. No legextreme inferred.','poseInterpretation':'Body-rest slices: neutral; source-strike captured four localX+.10675220489501955/head-.5090505059024657/jaw+.025392792943327247; actual captured Maker neck four-.034764171855032014/root nativeZ-.44696792385041154; authored max four+.1625/head-.509; inspection native breast localX+1.1/cranialZ+.08 plus actual9 exploded glTF-to-native offsets, rightwingY-.120. Other captured body/root/leg/yaw transforms omitted, not complete action capture or sweep.','changedMeshes':CHANGED,'limits':['Five static body-rest samples;68 declared neck guards/yokes against finite wholemesh neighbors via bounds acceleration. All same-owner pairs counted. No containment/swept/physical fit certificate.','Sameowner and era-common surfaces included; no exemption for supportseats.','Actual legextreme not sampled until captured runtime quaternion supplied.'],'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'poses':{}}
for p in POSES:
 a=load(source,p);b=load(candidate,p);sa={(x['changed'],x['other']):x for x in a['pairs']};sb={(x['changed'],x['other']):x for x in b['pairs']};out['poses'][p]={'source':a,'candidate':b,'comparison':{'sourcePairs':len(sa),'candidatePairs':len(sb),'newPairs':[sb[k]for k in sb.keys()-sa.keys()],'removedPairs':[sa[k]for k in sa.keys()-sb.keys()],'inheritedCountChanges':[{'changed':k[0],'other':k[1],'owners':sb[k]['owners'],'sourceStrictTrianglePairs':sa[k]['strictTrianglePairs'],'candidateStrictTrianglePairs':sb[k]['strictTrianglePairs'],'sourceChangedTriangles':sa[k]['changedTriangles'],'candidateChangedTriangles':sb[k]['changedTriangles']}for k in sa.keys()&sb.keys()if sa[k]['strictTrianglePairs']!=sb[k]['strictTrianglePairs']]}};(OUT/'finite-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('COMPARISON',p,len(sb.keys()-sa.keys()),flush=True)
