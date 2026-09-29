from pathlib import Path
import bpy,runpy,json,hashlib
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
O=R/'assets/audit/whole-character-v27/checkpoint-verification'
H=runpy.run_path(str(R/'scripts/build-uncaged-alignment-v7.py'))
a=R/'assets/audit/whole-character-v27/head-studies/attempt03/cranial-wrap.blend'
b=R/'assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(a)=='e9599d5d3926f16db9c379d138df23ff5f1a0e48ac82e91cc09e7303520757b6'
assert sha(b)=='3014ae3156f552716fcd34437b9ace9d567092ff4b99d3a3ded2e6f8bde66ceb'
bpy.ops.wm.open_mainfile(filepath=str(a));sa=H['scene_snapshot']();ma={m.name:H['material_signature'](m) for m in bpy.data.materials}
bpy.ops.wm.open_mainfile(filepath=str(b));sb=H['scene_snapshot']();mb={m.name:H['material_signature'](m) for m in bpy.data.materials}
assert sa==sb,'Integrated native differs from strict-screened regional native'
assert ma==mb
result={'status':'PASS exact native scene snapshot parity; no new continuous collision claim',
'regionalNativeSHA256':sha(a),'integratedNativeSHA256':sha(b),
'checks':{'allMeshSnapshotsExact':len(sa['meshes']),'allNamedNodesExact':len(sa['empties']),'materialDefinitionsExact':True},
'consequence':'Regional discrete head opening/jaw screen applies to identical integrated geometry and assembly rests. It remains the same bounded five-pose test, not an independently repeated sweep.'}
(O/'integrated-parity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
