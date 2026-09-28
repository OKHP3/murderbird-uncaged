"""Compose bounded v4 regional refinements from the preserved v3 native source.

Every rest joint is retained. Neutral materials expose shape changes. Each
recorded generated iteration is preserved before replacement; manually edited
outputs are never overwritten. Source illustrations are not dimensional data.
"""
from pathlib import Path
import ast
import hashlib
import json
import math
import shutil
import bpy
import bmesh
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/models/uncaged-alignment-v4'
AUDIT=ROOT/'assets/audit/alignment-v4'
BASE=ROOT/'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.blend'
BASE_SHA='6de7c16728ac2ac4926b9b0bd608d7eb5e03f702d3e1ef222db997c84fd7ff3a'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(BASE)==BASE_SHA,'Preserved v3 native source changed; reconcile first.'
OUT.mkdir(parents=True,exist_ok=True)
receipt=OUT/'alignment-inventory.json'
if receipt.exists():
    previous=json.loads(receipt.read_text())
    for item in previous['generatedFiles']:
        path=ROOT/item['path']
        assert not path.exists() or sha(path)==item['sha256'],f'Preserve manually edited output in a new native version first: {path}'
    model_record=next(item for item in previous['generatedFiles'] if item['path'].endswith('.glb'))
    iteration=model_record['sha256'][:12]
    for source_dir in [OUT,AUDIT]:
        if not source_dir.exists():continue
        destination=source_dir/'iterations'/iteration
        destination.mkdir(parents=True,exist_ok=True)
        for path in source_dir.iterdir():
            if path.is_file() and not path.name.startswith('.'):
                target=destination/path.name
                assert not target.exists() or sha(target)==sha(path),f'Existing iteration differs: {target}'
                if not target.exists():shutil.copy2(path,target)
        generated_sources=source_dir/'generation-source'
        if generated_sources.is_dir():
            for path in generated_sources.iterdir():
                target=destination/'generation-source'/path.name
                target.parent.mkdir(parents=True,exist_ok=True)
                assert not target.exists() or sha(target)==sha(path),f'Existing source iteration differs: {target}'
                if not target.exists():shutil.copy2(path,target)

bpy.ops.wm.open_mainfile(filepath=str(BASE))
bpy.context.scene.frame_set(1)
for obj in bpy.data.objects:obj.animation_data_clear()
for action in list(bpy.data.actions):bpy.data.actions.remove(action)
bpy.context.view_layer.update()
original_pivots={obj.name:list(obj.location) for obj in bpy.data.objects if obj.type=='EMPTY'}
for obj in bpy.data.objects:
    if obj.type=='EMPTY':assert (obj.scale-Vector((1,1,1))).length<1e-7,obj.name
ALL='maker,mechanic,builder'
parts=[]
mat={name:bpy.data.materials['Neutral / '+name] for name in ['plate','edge','frame','recess','bearing','repair','optic','inner']}
for filename,names in [
    ('build-uncaged-presence-study.py',{'material','group','mesh','bevel','rod','ring','tube'}),
    ('build-uncaged-neutral-v2.py',{'under','tag','wm','wr','wt','mix','sample','envelope','polygon_surface','patch','shell','fastener','curve'}),
    ('build-uncaged-alignment-v3.py',{'control','smooth_profile','side_plate'}),
]:
    tree=ast.parse((ROOT/'scripts'/filename).read_text())
    functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
    assert len(functions)==len(names),(filename,names-{node.name for node in functions})
    exec(compile(ast.Module(body=functions,type_ignores=[]),filename,'exec'))
head=bpy.data.objects['head'];crown=bpy.data.objects['cranial-cover'];bill=bpy.data.objects['upper-bill'];jaw=bpy.data.objects['jaw']
neck=bpy.data.objects['neck'];breast=bpy.data.objects['breastplate'];body=bpy.data.objects['body']
base_inventory=json.loads((BASE.parent/'alignment-inventory.json').read_text())
# Retain cervical curves with the unchanged cervical meshes. The regional
# workers replace the other controls together with their matching geometry.
control_records=[item for item in base_inventory['controls'] if item['owner']=='neck']
for obj in list(bpy.data.objects):
    if obj.type=='CURVE' and (not obj.parent or obj.parent.name!='neck'):bpy.data.objects.remove(obj,do_unlink=True)
controls=bpy.data.collections.new('Alignment v4 regional profiles')
bpy.context.scene.collection.children.link(controls)
for filename in ['alignment-v4-head.py','alignment-v4-body.py','alignment-v4-neck.py']:
    path=ROOT/'scripts'/filename
    exec(compile(path.read_text(),str(path),'exec'))
normalized_scales=[]
max_rest_bake_error=0.0

