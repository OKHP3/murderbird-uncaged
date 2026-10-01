"""Write-once rejected neck-envelope01 attempt02 from pinned first envelope.
Run from repo root: blender --background --python scripts/build-v38-neck-envelope01.py
"""
from pathlib import Path
import bpy,hashlib,json,math,struct,runpy,shutil
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/whole-character-v38/neck-envelope01/murderbird-v38-neck-envelope01.blend'
BASE_GLB=ROOT/'assets/models/whole-character-v38/neck-envelope01/murderbird-v38-neck-envelope01-rigid.glb'
OUT=ROOT/'assets/models/whole-character-v38/neck-envelope01/attempt02';AUDIT=ROOT/'assets/audit/whole-character-v38/neck-envelope01/attempt02'
NATIVE=OUT/'murderbird-v38-neck-envelope01-attempt02.blend';GLB=OUT/'murderbird-v38-neck-envelope01-attempt02-rigid.glb'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(value,message):
 if not value:raise RuntimeError(message)
require(not NATIVE.exists() and not GLB.exists() and not (AUDIT/'receipt.json').exists(),'Write-once output exists; only a diagnosed pre-export failure with no saved model can resume')
require(sha(BASE)=='081337aa8e7c12f657f5f18dcdf27462491bf89d52b344fcbae52702770022a0','Pinned first neck envelope native hash mismatch')
require(sha(BASE_GLB)=='29c815673c14c7f07d2a6a01b0881a3c2707f8b93e051d874b81625e0953ec19','Pinned first neck envelope GLB hash mismatch')
CANON=Path('/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged')
REFS=[CANON/'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png',CANON/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png',CANON/'assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png',CANON/'assets/img/library/murderbird-unified-mechanic-candidate-2026-09-06.png']
for path in REFS:require(path.is_file() and path.stat().st_size>1000,'Actual reference binary unavailable: '+str(path))
OUT.mkdir(parents=True,exist_ok=True);AUDIT.mkdir(parents=True,exist_ok=True)
for source,label in ((Path(__file__),'executed-builder.py'),(ROOT/'scripts/regions/v38-neck-envelope01.py','executed-region.py')):shutil.copy2(source,AUDIT/label)
def properties(o):return json.loads(json.dumps(dict(o.items()),sort_keys=True,default=lambda v:list(v)))
def matrix(m):return [list(row) for row in m]
def mesh_signature(o):
 data={'verts':[list(v.co) for v in o.data.vertices],'edges':[list(v.vertices) for v in o.data.edges],'faces':[(list(p.vertices),p.material_index,p.use_smooth) for p in o.data.polygons],
 'mats':[m.name if m else None for m in o.data.materials]}
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
def snapshot():
 bpy.context.view_layer.update()
 return {o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'matrixWorld':matrix(o.matrix_world),'matrixLocal':matrix(o.matrix_local),'matrixParentInverse':matrix(o.matrix_parent_inverse),
 'visibility':[o.hide_render,o.hide_viewport,o.hide_get()],'props':properties(o),'meshSignature':mesh_signature(o) if o.type=='MESH' else None,
 'materialSlots':[s.material.name if s.material else None for s in o.material_slots] if o.type=='MESH' else None,
 'modifiers':[(m.name,m.type) for m in o.modifiers]} for o in bpy.data.objects}
def art(path):return {'path':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),'bytes':path.stat().st_size,'sha256':sha(path)}

