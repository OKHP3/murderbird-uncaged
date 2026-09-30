"""Read-only actual finite mantle surfaces; three authored wing-only slices, not motion proof."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
base,candidate,output=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not output.exists();source=Path(__file__).resolve().parents[4]/'scripts/validate-neck-guard-envelope.py';namespace={'Vector':Vector}
code=source.read_text();exec(code[code.index('def inside('):code.index('def screen(')],namespace);edge=namespace['edge']
NODES=['left-mantle','right-mantle','left-wing-shield','right-wing-shield'];STATES=[('rest',[0,0,0,0]),('maker-wing',[0,-.38,0,.16]),('advanced-thrust',[.07,-.64,.18,.72])]
def load(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rest={n:bpy.data.objects[n].matrix_basis.copy() for n in NODES};stock=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not(o.name.startswith('V38 ') and ' mantle layered course ' in o.name):continue
  pts=[o.matrix_world@v.co for v in o.data.vertices];o.data.calc_loop_triangles();zero=[i for i in range(143) if (pts[i]-pts[i+143]).length<1e-10];degenerate=[t.index for t in o.data.loop_triangles if (pts[t.vertices[1]]-pts[t.vertices[0]]).cross(pts[t.vertices[2]]-pts[t.vertices[0]]).length*.5<1e-12]
  stock.append({'name':o.name,'zeroStockOuterIndices':zero,'degenerateTrianglesBelow1eMinus12M2':degenerate})
 return rest,stock
def screen(rest,angles):
 for n,angle in zip(NODES,angles):bpy.data.objects[n].matrix_basis=rest[n]@Matrix.Rotation(angle,4,'X')
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(','):continue
  selected=o.name.startswith('V38 ') and ' mantle layered course ' in o.name
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();pts=[ev.matrix_world@v.co for v in m.vertices];tri=[tuple(t.vertices) for t in m.loop_triangles];ev.to_mesh_clear()
  if not pts:continue
  bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)];items.append((o.name,o.parent.name,selected,pts,tri,bounds,BVHTree.FromPolygons(pts,tri,all_triangles=True)))
 assert sum(o[2] for o in items)==52;results=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if not(a[2] or b[2]) or a[1]==b[1] or any(a[5][k][1]<b[5][k][0] or b[5][k][1]<a[5][k][0] for k in range(3)):continue
   for ia,ib in a[6].overlap(b[6]):
    ta=[a[3][v] for v in a[4][ia]];tb=[b[3][v] for v in b[4][ib]]
    if any(edge(ta[k],ta[(k+1)%3],tb) or edge(tb[k],tb[(k+1)%3],ta) for k in range(3)):
     results.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'firstTrianglePair':[ia,ib],'witnessTriangles':[[list(v) for v in ta],[list(v) for v in tb]]});break
 return results
reports=[]
for label,path in [('baseline',base),('candidate',candidate)]:
 rest,stock=load(path);states=[]
 for state,angles in STATES:states.append({'pose':state,'localXAnglesRad':dict(zip(NODES,angles)),'pairs':screen(rest,angles)});print(label,state,len(states[-1]['pairs']),flush=True)
 reports.append({'label':label,'nativeSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'stockAndDegenerateDiagnostics':stock,'poses':states})
def key(pair):return tuple(sorted([pair['a'],pair['b']]))
delta=[]
for a,b in zip(reports[0]['poses'],reports[1]['poses']):
 old={key(p) for p in a['pairs']};new={key(p) for p in b['pairs']};delta.append({'pose':a['pose'],'baselinePairs':len(old),'candidatePairs':len(new),'introducedPairs':sorted(new-old),'retainedPairs':sorted(old&new),'removedPairs':sorted(old-new)})
output.write_text(json.dumps({'status':'scoped actual surface diagnostic; inspect introduced/residual identities','scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'strictEdgeMethodSourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'models':reports,'delta':delta,'limits':['Original strict edge-through-face predicates,1e-7m plane epsilon and1e-6 edge/barycentric margins; selected52 mantle plates vs different rigid owners.','Same-owner laps excluded; no containment, continuous-sweep or physical simulation certificate.','Wing-only localX authored slices from current Maker/Advanced amplitudes; not complete runtime body/neck motion or inspection opening.','Topologically manifold/positive volume is separate from retained collapsed triangles and stock reconstruction.']},indent=2)+'\n')
