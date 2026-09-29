"""Write-once V29 GLB from a hash-bound native; evaluate only in memory.

Distinct rigid objects remain distinct mesh nodes. Historical curves are not
exported. This is a review derivative, not model selection or acceptance.
"""
from pathlib import Path
import argparse,sys,hashlib,json,math,struct,shutil
import bpy
ROOT=Path(globals().get('SOURCE_ROOT',Path(__file__).resolve().parents[1]))
p=argparse.ArgumentParser();p.add_argument('--attempt',default='fit01');p.add_argument('--verify-existing',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
AUDIT=ROOT/f'assets/audit/whole-character-v29/attempt-{a.attempt}'
OUT=AUDIT/'export';OUT.mkdir(exist_ok=a.verify_existing)
receipt=json.loads((AUDIT/'receipt.json').read_text());native=ROOT/receipt['native']['path'];glb=native.with_suffix('.glb')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(native)==receipt['native']['sha256'],'Native hash mismatch'
assert glb.exists() if a.verify_existing else not glb.exists(),'GLB existence does not match requested operation'
existingHash=sha(glb) if a.verify_existing else None
source=Path(__file__);frozen=OUT/('executed-validation.py' if a.verify_existing else 'executed-export.py');assert not frozen.exists();shutil.copy2(source,frozen)
bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update()
def plain(props):return json.loads(json.dumps(dict(props),default=lambda value:list(value)))
def material_signature(m):
 return {'name':m.name,'diffuseColor':list(m.diffuse_color),'metallic':m.metallic,'roughness':m.roughness,'useNodes':m.use_nodes,'nodes':[(n.name,n.bl_idname,[(s.name,list(s.default_value) if hasattr(s.default_value,'__len__') and not isinstance(s.default_value,str) else s.default_value) for s in n.inputs if hasattr(s,'default_value')]) for n in m.node_tree.nodes] if m.node_tree else []}
materialsBefore=[material_signature(m) for m in bpy.data.materials]
objects=sorted([o for o in bpy.data.objects if o.type in {'EMPTY','MESH'}],key=lambda o:o.name)
nodes={o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'worldNative':[list(row) for row in o.matrix_world],'extras':plain(o.items())} for o in objects}
meshRecords={};dg=bpy.context.evaluated_depsgraph_get()
# Independent evaluated data copies retain each object's owner and world rest.
# No batching, operators that repair topology or native save are used.
for o in objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);m=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg);m.calc_loop_triangles()
 assert all(math.isfinite(x) for v in m.vertices for x in v.co),o.name
 mats=[mat.name if mat else None for mat in m.materials]
 used=sorted({mats[f.material_index] if f.material_index<len(mats) else None for f in m.polygons},key=lambda v:v or '')
 meshRecords[o.name]={'owner':o.parent.name if o.parent else None,'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'usedMaterials':used,'materialSlots':mats,'evaluatedModifiers':[q.type for q in o.modifiers],'extras':plain(o.items())}
 o.data=m;o.modifiers.clear()
assert materialsBefore==[material_signature(m) for m in bpy.data.materials],'Material definitions changed'
assert nodes=={o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'worldNative':[list(row) for row in o.matrix_world],'extras':plain(o.items())} for o in objects},'Rigid world rests or props changed'
bpy.ops.object.select_all(action='DESELECT')
for o in objects:
 o.hide_set(False);o.hide_viewport=False;o.select_set(True)
if not a.verify_existing:
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
else:assert sha(glb)==existingHash,'Existing GLB modified'
assert sha(native)==receipt['native']['sha256'],'Native modified'
b=glb.read_bytes();assert b[:4]==b'glTF' and struct.unpack_from('<I',b,4)[0]==2 and struct.unpack_from('<I',b,8)[0]==len(b)
length,kind=struct.unpack_from('<II',b,12);assert kind==0x4e4f534a
g=json.loads(b[20:20+length]);binOffset=20+length;binLength,binKind=struct.unpack_from('<II',b,binOffset);assert binKind==0x004e4942;binary=b[binOffset+8:binOffset+8+binLength]
components={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)};sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT2':4,'MAT3':9,'MAT4':16};accessors=[]
for i,ac in enumerate(g.get('accessors',[])):
 assert 'sparse' not in ac,'Sparse accessor requires explicit validation';fmt,width=components[ac['componentType']];count=sizes[ac['type']];bv=g['bufferViews'][ac['bufferView']];stride=bv.get('byteStride',width*count);offset=bv.get('byteOffset',0)+ac.get('byteOffset',0);end=offset+(ac['count']-1)*stride+width*count
 assert end<=bv.get('byteOffset',0)+bv['byteLength']<=len(binary)
 for row in range(ac['count']):assert all(math.isfinite(x) for x in struct.unpack_from('<'+fmt*count,binary,offset+row*stride)),f'accessor{i}'
 accessors.append({'index':i,'count':ac['count'],'type':ac['type'],'componentType':ac['componentType'],'finite':True})
