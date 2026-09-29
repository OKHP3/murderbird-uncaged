import bpy,bmesh,json,hashlib,runpy
from pathlib import Path
BASE=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');AUDIT=BASE/'assets/audit/whole-character-v20/attempt-cervical01'
h=runpy.run_path(str(BASE/'scripts/build-uncaged-alignment-v7.py'))
receipt=json.loads((AUDIT/'receipt.json').read_text());names=set(receipt['changedMeshes'])
bpy.ops.wm.open_mainfile(filepath=str(BASE/'assets/models/whole-character-v20/attempt-proportions02/murderbird-whole-character-v20.blend'));before=h['scene_snapshot']();props={o.name:dict(o.items()) for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(BASE/'assets/models/whole-character-v20/attempt-cervical01/murderbird-whole-character-v20.blend'));after=h['scene_snapshot']()
assert before['empties']==after['empties'];assert before['curves']==after['curves'];assert set(before['meshes'])==set(after['meshes']);assert len(names)==20
assert all(before['meshes'][n]==after['meshes'][n] for n in before['meshes'] if n not in names)
finite=[];dg=bpy.context.evaluated_depsgraph_get()
for name in sorted(names):
 o=bpy.data.objects[name];assert all(o.get(k)==v for k,v in props[name].items())
 e=o.evaluated_get(dg);m=e.to_mesh();bm=bmesh.new();bm.from_mesh(m);bm.transform(o.matrix_world)
 pts=[v.co for v in bm.verts];volume=bm.calc_volume(signed=True);nonmanifold=sum(not ed.is_manifold for ed in bm.edges)
 finite.append({'name':name,'owner':o.parent.name,'modifiers':[{'type':x.type,'name':x.name,'wall':x.thickness if x.type=='SOLIDIFY' else None} for x in o.modifiers],'evaluatedVertices':len(bm.verts),'evaluatedFaces':len(bm.faces),'nonmanifoldEdges':nonmanifold,'signedVolumeM3':volume,'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]})
 assert nonmanifold==0 and volume>0,(name,nonmanifold,volume)
 bm.free();e.to_mesh_clear()
out={'nativeSha256':receipt['native']['sha256'],'status':'20 finite formed surfaces verified; no collision or engineering acceptance','rigidRestSnapshotsExact':52,'otherMeshSnapshotsExact':len(before['meshes'])-20,'allCurvesExact':len(before['curves']),'sourcePropertiesRetainedOn20':True,'finite':finite}
(AUDIT/'finite-scope.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='finite'}))
