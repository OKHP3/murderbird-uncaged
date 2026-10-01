import bpy,bmesh,json,struct,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');A=Path(__file__).resolve().parent
models={'source':R/'assets/models/whole-character-v38/bill-vault01/attempt02/murderbird-v38-bill-vault01-attempt02.blend','candidate':R/'assets/models/whole-character-v38/facial-shell01/attempt02/murderbird-v38-facial-shell01-attempt02.blend'}
def vol(o):
 bm=bmesh.new();bm.from_mesh(o.data);v=abs(bm.calc_volume(signed=True));non=sum(not e.is_manifold for e in bm.edges);bm.free();return v,non
out={'method':'Two passive floors versus ALL exported actual head descendant mesh neighbors, rest only. Vertex-to-triangle distances are sampled upper bounds on surface separation; exact finite Boolean tested only AABB-overlapping neighbors. Positive common-stock requires manifold result bounded by both participant volumes. No continuous motion/coplanar seating proof.','recipeSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'models':{}}
for label,path in models.items():
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();raw=path.with_name(path.stem+'-rigid.glb').read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);names={n['name']for n in doc['nodes']};items={}
 for o in bpy.data.objects:
  if o.type!='MESH' or o.name not in names:continue
  parent=o.parent;head=False
  while parent:
   if parent.name=='head':head=True;break
   parent=parent.parent
  if not head:continue
  o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];f=[tuple(t.vertices)for t in o.data.loop_triangles];items[o.name]={'o':o,'v':v,'bvh':BVHTree.FromPolygons(v,f,all_triangles=True),'bounds':[(min(p[i]for p in v),max(p[i]for p in v))for i in range(3)]}
 rows=[]
 for side in[-1,1]:
  name=f'V31 passive optic cavity floor {side}';x=items[name];dist=[];common=[]
  for other,y in items.items():
   if other==name:continue
   best=None
   for p in x['v']:
    hit=y['bvh'].find_nearest(p)
    if hit[0]is not None and(best is None or hit[3]<best[0]):best=(hit[3],p,hit[0])
   if best:dist.append({'other':other,'owner':y['o'].parent.name,'sampledVertexTriangleDistanceM':best[0],'nativeWitness':[list(best[1]),list(best[2])]})
   if any(x['bounds'][i][1]<y['bounds'][i][0]or y['bounds'][i][1]<x['bounds'][i][0]for i in range(3)):continue
   a=x['o'];b=y['o'];tmp=a.copy();tmp.data=a.data.copy();bpy.context.scene.collection.objects.link(tmp);m=tmp.modifiers.new('Floor finite commonstock','BOOLEAN');m.operation='INTERSECT';m.solver='EXACT';m.object=b;bpy.context.view_layer.objects.active=tmp
   try:
    bpy.ops.object.modifier_apply(modifier=m.name);v,n=vol(tmp);av,_=vol(a);bv,_=vol(b);common.append({'other':other,'owner':b.parent.name,'volumeM3':v,'nonmanifoldEdges':n,'boundedByParticipants':0<v<=min(av,bv)*1.001})
   except Exception as e:common.append({'other':other,'error':str(e)})
   bpy.data.objects.remove(tmp,do_unlink=True)
  rows.append({'name':name,'headNeighborsConsidered':len(items)-1,'nearestActualSurfaces':sorted(dist,key=lambda d:d['sampledVertexTriangleDistanceM'])[:6],'commonStockAABBNeighborTests':common,'floorNativeXInterval':x['bounds'][0]})
 out['models'][label]=rows
(A/'inspect-floor-support.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2),flush=True)
