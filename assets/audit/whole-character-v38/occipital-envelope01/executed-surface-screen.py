# Occipital-envelope01: same18 watch source/candidate; full head/cervical neighbor pool.
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists()
code=(ROOT/'scripts/validate-neck-guard-envelope.py').read_text();ns={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],ns);edge=ns['edge']
ALLOWED=['V31 fixed temporal receiving wall -1', 'V31 fixed temporal receiving wall 1', 'V38 compact cranial inner shell', 'V38 fixed occipital closure plate', 'V33 swept temporal leaf -1 0', 'V33 swept temporal leaf -1 1', 'V33 swept temporal leaf -1 2', 'V33 swept temporal leaf -1 3', 'V33 swept temporal leaf -1 4', 'V33 swept temporal leaf -1 5', 'V33 swept temporal leaf -1 6', 'V33 swept temporal leaf 1 0', 'V33 swept temporal leaf 1 1', 'V33 swept temporal leaf 1 2', 'V33 swept temporal leaf 1 3', 'V33 swept temporal leaf 1 4', 'V33 swept temporal leaf 1 5', 'V33 swept temporal leaf 1 6']
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
 assert sum(a[2] for a in items) ==18;rows=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if not(a[2] or b[2])  or any(a[5][k][1]<b[5][k][0] or b[5][k][1]<a[5][k][0] for k in range(3)):continue
   for ia,ib in a[6].overlap(b[6]):
    ta=[a[3][j] for j in a[4][ia]];tb=[b[3][j] for j in b[4][ib]]
    if any(edge(ta[k],ta[(k+1)%3],tb) or edge(tb[k],tb[(k+1)%3],ta) for k in range(3)):
     rows.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'firstTrianglePair':[ia,ib],'witnessTriangles':[[list(p) for p in ta],[list(p) for p in tb]]});break
 return rows
reports=[]
POSES=[('rest',0,0,0,0,0,0),('jaw-016',0,0,0,.16,0,0),('jaw-032',0,0,0,.32,0,0),('maker-neck-turn',-.14,-.45,0,.32,0,0),('contact-neck',.65,0,-.731,.10,0,0),('cover-open',0,0,0,0,1,0),('cover-open-separated',0,0,0,0,1,1)]
for label,path in [('baseline',base),('candidate',candidate)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));jaw=bpy.data.objects['jaw'];rest=jaw.matrix_basis.copy();cover=bpy.data.objects['cranial-cover'];cr=cover.matrix_basis.copy();bowl=bpy.data.objects['V32 formed mandibular bowl'];meta=json.loads(jaw['makerControlSocketV1']);q=meta['point'];local=Vector((q[0],-q[2],q[1]));actual=min(bowl.data.vertices,key=lambda v:((bowl.matrix_world@v.co)-(jaw.matrix_world@local)).length).co.copy();sock={'metadata':meta,'actualSocketBowlVertexLocal':list(actual),'bowlLocalMatrix':[list(r) for r in bowl.matrix_local],'jawLocalMatrix':[list(r) for r in jaw.matrix_local]};seats=[];rows=[];exec(code[code.index('CHAIN='):code.index('def inside(')],globals())
 for name,pitch,yaw,head_angle,angle,opened,separation in POSES:
  pose((name,pitch,yaw,head_angle,angle));cover.matrix_basis=cr.copy();cover.matrix_basis.translation.z+=opened*.08+separation*.14;bpy.context.view_layer.update();pairs=screen();socket_now=jaw.matrix_world@local;actual_now=bowl.matrix_world@actual;rows.append({'pose':name,'neckPitch':pitch,'neckYaw':yaw,'headRelativePitch':head_angle,'jawRadians':angle,'coverOpen':opened,'coverSeparation':separation,'pairs':pairs,'actualSocketVertexDistanceM':(actual_now-socket_now).length});print(label,name,len(pairs),flush=True)

 reports.append({'label':label,'nativeSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'makerSocketActualBowlFootprint':sock,'actualSeatSurfaces':seats,'poses':rows})
key=lambda p:tuple(sorted((p['a'],p['b'])));delta=[]
for a,b in zip(reports[0]['poses'],reports[1]['poses']):
 old={key(p) for p in a['pairs']};new={key(p) for p in b['pairs']};delta.append({'pose':a['pose'],'baselinePairs':len(old),'candidatePairs':len(new),'introducedPairs':sorted(new-old),'removedPairs':sorted(old-new),'retainedPairs':sorted(new&old)})
for index,delta_row in enumerate(delta):
 keys=set(map(tuple,delta_row['introducedPairs']));delta_row['introducedWitnesses']=[q for q in reports[1]['poses'][index]['pairs']if key(q)in keys]
for model in reports:
 for row in model['poses']:row['pairs']=[{'a':q['a'],'b':q['b'],'owners':q['owners'],'firstTrianglePair':q['firstTrianglePair']}for q in row['pairs']]
a,b=[r['makerSocketActualBowlFootprint'] for r in reports];assert a['metadata']==b['metadata'] and a['bowlLocalMatrix']==b['bowlLocalMatrix'] and a['jawLocalMatrix']==b['jawLocalMatrix'];assert (Vector(a['actualSocketBowlVertexLocal'])-Vector(b['actualSocketBowlVertexLocal'])).length<3e-7;assert all(q['actualSocketVertexDistanceM']<1e-6 for r in reports for q in r['poses'])
out.write_text(json.dumps({'status':'Scoped actual finite-surface diagnostic; review every introduced/retained pair','models':reports,'delta':delta,'makerSocket':'PASS actual actual source socket physical footprint retained with new topology/index, localmetadata/matrices exact; saved mesh point error below3e-7m and sampled socket distance below1e-6m','predicate':'Unchanged1e-7m plane /1e-6 edge/barycentric; first witness per unordered pair','limits':['Actual18 watched vs full Builder-eligible finite head/cervical subtree pool; same-owner jaw/head joins included and reported, no ownership hiding.','Seven declared actual-chain neck/contact and cap opening/separation samples; cranial lift runtime+.08m open,+.14m separation. Other exploded owners not reproduced because outside changed head scope.','Native BVH nearest finite seat distances are not stock/attachment/fabrication approval.','No containment, continuous sweep, physics, actual browser certification or universal clearance.']},indent=2)+'\n')
