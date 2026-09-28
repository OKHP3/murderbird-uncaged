import bpy, json, hashlib, os, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path('/Users/okh/.codex/worktrees/uncaged-production/murderbird-uncaged')
BASE_BLEND = ROOT / '.local/alignment-composed-study/inputs/v5-sixth-1e7febcc03d9/murderbird-alignment-v5.blend'
BASE_GLB = ROOT / '.local/alignment-composed-study/inputs/v5-sixth-1e7febcc03d9/murderbird-alignment-v5.glb'
BASE_INVENTORY = ROOT / '.local/alignment-composed-study/inputs/v5-sixth-1e7febcc03d9/alignment-inventory.json'
GUARD_BLEND = ROOT / '.local/alignment-limb-study/v5-fourth-limb-profile-study-05/murderbird-limb-profile-study.blend'
GUARD_MANIFEST = ROOT / '.local/alignment-limb-study/v5-fourth-limb-profile-study-05/manifest.json'
COMBINED_BLEND = ROOT / '.local/alignment-composed-study/combined-guards-talons-02/murderbird-v5-sixth-guard-talon-study.blend'
COMBINED_GLB = ROOT / '.local/alignment-composed-study/combined-guards-talons-02/murderbird-v5-sixth-guard-talon-study.glb'
OUT = ROOT / 'assets/audit/alignment-v5-regional/edge-partition-audit/retained-foot-edge-source.json'

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def digest(path): return {'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':sha(path)}

def require(ok,msg):
    if not ok: raise RuntimeError(msg)

require(Path(bpy.data.filepath).resolve()==BASE_BLEND.resolve(),'Blender did not open the exact frozen base native .blend')
require(sha(BASE_GLB)=='1e7febcc03d9f8d1a644580c8422b124403cf4e5768aa01df747e3d9b6af9f1e','Frozen base GLB hash mismatch')
require(sha(BASE_INVENTORY)=='b9cfaf8cd7681396311d61537d2381ff6ef54f9cdc515c1aa1b77b34bd58beee','Frozen base native inventory hash mismatch')
inv=json.loads(BASE_INVENTORY.read_text())
gm=json.loads(GUARD_MANIFEST.read_text())
removed=set(gm['replacedObjects'])
expected_by_side={}
for side in ('left','right'):
    source=sorted(row['name'] for row in inv['parts'] if row.get('parent')==f'{side}-foot' and row.get('region')=='foot' and row.get('role')=='edge')
    replaced=sorted(name for name in source if name in removed)
    retained=sorted(set(source)-removed)
    expected_replaced=sorted(f'{side} ankle sheath lap rib {station}' for station in ('0.27','0.53','0.78'))
    expected_retained=sorted([f'{side} rear hallux sheath v4',f'{side} recessed axle cap -1.002',f'{side} recessed axle cap 1.002'])
    require(replaced==expected_replaced,f'{side}: exact replaced foot-edge objects differ: {replaced}')
    require(retained==expected_retained,f'{side}: exact retained foot-edge objects differ: {retained}')
    expected_by_side[side]={'allBaseFootEdgeSources':source,'replacedByGuard05':replaced,'retainedNames':retained}

bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
objects=[]
for side in ('left','right'):
  for name in expected_by_side[side]['retainedNames']:
    obj=bpy.data.objects.get(name)
    require(obj is not None and obj.type=='MESH',f'Missing retained source object: {name}')
    require(obj.parent is not None and obj.parent.name==f'{side}-foot',f'Unexpected parent for {name}')
    require(obj.data.users==1,f'Shared mesh datablock on retained source: {name}, users={obj.data.users}')
    require(not obj.hide_viewport and not obj.hide_render and not obj.hide_get() and obj.visible_get(),f'Hidden/invisible retained source object: {name}')
    require(not obj.modifiers,f'Unexpected modifier on retained source object: {name}')
    require(all(abs(float(x)-1.0)<1e-9 for x in obj.scale),f'Non-unit object scale: {name}')
    mesh=obj.data
    mesh.calc_loop_triangles()
    tris=[]
    for tri in mesh.loop_triangles:
      tris.append([list(obj.matrix_world @ mesh.vertices[index].co) for index in tri.vertices])
    materials=[slot.material.name if slot.material else None for slot in obj.material_slots]
    rec={'name':name,'owner':obj.parent.name,'region':obj.get('region'),'surfaceRole':obj.get('surfaceRole'),'exteriorEras':obj.get('exteriorEras'),'dataName':mesh.name,'dataUsers':mesh.users,'visible':obj.visible_get(),'hideViewport':obj.hide_viewport,'hideRender':obj.hide_render,'hideSet':obj.hide_get(),'hideSelect':obj.hide_select,'modifierCount':len(obj.modifiers),'localScale':list(obj.scale),'worldMatrix':[list(row) for row in obj.matrix_world],'vertexCount':len(mesh.vertices),'polygonCount':len(mesh.polygons),'triangleCount':len(tris),'materialNames':materials,'worldTriangleVertices':tris}
    objects.append(rec)

# Capture removed lap-rib counts to document the exact source partition.
replaced_object_stats=[]
for side in ('left','right'):
  for name in expected_by_side[side]['replacedByGuard05']:
    obj=bpy.data.objects.get(name)
    require(obj is not None and obj.type=='MESH',f'Missing replaced lap rib: {name}')
    obj.data.calc_loop_triangles()
    replaced_object_stats.append({'name':name,'owner':obj.parent.name if obj.parent else None,'triangleCount':len(obj.data.loop_triangles),'vertexCount':len(obj.data.vertices),'visible':obj.visible_get(),'hideViewport':obj.hide_viewport,'hideRender':obj.hide_render,'hideSet':obj.hide_get(),'dataUsers':obj.data.users,'modifierCount':len(obj.modifiers)})
# Capture the 51 pivot identities/matrices from the same native file without changing them.
pivots=[]
for obj in sorted((obj for obj in bpy.data.objects if obj.type=='EMPTY'),key=lambda x:x.name):
    pivots.append({'name':obj.name,'worldMatrix':[list(row) for row in obj.matrix_world]})
require(len(pivots)==51,f'Expected 51 original rig pivots, found {len(pivots)}')
script_path=Path(__file__).resolve()
report={'schema':'alignment-regional-retained-foot-edge-source/v1','scope':'Exact source geometry for six retained V5 sixth foot-edge objects only; the six 268-triangle ankle lap ribs are explicitly replaced by guard-study05 and excluded.','auditHelper':digest(script_path),'sourceFiles':{label:digest(path) for label,path in [('baseBlend',BASE_BLEND),('baseGlb',BASE_GLB),('baseInventory',BASE_INVENTORY),('guardStudy05Blend',GUARD_BLEND),('guardStudy05Manifest',GUARD_MANIFEST),('combined02Blend',COMBINED_BLEND),('combined02Glb',COMBINED_GLB)]},'guardReplacementContract':{'guardManifestReplacedObjectCount':len(removed),'footEdgeBySide':expected_by_side},'retainedObjects':objects,'replacedLapRibs':replaced_object_stats,'originalRigPivots':pivots,'checks':{'baseNativeInputExact':True,'baseInventoryExact':True,'retainedObjectsVisibleUnhiddenUnmodifiedUnshared':True,'allSixFootEdgeRibsListedAsReplaced':True,'replacedRibsEach268Triangles':all(row['triangleCount']==268 for row in replaced_object_stats),'originalPivotCount':len(pivots)}}
OUT.write_text(json.dumps(report,indent=2)+'\n')
print('EDGE_PARTITION_JSON='+json.dumps({'output':str(OUT),'retained':[{k:o[k] for k in ('name','owner','triangleCount','vertexCount','materialNames','visible','hideViewport','hideRender','hideSet','dataUsers','modifierCount')} for o in objects],'replaced':replaced_object_stats,'pivotCount':len(pivots),'sourceFiles':report['sourceFiles']}))
