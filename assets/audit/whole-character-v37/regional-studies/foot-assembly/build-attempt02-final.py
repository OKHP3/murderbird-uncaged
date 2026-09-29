import bpy,runpy,json,hashlib,shutil
from pathlib import Path
R=Path.cwd();A=R/'assets/audit/whole-character-v37/regional-studies/foot-assembly/attempt02-final';O=R/'assets/models/whole-character-v37/regional-studies/foot-assembly/attempt02-final'
assert not A.exists() and not O.exists();A.mkdir();O.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=R/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend';assert sha(base)=='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0'
module=R/'scripts/regions/whole-character-v37-foot-assembly.py';shutil.copy2(module,A/'executed-region.py')
h=runpy.run_path(str(R/'scripts/build-uncaged-alignment-v7.py'))
bpy.ops.wm.open_mainfile(filepath=str(base));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
result=runpy.run_path(str(module))['apply']();after=h['scene_snapshot']()
changed=set(result['changedMeshes']);nodes=set(result['changedNodes'])
assert set(before['meshes'])==set(after['meshes'])
assert set(before['empties'])==set(after['empties'])
for n,v in before['meshes'].items():
 if n not in changed:assert v==after['meshes'][n],n
for n,v in before['empties'].items():
 if n not in nodes:assert v==after['empties'][n],n
assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
native=O/'murderbird-v37-foot-assembly.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'regional reconstruction proposal; awaiting visual and strict motion checks','base':{'path':str(base.relative_to(R)),'sha256':sha(base)},'native':{'path':str(native.relative_to(R)),'sha256':sha(native),'bytes':native.stat().st_size},'module':{'path':str(module.relative_to(R)),'sha256':sha(module)},'result':result,'checks':{'unrelatedMeshesExact':len(before['meshes'])-len(changed),'unrelatedNodesExact':len(before['empties'])-len(nodes),'materialsExact':True,'saveReopenExact':True}}
(A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt['native']));print(json.dumps(result['footEnvelope']))
# Temporary evaluation GLB only, never application integration.
objects=[o for o in bpy.data.objects if o.type in {'EMPTY','MESH'} and not o.get('authoringGuide')]
dg=bpy.context.evaluated_depsgraph_get()
for o in objects:
 if o.type=='MESH':o.data=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);o.modifiers.clear()
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.hide_set(False);o.hide_viewport=False;o.select_set(True)
glb=A/'evaluation-only.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
(A/'evaluation-glb-receipt.json').write_text(json.dumps({'path':str(glb.relative_to(R)),'sha256':sha(glb),'purpose':'fresh actual node pose matrices for bounded regional validation only; not application export or selection'},indent=2)+'\n')
