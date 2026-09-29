"""Write-once runtime02: repair only coincident raw tips of two breast laminas.
No artistic or motion change; no source, prior native, material or pivot overwrite.
"""
from pathlib import Path
import bpy,bmesh,runpy,json,hashlib,math
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/whole-character-v20/attempt-runtime01/murderbird-whole-character-v20.blend'
EXPECTED='44883b9e4477b7b7b292c1e5020c5ee358bbf5743c60e47e8bbe20bf0f25d602'
AUDIT=ROOT/'assets/audit/whole-character-v20/attempt-runtime02';MODEL=ROOT/'assets/models/whole-character-v20/attempt-runtime02';NATIVE=MODEL/'murderbird-whole-character-v20.blend'
TARGETS=('V17 breast directional lamina 3 1 left','V17 breast directional lamina 3 1 right');TOLERANCE=1e-8

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
assert sha(BASE)==EXPECTED and not MODEL.exists() and not(AUDIT/'repair-receipt.json').exists() and not(AUDIT/'executed-repair.py').exists()
AUDIT.mkdir(parents=True,exist_ok=True);MODEL.mkdir(parents=True)
with (AUDIT/'executed-repair.py').open('xb') as out:out.write(Path(__file__).read_bytes())
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'));bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();nodeprops={o.name:h['id_properties'](o) for o in bpy.data.objects if o.type=='EMPTY'};materials={m.name:h['material_signature'](m) for m in bpy.data.materials};layout=bpy.data.objects['body']['mechanismLayoutV1']

def evaluated_checks():
 dg=bpy.context.evaluated_depsgraph_get();out=[]
 for o in list(bpy.data.objects):
  if o.type!='MESH':continue
  e=o.evaluated_get(dg);m=e.to_mesh();nonfinite=[v.index for v in m.vertices if not all(math.isfinite(x) for x in v.co)];c=m.copy();repairs=c.validate();bpy.data.meshes.remove(c)
  r={'name':o.name,'vertices':len(m.vertices),'faces':len(m.polygons),'nonfiniteVertices':nonfinite,'validationRepairedDisposableCopy':bool(repairs)}
  if o.name in TARGETS:
   bm=bmesh.new();bm.from_mesh(m);r.update({'nonmanifoldEdges':sum(not ed.is_manifold for ed in bm.edges),'boundaryEdges':sum(ed.is_boundary for ed in bm.edges),'wireEdges':sum(ed.is_wire for ed in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)});bm.free()
  out.append(r);e.to_mesh_clear()
 return out

pre_eval=evaluated_checks();repairs=[]
for name in TARGETS:
 o=bpy.data.objects[name];mesh=o.data;bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table();oldn={'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces)}
 # Union only coincident source vertices, with the explicitly authorized tolerance.
 parent=list(range(len(bm.verts)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 vv=list(bm.verts)
 for i,a in enumerate(vv):
  for j in range(i+1,len(vv)):
   if (a.co-vv[j].co).length<=TOLERANCE:parent[root(j)]=root(i)
 groups={}
 for i in range(len(vv)):groups.setdefault(root(i),[]).append(i)
 groups=[ids for ids in groups.values() if len(ids)>1];assert groups,'Expected inherited coincident tip absent'
 witness=[{'indices':ids,'coordinates':[list(vv[i].co) for i in ids],'maxSeparationM':max((vv[i].co-vv[j].co).length for i in ids for j in ids)} for ids in groups]
 selected=[vv[i] for ids in groups for i in ids];bmesh.ops.remove_doubles(bm,verts=selected,dist=TOLERANCE)
 # Remove only resulting collapsed tip faces, if any remain after exact welding.
 collapsed=[f for f in bm.faces if f.calc_area()<=TOLERANCE*TOLERANCE]
 if collapsed:bmesh.ops.delete(bm,geom=collapsed,context='FACES')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));newn={'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces)}
 bm.to_mesh(mesh);bm.free();mesh.update()
 repairs.append({'name':name,'owner':o.parent.name,'rawBefore':oldn,'rawAfter':newn,'coincidentGroups':witness,'removedResidualCollapsedFaces':len(collapsed),'finiteModifiersRetained':h['modifier_signature'](o)})

bpy.context.view_layer.update();after=h['scene_snapshot']();post_eval=evaluated_checks()
assert before['empties']==after['empties'] and before['curves']==after['curves']
assert set(before['meshes'])==set(after['meshes']) and len(after['meshes'])==744
changed=[n for n in before['meshes'] if before['meshes'][n]!=after['meshes'][n]];assert set(changed)==set(TARGETS)
for n in TARGETS:
 assert before['meshes'][n]['matrix']==after['meshes'][n]['matrix'] and before['meshes'][n]['props']==after['meshes'][n]['props'] and before['meshes'][n]['modifiers']==after['meshes'][n]['modifiers']
assert nodeprops=={o.name:h['id_properties'](o) for o in bpy.data.objects if o.type=='EMPTY'}
assert materials=={m.name:h['material_signature'](m) for m in bpy.data.materials}
assert layout==bpy.data.objects['body']['mechanismLayoutV1']
assert all(not r['nonfiniteVertices'] and not r['validationRepairedDisposableCopy'] for r in post_eval)
for r in post_eval:
 if r['name'] in TARGETS:assert r['nonmanifoldEdges']==0 and math.isfinite(r['signedVolumeM3']) and r['signedVolumeM3']>0
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(NATIVE));assert h['scene_snapshot']()==after and nodeprops=={o.name:h['id_properties'](o) for o in bpy.data.objects if o.type=='EMPTY'} and layout==bpy.data.objects['body']['mechanismLayoutV1'];assert sha(BASE)==EXPECTED
# Strict JSON avoids encoding nonfinite pre-repair volume as NaN.
def clean(v):
 if isinstance(v,float) and not math.isfinite(v):return 'nonfinite'
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
 if isinstance(v,list):return [clean(x) for x in v]
 return v
receipt={'status':'technical two-lamina coincident-tip repair; no artistic, motion or engineering acceptance','base':artifact(BASE),'native':artifact(NATIVE),'executedRepair':artifact(AUDIT/'executed-repair.py'),'toleranceM':TOLERANCE,'repairs':repairs,'changedMeshes':changed,'checks':{'allEvaluatedMeshesFinite':len(post_eval),'allEvaluatedValidateWithoutRepair':len(post_eval),'targetClosedPositiveVolumeCount':2,'rigidRestSnapshotsExact':len(before['empties']),'otherMeshSnapshotsExact':len(before['meshes'])-2,'curvesExact':len(before['curves']),'materialsExact':True,'allNodePropertiesExact':True,'mechanismLayoutSaveReopenExact':True,'saveReopenSnapshotExact':True,'baseUnchanged':True},'evaluatedBefore':pre_eval,'evaluatedAfter':post_eval,'limits':['This repairs the inherited NaN-generating tip degeneracy only.','Other finite near-zero triangles, source-surface parity and existing motion/likeness holds remain separate checks.']}
(AUDIT/'repair-receipt.json').write_text(json.dumps(clean(receipt),indent=2,allow_nan=False));print(json.dumps({'native':receipt['native'],'checks':receipt['checks'],'repairCounts':[{'name':r['name'],'before':r['rawBefore'],'after':r['rawAfter']} for r in repairs]},indent=2))
