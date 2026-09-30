"""Write-once body-study02: exact V37 native, rigid GLB and neutral matched views.
Run: blender -b --python scripts/build-v38-body-mass.py
"""
from pathlib import Path
import bpy, hashlib, json, math, struct, runpy
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
CANON=Path('/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged')
BASE=CANON/'assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.blend'
BASE_GLB=CANON/'assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.glb'
EXPECTED={'native':'230f67cfaa69ff5bbd42f6167e290c6511dfe05b49571e94179cb5301e86a32a','glb':'4b7c3d248d69a038795b0a5c7b7742b8a5b77d0a9050b7e5afa32b544b0d4e25'}
OUT=ROOT/'assets/models/whole-character-v38/body-study02'
AUDIT=ROOT/'assets/audit/whole-character-v38/body-study02'
NATIVE=OUT/'murderbird-v38-body-study02.blend';GLB=OUT/'murderbird-v38-body-study02-rigid.glb'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(value,message):
 if not value:raise RuntimeError(message)
require(not OUT.exists() and not AUDIT.exists(),'Write-once study already exists; preserve it and scope a separately named second attempt')
require(sha(BASE)==EXPECTED['native'] and sha(BASE_GLB)==EXPECTED['glb'],'Canonical V37 inputs do not match pinned release receipts')
REFS=[CANON/'context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg',CANON/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png']
for p in REFS:require(p.is_file() and p.stat().st_size>1000,'Reference must be actual binary: '+str(p))
OUT.mkdir(parents=True);AUDIT.mkdir(parents=True)

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

VIEWS=[('three-quarter',(-6,-3.5,2.75),(0,-.08,1.02),2.25),('front',(0,-7,1.65),(0,-.08,1.02),2.25),('side',(-7,0,1.35),(0,-.08,1.02),2.25),('rear',(0,7,1.65),(0,-.08,1.02),2.25)]
def render_setup():
 scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
 scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 data=bpy.data.cameras.new('temporary body study matched camera');data.type='ORTHO';obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj);scene.camera=obj
 return scene,obj,data

def render(prefix,views):
 scene,camera,data=render_setup();result=[]
 for name,pos,target,scale in views:
  camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
  path=AUDIT/f'{prefix}-{name}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
  result.append({**art(path),'camera':{'position':pos,'target':target,'orthoScale':scale},'lighting':'neutral Workbench single color, no cast shadows','size':[1200,1200]})
  print('FIRST_MEDIA',str(path),flush=True)
 bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(data);scene.camera=None
 return result

bpy.ops.wm.open_mainfile(filepath=str(BASE));baseline_views=render('baseline',VIEWS)
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=snapshot()
material_before={m.name:(tuple(m.diffuse_color),m.metallic,m.roughness) for m in bpy.data.materials}
module=ROOT/'scripts/regions/v38-body-mass.py';regional=runpy.run_path(str(module));contract=regional['apply']();after=snapshot()
changed={n for n in before if n in after and before[n]!=after[n]};added=set(after)-set(before);removed=set(before)-set(after)
require(changed<=set(contract['changedMeshes']),'Undeclared object changes: '+str(changed-set(contract['changedMeshes'])))
require(added==set(contract['addedMeshes']) and not removed,'Added/removed object mismatch')
for n in changed:
 old=dict(before[n]);new=dict(after[n]);old.pop('meshSignature');new.pop('meshSignature')
 require(old==new,'Changed mesh owner/rest/visibility/props/material slot differs: '+n)
require(material_before=={m.name:(tuple(m.diffuse_color),m.metallic,m.roughness) for m in bpy.data.materials},'Existing material defaults changed')
require(all(after[n]['type']=='MESH' and after[n]['parent'] in ('body','left-thigh','right-thigh') for n in added),'Invalid rigid added owner')
for n in before:
 if n not in changed:require(before[n]==after[n],'Protected original object differs: '+n)
# Save the actual construction before temporary cameras, display and pose edits.
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));require(snapshot()==after,'Saved native object snapshot differs')
bpy.ops.object.select_all(action='DESELECT')
selected=[o for o in bpy.data.objects if o.type in ('EMPTY','MESH') and o.get('authoringGuide') is not True]
for o in selected:o.hide_set(False);o.hide_viewport=False;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
raw=GLB.read_bytes();size,kind=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+size]);names=[n['name'] for n in doc['nodes']]
require(len(names)==len(set(names)) and set(names)=={o.name for o in selected},'Rigid GLB node identity mismatch')
parents={doc['nodes'][child]['name']:n['name'] for n in doc['nodes'] for child in n.get('children',[])}
for o in selected:
 if o.parent:require(parents.get(o.name)==o.parent.name,'Rigid GLB owner changed: '+o.name)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));candidate_views=render('candidate',VIEWS)
# Authored bounded pose glance. Retained parent rotations only; no telemetry or
# planted-foot/full collision claim. Restore/reopen native before each sample.
pose_views=[]
for name,angles in [('hip-step',{'left-thigh':.30,'right-thigh':-.30}),('crouch',{'left-thigh':-.45,'right-thigh':-.45,'left-shin':.65,'right-shin':.65})]:
 bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
 for owner,angle in angles.items():bpy.data.objects[owner].rotation_euler.x+=angle
 bpy.context.view_layer.update();pose_views+=render(name,[VIEWS[0],VIEWS[2]])
receipt={'status':'Second focused repair of lower-body mass proposal; not selected or owner accepted; not validated engineering',
 'inputs':{'native':art(BASE),'glb':art(BASE_GLB),'references':[art(p) for p in REFS]},'outputs':{'native':art(NATIVE),'rigidGlb':art(GLB)},
 'scripts':{str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),module)},'assignment':contract,'priorStudy':'assets/audit/whole-character-v38/body-study01/receipt.json',
 'changeAllowlist':list(regional['ALLOWLIST']),'actualChangedMeshes':sorted(changed),'addedMeshes':sorted(added),'removedMeshes':[],
 'beforeAfterSignatures':{n:{'before':before[n],'after':after[n]} for n in sorted(changed)},
 'attachmentEraMap':contract['attachments'],
 'preservation':{'unchangedOriginalObjectCount':len(before)-len(changed),'allOriginalObjectsRetained':True,'allOtherOriginalSnapshotsExact':True,
 'pivotsContactAnchorsHeadNeckShouldersFeetLeftLimitsAndEraGatesExact':True,'v28SupportsExact':True,'existingMaterialDefaultsAndSlotsExact':True,'saveReopenSnapshotExact':True,'glbNamesAndRigidParentsExact':True},
 'views':{'baseline':baseline_views,'candidate':candidate_views,'authoredPoseGlance':pose_views},
 'poseGlance':{'hipStepThighRotationXRad':[.30,-.30],'crouchThighRotationXRad':-.45,'crouchShinRotationXRad':.65,'status':'Authored rotations on retained joints; not captured runtime movement or planted-foot certification'},
 'limits':['Second and final focused attempt; preserved body-study01 remains separate. No material fork combined; hip-study01 not selected or loaded.','References guide apparent mass, not recovered dimensions.','Authored pose glance and actual-solid sampled receiving cuts do not certify continuous collision freedom or physical loads.','No runtime integration, full validation suite, release, deployment or owner acceptance.']}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('BODY_STUDY_RECEIPT',json.dumps({'outputs':receipt['outputs'],'changed':len(changed),'added':len(added),'protected':len(before)-len(changed)}),flush=True)
