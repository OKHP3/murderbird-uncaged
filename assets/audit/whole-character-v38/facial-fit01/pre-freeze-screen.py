import bpy,bmesh,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
R=Path('/Users/okh/.codex/worktrees/v38-facial-fit/murderbird-uncaged')
TARGET=[f'V31 passive optic cavity floor {s}'for s in[-1,1]]+[f'V38 facial-shell {part} {s}'for s in[-1,1]for part in['brow roof','cheek bridge']]
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

def items():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();raw=(R/'assets/models/whole-character-v38/facial-shell01/attempt02/murderbird-v38-facial-shell01-attempt02-rigid.glb').read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);names={n['name']for n in doc['nodes']};out={}
 for o in bpy.data.objects:
  if o.type!='MESH' or o.name not in names:continue
  p=o.parent;yes=False
  while p:
   if p.name=='head':yes=True;break
   p=p.parent
  if not yes:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles];out[o.name]={'v':v,'f':f,'bvh':BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0),'bounds':[(min(p[i]for p in v),max(p[i]for p in v))for i in range(3)],'owner':o.parent.name,'eras':str(o.get('exteriorEras','maker,mechanic,builder')).split(',')};ev.to_mesh_clear()
 return out
def crossing(x,y):
 raw=x['bvh'].overlap(y['bvh']);pairs=[]
 for ia,ib in raw:
  tx=[x['v'][j]for j in x['f'][ia]];ty=[y['v'][j]for j in y['f'][ib]]
  if any(edge(tx[k],tx[(k+1)%3],ty)or edge(ty[k],ty[(k+1)%3],tx)for k in range(3)):pairs.append((ia,ib))
 return pairs
def screen():
 crown=bpy.data.objects['cranial-cover'];jaw=bpy.data.objects['jaw'];cp=crown.location.copy();jm=jaw.matrix_basis.copy();out={'method':'Finite evaluated exported head triangles. Strict edge-through-face1e-7m plane epsilon/1e-6 margin. Same-owner contacts included; no coplanar/grazing/containment or continuous-motion proof.','poses':{},'self':[]}
 for label,z,j in[('rest',0,0),('crownIntermediate',.04,0),('crownOpen',.08,0),('crownOpenSeparated',.22,0),('jawMaximum',0,.32)]:
  crown.location=cp+Vector((0,0,z));jaw.matrix_basis=jm
  if j:jaw.matrix_basis=jm@__import__('mathutils').Matrix.Rotation(j,4,'X')
  ob=items();pairs=[]
  for name in TARGET:
   x=ob[name]
   if label=='rest':
    own=[]
    for ia,ib in x['bvh'].overlap(x['bvh']):
     if ia>=ib or set(x['f'][ia])&set(x['f'][ib]):continue
     tx=[x['v'][v]for v in x['f'][ia]];ty=[x['v'][v]for v in x['f'][ib]]
     if any(edge(tx[k],tx[(k+1)%3],ty)or edge(ty[k],ty[(k+1)%3],tx)for k in range(3)):own.append((ia,ib))
    out['self'].append({'name':name,'strictPairs':len(own),'firstWitness':own[:1]})
   for other,y in ob.items():
    if other==name or(other in TARGET and other<name)or not(set(x['eras'])&set(y['eras'])):continue
    if any(x['bounds'][i][1]<y['bounds'][i][0]or y['bounds'][i][1]<x['bounds'][i][0]for i in range(3)):continue
    hit=crossing(x,y)
    if hit:
     ia,ib=hit[0];pairs.append({'changed':name,'other':other,'owners':[x['owner'],y['owner']],'strictTrianglePairs':len(hit),'firstWitness':{'triangles':[ia,ib],'centresNative':[list(sum((o['v'][v]for v in o['f'][t]),Vector())/3)for o,t in[(x,ia),(y,ib)]]}})
  out['poses'][label]={'crownLocalNativeZOffsetM':z,'jawLocalXDeltaRad':j,'pairs':pairs}
 crown.location=cp;jaw.matrix_basis=jm;bpy.context.view_layer.update()
 out['summary']={'pairCounts':{n:len(q['pairs'])for n,q in out['poses'].items()},'strictSelfPairs':sum(q['strictPairs']for q in out['self']),'openingOwnerPairs':{n:len([q for q in v['pairs']if q['owners'][1]=='cranial-cover'])for n,v in out['poses'].items()},'temporalLeafPairs':{n:len([q for q in v['pairs']if 'swept temporal leaf'in q['other']])for n,v in out['poses'].items()}}
 return out