def materials():
 return {m.name:{'props':properties(m),'diffuse':list(m.diffuse_color),'metallic':m.metallic,'roughness':m.roughness,
 'nodes':[(n.name,n.type,[(i.name,repr(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes] if m.use_nodes else []} for m in bpy.data.materials}

VIEWS=[('full-bird-three-quarter',(-6,-3.5,2.75),(0,-.08,1.03),2.4),('full-bird-profile',(-7,0,2.75),(0,-.08,1.03),2.4),('full-bird-front',(0,-7,2.75),(0,-.08,1.03),2.4),('full-bird-rear',(0,7,2.75),(0,-.08,1.03),2.4)]
def render_views(prefix,views):
 scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
 scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 data=bpy.data.cameras.new('temporary matched ribcage construction review');data.type='ORTHO';camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera;records=[]
 for name,pos,target,scale in views:
  camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
  path=AUDIT/f'{prefix}-{name}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
  records.append({**art(path),'camera':{'position':pos,'target':target,'orthoScale':scale},'size':[1200,1200],'render':'neutral Workbench single color, no cast shadows'})
  print('MEDIA',str(path),flush=True)
 bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(data);scene.camera=None
 return records

def read_glb(path):
 raw=path.read_bytes();magic,version,total=struct.unpack_from('<4sII',raw);require(magic==b'glTF' and version==2 and total==len(raw),'Invalid GLB')
 offset=12;chunks=[]
 while offset<len(raw):
  size,kind=struct.unpack_from('<II',raw,offset);offset+=8;chunks.append((kind,raw[offset:offset+size]));offset+=size
 return chunks,json.loads(chunks[0][1])

def retain_profiles():
 chunks,doc=read_glb(GLB);_,base=read_glb(BASE_GLB);source={m['name']:m for m in base['materials']}
 require(not base.get('images') and not base.get('textures'),'Scope this material transfer separately if texture indices exist')
 for i,material in enumerate(doc['materials']):
  name=material.get('name');require(name in source,'Unexpected material: '+str(name));doc['materials'][i]=json.loads(json.dumps(source[name]))
  profiles=doc['materials'][i].get('extras',{}).get('eraFinishes');require(isinstance(profiles,dict),'Era finishes must reach GLTFLoader as objects')
  require(json.loads(bpy.data.materials[name]['eraFinishes'])==profiles,'Native/GLB era profiles differ: '+name)
 payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4)
 out=bytearray(struct.pack('<4sII',b'glTF',2,0))
 for kind,data in chunks:
  value=payload if kind==0x4e4f534a else data;out+=struct.pack('<II',len(value),kind)+value
 struct.pack_into('<I',out,8,len(out));GLB.write_bytes(out)
 return doc

baseline=json.loads((ROOT/'assets/audit/whole-character-v38/neck-envelope01/receipt.json').read_text())['views']['candidate']
for v in baseline:require(sha(ROOT/v['path'])==v['sha256'],'Reused exact baseline view hash mismatch')
baseline_poses=[]
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=snapshot();material_before=materials()
module=ROOT/'scripts/regions/v38-neck-envelope01.py';regional=runpy.run_path(str(module));contract=regional['apply']();after=snapshot()
removed=set(before)-set(after);added=set(after)-set(before);changed={n for n in set(before)&set(after) if before[n]!=after[n]}
require(removed==set(contract['removedMeshes']) and added==set(contract['addedMeshes'])|set(contract.get('addedNodes',[])) and changed<=set(contract['changedMeshes'])|set(contract['changedNodes']),'Undeclared geometry/object changes')
require(materials()==material_before,'Source material response/profiles changed')
require(all(before[n]==after[n] for n in set(before)&set(after)-changed),'Unrelated source snapshot differs')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));require(snapshot()==after,'Native save/reopen snapshot mismatch')
bpy.ops.object.select_all(action='DESELECT');selected=[o for o in bpy.data.objects if o.type in ('EMPTY','MESH') and o.get('authoringGuide') is not True]
for o in selected:o.hide_set(False);o.hide_viewport=False;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
doc=retain_profiles();names=[n['name'] for n in doc['nodes']];require(len(names)==len(set(names)) and set(names)=={o.name for o in selected},'Rigid node identity mismatch')
parents={doc['nodes'][child]['name']:n['name'] for n in doc['nodes'] for child in n.get('children',[])}
for o in selected:
 if o.parent:require(parents.get(o.name)==o.parent.name,'Rigid node owner changed: '+o.name)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));candidate=render_views('candidate',VIEWS);candidate_poses=[]
