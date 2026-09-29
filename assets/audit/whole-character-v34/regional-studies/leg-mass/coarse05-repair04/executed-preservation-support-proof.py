from pathlib import Path
import bpy,bmesh,runpy,json,hashlib
from mathutils import Vector
A=Path(__file__).parent;R=A.parents[5];B=R/'assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.blend';N=R/'assets/models/whole-character-v34/regional-studies/leg-mass/coarse05-repair04/murderbird-v34-leg-mass.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((A/'receipt.json').read_text());assert sha(N)==d['native']['sha256'];assert sha(B)==d['base']['sha256']
h=runpy.run_path(str(A/'executed-focused-joint-screen.py').replace('executed-focused-joint-screen.py','../input-inspection/does-not-exist.py')) if False else None
# Reuse exact actual matrix installation helper without running its report/render loop.
s=(A/'executed-focused-joint-screen.py').read_text();ns={};exec(compile(s[:s.index("result={'scope'")],str(A/'executed-focused-joint-screen.py'),'exec'),ns)
changed=set(d['result']['changedMeshes']);bpy.ops.wm.open_mainfile(filepath=str(N));dg=bpy.context.evaluated_depsgraph_get();finite=[]
for name in sorted(changed):
 o=bpy.data.objects[name];ev=o.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);v=bm.calc_volume(signed=True);closed=all(e.is_manifold for e in bm.edges);good=all(__import__('math').isfinite(c) for x in bm.verts for c in x.co);bm.free();ev.to_mesh_clear();assert closed and good and v>0,(name,closed,v)
 finite.append({'name':name,'rigidOwner':o.parent.name,'evaluatedFiniteClosedPositiveVolumeM3':v})
def support():
 dg=bpy.context.evaluated_depsgraph_get();out={}
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.name in changed:continue
  if not any(x in o.parent.name for x in ('foot','toe','digit')):continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();v=[ev.matrix_world@x.co for x in me.vertices];ev.to_mesh_clear()
  if not v:continue
  out[o.name]={'owner':o.parent.name,'minimumZ':min(x.z for x in v),'bounds':[[min(x[k] for x in v),max(x[k] for x in v)] for k in range(3)]}
 return out
poses=[]
for pose in ns['POSE_DATA']['poses']:
 ns['screen'](B,pose);before=support();ns['screen'](N,pose);after=support();assert before==after,pose['id']
 poses.append({'pose':pose['id'],'protectedFootToeDigitMeshCount':len(before),'evaluatedBoundsAndMinimumZExact':True,'maximumBoundsDeltaM':0,'perMesh':before})
(A/'preservation-support-proof.json').write_text(json.dumps({'nativeSHA256':sha(N),'baseSHA256':sha(B),'sourceSHA256':sha(Path(__file__)),'actualPoseFileSHA256':ns['sha'](ns['POSE_PATH']),'evaluatedFiniteClosedChangedSolids':finite,'protectedGroundSupportGeometrySamples':poses,'limitations':['Same actual10 discrete poses and original grounding transforms; unchanged contact geometry does not prove balance, physics or continuous motion.','No source motion, support controller or ground-contact digit edit.']},indent=2)+'\n')
print('evaluated finite closed positive',len(finite),'protected support meshes',len(poses[0]['perMesh']),'exact poses',len(poses),flush=True)
