import bpy,json,struct,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');A=Path(__file__).resolve().parent;N=R/'assets/models/whole-character-v38/breast-shields01/attempt02/murderbird-v38-breast-shields01-attempt02.blend';G=N.with_name(N.stem+'-rigid.glb');raw=G.read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);active={n['name']for n in doc['nodes']};bpy.ops.wm.open_mainfile(filepath=str(N));bpy.context.view_layer.update();verts=[];faces=[];owners=[];dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.type!='MESH' or o.name not in active or o.get('silhouetteStudyHistoricalHidden')is True or o.get('authoringGuide')is True or 'builder'not in str(o.get('exteriorEras','maker,mechanic,builder')).split(','):continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();offset=len(verts);verts.extend(ev.matrix_world@p.co for p in m.vertices)
 for t in m.loop_triangles:faces.append(tuple(offset+k for k in t.vertices));owners.append(o.name)
 ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=0);direction=(Vector((0,-.20,.995))-Vector((-6,-3.5,1.70))).normalized();out=[]
for o in bpy.data.objects:
 if not o.name.startswith('V38 breast layered shield '):continue
 o.data.calc_loop_triangles();half=len(o.data.vertices)//2;outer=[t for t in o.data.loop_triangles if all(k<half for k in t.vertices)];samples=[outer[min(len(outer)-1,int((i+.5)*len(outer)/24))]for i in range(24)];counts=Counter();witness=[]
 for t in samples:
  point=sum((o.matrix_world@o.data.vertices[k].co for k in t.vertices),Vector())/3;origin=point-direction*10;hit,n,idx,d=bvh.ray_cast(origin,direction,10.01);name=owners[idx]if idx is not None else 'NOHIT';counts[name]+=1
  if name!=o.name and len(witness)<4:witness.append({'sampleTriangle':t.index,'centroid':list(point),'hitObject':name,'hitPoint':list(hit)if hit is not None else None,'distanceAheadOfSampleM':10-d if d is not None else None})
 out.append({'plate':o.name,'outerCentroidSamples':24,'firstHitCounts':dict(counts),'witnesses':witness})
result={'candidateSHA256':hashlib.sha256(N.read_bytes()).hexdigest(),'method':'24representative outertriangle centroid samples perplate; orthographic rays parallel actual breast3Qcamera(-6,-3.5,1.70)->target(0,-.20,.995); nearest firsthit acrossactual eligible exported builder scene. Not occlusionareapercentage/wholeplate clearance/selftest; finitecentroid rays only.','eligibleMeshTriangleCount':len(faces),'parts':out};(A/'inspect-visible-occluders.json').write_text(json.dumps(result,indent=2)+'\n');print([(p['plate'],p['firstHitCounts'])for p in out])
