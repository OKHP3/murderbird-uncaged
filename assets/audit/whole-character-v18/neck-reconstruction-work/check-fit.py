from pathlib import Path
import sys,runpy,json,hashlib,bpy
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[4]
H=runpy.run_path(str(ROOT/'scripts/diagnose-native-regional-clearance.py'),run_name='surface_helpers')
K=runpy.run_path(str(ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'),run_name='strict_kernel')
p=sys.argv[sys.argv.index('--')+1:];attempt=p[0]
N=ROOT/f'assets/models/whole-character-v18/attempt-{attempt}/murderbird-whole-character-v18.blend'
P=ROOT/'assets/audit/whole-character-v17/attempt-02/runtime-poses/pose-snapshot.json'
R=ROOT/f'assets/audit/whole-character-v18/attempt-{attempt}/receipt.json'
O=ROOT/f'assets/audit/whole-character-v18/attempt-{attempt}/neck-strict-clearance';assert not O.exists();O.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)=='1964918661da857878376ff95457f3b8e0bc73479bd83225a8419fb1e2a627f9'
subjects=json.loads(R.read_text())['changedMeshes']
rows=[]
for variant,native in [('base',ROOT/'assets/models/whole-character-v17/attempt-02/murderbird-whole-character-v17.blend'),('study',N)]:
 bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
 meshes={o.name:o for o in bpy.data.objects if o.type=='MESH'}
 targets=[o for o in meshes.values() if o.parent and o.parent.name in ['body','breastplate','neck','cervical-upper','left-wing','right-wing','left-wing-shield','right-wing-shield']]
 for pose in json.loads(P.read_text())['poses']:
  pr={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
  for name in sorted(pivots,key=lambda n:H['depth'](pivots[n])):
   pivots[name].matrix_world=H['converted'](pr[name]['worldMatrix']);bpy.context.view_layer.update()
  err=max(H['error'](pivots[n].matrix_world,H['converted'](pr[n]['worldMatrix'])) for n in pivots);assert err<2e-6
  dg=bpy.context.evaluated_depsgraph_get();cache={};pairs=[];seen=set();tested=0
  for sn in subjects:
   for target in targets:
    subject=meshes[sn]
    if subject==target or subject.parent==target.parent:continue
    pair=tuple(sorted([sn,target.name]))
    if pair in seen:continue
    seen.add(pair);tested+=1
    for name in pair:
     if name not in cache:cache[name]=H['surface'](meshes[name],dg)
    a,b=cache[sn],cache[target.name]
    if not H['bounds_overlap'](a,b):continue
    overlap=a['tree'].overlap(b['tree'])
    if not overlap:continue
    proof=K['proper_crossing_receipt'](a,b,overlap,Matrix.Identity(4),Matrix.Identity(4))
    crossing=bool(proof['confirmedSubjectTriangleCount'] or proof['confirmedTargetTriangleCount'])
    pairs.append({'subject':sn,'target':target.name,'strictCrossing':crossing,'broadphaseCandidates':len(overlap),'proof':proof if crossing else None})
  row={'variant':variant,'poseId':pose['id'],'matrixMaxError':err,'testedDifferentOwnerPairs':tested,'pairs':pairs}
  rows.append(row);print(variant,pose['id'],sum(p['strictCrossing'] for p in pairs),flush=True)
result={'native':{'path':str(N.relative_to(ROOT)),'sha256':sha(N)},'poses':{'path':str(P.relative_to(ROOT)),'sha256':sha(P)},'checker':{'path':str(Path(__file__).relative_to(ROOT)),'sha256':sha(Path(__file__))},'changedMeshes':subjects,'targetOwners':['body','breastplate','neck','cervical-upper','left-wing','right-wing','left-wing-shield','right-wing-shield'],'rows':rows,'limits':['Discrete surface crossings only; no full containment, penetration depth, continuous sweep or physical certification.','Same direct-owner assembly mating pairs excluded; no acceptance of their engineering is implied.','This regional comparison does not resolve inherited unrelated crossings.']}
(O/'strict-clearance.json').write_text(json.dumps(result,indent=2)+'\n')