NECKVIEWS=[('neck-profile',(-6,0,1.95),(0,-.35,1.41),.68),('neck-three-quarter',(-6,-3.5,2.1),(0,-.35,1.41),.73)]
candidate_poses+=render_views('candidate-rest',NECKVIEWS)
for prefix,model,records in [('candidate',NATIVE,candidate_poses),('source',BASE,baseline_poses)]:
 bpy.ops.wm.open_mainfile(filepath=str(model))
 for name in ['neck','cervical-mid-a','cervical-mid-b','cervical-upper']:
  o=bpy.data.objects[name];o.matrix_basis=o.matrix_basis@Matrix.Rotation(.10675220489501955,4,'X')
 o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(-.5090505059024657,4,'X');o=bpy.data.objects['jaw'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(.025392792943327247,4,'X');bpy.context.view_layer.update();records+=render_views(prefix+'-captured-pitch',NECKVIEWS[:1])
bpy.ops.wm.open_mainfile(filepath=str(BASE));baseline_poses+=render_views('source-rest',NECKVIEWS);bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
for source,label in ((Path(__file__),'executed-builder.py'),(module,'executed-region.py')):shutil.copy2(source,AUDIT/label)
# Reconstructed rigid jaw side blades; no material or other regional changes.
receipt={'status':'Neck-envelope01 broad swept crescent courses and owner-local carriers; visual/support/moving fit unaccepted',
 'inputs':{'native':art(BASE),'glb':art(BASE_GLB),'viewedReferences':[art(p) for p in REFS]},'outputs':{'native':art(NATIVE),'rigidGlb':art(GLB)},
 'recipes':{str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),module)},'executedSourceCopies':['executed-builder.py','executed-region.py'],
 'contract':contract,'changedBeforeSignatures':{n:{'meshSignature':before[n]['meshSignature'],'parent':before[n]['parent']}for n in sorted(changed)},'changedAfterSignatures':{n:{'meshSignature':after[n]['meshSignature'],'parent':after[n]['parent']}for n in sorted(changed)},'newAfterSignatures':{n:{'meshSignature':after[n]['meshSignature'],'parent':after[n]['parent']}for n in sorted(added)},
 'exclusionsDigest':hashlib.sha256(json.dumps({n:before[n] for n in sorted(set(before)-changed-set(removed))},sort_keys=True).encode()).hexdigest(),
 'preservation':{'originalObjectsExactExceptDeclaredNeckMeshes':len(before)-len(changed)-len(removed),'retainedRestWorldTransformsExactExceptDeclaredOwnerChange':True,'leftRestrictionAndRepairLandmarkExact':True,'allUndeclaredGeometryExact':True,'existingMaterialsAndEraProfilesExact':True,'nativeSaveReopenExact':True,'glbNodeNamesAndRigidParentsExact':True,'standardPbrRecordsAndEraFinishesCopiedExactlyFromSourceGlb':True},
 'views':{'baseline':baseline,'candidate':candidate,'baselineAuthoredPoseGlances':baseline_poses,'candidateAuthoredPoseGlances':candidate_poses},
 'poseDirections':{},'poseScope':'Four matched candidate wholebird views and source/candidate rest neck profile/3Q. No pose/finite proof until root visual gate.',
 'limits':['58 neck/throat skins and10 existing yokes only; all non-neck geometry, bearings, joint owners/rests/materials exact; support and moving fit unaccepted.','No runtime edits, production, release or artistic/engineering acceptance.']}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('NECK_ENVELOPE_CHECKPOINT',json.dumps({'outputs':receipt['outputs'],'removed':len(removed),'added':len(added),'changed':len(changed),'protected':len(before)-len(changed)-len(removed)}),flush=True)

(AUDIT/'scope.json').write_text(json.dumps({'changed':contract['changedMeshes'],'added':{n:{'parent':bpy.data.objects[n].parent.name,'exteriorEras':bpy.data.objects[n].get('exteriorEras')}for n in contract['addedMeshes']},'removed':contract['removedMeshes'],'changedNodes':contract['changedNodes']},indent=2)+'\n')
