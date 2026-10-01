# Head-fit01: unchanged83 watch; actual65 changed; clipped finite receiver faces.
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists()
code=(ROOT/'scripts/validate-neck-guard-envelope.py').read_text();ns={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],ns);edge=ns['edge']
ALLOWED=['V38 swept crown course 0 column 0 leaf 1', 'V38 swept crown course 0 column 0 leaf 2', 'V38 swept crown course 0 column 1 leaf 1', 'V38 swept crown course 0 column 1 leaf 2', 'V38 swept crown course 0 column 2 leaf 1', 'V38 swept crown course 0 column 2 leaf 2', 'V38 swept crown course 0 column 3 leaf 1', 'V38 swept crown course 0 column 3 leaf 2', 'V38 swept crown course 0 column 4 leaf 1', 'V38 swept crown course 0 column 4 leaf 2', 'V38 swept crown course 0 column 5 leaf 1', 'V38 swept crown course 0 column 5 leaf 2', 'V38 swept crown course 0 column 6 leaf 1', 'V38 swept crown course 0 column 6 leaf 2', 'V38 swept crown course 1 column 0 leaf 1', 'V38 swept crown course 1 column 0 leaf 2', 'V38 swept crown course 1 column 1 leaf 1', 'V38 swept crown course 1 column 1 leaf 2', 'V38 swept crown course 1 column 2 leaf 1', 'V38 swept crown course 1 column 2 leaf 2', 'V38 swept crown course 1 column 3 leaf 1', 'V38 swept crown course 1 column 3 leaf 2', 'V38 swept crown course 1 column 4 leaf 1', 'V38 swept crown course 1 column 4 leaf 2', 'V38 swept crown course 1 column 5 leaf 1', 'V38 swept crown course 1 column 5 leaf 2', 'V38 swept crown course 1 column 6 leaf 1', 'V38 swept crown course 1 column 6 leaf 2', 'V38 swept crown course 2 column 0 leaf 1', 'V38 swept crown course 2 column 0 leaf 2', 'V38 swept crown course 2 column 1 leaf 1', 'V38 swept crown course 2 column 1 leaf 2', 'V38 swept crown course 2 column 2 leaf 1', 'V38 swept crown course 2 column 2 leaf 2', 'V38 swept crown course 2 column 3 leaf 1', 'V38 swept crown course 2 column 3 leaf 2', 'V38 swept crown course 2 column 4 leaf 1', 'V38 swept crown course 2 column 4 leaf 2', 'V38 swept crown course 2 column 5 leaf 1', 'V38 swept crown course 2 column 5 leaf 2', 'V38 swept crown course 2 column 6 leaf 1', 'V38 swept crown course 2 column 6 leaf 2', 'V38 swept crown course 3 column 1 leaf 1', 'V38 swept crown course 3 column 1 leaf 2', 'V38 swept crown course 3 column 2 leaf 1', 'V38 swept crown course 3 column 2 leaf 2', 'V38 swept crown course 3 column 3 leaf 1', 'V38 swept crown course 3 column 3 leaf 2', 'V38 swept crown course 3 column 4 leaf 1', 'V38 swept crown course 3 column 4 leaf 2', 'V38 swept crown course 3 column 5 leaf 1', 'V38 swept crown course 3 column 5 leaf 2', 'V38 swept crown course 4 column 2 leaf 1', 'V38 swept crown course 4 column 2 leaf 2', 'V38 swept crown course 4 column 3 leaf 1', 'V38 swept crown course 4 column 3 leaf 2', 'V38 swept crown course 4 column 4 leaf 1', 'V38 swept crown course 4 column 4 leaf 2', 'V31 fixed temporal receiving wall -1', 'V31 fixed temporal receiving wall 1', 'V38 optic cheek shield -1 0', 'V38 optic cheek shield -1 1', 'V38 optic cheek shield -1 2', 'V38 optic cheek shield 1 0', 'V38 optic cheek shield 1 1', 'V38 optic cheek shield 1 2', 'V33 formed lower cheek receiver -1 0', 'V33 formed lower cheek receiver -1 1', 'V33 formed lower cheek receiver 1 0', 'V33 formed lower cheek receiver 1 1', 'V31 temporal fitting root -1 0', 'V31 temporal fitting root -1 1', 'V31 temporal fitting root -1 2', 'V31 temporal fitting root 1 0', 'V31 temporal fitting root 1 1', 'V31 temporal fitting root 1 2', 'V31 passive temporal fitting -1 0', 'V31 passive temporal fitting -1 1', 'V31 passive temporal fitting -1 2', 'V31 passive temporal fitting 1 0', 'V31 passive temporal fitting 1 1', 'V31 passive temporal fitting 1 2', 'V38 fixed occipital closure plate']
def in_head(o):
 while o is not None:
  if o.name in ['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']:return True
  o=o.parent
 return False

def screen():
 dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if not in_head(o) or o.type!='MESH' or not o.parent or o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(','):continue
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices) for q in m.loop_triangles];e.to_mesh_clear()
  if not v:continue
  bounds=[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)];items.append((o.name,o.parent.name,o.name in ALLOWED,v,t,bounds,BVHTree.FromPolygons(v,t,all_triangles=True)))
 assert sum(a[2] for a in items) ==83;rows=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if not(a[2] or b[2])  or any(a[5][k][1]<b[5][k][0] or b[5][k][1]<a[5][k][0] for k in range(3)):continue
   for ia,ib in a[6].overlap(b[6]):
    ta=[a[3][j] for j in a[4][ia]];tb=[b[3][j] for j in b[4][ib]]
    if any(edge(ta[k],ta[(k+1)%3],tb) or edge(tb[k],tb[(k+1)%3],ta) for k in range(3)):
     rows.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'firstTrianglePair':[ia,ib],'witnessTriangles':[[list(p) for p in ta],[list(p) for p in tb]]});break
 return rows

bpy.ops.wm.open_mainfile(filepath=str(candidate));rows=screen();wanted=[q for q in rows if ("V32 formed mandibular bowl" in [q["a"],q["b"]] and any("optic cheek shield" in x for x in [q["a"],q["b"]])) or (any("temporal fitting root" in x for x in [q["a"],q["b"]]) and "V38 compact cranial inner shell" in [q["a"],q["b"]])];out.write_text(json.dumps({"actualResidualRestWitnesses":wanted,"limits":"Actual first strict witness, not penetration depth; no source shapes changed"},indent=2)+"\n")
