from pathlib import Path
import hashlib,json,runpy,datetime
import bpy
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'assets/models/uncaged-orbital-crown-v14/attempt-04/murderbird-orbital-crown-v14.blend'
EXPECTED='eb599da565c179c59d02176c29dc29e545570805d63b5a9024777890ef011703'
HELPER=ROOT/'scripts/diagnose-native-regional-clearance.py'
KERNEL=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
OUT=ROOT/'assets/audit/uncaged-orbital-crown-v14/attempt-04/brow-underlap-design-v1'
SHELLS=('Rounded swept crown lamina 0','Rounded swept crown lamina 1','Swept temporal lamina -1 0 0','Swept temporal lamina 1 0 0')
BROWS=('Forged orbital brow -1','Forged orbital brow 1')
SCALES=(.85,.70)
LIFTS=(0.0,.02)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert NATIVE.is_file() and sha(NATIVE)==EXPECTED and OUT.is_dir()
 H=runpy.run_path(str(HELPER),run_name='underlap_helpers'); K=runpy.run_path(str(KERNEL),run_name='underlap_kernel')
 surface=H['surface']; overlap_bounds=H['bounds_overlap']; proper=K['proper_crossing_receipt']
 bpy.ops.wm.open_mainfile(filepath=str(NATIVE)); sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
 objs={o.name:o for o in bpy.data.objects}; brows=[objs[n] for n in BROWS];shells=[objs[n] for n in SHELLS];cover=objs['cranial-cover']
 assert len(brows)==2 and len(shells)==4
 orig={b.name:[v.co.copy() for v in b.data.vertices] for b in brows}; world0={b.name:b.matrix_world.copy() for b in brows}; cover0=cover.matrix_world.copy()
 # Apply X compression in world coordinates about the animal sagittal plane X=0; only in memory.
 def set_scale(s):
  for b in brows:
   inv=world0[b.name].inverted()
   for v,co in zip(b.data.vertices,orig[b.name]):
    p=world0[b.name]@co;p.x*=s;v.co=inv@p
   b.data.update()
  bpy.context.view_layer.update()
 records=[]
 for s in SCALES:
  set_scale(s)
  for dz in LIFTS:
   m=cover0.copy();m.translation.z+=dz;cover.matrix_world=m;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
   rows=[]
   for shell in shells:
    a=surface(shell,dg)
    for brow in brows:
     b=surface(brow,dg)
     if not a or not b or not overlap_bounds(a,b):continue
     candidates=a['tree'].overlap(b['tree'])
     if not candidates:continue
     proof=proper(a,b,candidates,Matrix.Identity(4),Matrix.Identity(4))
     strict=bool(proof['confirmedSubjectTriangleCount'] or proof['confirmedTargetTriangleCount'])
     rows.append({'shell':shell.name,'brow':brow.name,'bvhCandidates':len(candidates),'strictNoncoplanarCrossing':strict,'receipt':proof if strict else None})
   records.append({'worldXSagittalCompression':s,'cranialCoverWorldZLiftM':dz,'strictPairCount':sum(r['strictNoncoplanarCrossing'] for r in rows),'pairs':rows})
 # Restore in-memory data and ensure native remains byte-identical.
 for b in brows:
  for v,co in zip(b.data.vertices,orig[b.name]):v.co=co
  b.data.update()
 cover.matrix_world=cover0;bpy.context.view_layer.update()
 out={'schema':'orbital-crown-v14-a04-brow-underlap-trial/v1','native':{'path':str(NATIVE.relative_to(ROOT)),'sha256':sha(NATIVE)},'blender':bpy.app.version_string,
 'method':'Read-only in-memory world-X compression of both fixed brow meshes about sagittal plane X=0; cranial-cover shell then translated +world-Z. Strict noncoplanar edge-through-face receipts follow BVH candidates.',
 'scales':list(SCALES),'liftsM':list(LIFTS),'shells':list(SHELLS),'brows':list(BROWS),'samples':records,
 'limits':['Only four identified shell meshes and two brows were screened.','No full containment, coplanar/tangent proof, penetration depth, continuous sweep, optic/rack check, visual review, or acceptance claim.','No native file was saved or modified.']}
 (OUT/'diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'sha':sha(NATIVE),'results':[{'scale':r['worldXSagittalCompression'],'lift':r['cranialCoverWorldZLiftM'],'strict':r['strictPairCount'],'pairs':[x['shell']+' × '+x['brow'] for x in r['pairs'] if x['strictNoncoplanarCrossing']]} for r in records]},indent=2))
 assert sha(NATIVE)==EXPECTED
main()
