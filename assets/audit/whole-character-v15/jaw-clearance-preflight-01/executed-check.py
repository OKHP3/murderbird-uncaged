"""Read-only nine-position jaw versus actual bill, cheek and optic surfaces."""
from pathlib import Path
import argparse,sys,json,hashlib,runpy,shutil
import bpy
from mathutils import Matrix

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--native',required=True);p.add_argument('--sha',required=True);p.add_argument('--out',required=True)
p.add_argument('--apply-head',action='store_true',help='Preflight current head module on pinned V14, without saving a native')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
native=ROOT/a.native;out=ROOT/a.out
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(native)==a.sha and not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(native))
patch=None
if a.apply_head:
    src=ROOT/'scripts/regions/whole-character-v15-head.py';patch={'path':str(src.relative_to(ROOT)),'sha256':sha(src)}
    runpy.run_path(str(src),run_name='head_preflight')['apply']()
h=runpy.run_path(str(ROOT/'scripts/diagnose-native-regional-clearance.py'),run_name='jaw_surface')
k=runpy.run_path(str(ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'),run_name='jaw_kernel')
fixed=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(('Profiled upper bill blade','Broad swept cheek band','Forged orbital mounting plate')) or o.get('region')=='optic')]
moving=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Forked forged mandible','Distal mandible bridge'))]
assert len(moving)==3 and len(fixed)>=6
rows=[]
for angle in [i*.04 for i in range(9)]:
    bpy.data.objects['jaw'].rotation_euler.x=angle;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    ss={o.name:h['surface'](o,dg) for o in fixed+moving};pairs=[]
    for left in moving:
        for right in fixed:
            u,v=ss[left.name],ss[right.name]
            if not h['bounds_overlap'](u,v):continue
            candidates=u['tree'].overlap(v['tree'])
            if not candidates:continue
            proof=k['proper_crossing_receipt'](u,v,candidates,Matrix.Identity(4),Matrix.Identity(4))
            crossing=bool(proof['confirmedSubjectTriangleCount'] or proof['confirmedTargetTriangleCount'])
            pairs.append({'moving':left.name,'fixed':right.name,'candidateTriangles':len(candidates),'crossing':crossing,'proof':proof if crossing else None})
    rows.append({'jawRadians':angle,'strictCrossingPairs':sum(r['crossing'] for r in pairs),'pairs':pairs})
out.mkdir(parents=True);shutil.copy2(__file__,out/'executed-check.py')
if patch:shutil.copy2(ROOT/patch['path'],out/'executed-head.py')
receipt={'native':{'path':a.native,'sha256':a.sha},'status':'FAIL' if any(r['strictCrossingPairs'] for r in rows) else 'PASS within sampled surface scope','samples':rows,'moving':[o.name for o in moving],'fixed':[o.name for o in fixed],'limits':['Discrete 0 to 0.32 rad samples only.','No containment, continuous collision, stress, physical simulation or artistic acceptance.','No native was saved.']}
receipt['appliedHeadPatch']=patch
(out/'resting-jaw.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(native)==a.sha
print(json.dumps({'status':receipt['status'],'crossingCounts':[r['strictCrossingPairs'] for r in rows]}))
