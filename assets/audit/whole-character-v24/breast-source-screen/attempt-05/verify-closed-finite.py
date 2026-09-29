import bpy, bmesh, hashlib, json, math
from pathlib import Path
NATIVE=Path('/tmp/v24-breast-study/attempt-05/murderbird-v24-breast-study.blend')
OUT=Path('/tmp/v24-breast-study/attempt-05/closed-finite-check.json')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert sha(NATIVE)=='9189210608be0ed2e30fd2cb0612712b502f441c3b10ce08d46dff6078059474'
assert not OUT.exists()
objects=sorted((o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V24 ')),key=lambda o:o.name)
assert len(objects)==35
results=[]
for obj in objects:
 ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=ev.to_mesh()
 try:
  mesh.calc_loop_triangles()
  bm=bmesh.new();bm.from_mesh(mesh)
  areas=[f.calc_area() for f in bm.faces]
  nonmanifold=[e for e in bm.edges if not e.is_manifold]
  boundary=sum(e.is_boundary for e in nonmanifold)
  results.append({'name':obj.name,'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'nonFiniteVertexCount':sum(not all(math.isfinite(c) for c in v.co) for v in mesh.vertices),'nonFiniteFaceCount':sum(not math.isfinite(a) for a in areas),'degenerateFaceCount':sum(a<=1e-12 for a in areas),'nonManifoldEdgeCount':len(nonmanifold),'boundaryEdgeCount':boundary})
  bm.free()
 finally:ev.to_mesh_clear()
report={'native':{'path':str(NATIVE),'sha256':sha(NATIVE)},'objectsChecked':len(results),'allEvaluatedFinite':all(not r['nonFiniteVertexCount'] and not r['nonFiniteFaceCount'] and not r['degenerateFaceCount'] for r in results),'allEvaluatedClosedManifold':all(not r['nonManifoldEdgeCount'] for r in results),'results':results}
OUT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('objectsChecked','allEvaluatedFinite','allEvaluatedClosedManifold')}))
