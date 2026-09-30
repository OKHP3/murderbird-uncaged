"""Build the isolated V38 hip-transition native, rigid-node GLB and matched views."""
from pathlib import Path
import bpy, hashlib, json, math, shutil, sys, struct
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
CANON=Path('/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged')
BASE=CANON/'assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.blend'
BASE_GLB=CANON/'assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.glb'
EXPECTED={'blend':'230f67cfaa69ff5bbd42f6167e290c6511dfe05b49571e94179cb5301e86a32a','glb':'4b7c3d248d69a038795b0a5c7b7742b8a5b77d0a9050b7e5afa32b544b0d4e25'}
OUT=ROOT/'assets/models/whole-character-v38/hip-study01'; AUDIT=ROOT/'assets/audit/whole-character-v38/hip-study01'
OUT.mkdir(parents=True,exist_ok=True); AUDIT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(x,msg):
    if not x: raise RuntimeError(msg)
require(not (OUT/'murderbird-whole-character-v38.blend').exists() and not (OUT/'murderbird-whole-character-v38.glb').exists(), 'Study01 already exists; preserve it and select a new versioned output before regeneration')
require(sha(BASE)==EXPECTED['blend'] and sha(BASE_GLB)==EXPECTED['glb'],'Canonical V37 input hash mismatch')

def mesh_sig(o):
    return hashlib.sha256(json.dumps({'verts':[tuple(round(float(c),8) for c in v.co) for v in o.data.vertices],
        'faces':[(tuple(p.vertices),p.material_index) for p in o.data.polygons],
        'mats':[m.name if m else None for m in o.data.materials]},sort_keys=True).encode()).hexdigest()
def matrix(o):return [[float(o.matrix_world[r][c]) for c in range(4)] for r in range(4)]
def snap():
    return {o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':matrix(o),
        'mesh':mesh_sig(o) if o.type=='MESH' else None,
        'props':{k:str(v) for k,v in o.items() if k not in {'_RNA_UI'}}} for o in bpy.data.objects}

def setup_render():
    scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'
    sh=scene.display.shading; sh.light='STUDIO'; sh.studio_light='paint.sl'; sh.color_type='SINGLE'; sh.single_color=(.56,.58,.60)
    sh.show_shadows=False; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.background_type='WORLD'; scene.world.color=(.12,.13,.14)
    scene.render.resolution_x=scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'
    data=bpy.data.cameras.new('V38 temporary matched review camera'); camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
    views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5)]
    return scene,camera,data,views
def render_views(prefix, views, scene, camera, data, folder):
    receipt=[]
    for name,pos,target,scale in views:
        camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
        scene.render.filepath=str(folder/f'{prefix}-{name}.png');bpy.ops.render.render(write_still=True)
        receipt.append({'file':Path(scene.render.filepath).name,'camera':{'position':pos,'target':target,'orthoScale':scale}})
    return receipt

# Render V37 baselines from the canonical source before the construction fork.
bpy.ops.wm.open_mainfile(filepath=str(BASE)); bpy.context.view_layer.update(); before=snap()
scene,camera,data,views=setup_render(); baseline=render_views('baseline',views,scene,camera,data,AUDIT)
bpy.data.objects.remove(camera,do_unlink=True); bpy.data.cameras.remove(data); scene.camera=None

# Reopen the hash-bound source to keep the baseline render setup out of the native.
bpy.ops.wm.open_mainfile(filepath=str(BASE)); bpy.context.view_layer.update(); before=snap()
region=ROOT/'scripts/regions/v38-hip-transition.py'
exec(compile(region.read_text(),str(region),'exec'),globals())
added=apply(); after=snap()
require(set(after)-set(before)==set(added),'Unexpected object additions')
for name,record in before.items(): require(after[name]==record,'Unchanged V37 object differs: '+name)
require(all(bpy.data.objects[n].type=='MESH' and bpy.data.objects[n].parent for n in added),'Study pieces must be rigid meshes with owners')
require({bpy.data.objects[n].parent.name for n in added}=={'body','left-thigh','right-thigh'},'Unexpected hip study ownership')

