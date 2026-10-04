"""Read-only FEET14 geometry determinism and exact scope check."""
import hashlib,importlib.util,json,sys
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[3]
inp=Path(sys.argv[sys.argv.index('--input-root')+1]);out=root/'assets/audit/cg-supervised-feet14';
def mod(name):
 s=importlib.util.spec_from_file_location(name,root/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
feet=mod('cg-supervised-feet14.py');exp=mod('cg-supervised-export.py')
manifest=json.loads((inp/'assets/audit/cg-supervised01/feet-macro-diagnosis.json').read_text())['one_authoring_brief']['hide_manifest']['exact_names'];assert set(feet.whitelist())==set(manifest) and len(feet.whitelist())==74
fingerprints={};bounds={};bindings={}
for era,path in {'builder':out/'replicated02/murderbird-feet14.blend','maker':out/'replicated02/era-readback/murderbird-feet14-maker.blend','mechanic':out/'replicated02/era-readback/murderbird-feet14-mechanic.blend'}.items():
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;meshes=[o for o in s.objects if o.get(feet.TAG)];assert len(meshes)==104;fingerprints[era]={o.name:exp._digest_mesh(o.data) for o in meshes};bindings[era]={o.name:[m.name for m in o.data.materials] for o in meshes};vs=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];bounds[era]=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
assert fingerprints['builder']==fingerprints['maker']==fingerprints['mechanic']
bpy.ops.wm.open_mainfile(filepath=str(inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'));result=feet.apply(bpy.context.scene,inp);fresh={o.name:exp._digest_mesh(o.data) for o in bpy.context.scene.objects if o.get(feet.TAG)};assert fresh==fingerprints['builder']
receipt={'exact74HideManifestMatch':True,'threeEraNewGeometryIdentical':True,'freshReceiving06ApplyMatchesSavedGeometry':True,'newGeometryFingerprints':fingerprints['builder'],'threeEraExistingMaterialBindings':bindings,'newBounds':bounds,'designsAttempted':2,'ownerAcceptance':'pending','staticOnly':True};(out/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print('FEET14_SCOPE_DETERMINISM_PASS',flush=True)
