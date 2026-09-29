import bpy,bmesh,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];native=root/'assets/models/whole-character-v19/attempt-torso03/murderbird-whole-character-v19.blend';audit=root/'assets/audit/whole-character-v19/attempt-torso03'
bpy.ops.wm.open_mainfile(filepath=str(native));j=json.loads((audit/'receipt.json').read_text());result=[];dg=bpy.context.evaluated_depsgraph_get()
names=j['addedMeshes']+[g['name'] for g in j['regions'][0]['result']['guards']]
for name in names:
 o=bpy.data.objects[name];e=o.evaluated_get(dg);me=e.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 result.append({'name':name,'owner':o.parent.name,'evaluatedVertices':len(bm.verts),'evaluatedFaces':len(bm.faces),'boundaryEdges':sum(x.is_boundary for x in bm.edges),'nonManifoldEdges':sum(not x.is_manifold for x in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True),'areaM2':sum(f.calc_area() for f in bm.faces)})
 bm.free();e.to_mesh_clear()
out={'native':{'path':str(native.relative_to(root)),'sha256':hashlib.sha256(native.read_bytes()).hexdigest()},'status':'PASS' if all(r['nonManifoldEdges']==0 and abs(r['signedVolumeM3'])>1e-9 for r in result) else 'FAIL','scope':'eight reconstructed lower-neck walls and seven new hinge support meshes; evaluated surface closure only, not clearance/containment/engineering','objects':result}
(audit/'finite-wall-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
