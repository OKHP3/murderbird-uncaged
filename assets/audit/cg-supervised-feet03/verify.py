"""Read-only saved native preservation and new UV audit."""
import importlib.util,json,math,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('feet03',root/'scripts/cg-supervised-feet03.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
r=json.loads((out/'receipt.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(out/'murderbird-feet03-study.blend'))
s=bpy.context.scene;a=r['application'];changed=[]
for n,d in a['originalPayloadSHA256'].items():
    o=s.objects.get(n)
    if o is None or mod._digest(o)!=d:changed.append(n)
hidden=[n for n in a['hiddenRetainedMeshes'] if not s.objects[n].hide_render]
new=[s.objects[n] for n in a['newMeshes']]
uv_fail=[o.name for o in new if not o.data.uv_layers or any(not math.isfinite(v) for q in o.data.uv_layers[0].data for v in q.uv)]
ankles={o.name:max((o.matrix_world@Vector(c)).z for c in o.bound_box) for o in s.objects if o.name in ('CG1c left ankle concentric hinge','CG1c right ankle concentric hinge')}
upper=max(v.co.z for o in new for v in o.data.vertices)
source=root/'assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'savedNativeSourcePayload':{'status':'PASS' if not changed else 'FAIL','changed':changed,'sourceMeshesAndEmpties':len(a['originalPayloadSHA256'])},
 'supersededVisibility':{'status':'PASS' if not hidden else 'FAIL','stillVisible':hidden,'retainedHiddenCount':len(a['hiddenRetainedMeshes'])},
 'editableFiniteUVs':{'status':'PASS' if not uv_fail else 'FAIL','invalid':uv_fail,'newMeshCount':len(new)},
 'noAboveAnkleGeometry':{'status':'PASS' if upper<=min(ankles.values()) else 'FAIL','newMaximumZ':upper,'sourceAnkleUpperBounds':ankles},
 'inputBinary':{'status':'PASS' if sha(source)==r['nativeInputSHA256'] else 'FAIL','sha256':sha(source)},
 'artisticAcceptance':'NOT CLAIMED','browserAndRuntime':'NOT RUN; development-only native module, integration owns browser validation'}
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert all(q['status']=='PASS' for q in result.values() if isinstance(q,dict) and 'status' in q)
