import bpy,runpy,json,hashlib,shutil,math,bmesh
from pathlib import Path
R=Path.cwd();A=R/'assets/audit/whole-character-v37/regional-studies/foot-assembly/attempt03';O=R/'assets/models/whole-character-v37/regional-studies/foot-assembly/attempt03'
assert not A.exists() and not O.exists();A.mkdir();O.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((R/'assets/audit/whole-character-v37/regional-studies/foot-assembly/attempt02-final/receipt.json').read_text());base=R/prior['native']['path'];assert sha(base)==prior['native']['sha256']
module=R/'scripts/regions/whole-character-v37-foot-assembly.py';shutil.copy2(module,A/'executed-region.py')
h=runpy.run_path(str(R/'scripts/build-uncaged-alignment-v7.py'));bpy.ops.wm.open_mainfile(filepath=str(base));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
revision=runpy.run_path(str(module))['apply_receiving_revision']();after=h['scene_snapshot']();changed=set(revision['changedMeshes'])
assert set(before['meshes'])==set(after['meshes']);assert before['empties']==after['empties']
for n,v in before['meshes'].items():
 if n not in changed:assert v==after['meshes'][n],n
assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
# Connectivity is tested on designed stock adjacency, not certified material.
# Raw meshes retain separate closed stock volumes and disclose all overlaps.
stock=[]
for n in sorted(changed):
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
 assert boundary==0 and nonmanifold==0,n
 stock.append({'name':n,'finite':all(math.isfinite(c) for v in o.data.vertices for c in v.co),'boundaryEdges':boundary,'nonmanifoldEdges':nonmanifold,'rawClosedStockVolumes':True,'booleanUnionValidated':False,'stockContactGraph':'Designed annular collar/cheek and web volumes meet or overlap at fixed fabrication seats; geometric connected-material proof separately recorded, not inferred from closed components.'})
native=O/'murderbird-v37-foot-assembly.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
result=prior['result'];result['receivingSeatRevision']=revision
for row in result['changedFootMeshes']:
 o=bpy.data.objects[row['name']];pts=[o.matrix_world@v.co for v in o.data.vertices];row['worldBounds']=[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)]
receipt={'status':'targeted receiving construction proposal; pending strict screen','base':prior['base'],'receivingRevisionBase':prior['native'],'native':{'path':str(native.relative_to(R)),'sha256':sha(native),'bytes':native.stat().st_size},'module':{'path':str(module.relative_to(R)),'sha256':sha(module)},'result':result,'checks':{'unrelatedMeshesExactToAttempt02Final':len(before['meshes'])-len(changed),'allNodeSnapshotsExactToAttempt02Final':len(before['empties']),'materialsExact':True,'saveReopenExact':True,'targetedMeshes':len(changed),'closedStockMeshes':stock}}
(A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt['native']))
objects=[o for o in bpy.data.objects if o.type in {'EMPTY','MESH'} and not o.get('authoringGuide')];dg=bpy.context.evaluated_depsgraph_get()
for o in objects:
 if o.type=='MESH':o.data=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);o.modifiers.clear()
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.hide_set(False);o.hide_viewport=False;o.select_set(True)
glb=A/'evaluation-only.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
(A/'evaluation-glb-receipt.json').write_text(json.dumps({'path':str(glb.relative_to(R)),'sha256':sha(glb),'purpose':'fresh actual node-pose sampling only; not application export'},indent=2)+'\n')
