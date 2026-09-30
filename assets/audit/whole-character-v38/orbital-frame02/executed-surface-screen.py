import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists()
code=(ROOT/'scripts/validate-neck-guard-envelope.py').read_text();ns={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],ns);edge=ns['edge']
ALLOWED=[f'V33 diagonal brow receiver {s} {i}'for s in(-1,1)for i in range(3)]+[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
def screen():
 dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(','):continue
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices) for q in m.loop_triangles];e.to_mesh_clear()
  if not v:continue
  bounds=[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)];items.append((o.name,o.parent.name,o.name in ALLOWED,v,t,bounds,BVHTree.FromPolygons(v,t,all_triangles=True)))
 assert sum(a[2] for a in items) ==12;rows=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if not(a[2] or b[2])  or any(a[5][k][1]<b[5][k][0] or b[5][k][1]<a[5][k][0] for k in range(3)):continue
   for ia,ib in a[6].overlap(b[6]):
    ta=[a[3][j] for j in a[4][ia]];tb=[b[3][j] for j in b[4][ib]]
    if any(edge(ta[k],ta[(k+1)%3],tb) or edge(tb[k],tb[(k+1)%3],ta) for k in range(3)):
     rows.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'firstTrianglePair':[ia,ib],'witnessTriangles':[[list(p) for p in ta],[list(p) for p in tb]]});break
 return rows
def seat_report():
 dg=bpy.context.evaluated_depsgraph_get();rows=[]
 def tree(o):
  e=o.evaluated_get(dg);m=e.to_mesh();t=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return t
 for side in (-1,1):
  lens=bpy.data.objects[f'V31 Advanced optical aperture {side}'];cup=bpy.data.objects[f'V31 optic recessed receiving cup {side}'];lip=bpy.data.objects[f'V33 recessed optic retaining lip {side}'];wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];points=[lens.matrix_world@v.co for v in lens.data.vertices];ct=tree(cup);dist=[ct.find_nearest(p)[3] for p in points];cpts=[cup.matrix_world@v.co for v in cup.data.vertices];lpts=[lip.matrix_world@v.co for v in lip.data.vertices]
  rows.append({'side':side,'apertureActualVertices':len(points),'lensActualXBounds':[min(abs(p.x) for p in points),max(abs(p.x) for p in points)],'cupActualXBounds':[min(abs(p.x) for p in cpts),max(abs(p.x) for p in cpts)],'retainingLipActualXBounds':[min(abs(p.x) for p in lpts),max(abs(p.x) for p in lpts)],'actualLensVertexToCupSurfaceDistanceMinMaxM':[min(dist),max(dist)],'lipOuterMinusLensOuterM':max(abs(p.x) for p in lpts)-max(abs(p.x) for p in points),'method':'Actual finite exported-owner source vertices + native BVH nearest cup surface; not attachment acceptance or axial stock proof'})
  wt=tree(wall)
  for i in range(3):
   root=bpy.data.objects[f'V31 temporal fitting root {side} {i}'];pts=[root.matrix_world@v.co for v in root.data.vertices];lo=min(abs(p.x) for p in pts);hi=max(abs(p.x) for p in pts)
   for label,x in [('retainedReturn',lo),('mountSeat',hi)]:
    section=[p for p in pts if abs(abs(p.x)-x)<1e-6];point=sum(section,Vector())/len(section);hit=wt.find_nearest(point);rows.append({'root':root.name,'section':label,'actualFiniteSectionCenter':list(point),'wallNearestSurfacePoint':list(hit[0]),'wallNearestSurfaceDistanceM':hit[3]})
 return rows
reports=[]
POSES=[('rest',0,0,0),('jaw-half',.16,0,0),('jaw-extreme',.32,0,0),('cover-half',0,.5,0),('cover-open',0,1,0),('cover-separate-half',0,1,.5),('cover-separate-full',0,1,1)]
for label,path in [('baseline',base),('candidate',candidate)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));jaw=bpy.data.objects['jaw'];rest=jaw.matrix_basis.copy();cover=bpy.data.objects['cranial-cover'];cr=cover.matrix_basis.copy();bowl=bpy.data.objects['V32 formed mandibular bowl'];meta=json.loads(jaw['makerControlSocketV1']);q=meta['point'];local=Vector((q[0],-q[2],q[1]));actual=bowl.data.vertices[397].co.copy();sock={'metadata':meta,'sourceVertex397BowlLocal':list(actual),'bowlLocalMatrix':[list(r) for r in bowl.matrix_local],'jawLocalMatrix':[list(r) for r in jaw.matrix_local]};seats=seat_report();rows=[]
 for name,angle,opened,separation in POSES:
  jaw.matrix_basis=rest@Matrix.Rotation(angle,4,'X');cover.matrix_basis=cr.copy();cover.matrix_basis.translation.z+=opened*.08+separation*.14;bpy.context.view_layer.update();pairs=screen();socket_now=jaw.matrix_world@local;actual_now=bowl.matrix_world@actual;rows.append({'pose':name,'jawRadians':angle,'coverOpen':opened,'coverSeparation':separation,'pairs':pairs,'actualSocketVertexDistanceM':(actual_now-socket_now).length});print(label,name,len(pairs),flush=True)
 reports.append({'label':label,'nativeSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'makerSocketActualBowlFootprint':sock,'actualSeatSurfaces':seats,'poses':rows})
key=lambda p:tuple(sorted((p['a'],p['b'])));delta=[]
for a,b in zip(reports[0]['poses'],reports[1]['poses']):
 old={key(p) for p in a['pairs']};new={key(p) for p in b['pairs']};delta.append({'pose':a['pose'],'baselinePairs':len(old),'candidatePairs':len(new),'introducedPairs':sorted(new-old),'removedPairs':sorted(old-new),'retainedPairs':sorted(new&old)})
assert reports[0]['makerSocketActualBowlFootprint']==reports[1]['makerSocketActualBowlFootprint'];assert all(q['actualSocketVertexDistanceM']<1e-6 for r in reports for q in r['poses'])
out.write_text(json.dumps({'status':'Scoped actual finite-surface diagnostic; review every introduced/retained pair','models':reports,'delta':delta,'makerSocket':'PASS actual397/localmetadata/matrices exact, surface error below1e-6m','predicate':'Unchanged1e-7m plane /1e-6 edge/barycentric; first witness per unordered pair','limits':['Actual12 changed vs full Builder-eligible finite mesh pool; same-owner head joins included and reported, no ownership hiding.','Seven jaw/cap opening/separation samples; cranial lift runtime+.08m open,+.14m separation. Other exploded owners not reproduced because outside changed head scope.','Native BVH nearest finite seat distances are not stock/attachment/fabrication approval.','No containment, continuous sweep, physics, actual browser certification or universal clearance.']},indent=2)+'\n')
