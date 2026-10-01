"""Bounded actual finite triangle surfaces, strict crossing counts and first witnesses."""
import bpy,json,hashlib,bmesh
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
ROOT=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');OUT=Path(__file__).resolve().parent
SCOPE=json.loads((OUT/'scope.json').read_text());CHANGED=SCOPE['removed']+list(SCOPE['added']);import struct
EXPORT=set()
for rel in ['assets/models/whole-character-v38/jaw-stock01/murderbird-v38-jaw-stock01-rigid.glb','assets/models/whole-character-v38/crown-layout01/murderbird-v38-crown-layout01-rigid.glb']:
 raw=(ROOT/rel).read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);EXPORT.update(n['name']for n in doc['nodes'])
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper']

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
 if pose in ('capturedContact','contactJawMaximum'):
  for n in CHAIN:o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Matrix.Rotation(.10675220489501955,4,'X')
  o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(-.5090505059024657,4,'X')
 if pose in ('jawHalf','jawMaximum','contactJawMaximum'):
  o=bpy.data.objects['jaw'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(.16 if pose=='jawHalf'else .32,4,'X')
 if pose=='cranialInspection':bpy.data.objects['cranial-cover'].location.z+=.08
 if pose in ('maximumPitch','makerDip','attentionYaw'):
  from mathutils import Euler
  pitch=.1625 if pose=='maximumPitch'else(-.035 if pose=='makerDip'else 0)
  yaw=-.45 if pose=='makerDip'else(.312 if pose=='attentionYaw'else 0)
  for n in CHAIN:
   o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Euler((pitch,0,yaw if n=='neck'else 0),'XYZ').to_matrix().to_4x4()
  if pose=='maximumPitch':
   o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(-.5090505059024657,4,'X')
 if pose=='recordedThrustWing':
  for n,a in {'right-mantle':-.3143086,'right-wing-shield':.3535971,'left-mantle':.0343775,'left-wing-shield':.0883993}.items():o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Matrix.Rotation(a,4,'X')
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items={};stocks=[]
 for o in bpy.data.objects:
  if o.type!='MESH'or o.name not in EXPORT or o.get('authoringGuide')is True:continue
  ancestor=o.parent;headOwned=False
  while ancestor:
   if ancestor.name=='head':headOwned=True;break
   ancestor=ancestor.parent
  if not headOwned:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles]
  if v:items[o.name]={'v':v,'f':f,'bvh':BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0),'bounds':[(min(p[i]for p in v),max(p[i]for p in v))for i in range(3)],'owner':o.parent.name if o.parent else None,'eras':str(o.get('exteriorEras','maker,mechanic,builder')).split(',')}
  if label=='neutral'and o.name in CHANGED:
   bm=bmesh.new();bm.from_mesh(m);rec={'name':o.name,'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)};bm.free()
   if o.name.startswith('V23 cervical 4 directional guard'):
    center=bpy.data.objects['head'].matrix_world.translation;diff=[(v[i]-center).length-(v[475+i]-center).length for i in range(9*19)];rec['pairedRadialWallAboutActualHeadCenterM']={'min':min(diff),'max':max(diff),'negativeSamples':sum(x<0 for x in diff),'count':len(diff),'qualification':'Paired radial separation at formed receiving rows0–8, not full normal wall/physical stock certificate.'}
   if o.name in CHANGED:
    bvh=BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0);cross=set()
    for ia,ib in bvh.overlap(bvh):
     if ia>=ib or set(f[ia])&set(f[ib]):continue
     ta=[v[j]for j in f[ia]];tb=[v[j]for j in f[ib]]
     if any(edge(ta[k],ta[(k+1)%3],tb)or edge(tb[k],tb[(k+1)%3],ta)for k in range(3)):cross.add((ia,ib))
    rec['nonAdjacentSelfStrictTrianglePairs']=len(cross);rec['firstSelfWitnesses']=[{'triangles':[ia,ib],'vertexIndices':[f[ia],f[ib]],'centresNative':[list(sum((v[j]for j in f[k]),Vector((0,0,0)))/3)for k in[ia,ib]]}for ia,ib in sorted(cross)[:3]]
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

source=ROOT/'assets/models/whole-character-v38/jaw-stock01/murderbird-v38-jaw-stock01.blend';candidate=ROOT/'assets/models/whole-character-v38/crown-layout01/murderbird-v38-crown-layout01.blend'
out={'method':'Actual exported head-subtree evaluated triangles; strict edge-through-face at plane epsilon1e-7m/interior margin1e-6. Sameowner counts included. No containment/coplanar/grazing/swept proof. Source58removed vs candidate13added crown parts: identities differ, so pair sets are not inherited-pair evidence. Root coplanar seating not confirmed by this method. Candidate invalid stock remains HOLD.','posesInterpretation':'Bodyrest and cranial-cover nativeZ+.08 inspection only; no jaw/strike/fullcontinuous motion.','sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'poses':{}}
for p in ['neutral','cranialInspection']:
 a=load(source,p);b=load(candidate,p)
 def compact(v):
  return {'pairs':v['pairs'],'screenedMeshCount':v['screenedMeshCount'],'stocks':v['stocks'],'pairCategories':{'crownToCrown':sum(x['other']in CHANGED for x in v['pairs']),'crownToUnchangedHead':sum(x['other']not in CHANGED for x in v['pairs'])},'stockTotals':{'meshes':len(v['stocks']),'nonManifoldEdges':sum(x['nonManifoldEdges']for x in v['stocks']),'nonAdjacentSelfStrictTrianglePairs':sum(x['nonAdjacentSelfStrictTrianglePairs']for x in v['stocks'])}}
 out['poses'][p]={'source':compact(a),'candidate':compact(b)};(OUT/'finite-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('COMPARED',p,flush=True)
