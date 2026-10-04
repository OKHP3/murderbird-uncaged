"""Restore exact receiving visibility, keeping rejected cassette hidden for inspection."""
import bpy, sys, json, hashlib, importlib.util
from pathlib import Path
root=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('body09',root/'scripts/cg-supervised-body09.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
source=Path(sys.argv[sys.argv.index('--')+1]);folder=Path(__file__).resolve().parent/'attempt02'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
payload={o.name:module.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')}
visibility={o.name:(o.hide_render,o.hide_viewport,o.hide_get()) for o in s.objects}
materials=module.material_digest()
bpy.ops.wm.open_mainfile(filepath=str(folder/'murderbird-body09.blend'));s=bpy.context.scene
for n,state in visibility.items():
 o=s.objects[n];o.hide_render,o.hide_viewport=state[:2];o.hide_set(state[2])
for o in s.objects:
 if o.get('cgSupervisedBody09'):o.hide_render=True;o.hide_set(True)
assert not [n for n,h in payload.items() if module.digest(s.objects[n])!=h]
assert module.material_digest()==materials
file=folder/'murderbird-body09-restored.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(file))
bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene
changed=[n for n,h in payload.items() if module.digest(s.objects[n])!=h]
visibility_changed=[n for n,state in visibility.items() if (s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get())!=state]
assert not changed and not visibility_changed
record=dict(status='REJECTED experiment; exact original visibility restored; new objects hidden',sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),restoredNativeSHA256=hashlib.sha256(file.read_bytes()).hexdigest(),originalObjectsVisibilityChecked=len(visibility),originalMeshEmptyPayloadChecked=len(payload),payloadChanged=changed,originalVisibilityChanged=visibility_changed,newCassetteHidden=[o.name for o in s.objects if o.get('cgSupervisedBody09')],receivingMaterialGraphsPreserved=module.material_digest()==materials)
(folder/'rollback-receipt.json').write_text(json.dumps(record,indent=2)+'\n');print('BODY09_ROLLBACK_COMPLETE',file)
