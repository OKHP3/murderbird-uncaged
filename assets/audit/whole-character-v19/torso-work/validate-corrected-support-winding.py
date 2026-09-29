import bpy,bmesh,json,runpy,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];source=root/'scripts/regions/whole-character-v19-torso-neck.py'
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.blend'))
r=runpy.run_path(str(source))['apply']();dg=bpy.context.evaluated_depsgraph_get();out=[]
for n in r['added']:
 o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();bm=bmesh.new();bm.from_mesh(m);out.append({'name':n,'signedVolume':bm.calc_volume(signed=True),'nonManifoldEdges':sum(not v.is_manifold for v in bm.edges)});bm.free();e.to_mesh_clear()
j={'status':'PASS' if all(x['signedVolume']>0 and x['nonManifoldEdges']==0 for x in out) else 'FAIL','sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'corrected final regional source applied on pinned V18 base in memory; no native02 rewrite or third shape candidate','supports':out};(root/'assets/audit/whole-character-v19/torso-work/corrected-support-winding.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