# Contact landmark records an actual bill vertex before export transformations.
bpy.context.view_layer.update()
vertices=[o.matrix_world@v.co for o in bpy.data.objects if o.type=='MESH' and under(o,bill) for v in o.data.vertices]
contact=bpy.data.objects['bill-contact'];point=min(vertices,key=lambda p:p.y)
contact.parent=bill;contact.matrix_parent_inverse=Matrix.Identity(4);contact.location=bill.matrix_world.inverted()@point
bpy.context.view_layer.update()
contact_world=list(contact.matrix_world.translation)
for o in bpy.data.objects:
    if o.type=='EMPTY' and o.name in original_pivots and o.name!='bill-contact':
        assert (o.location-Vector(original_pivots[o.name])).length<1e-7,o.name

# Preserve actual independent mesh pieces in native source; batch only export.
for o in list(bpy.context.scene.objects):
    if o.type!='MESH':continue
    bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    bm=bmesh.new();bm.from_mesh(o.data)
    bad=[f for f in bm.faces if f.calc_area()<1e-12]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
parts=[{'name':o.name,'parent':o.parent.name,'region':o.get('region','back'),'role':o.get('surfaceRole','frame'),'eras':o.get('exteriorEras',ALL).split(','),'class':o.get('constructionClass','inherited-passive')} for o in bpy.context.scene.objects if o.type=='MESH']
pivots=[{'name':o.name,'parent':o.parent.name if o.parent else None,'local':list(o.location),'world':list(o.matrix_world.translation),'scale':list(o.scale)} for o in bpy.context.scene.objects if o.type=='EMPTY']
root=bpy.data.objects['murderbird'];root['status']='alignment-v4 geometry and articulation candidate; owner likeness review pending'
head.rotation_euler.z=0
for frame,angle in [(1,0),(16,.12),(31,0)]:head.rotation_euler.z=angle;head.keyframe_insert(data_path='rotation_euler',frame=frame)
head.animation_data.action.name='attention-export-proof';bpy.context.scene.frame_set(1)
bpy.context.preferences.filepaths.save_version=0
blend=OUT/'murderbird-alignment-v4.blend';pending=OUT/'.building-alignment.blend';bpy.ops.wm.save_as_mainfile(filepath=str(pending));pending.replace(blend)
groups={}
for o in list(bpy.context.scene.objects):
    if o.type=='MESH':groups.setdefault((o.parent,o.get('exteriorEras',ALL),o.get('region','back'),o.get('surfaceRole','frame')),[]).append(o)
for (parent,eras,reg,role),objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=f'{parent.name}-{reg}-{role}';o['exteriorEras']=eras;o['region']=reg;o['surfaceRole']=role
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type in {'MESH','EMPTY'}:o.select_set(True)
model=OUT/'murderbird-alignment-v4.glb';pending=OUT/'.building-alignment.glb'
bpy.ops.export_scene.gltf(filepath=str(pending),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=True,export_animation_mode='ACTIONS',export_frame_range=True);pending.replace(model)
manifest={'status':'neutral geometry proposal awaiting owner review','startingRevision':'3e6d340e616e79708d2a62ec9255fd997d14ea4f','base':{'path':str(BASE.relative_to(ROOT)),'sha256':BASE_SHA},'conventions':'metres; X anatomical left, -Y forward, Z up; authored dimensions, not source metrology','parts':parts,'pivots':pivots,'billContact':contact_world,'billContactSpace':'Blender world at rest before export axis conversion','controls':control_records,'sourceReferences':json.loads((ROOT/'assets/models/uncaged-neutral-v2/reference-packet.json').read_text()),'restTransformNormalization':{'inheritedFrom':'alignment-v3','newScaleBakePerformed':False,'allRestJointWorldPositionsPreserved':True},'jointContract':'V3 rigid joint transforms preserved except the bill-contact surface landmark. Inherited unit scales retained; +X opens mandible downward. Individual digit owners remain independent.','limits':['Hidden construction remains proposed','V10 chronology retained provisionally, not owner-approved','No purposeful supported claw grip or physical simulation established','No final surface or likeness acceptance'],'generatedFiles':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [blend,model]]}
generation_sources=OUT/'generation-source';generation_sources.mkdir(exist_ok=True)
for filename in ['build-uncaged-alignment-v4.py','alignment-v4-head.py','alignment-v4-body.py','alignment-v4-neck.py']:
    path=generation_sources/filename;shutil.copy2(ROOT/'scripts'/filename,path)
    manifest['generatedFiles'].append({'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':sha(path)})
manifest['inheritedHelperSources']=[{'path':'scripts/'+filename,'sha256':sha(ROOT/'scripts'/filename)} for filename in ['build-uncaged-presence-study.py','build-uncaged-neutral-v2.py','build-uncaged-alignment-v3.py']]
receipt.write_text(json.dumps(manifest,indent=2)+'\n')
print('ALIGNMENT_V4_SAVED',len(parts),'pieces',len(control_records),'editable curves',sha(model))
