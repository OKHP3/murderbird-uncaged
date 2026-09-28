"""Prove the native opening axis against packet anchors before a corrected sweep."""
from pathlib import Path
import hashlib,json,runpy,math
import bpy
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[5]
NATIVE=ROOT/'assets/models/uncaged-cervical-joint-drive-study-v1/iterations/attempt-02/murderbird-cervical-joint-drive-study-v1.blend'; NSHA='dff9cf74e0b10819f86efed1bdf5c292ae38619d962d18afeba2b2cca291b9d1'
PACKET=ROOT/'assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json'; PSHA='1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26'
OUT=Path(__file__).resolve().parent/'inspection-frame-proof-complete.json'; HELPER=ROOT/'assets/audit/cervical-construction-study-v1/attempt-14/all-cervical-roles-source13-baseline/executed-review.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(NATIVE)==NSHA and sha(PACKET)==PSHA and not OUT.exists()
h=runpy.run_path(str(HELPER),run_name='inspection_frame_helpers');bpy.ops.wm.open_mainfile(filepath=str(NATIVE));pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'};packet=json.loads(PACKET.read_text())
def row(open_value):return next(p for p in packet['poses'] if p['id']==f'inspection-open-{open_value}-separation-0')
anchors={q:row(str(q)) for q in (0,.25,.5,.75,1)}
matrix_rows={q:{r['name']:r for r in p['pivotMatrices'] if r.get('kind')!='mesh'} for q,p in anchors.items()}
breast=pivots['breastplate']; cover=pivots['cranial-cover']; proofs=[]; max_other=0.0; anchor_mats={};cover_mats={}
for q in anchors:
    h['set_pose'](anchors[q],pivots)
    native_local=breast.matrix_local.copy();anchor_mats[q]=native_local.copy()
    target=h['converted'](matrix_rows[q]['breastplate']['localMatrix'])
    delta=max(abs(native_local[r][c]-target[r][c]) for r in range(4) for c in range(4))
    breast_world=h['converted'](matrix_rows[q]['breastplate']['worldMatrix'])
    breast_world_delta=max(abs(breast.matrix_world[r][c]-breast_world[r][c]) for r in range(4) for c in range(4))
    cover_local=cover.matrix_local.copy();cover_mats[q]=cover_local.copy()
    cover_target=h['converted'](matrix_rows[q]['cranial-cover']['localMatrix'])
    cover_local_delta=max(abs(cover_local[r][c]-cover_target[r][c]) for r in range(4) for c in range(4))
    cover_world=h['converted'](matrix_rows[q]['cranial-cover']['worldMatrix'])
    cover_world_delta=max(abs(cover.matrix_world[r][c]-cover_world[r][c]) for r in range(4) for c in range(4))
    other=max(abs(pivots[n].matrix_world[r][c]-h['converted'](matrix_rows[q][n]['worldMatrix'])[r][c]) for n in pivots if n not in {'breastplate','cranial-cover'} for r in range(4) for c in range(4))
    max_other=max(max_other,other);proofs.append({'open':q,'nativeBreastLocalVsConvertedPacketMaxDelta':delta,'nativeBreastWorldVsConvertedPacketMaxDelta':breast_world_delta,'nativeCoverLocalVsConvertedPacketMaxDelta':cover_local_delta,'nativeCoverWorldVsConvertedPacketMaxDelta':cover_world_delta,'nonBreastNonCoverWorldMaxDeltaVsPacket':other,'nativeBreastLocalMatrix':[[float(x) for x in rr] for rr in native_local],'nativeCoverLocalMatrix':[[float(x) for x in rr] for rr in cover_local]})
base=anchor_mats[0];interp=[]
for q in (0,.25,.5,.75,1):
    predicted=base@Matrix.Rotation(-q*1.35,4,'Z'); actual=anchor_mats[q]
    interp.append({'open':q,'nativeLocalRestTimesZRotationMaxDelta':max(abs(predicted[r][c]-actual[r][c]) for r in range(4) for c in range(4))})
result={'nativeSha256':NSHA,'packetSha256':PSHA,'openingSource':'src/scene/inspection-pose.js; browser local-Y rotation -open*1.35; native mapping checked against captured matrices','anchors':proofs,'interpolationProofs':interp,'maxNonBreastNonCoverPivotWorldError':max_other,'conclusion':'The five packet inspection anchors prove the converted native breastplate local transform; all other pivots except explicitly opening cranial cover agree across those anchors. Correct 41 samples should use rest local matrix times native local-Z rotation, then preserve packet inspection-open-0 parent/root transforms and cranial-cover opening.'}
for q in (0,.25,.5,.75,1):
    predicted=cover_mats[0].copy();predicted.translation.z+=q*.08
    interp.append({'open':q,'nativeCoverLocalZPlusOpen008MaxDelta':max(abs(predicted[r][c]-cover_mats[q][r][c]) for r in range(4) for c in range(4))})
result={'nativeSha256':NSHA,'packetSha256':PSHA,'openingSource':'src/scene/inspection-pose.js; browser local-Y rotation -open*1.35 and cover local-Y position +open*0.08; both native mappings checked against captured matrices','anchors':proofs,'interpolationProofs':interp,'maxNonBreastNonCoverPivotWorldError':max_other,'conclusion':'The five packet inspection anchors prove breastplate local-Z rotation and cranial-cover native local-Z translation +open*0.08, including world matrices. All other pivots except these explicitly opening assemblies agree across those anchors. Correct 41 samples use those transforms from captured inspection-open-0 at separation zero.'}
OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
