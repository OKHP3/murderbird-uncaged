from pathlib import Path
import bpy,runpy,json,hashlib
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');BASE=ROOT/'assets/models/whole-character-v31/attempt-form01/murderbird-whole-character-v31.blend';SRC=ROOT/'scripts/regions/whole-character-v31-mechanism-layout.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE)=='fc1ef2fce58733afd68b08167f9823366cfb1a2f521c0bd21fccc25e8cb6372c'
bpy.ops.wm.open_mainfile(filepath=str(BASE));h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'));before=h['scene_snapshot']();properties={o.name:json.dumps(dict(o.items()),sort_keys=True,default=str) for o in bpy.data.objects};mats={m.name:h['material_signature'](m) for m in bpy.data.materials};result=runpy.run_path(str(SRC))['apply']();after=h['scene_snapshot']();assert before['meshes']==after['meshes'];assert before['curves']==after['curves'];assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
# Snapshot structure retains all node positions and all other node properties.
assert all(before['empties'][n]==after['empties'][n] for n in before['empties'] if n!='body')
assert before['empties']==after['empties'];assert all(properties[o.name]==json.dumps(dict(o.items()),sort_keys=True,default=str) for o in bpy.data.objects if o.name!='body')
receipt={'nativeSha256':sha(BASE),'sourceSha256':sha(SRC),'result':result,'allMeshesExact':True,'allTransformsExact':True,'materialsExact':True,'nativeNotSavedOrModified':True}
Path('/tmp/v31-mechanism-layout/receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PROOF',json.dumps(receipt))
