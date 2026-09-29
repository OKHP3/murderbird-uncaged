from pathlib import Path
import hashlib,json,importlib.util
import bpy
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[5]
NATIVE=ROOT/'assets/models/whole-character-v18/attempt-breast-fit08/murderbird-whole-character-v18.blend'
POSES=ROOT/'assets/audit/whole-character-v17/attempt-02/runtime-poses/pose-snapshot.json'
OUT=Path(__file__).resolve().parent
EXPECTED_NATIVE='a4f9ffd68067e14d5ff9e6abf8fc1d1c116d55692381d18673bfd4db5495147c'
EXPECTED_POSES='1964918661da857878376ff95457f3b8e0bc73479bd83225a8419fb1e2a627f9'
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cv(flat):
 m=Matrix([[flat[c*4+r] for c in range(4)] for r in range(4)])
 return C.inverted()@m@C
def depth(o):return 0 if o.parent is None else depth(o.parent)+1
def surface(o,dg):
 e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles()
 pts=[e.matrix_world@v.co for v in m.vertices];faces=[tuple(t.vertices) for t in m.loop_triangles];e.to_mesh_clear()
 if not faces:return None
 return {'tree':BVHTree.FromPolygons(pts,faces,all_triangles=True,epsilon=0.0),'points':pts,'faces':faces,
         'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
def bounds(a,b):return all(a['min'][i]<=b['max'][i] and b['min'][i]<=a['max'][i] for i in range(3))
assert sha(NATIVE)==EXPECTED_NATIVE and sha(POSES)==EXPECTED_POSES
packet=json.loads(POSES.read_text()); hm={p['id']:p for p in packet['poses']}
helper=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
spec=importlib.util.spec_from_file_location('strict_kernel',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE)); piv={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
assert len(piv)==52
meshes={o.name:o for o in bpy.data.objects if o.type=='MESH'}
plates=[n for n in meshes if n.startswith('V17 breast directional lamina 1 ')]
ribs=['Passive rib behind access cover.002','Passive rib behind access cover.003']
guards=[*(f'Cervical flank lamina {s} {i}' for i in (5,6) for s in (-1,1)),*(f'Throat formed lamina {i}' for i in (4,5,6))]
assert len(plates)==8 and all(n in meshes for n in ribs+guards)
pairs=[('Breast inner access shell',n,'shell-vs-rib') for n in ribs]
pairs += [(p,r,'first-course-vs-rib') for p in plates for r in ribs]
pairs += [(p,g,'first-course-vs-lower-neck') for p in plates for g in guards]
rest={n:o.matrix_world.copy() for n,o in meshes.items()}; ident=Matrix.Identity(4); rows=[]
for pose in packet['poses']:
 pr={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
 for name in sorted(piv,key=lambda n:depth(piv[n])):piv[name].matrix_world=cv(pr[name]['worldMatrix'])
 bpy.context.view_layer.update(); err=max(abs(piv[n].matrix_world[r][c]-cv(pr[n]['worldMatrix'])[r][c]) for n in piv for r in range(4) for c in range(4));assert err<2e-6
 dg=bpy.context.evaluated_depsgraph_get();cache={};hits=[]
 for a,b,group in pairs:
  cache.setdefault(a,surface(meshes[a],dg));cache.setdefault(b,surface(meshes[b],dg));sa,sb=cache[a],cache[b]
  if not sa or not sb or not bounds(sa,sb):continue
  ov=sa['tree'].overlap(sb['tree'])
  if not ov:continue
  proof=mod.proper_crossing_receipt(sa,sb,ov,ident,ident)
  hits.append({'group':group,'a':a,'b':b,'ownerA':meshes[a].parent.name if meshes[a].parent else None,'ownerB':meshes[b].parent.name if meshes[b].parent else None,'triangleOverlapCandidates':len(ov),'strictCrossing':proof['confirmedSubjectTriangleCount']>0,'strictSubjectTriangles':proof['confirmedSubjectTriangleCount'],'strictTargetTriangles':proof['confirmedTargetTriangleCount'],'examples':proof['examples'][:2]})
 rows.append({'poseId':pose['id'],'poseMatrixMaxError':err,'candidatePairs':len(hits),'strictPairs':[h for h in hits if h['strictCrossing']]})
result={'status':'Exact discrete V17 runtime-module pose replay on held V18 proposal; strict intersection diagnostic','native':{'path':str(NATIVE.relative_to(ROOT)),'sha256':sha(NATIVE)},'poses':{'path':str(POSES.relative_to(ROOT)),'sha256':sha(POSES),'count':len(packet['poses']),'origin':'fresh Node samples of actual runtime modules, not browser captures'},'scope':{'shellVsRibs':len(ribs),'course1VsRibs':len(plates)*len(ribs),'course1VsLowerNeck':len(plates)*len(guards),'lowerNeckNames':guards},'kernel':{'path':str(helper.relative_to(ROOT)),'sha256':sha(helper),'method':'strict noncoplanar triangle edge-through-face crossing; tangent/coplanar excluded'},'rows':rows,'limits':['Discrete sampled surface intersections only; no continuous sweep or full containment depth.','Candidate V18 retains the V17 rest pivots; runtime actions were not re-sampled against modified geometry.','Strict noncoplanar crossings do not prove supported sliding contact, strength, or likeness.']}
(OUT/'strict-crossings.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'poses':len(rows),'strict_pairs_per_pose':{r['poseId']:len(r['strictPairs']) for r in rows},'output':str(OUT/'strict-crossings.json')}))
