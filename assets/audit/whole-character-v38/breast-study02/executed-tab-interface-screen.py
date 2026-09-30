"""Read-only finite same-owner tab/return and tab/liner interfaces; not weld proof."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4];a,b,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();source=ROOT/'scripts/validate-neck-guard-envelope.py';code=source.read_text();ns={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],ns);edge=ns['edge']
def surf(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@p.co for p in m.vertices];t=[tuple(q.vertices) for q in m.loop_triangles];e.to_mesh_clear();return v,t,BVHTree.FromPolygons(v,t,all_triangles=True)
result=[]
for label,path in [('baseline',a),('candidate',b)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rows=[]
 for side in (-1,1):
  tab=bpy.data.objects[f'V30 breast liner receiving tab {side}'];v,t,tree=surf(tab)
  for section,name,indices in [('return',f'V23 breast moving return {side}',range(8)),('liner','V30 continuous tapered breast liner',range(16,24))]:
   target=bpy.data.objects[name];w,u,other=surf(target);overlaps=tree.overlap(other);witness=[]
   for i,j in overlaps:
    ta=[v[k] for k in t[i]];tb=[w[k] for k in u[j]]
    if any(edge(ta[k],ta[(k+1)%3],tb) or edge(tb[k],tb[(k+1)%3],ta) for k in range(3)):
     witness=[{'triangleIndices':[i,j],'triangles':[[list(q) for q in ta],[list(q) for q in tb]]}];break
   distances=[other.find_nearest(v[k])[3] for k in indices];rows.append({'tab':tab.name,'target':name,'section':section,'owners':[tab.parent.name,target.parent.name],'bvhSurfaceCandidateCount':len(overlaps),'strictEdgeThroughFaceWitness':witness,'sectionVertexNearestSurfaceDistanceMinM':min(distances),'sectionVertexNearestSurfaceDistanceMaxM':max(distances),'sectionEdgeLengthsM':[(v[i]-v[(i+1)%8+indices.start]).length for i in indices]})
 result.append({'label':label,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'interfaces':rows})
out.write_text(json.dumps({'status':'finite interface disposition only; same-owner intersection is a proposed rigid joined tab, not fabrication acceptance','models':result,'predicateSourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'limits':['Actual triangles, same unchanged strict edge predicate as external screen; broadphase candidates alone do not prove contact or volume penetration.','Tab return-side section8vertices exact; liner side changed to actual liner surface center. Surface/edge evidence does not certify joining strength, weld size or material thickness everywhere.','Same-owner parts stay a single rigid opening cover; no moving-owner bridge introduced.']},indent=2)+'\n')
