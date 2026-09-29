from pathlib import Path
import bpy,hashlib,json,runpy,shutil
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v32/regional-studies/cranial-frame/coarse01'
BASE=ROOT/'assets/models/whole-character-v31/attempt-form02/murderbird-whole-character-v31.blend';SHA='81280c2a7103bc3b85603a5fd108daab5e337842f6a7f7c8e298be5049e07e2a';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE)==SHA;assert not OUT.exists();OUT.mkdir(parents=True)
for src,name in [(Path(__file__),'executed-builder.py'),(ROOT/'scripts/regions/whole-character-v32-cranial-frame.py','executed-region.py'),(ROOT/'scripts/build-uncaged-alignment-v7.py','executed-snapshot-helper.py')]:shutil.copy2(src,OUT/name)
h=runpy.run_path(str(OUT/'executed-snapshot-helper.py'));bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
result=runpy.run_path(str(OUT/'executed-region.py'))['apply']();after=h['scene_snapshot']();assert before['empties']==after['empties'];assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
assert set(before['meshes'])==set(after['meshes']);changed=sorted(n for n in before['meshes'] if before['meshes'][n]!=after['meshes'][n]);assert changed==sorted(result['changedMeshes'])
for n in changed:
 assert before['meshes'][n]['parent']==after['meshes'][n]['parent'];assert before['meshes'][n]['matrix']==after['meshes'][n]['matrix'];assert before['meshes'][n]['materials']==after['meshes'][n]['materials'];assert before['meshes'][n]['props']==after['meshes'][n]['props']
native=OUT/'murderbird-v32-cranial-frame.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'Bounded passive frame candidate; screening pending','base':{'path':str(BASE.relative_to(ROOT)),'sha256':SHA},'native':{'path':str(native.relative_to(ROOT)),'sha256':sha(native)},'sourceSHA256':sha(OUT/'executed-region.py'),'result':result,'checks':{'outsideMeshesExact':len(before['meshes'])-len(changed),'allEmptyNodesExact':True,'allMeshTransformsExact':True,'allPropertiesExact':True,'materialsExact':True,'saveReopenExact':True}}
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(BASE)==SHA
print(json.dumps({'nativeSHA256':sha(native),'sourceSHA256':sha(OUT/'executed-region.py'),'checks':receipt['checks']}),flush=True)
