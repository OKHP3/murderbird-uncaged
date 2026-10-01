import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
ROOT=Path(__file__).resolve().parents[4];A=Path(__file__).resolve().parent;BASE=ROOT/'assets/models/whole-character-v38/orbital-clearance02/murderbird-v38-orbital-clearance02.blend';assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='92d5ee9cc3cb0f3d7fb83e4179b5e7fdcaeeaeab99747922d8658d26388038dd';out=A/'source-inventory.json';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update()
names=[o.name for o in bpy.data.objects if o.type=='MESH' and (o.parent and o.parent.name in ['upper-bill','jaw'] or any(s in o.name.lower()for s in ['lower cheek','jaw cheek','jaw journal','annular journal','jaw rim','jaw clevis']))];rows=[]
for n in names:
 o=bpy.data.objects[n];v=[o.matrix_world@q.co for q in o.data.vertices];rows.append({'name':n,'owner':o.parent.name,'vertices':len(v),'nativeWorldBounds':[[min(p[k]for p in v),max(p[k]for p in v)]for k in range(3)],'localMatrix':[list(r)for r in o.matrix_local],'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials]})
code=(ROOT/'scripts/validate-neck-guard-envelope.py').read_text();ns={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],ns);edge=ns['edge'];jaw=bpy.data.objects['jaw'];rest=jaw.matrix_basis.copy();tests=[]
for angle in [0,-.08,-.16,-.24,-.32]:
 jaw.matrix_basis=rest@Matrix.Rotation(angle,4,'X');bpy.context.view_layer.update();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent:continue
  p=o
  while p and p.name!='head':p=p.parent
  if not p:continue
  m=o.data;m.calc_loop_triangles();v=[o.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices)for q in m.loop_triangles];items.append((o.name,o.parent.name,v,t,BVHTree.FromPolygons(v,t,all_triangles=True)))
 pairs=[]
 for a in items:
  if a[0]!='V32 formed mandibular bowl':continue
  for b in items:
   if b is a:continue
   for ia,ib in a[4].overlap(b[4]):
    ta=[a[2][i]for i in a[3][ia]];tb=[b[2][i]for i in b[3][ib]]
    if any(edge(ta[k],ta[(k+1)%3],tb)or edge(tb[k],tb[(k+1)%3],ta)for k in range(3)):
     pairs.append({'a':a[0],'b':b[0],'firstTriangles':[ia,ib],'witness':[[list(p)for p in ta],[list(p)for p in tb]]});break
 bowl=bpy.data.objects['V32 formed mandibular bowl'];points=[bowl.matrix_world@v.co for v in bowl.data.vertices];tip=min(points,key=lambda p:p.y);tests.append({'radians':angle,'jawTipNative':list(tip),'strictPairs':pairs});print('rotation',angle,'tip',list(tip),'pairs',[p['b']for p in pairs],flush=True)
result={'sourceNativeSha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'region':rows,'jawRestLocalMatrix':[list(r)for r in jaw.matrix_local],'jawRestMatrixBasis':[list(r)for r in rest],'jawSocket':json.loads(jaw['makerControlSocketV1']),'rigidClosingDiagnostic':tests,'limits':'Negative rotations are read-only feasibility samples, not approved rest changes. Same strict finite predicate; no containment or sweep certificate.'};out.write_text(json.dumps(result,indent=2)+'\n');print('INVENTORY',json.dumps(rows),flush=True)
