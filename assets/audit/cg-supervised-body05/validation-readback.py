import bpy,json,hashlib,importlib.util
from pathlib import Path
root=Path('/Users/okh/.codex/worktrees/cg-supervised-curved-body05/murderbird-uncaged');out=root/'assets/audit/cg-supervised-body05/attempt02'
spec=importlib.util.spec_from_file_location('body05',root/'scripts/cg-supervised-body05.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def prop(o):
 return {k:(v.to_list() if hasattr(v,'to_list') else v.to_dict() if hasattr(v,'to_dict') else v) for k,v in o.items()}
source=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/integration04/murderbird-supervised-builder.blend')
bpy.ops.wm.open_mainfile(filepath=str(source));base={o.name:m.digest(o) for o in bpy.context.scene.objects if o.type in ('MESH','EMPTY')};props={o.name:prop(o) for o in bpy.context.scene.objects if o.type in ('MESH','EMPTY')}
bpy.ops.wm.open_mainfile(filepath=str(out/'murderbird-body05.blend'));s=bpy.context.scene
changed=[n for n,d in base.items() if m.digest(s.objects[n])!=d];changedprops=[n for n,d in props.items() if prop(s.objects[n])!=d]
valid={'head-armor','breast-armor','wing-armor','forged-steel','machined-steel','worn-bronze','black-iron','protected-optic','protected-glass'};fail=[];routes=0
for o in s.objects:
 if o.type!='MESH' or not o.get('cgSupervisedBody05'):continue
 families=json.loads(o['cgSurfaceFamilies']);routes+=len(families)
 if len(families)!=len(o.data.materials) or any(f not in valid for f in families) or any(p.material_index>=len(families) for p in o.data.polygons):fail.append(o.name)
r=json.loads((out/'receipt.json').read_text());pairs=[]
for view in ('whole-clay','whole-pbr','body-grazing-clay','front-clay','side-clay','body-pbr'):
 if r['cameras']['before-'+view]!=r['cameras']['after-'+view]:pairs.append(view)
assert not changed and not changedprops and not fail and not pairs,(changed,changedprops,fail,pairs)
result={'receivingObjectsPreserved':len(base),'geometryUVFaceIndicesMaterialSlotsTransforms':'PASS','receivingCustomProperties':'PASS','orderedSurfaceFamilies':'PASS','newSlotsChecked':routes,'sameCameraAndLightPairs':'PASS','sameCameraPairsChecked':6,'nativeReadback':'PASS','originalInputSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'finalNativeSHA256':hashlib.sha256((out/'murderbird-body05.blend').read_bytes()).hexdigest(),'scriptSHA256':hashlib.sha256((root/'scripts/cg-supervised-body05.py').read_bytes()).hexdigest(),'limits':['Surface gaps and overlap are design targets, not measured final distances','Receiving head and stance preserved; visual match unaccepted','No browser/runtime/CI/deployment or three-era finish check']}
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