parents={child:i for i,node in enumerate(g['nodes']) for child in node.get('children',[])};byName={node['name']:(i,node) for i,node in enumerate(g['nodes'])}
assert len(byName)==len(g['nodes']),'Duplicate exported node names'
assert set(byName)==set(nodes),'Exported mesh/EMPTY identity set differs'
materialNames={m['name'] for m in g.get('materials',[])};sourceMaterials={m['name'] for m in materialsBefore}
assert materialNames<=sourceMaterials,'Unknown exported material'
for name,record in nodes.items():
 index,node=byName[name];parent=g['nodes'][parents[index]]['name'] if index in parents else None
 assert parent==record['parent'],f'Parent mismatch: {name}'
 for key,value in record['extras'].items():assert node.get('extras',{}).get(key)==value,f'Extra lost: {name}.{key}'
 if record['type']=='MESH':
  assert 'mesh' in node,name;primitives=g['meshes'][node['mesh']]['primitives'];assert all(p.get('mode',4)==4 for p in primitives)
  triangles=sum(g['accessors'][q['indices']]['count']//3 for q in primitives)
  assert triangles==meshRecords[name]['triangles'],f'Triangle parity: {name}'
  names={g['materials'][q['material']]['name'] if 'material' in q else None for q in primitives}
  assert names==set(meshRecords[name]['usedMaterials']),f'Material slots mismatch: {name}'
assert not g.get('animations') and not g.get('cameras') and not g.get('extensions',{}).get('KHR_lights_punctual')
layout=json.loads(byName['body'][1]['extras']['cervicalLayoutV2']);assert all(layout.get(key)==value for key,value in {'schema':1,'pitchJoints':['neck','cervical-mid-a','cervical-mid-b','cervical-upper'],'weights':[.25,.25,.25,.25],'rootYaw':'neck','headOwner':'head'}.items())
result={'status':'review GLB derivative; not selected or accepted','native':receipt['native'],'glb':{'path':str(glb.relative_to(ROOT)),'sha256':sha(glb),'bytes':glb.stat().st_size},'exporter':{'path':str((OUT/'executed-export.py').relative_to(ROOT)),'sha256':sha(OUT/'executed-export.py')},'validator':{'path':str(frozen.relative_to(ROOT)),'sha256':sha(frozen)},'validationOnly':a.verify_existing,'counts':{'meshObjects':len(meshRecords),'emptyObjects':len(objects)-len(meshRecords),'glbNodes':len(g['nodes']),'glbMeshes':len(g['meshes']),'accessors':len(accessors),'triangles':sum(m['triangles'] for m in meshRecords.values()),'materials':len(materialNames)},'checks':{'nativeUnmodified':True,'exactNamesAndParenting':True,'extrasPreserved':True,'meshTriangleCountsPreserved':True,'evaluatedModifiersInIndependentCopies':True,'allAccessorsFinite':True,'materialDefinitionsUnmodifiedAndPrimitiveAssignmentsPreserved':True,'noCamerasLightsAnimations':True},'cervicalLayoutV2':layout,'contactAdjustments':receipt['contactAdjustments'],'limits':['Node/geometry/material identity export validation only; no armor clearance, engineering, appearance or owner acceptance.','Historical CURVE geometry excluded by explicit mesh/EMPTY selection.','Actual GLTFLoader joint validation is separate.']}
(OUT/'native-export-input.json').write_text(json.dumps({'nodes':nodes,'meshes':meshRecords,'materials':materialsBefore},indent=2)+'\n');(OUT/'accessors.json').write_text(json.dumps(accessors,indent=2)+'\n');(OUT/'export-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('EXPORT_RECEIPT',json.dumps(result))
