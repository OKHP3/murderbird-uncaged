import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists()
code=(ROOT/'scripts/validate-neck-guard-envelope.py').read_text();ns={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],ns);edge=ns['edge']
ALLOWED=[f'V32 returned upper bill course {i}' for i in range(3)]+[f'V33 formed lower cheek receiver {s} {i}' for s in (-1,1) for i in range(2)]+['V32 formed mandibular bowl']
def screen():
 dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(','):continue
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices) for q in m.loop_triangles];e.to_mesh_clear()
  if not v:continue
  bounds=[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)];items.append((o.name,o.parent.name,o.name in ALLOWED,v,t,bounds,BVHTree.FromPolygons(v,t,all_triangles=True)))
 assert sum(a[2] for a in items)==8;rows=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if not(a[2] or b[2]) or (a[1]==b[1] and a[1]!='jaw') or any(a[5][k][1]<b[5][k][0] or b[5][k][1]<a[5][k][0] for k in range(3)):continue
   for ia,ib in a[6].overlap(b[6]):
    ta=[a[3][j] for j in a[4][ia]];tb=[b[3][j] for j in b[4][ib]]
    if any(edge(ta[k],ta[(k+1)%3],tb) or edge(tb[k],tb[(k+1)%3],ta) for k in range(3)):
     rows.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'firstTrianglePair':[ia,ib],'witnessTriangles':[[list(p) for p in ta],[list(p) for p in tb]]});break
 return rows
reports=[]
for label,path in [('baseline',base),('candidate',candidate)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));jaw=bpy.data.objects['jaw'];rest=jaw.matrix_basis.copy();bowl=bpy.data.objects['V32 formed mandibular bowl'];meta=json.loads(jaw['makerControlSocketV1']);q=meta['point'];local=Vector((q[0],-q[2],q[1]));socket=jaw.matrix_world@local;world=[bowl.matrix_world@v.co for v in bowl.data.vertices];index=min(range(len(world)),key=lambda i:(world[i]-socket).length);sock={'metadata':meta,'nearestActualBowlVertexIndex':index,'distanceM':(world[index]-socket).length,'actualBowlVertexLocal':list(bowl.data.vertices[index].co),'bowlLocalMatrix':[list(r) for r in bowl.matrix_local],'jawLocalMatrix':[list(r) for r in jaw.matrix_local]};rows=[]
 for angle in (0,.16,.32):
  jaw.matrix_basis=rest@Matrix.Rotation(angle,4,'X');bpy.context.view_layer.update();pairs=screen();rows.append({'jawRadians':angle,'pairs':pairs});print(label,angle,len(pairs),flush=True)
 reports.append({'label':label,'nativeSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'makerSocketActualBowlFootprint':sock,'poses':rows})
key=lambda p:tuple(sorted((p['a'],p['b'])));delta=[]
for a,b in zip(reports[0]['poses'],reports[1]['poses']):
 old={key(p) for p in a['pairs']};new={key(p) for p in b['pairs']};delta.append({'jawRadians':a['jawRadians'],'baselinePairs':len(old),'candidatePairs':len(new),'introducedPairs':sorted(new-old),'removedPairs':sorted(old-new),'retainedPairs':sorted(new&old)})
s0,s1=[r['makerSocketActualBowlFootprint'] for r in reports];socket_exact=s0==s1 and s1['distanceM']<1e-6
out.write_text(json.dumps({'status':'Actual discrete strict surface diagnostic; not universal clearance','models':reports,'delta':delta,'makerSocket':{'exactActualFootprint':socket_exact,'status':'PASS' if socket_exact else 'HOLD actual bowl socket footprint differs; metadata/matrices preserved alone insufficient'},'predicate':'Unchanged1e-7m plane /1e-6 edge/barycentric; first witness per unordered pair','limits':['All changed8 vs full Builder finite pool, same-owner jaw axle/caps included; same-owner head/upper-bill intentional joins excluded.','Three localX jaw samples0/.16/.32; no containment, continuous sweep, loading or physical fit certification.','Source/candidate contact geometry measured separately; actual exported solver is integrator scope.']},indent=2)+'\n')
