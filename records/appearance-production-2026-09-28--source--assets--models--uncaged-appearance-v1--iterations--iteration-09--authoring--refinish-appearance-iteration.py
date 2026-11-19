"""Create a new appearance iteration by refinishing frozen, verified geometry.

No geometry is rebuilt. A before/after digest verifies every mesh position,
face and object transform. The parent iteration and both authoring scripts
remain bound by hashes in the new inventory; prior files are never replaced.
"""
from pathlib import Path
import argparse, copy, hashlib, json, re, runpy, shutil, struct, sys
import bpy

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source-iteration',required=True);p.add_argument('--iteration',required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
for value in (args.source_iteration,args.iteration):
    assert re.fullmatch(r'iteration-\d+',value),value
assert args.iteration!=args.source_iteration
base=ROOT/'assets/models/uncaged-appearance-v1/iterations'/args.source_iteration
out=base.parent/args.iteration
assert not out.exists(),'Preserve prior iteration'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((base/'appearance-inventory.json').read_text())
source=base/'murderbird-appearance.blend'
source_sha=sha(source)
assert source_sha==next(f['sha256'] for f in record['generatedFiles'] if f['path'].endswith('.blend'))
bpy.ops.wm.open_mainfile(filepath=str(source))

def geometry_digest():
    digest=hashlib.sha256()
    for obj in sorted(bpy.context.scene.objects,key=lambda o:o.name):
        digest.update((obj.name+'|'+(obj.parent.name if obj.parent else '')).encode())
        digest.update(struct.pack('<16d',*(v for row in obj.matrix_local for v in row)))
        if obj.type=='MESH':
            for vertex in obj.data.vertices:digest.update(struct.pack('<3d',*vertex.co))
            for polygon in obj.data.polygons:
                digest.update(struct.pack('<I',len(polygon.vertices)))
                digest.update(struct.pack('<'+'I'*len(polygon.vertices),*polygon.vertices))
    return digest.hexdigest()

before=geometry_digest()
old_images={image.name:image for image in bpy.data.images if image.name.startswith('appearance-')}
module=runpy.run_path(str(ROOT/'scripts/appearance-materials.py'))
finish=module['build']({})
replaced=[]
for new_image in finish['textures']:
    original_name=re.sub(r'\.\d{3}$','',new_image.name)
    assert original_name in old_images,original_name
    old=old_images[original_name]
    old.user_remap(new_image)
    bpy.data.images.remove(old)
    new_image.name=original_name
    replaced.append(original_name)
assert len(replaced)==9
rebound=[]
for obj in list(bpy.context.scene.objects):
    if obj.type!='MESH' or not obj.data.materials:continue
    desired=module['_resolve_role'](obj)
    current=obj.data.materials[0].get('appearanceRole')
    if current!=desired:
        finish['assign'](obj,obj.get('exteriorEras'),role=desired)
        rebound.append({'part':obj.name,'from':current,'to':desired})
after=geometry_digest()
assert before==after,'Material work altered retained geometry or hierarchy'
out.mkdir(parents=True)
snapshot=out/'authoring';snapshot.mkdir()
scripts=['refinish-appearance-iteration.py','appearance-materials.py']
for name in scripts:shutil.copy2(ROOT/'scripts'/name,snapshot/name)
bpy.context.preferences.filepaths.save_version=0
native=out/'murderbird-appearance.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native))
groups={}
for obj in list(bpy.context.scene.objects):
    if obj.type!='MESH':continue
    obj.hide_set(False);obj.hide_render=False
    groups.setdefault((obj.parent,obj.get('exteriorEras'),obj.get('region'),obj.get('surfaceRole')),[]).append(obj)
for (parent,era,region,role),objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    if len(objects)>1:bpy.ops.object.join()
    obj=bpy.context.object;obj.name=f'{parent.name}-{region}-{role}-{era}'
    obj['exteriorEras']=era;obj['region']=region;obj['surfaceRole']=role
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:obj.select_set(obj.type in {'MESH','EMPTY'})
model=out/'murderbird-appearance.glb'
bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_tangents=True)
assert sha(source)==source_sha
record['iteration']=args.iteration
record['geometrySource']={'iteration':args.source_iteration,'nativePath':str(source.relative_to(ROOT)),'nativeSha256':source_sha,'inventoryPath':str((base/'appearance-inventory.json').relative_to(ROOT)),'inventorySha256':sha(base/'appearance-inventory.json'),'beforeGeometryDigest':before,'afterGeometryDigest':after,'geometryAndHierarchyUnchanged':True}
record['notes']['materials']=finish['notes']
record['notes']['refinish']={'imageMapsReplaced':replaced,'rolesRebound':rebound,'scope':'Same frozen geometry; revised image maps and corrected metadata-first hardware material routing.'}
record['upstreamAuthoringScripts']=copy.deepcopy(record['scripts'])
record['scripts']=[{'path':'scripts/'+name,'sha256':sha(snapshot/name)} for name in scripts]
record['authoringSnapshot']=str(snapshot.relative_to(ROOT))
record['generatedFiles']=[{'path':str(f.relative_to(ROOT)),'sha256':sha(f),'bytes':f.stat().st_size} for f in [native,model]]
(out/'appearance-inventory.json').write_text(json.dumps(record,indent=2)+'\n')
print('REFINISH_COMPLETE',json.dumps({'iteration':args.iteration,'geometryUnchanged':before==after,'reboundParts':len(rebound),'modelBytes':model.stat().st_size,'modelSha256':sha(model)}))
