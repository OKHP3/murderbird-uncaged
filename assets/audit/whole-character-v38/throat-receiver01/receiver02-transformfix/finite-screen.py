"""Bounded actual finite triangle surfaces, strict crossing counts and first witnesses."""
import bpy,json,hashlib,bmesh
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
SCOPE=json.loads((OUT/'scope.json').read_text());CHANGED=SCOPE['changed']+[f'V33 tapered throat cheek plate {side} 1 {col}'for side in(-1,0,1)for col in range(3)]+[f'V23 cervical 4 directional guard {g}'for g in range(1,11)]+list(SCOPE['added']);CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper'];OWNERS=CHAIN+['cervical-skull-cover','head','jaw','upper-bill','cranial-cover','builder-optics','body','breastplate']
POSES=[('neutral',0,0,0,0,0),('maker-neck-jaw',-.14,-.45,0,.32,0),('captured-contact',4*.10675220489501955,0,-.5090505059024657,.1,0),('attention-yaw-minus',0,0,0,0,-.312),('attention-yaw-plus',0,0,0,0,.312),('contact-yaw-minus',4*.10675220489501955,0,-.5090505059024657,.1,-.312),('contact-yaw-plus',4*.10675220489501955,0,-.5090505059024657,.1,.312)]
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
 bpy.ops.wm.open_mainfile(filepath=str(path));label,pitch,yaw,head,jaw,headyaw=pose
 for i,n in enumerate(CHAIN):
  o=bpy.data.objects[n];d=Matrix.Rotation(pitch/4,4,'X')
  if i==0:d=d@Matrix.Rotation(yaw,4,'Z')
  o.matrix_basis=o.matrix_basis@d
 delta=Matrix.Rotation(head,4,'X')@Matrix.Rotation(headyaw,4,'Z');o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@delta
 o=bpy.data.objects['jaw'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(jaw,4,'X')
 if 'cervical-skull-cover'in bpy.data.objects:
  o=bpy.data.objects['cervical-skull-cover'];half=Quaternion().slerp(delta.to_quaternion(),.5);o.matrix_basis=o.matrix_basis@half.to_matrix().to_4x4()
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items={};stocks=[]
 for o in bpy.data.objects:
  if o.type!='MESH'or o.get('authoringGuide')is True:continue
  if o.name not in CHANGED and(not o.parent or o.parent.name not in OWNERS):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles]
  if v:items[o.name]={'v':v,'f':f,'bvh':BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0),'bounds':[(min(p[i]for p in v),max(p[i]for p in v))for i in range(3)],'owner':o.parent.name if o.parent else None,'eras':str(o.get('exteriorEras','maker,mechanic,builder')).split(',')}
  if label=='neutral'and o.name in CHANGED:
   bm=bmesh.new();bm.from_mesh(m);stocks.append({'name':o.name,'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)});bm.free()
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
     if witness is None:witness={'triangleIndices':[ia,ib],'worldTriangles':[[list(p)for p in tx],[list(p)for p in ty]]}
   if strict:pairs.append({'changed':a,'other':b,'owners':[x['owner'],y['owner']],'sameOwner':x['owner']==y['owner'],'eraIntersection':sorted(set(x['eras'])&set(y['eras'])),'strictTrianglePairs':len(strict),'changedTriangles':len({p[0]for p in strict}),'otherTriangles':len({p[1]for p in strict}),'firstWitness':witness})
 if label in ['maker-neck-jaw','captured-contact','attention-yaw-minus','attention-yaw-plus']:
  import runpy
  render=runpy.run_path(str(OUT/'pose-render.py'))['render'];render(('baseline'if str(path).endswith('curved-neck01.blend')else'candidate')+'-'+label)
 print(label,len(pairs),flush=True);return {'pairs':pairs,'stocks':stocks,'screenedMeshCount':len(items),'pose':pose}
source=ROOT/'assets/models/whole-character-v38/curved-neck01/murderbird-v38-curved-neck01.blend';candidate=ROOT/'assets/models/whole-character-v38/throat-receiver01/murderbird-v38-throat-receiver01-receiver02-transformfix.blend';out={'method':'Evaluated finite world triangles with strict edge-through-face crossings;1e-7m signed-plane epsilon,1e-6 interior barycentric/edge margin. Same-owner and era-common surfaces INCLUDED; not containment, depth, swept fit or intended seat recognition.','poseInterpretation':'Native rest-relative localX cervical bend equally distributed at four unchanged pivots; root yawlocalZ. Captured-contact uses actual recorded joint/head angles. Maximum-contact-envelope assumes bodyrest0, declared totalbend.65 and head−.65, not actual runtime timeline. Jawdeclared Maker+.32; poses are diagnostic samples.','changedMeshes':CHANGED,'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'poses':{}}
for p in POSES:
 a=load(source,p);b=load(candidate,p);sa={(x['changed'],x['other']):x for x in a['pairs']};sb={(x['changed'],x['other']):x for x in b['pairs']};out['poses'][p[0]]={'source':a,'candidate':b,'comparison':{'sourcePairs':len(sa),'candidatePairs':len(sb),'newPairs':[sb[k]for k in sb.keys()-sa.keys()],'removedPairs':[sa[k]for k in sa.keys()-sb.keys()],'inheritedCountChanges':[{'changed':k[0],'other':k[1],'owners':sb[k]['owners'],'sourceStrictTrianglePairs':sa[k]['strictTrianglePairs'],'candidateStrictTrianglePairs':sb[k]['strictTrianglePairs'],'sourceChangedTriangles':sa[k]['changedTriangles'],'candidateChangedTriangles':sb[k]['changedTriangles']}for k in sa.keys()&sb.keys()if sa[k]['strictTrianglePairs']!=sb[k]['strictTrianglePairs']]}};(OUT/'finite-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('COMPARISON',p[0],len(sb.keys()-sa.keys()),flush=True)
