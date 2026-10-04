from pathlib import Path
import bpy, json, importlib.util
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('head',ROOT/'scripts/cg-supervised-head-neck.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
checks={}
for era in ('maker','mechanic'):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/cinematic-cg-milestone02b/murderbird-cg-2b-builder.blend'))
    mod.apply(bpy.context.scene,ROOT,era)
    values={o.name:o.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and o.get('surfaceRole')=='optic' and o.get('cg1cRegion')=='head'}
    assert values and all(v==0 for v in values.values());checks[era]={'opticEmissions':values,'darkOpticCheck':'PASS','render':'NOT RUN'}
bpy.ops.wm.open_mainfile(filepath=str(OUT/'murderbird-supervised-head01.blend'))
new=[o for o in bpy.context.scene.objects if o.get('cgSupervisedHead01')]
assert len(new)==151
assert all(o.type=='MESH' and o.data.uv_layers and len(o.data.vertices)>0 for o in new)
checks['nativeReload']={'status':'PASS','newMeshes':len(new),'explicitUVs':'PASS','visible':sum(not o.hide_render for o in new)}
(OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print('HEAD01_CHECKS_PASS')
