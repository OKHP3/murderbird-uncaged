"""Read-only changed36 actual surfaces, unchanged strict predicate, five openings."""
import bpy,json,sys,hashlib,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists()
kernel=ROOT/'scripts/validate-neck-guard-envelope.py';code=kernel.read_text();namespace={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],namespace);edge=namespace['edge']
RECEIVERS=[]
NAMES=[f'V34 formed breast course {r} plate {c}'for r,n in[(1,5),(2,6)]for c in range(1,n+1)]
opening=ROOT/'scripts/check-v19-breast-opening.py';helper=runpy.run_path(str(opening));reports=[]
def surfaces():
 dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(','):continue
  selected=o.name in NAMES
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices) for q in m.loop_triangles];e.to_mesh_clear()
  if not v:continue
  b=[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)];items.append((o.name,o.parent.name,selected,v,t,b,BVHTree.FromPolygons(v,t,all_triangles=True)))
 assert sum(q[2] for q in items)==11;return items
def screen():
 items=surfaces();rows=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if not(a[2] or b[2]) or any(a[5][k][1]<b[5][k][0] or b[5][k][1]<a[5][k][0] for k in range(3)):continue
   for ia,ib in a[6].overlap(b[6]):
    ta=[a[3][j] for j in a[4][ia]];tb=[b[3][j] for j in b[4][ib]]
    if any(edge(ta[k],ta[(k+1)%3],tb) or edge(tb[k],tb[(k+1)%3],ta) for k in range(3)):
     rows.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'sameBodyOwner':a[1]==b[1],'modifiedReceiverInPair':a[0] in RECEIVERS or b[0] in RECEIVERS,'firstTrianglePair':[ia,ib],'witnessTriangles':[[list(p) for p in ta],[list(p) for p in tb]]});break
 return rows
def adjacency():
 result=[];dg=bpy.context.evaluated_depsgraph_get()
 for side in (-1,1):
  tab=bpy.data.objects[f'V30 breast liner receiving tab {side}'];pts=[tab.matrix_world@v.co for v in tab.data.vertices]
  for label,point,target in [('return',sum(pts[:8],Vector())/8,bpy.data.objects[f'V23 breast moving return {side}']),('liner',sum(pts[16:24],Vector())/8,bpy.data.objects['V30 continuous tapered breast liner'])]:
   e=target.evaluated_get(dg);m=e.to_mesh();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();hit=tree.find_nearest(point)
   result.append({'tab':tab.name,'section':label,'sectionCenter':list(point),'target':target.name,'nearestSurfaceDistanceM':hit[3],'nearestSurfacePoint':list(hit[0])})
 return result
from mathutils import Quaternion
poseCode=kernel.read_text();poseCode=poseCode[poseCode.index('CHAIN='):poseCode.index('def inside(')]
for label,path in [('baseline',base),('candidate',candidate)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));exec(poseCode,globals());p=bpy.data.objects['breastplate'];c=bpy.data.objects['cranial-cover'];rest=p.matrix_local.copy();cr=c.matrix_local.copy();axis=p.get('inspectionAxis');radians=p.get('inspectionOpenRadians');rows=[]
 for fraction in [0,.25,.5,.75,1]:
  helper['set_runtime_open'](p,c,rest,cr,fraction,axis,radians);pairs=screen();rows.append({'pose':'cover-open-'+str(fraction),'pairs':pairs});print(label,rows[-1]['pose'],len(pairs),flush=True)
 helper['set_runtime_open'](p,c,rest,cr,0,axis,radians)
 for state in [STATES[1],STATES[3]]:
  pose(state);pairs=screen();rows.append({'pose':state[0],'angles':list(state[1:]),'pairs':pairs});print(label,state[0],len(pairs),flush=True)
 reports.append({'label':label,'nativeSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'samples':rows})
def key(p):return tuple(sorted([p['a'],p['b']]))
delta=[]
for a,b in zip(reports[0]['samples'],reports[1]['samples']):
 old={key(p)for p in a['pairs']};new={key(p)for p in b['pairs']};delta.append({'pose':a['pose'],'baselinePairs':len(old),'candidatePairs':len(new),'introducedPairs':sorted(new-old),'retainedPairs':sorted(new&old),'removedPairs':sorted(old-new)})
out.write_text(json.dumps({'status':'Changed11 finite surface diagnostic, same-owner contacts included','scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'predicateSourceSha256':hashlib.sha256(kernel.read_bytes()).hexdigest(),'models':reports,'delta':delta,'limits':['Actual changed11 vs full Builder-eligible finite pool, including sameowner liner/laps; source/candidate exact selection.','Strict1e-7m plane and1e-6 edge/barycentric margins unchanged; first witness per pair not solidpenetration depth.','Five exact cover hinge opening samples separation0; actual fixedlength chain Maker/contact neck samples; no continuous motion/containment/loading proof.','Existing liner/frame gap16.25mm WARN untouched; preserved rootvertex band does not establish wholeplate support or all finite stock.']},indent=2)+'\n')