scene,camera,data,views=setup_render(); rendered=render_views('after',views,scene,camera,data,AUDIT)
# Bounded articulated clearance glance: swing both retained thigh roots within a
# small step/crouch pose, render, then restore the exact rest matrices.
rest={n:bpy.data.objects[n].matrix_world.copy() for n in ('left-thigh','right-thigh')}
for n,angle in (('left-thigh',.22),('right-thigh',-.16)):
    o=bpy.data.objects[n];o.rotation_euler.x += angle
bpy.context.view_layer.update()
scene.render.filepath=str(AUDIT/'step-pose-check.png');bpy.ops.render.render(write_still=True)
for n,m in rest.items():bpy.data.objects[n].matrix_world=m
bpy.context.view_layer.update()
bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(data);scene.camera=None
native=OUT/'murderbird-whole-character-v38.blend';bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
saved=snap();bpy.ops.wm.open_mainfile(filepath=str(native));require(snap()==saved,'Save/reopen object inventory changed')
# Separate rigid-object GLB derivative: preserve every EMPTY/MESH as its own node;
# omit historical CURVEs exactly as the V37 export recipe does.
glb=OUT/'murderbird-whole-character-v38.glb';bpy.ops.object.select_all(action='DESELECT')
selected=[o for o in bpy.data.objects if o.type in {'EMPTY','MESH'} and o.get('authoringGuide') is not True]
for o in selected:o.hide_set(False);o.hide_viewport=False;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
blob=glb.read_bytes();require(blob[:4]==b'glTF' and struct.unpack_from('<I',blob,4)[0]==2,'Invalid GLB header')
jslen,kind=struct.unpack_from('<II',blob,12);require(kind==0x4e4f534a,'GLB JSON chunk missing')
gltf=json.loads(blob[20:20+jslen]); glb_names=[n['name'] for n in gltf['nodes']]
expected_names=[o.name for o in bpy.data.objects if o.type in {'EMPTY','MESH'} and o.get('authoringGuide') is not True]
require(len(glb_names)==len(set(glb_names)) and set(glb_names)==set(expected_names),'Rigid GLB node identity mismatch')
receipt={'status':'bounded hip-transition construction proposal; not selected, likeness accepted, or engineering validated',
 'base':{'path':str(BASE),'sha256':EXPECTED['blend'],'bytes':BASE.stat().st_size},
 'baseGlb':{'path':str(BASE_GLB),'sha256':EXPECTED['glb'],'bytes':BASE_GLB.stat().st_size},
 'native':{'path':str(native.relative_to(ROOT)),'sha256':sha(native),'bytes':native.stat().st_size},
 'glb':{'path':str(glb.relative_to(ROOT)),'sha256':sha(glb),'bytes':glb.stat().st_size},
 'scripts':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),region]},
 'studyPieces':[{'name':n,'owner':bpy.data.objects[n].parent.name,'role':bpy.data.objects[n].get('surfaceRole'),'eras':bpy.data.objects[n].get('exteriorEras')} for n in added],
 'eraMap':{n:bpy.data.objects[n].get('exteriorEras') for n in added},
 'preservation':{'allBaseObjectsPresent':set(before)==set(after)-set(added),'unmodifiedBaseObjectsExact':True,'baseMaterialsUnchanged':True,'thighPivotsAndExistingOwnersUnchanged':True,'shouldersFeetHeadAndUnrelatedGeometryUnchanged':True,'existingEraGatesPreserved':True,'articulationNodesUnchanged':True},
 'views':{'baseline':baseline,'after':rendered,'targetedStepPose':'step-pose-check.png'},
 'limits':['Annular seat and cheek are shape proposals; dynamic swept clearance is not established.','The study does not resolve the whole-character likeness gaps or imply owner approval.','GLB is a review derivative; no app integration or deployment.']}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('V38_RECEIPT',json.dumps(receipt))
