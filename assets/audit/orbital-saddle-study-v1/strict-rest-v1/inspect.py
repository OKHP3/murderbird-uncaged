from pathlib import Path
import bpy,runpy,json,hashlib
from mathutils import Matrix
R=Path.cwd();A=R/'assets/audit/orbital-saddle-study-v1/strict-rest-v1'
D=R/'scripts/diagnose-native-regional-clearance.py'
K=R/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
N=R/'assets/models/uncaged-orbital-saddle-study-v1/murderbird-orbital-saddle-study-v1.blend'
def art(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
assert art(N)['sha256']=='288c2bd755761c72ff6a1d002e7ed8d61ae93caa147a3a063dfa8c0b155d952f'
h=runpy.run_path(str(D),run_name='helper');k=runpy.run_path(str(K),run_name='kernel')
bpy.ops.wm.open_mainfile(filepath=str(N));deps=bpy.context.evaluated_depsgraph_get()
r=json.loads((A.parent/'movement-screen-v1/native-clearance-comparison.json').read_text());pairs=r['reports']['study']['poses'][0]['pairsWithOverlapCandidates']
results=[]
for pair in pairs:
 a,b=[bpy.data.objects[pair[key]] for key in ['subject','target']];sa,sb=h['surface'](a,deps),h['surface'](b,deps)
 overlaps=sa['tree'].overlap(sb['tree']);proof=k['proper_crossing_receipt'](sa,sb,overlaps,Matrix.Identity(4),Matrix.Identity(4))
 results.append({'subject':a.name,'target':b.name,'proof':proof,'nativeVertexCounts':[len(a.data.vertices),len(b.data.vertices)]})
(A/'receipt.json').write_text(json.dumps({'native':art(N),'diagnostic':art(D),'kernel':art(K),'inspectionSource':art(Path(__file__)),'scope':'Strict rest-only confirmation of prior different-owner candidates. No full containment or moving seam proof.','results':results},indent=2)+'\n')
print(json.dumps([{'pair':[p['subject'],p['target']],'vertices':p['nativeVertexCounts'],'strict':p['proof']['confirmedSubjectTriangleCount'],'bounds':p['proof']['subjectCrossingRestWorldBoundsNativeXYZ']} for p in results]))
